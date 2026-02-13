import asyncio
from typing import Optional

from agent.browser_controller import BrowserController
from config.settings import settings
from utils.logger import activity_logger


class AccountManager:
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.is_logged_in = False
    
    async def login(self, email: Optional[str] = None, password: Optional[str] = None):
        self.email = email or settings.google_email
        self.password = password or settings.google_password
        
        email = self.email
        password = self.password
        
        if not email or not password:
            activity_logger.log_activity(
                "Login", 
                "No credentials provided", 
                "error"
            )
            return False
        
        try:
            activity_logger.log_activity("Login", f"Logging in as {email}")
            
            await self.browser.navigate("https://accounts.google.com/")
            await asyncio.sleep(2)
            
            # Check if we are already logged in (redirected to myaccount)
            if "myaccount.google.com" in self.browser.page.url:
                activity_logger.log_activity("Login", "Already logged in (redirected to myaccount)")
                self.is_logged_in = True
                return True
                
            # Check for "Welcome" header or Avatar which means already logged in
            welcome_header = await self.browser.page.query_selector('h1[id="headingText"] span')
            if welcome_header:
                text = await welcome_header.inner_text()
                if "Bem-vindo" in text or "Welcome" in text:
                     # Verify if it's the welcome back screen (password only) or welcome (already logged)
                     # Usually if we are at prompt, we need to login.
                     pass

            email_input = await self.browser.page.query_selector('input[type="email"]')
            
            # If no email input but URL is accounts.google.com, maybe we are at password screen or list of accounts
            if not email_input:
                # Check for "Choose an account" list
                account_list = await self.browser.page.query_selector('ul.account-list')
                if account_list:
                    # Click on the first account (assuming it's the right one or logic needed)
                    # For now just log
                    activity_logger.log_activity("Login", "Found account list, selecting first one...")
                    await self.browser.page.click('li div[data-email]')
                    await asyncio.sleep(2)
                    # Now should be at password
                
                # Check for password input directly
                password_input = await self.browser.page.query_selector('input[type="password"]')
                if password_input:
                    activity_logger.log_activity("Login", "Already at password screen")
                    await password_input.fill(password)
                    await asyncio.sleep(0.5)
                    next_button = await self.browser.page.wait_for_selector('#passwordNext')
                    await next_button.click()
                    await asyncio.sleep(5)
                    self.is_logged_in = True
                    return True
                
                # If neither, check if we are actually logged in (Avatar top right)
                avatar = await self.browser.page.query_selector('a[aria-label*="Google Account"], a[aria-label*="Conta do Google"]')
                if avatar:
                     activity_logger.log_activity("Login", "Already logged in (Avatar detected)")
                     self.is_logged_in = True
                     return True

            if not email_input:
                 # Last check for url to be sure
                 if "myaccount.google.com" in self.browser.page.url:
                     self.is_logged_in = True
                     return True
                 # Else fail
                 raise Exception("Could not find email input or detect login state")

            await email_input.fill(email)
            await asyncio.sleep(0.5)
            
            next_button = await self.browser.page.wait_for_selector('#identifierNext')
            await next_button.click()
            await asyncio.sleep(3)
            
            password_input = await self.browser.page.wait_for_selector(
                'input[type="password"]',
                timeout=10000
            )
            await password_input.fill(password)
            await asyncio.sleep(0.5)
            
            next_button = await self.browser.page.wait_for_selector('#passwordNext')
            await next_button.click()
            await asyncio.sleep(5)
            
            await self.browser.save_session()
            
            self.is_logged_in = True
            activity_logger.log_activity("Login", "Successfully logged in")
            return True
            
        except Exception as e:
            # Take screenshot on failure
            try:
                await self.browser.screenshot("login_failed")
            except: pass
            
            activity_logger.log_activity(
                "Login", 
                f"Failed: {str(e)}", 
                "error"
            )
            return False
    
    async def ensure_logged_in(self) -> bool:
        """
        Verifies if user is logged in on the current page.
        If not, tries to restore session by clicking 'Sign in' or performing full login.
        """
        try:
            # Check for avatar (logged in indicator)
            avatar = await self.browser.page.query_selector('button#avatar-btn, img.style-scope.yt-img-shadow')
            if avatar:
                self.is_logged_in = True
                return True
            
            activity_logger.log_activity("Login Check", "Session lost, attempting to restore...")
            self.is_logged_in = False # Force false until proven true
            
            # Check for "Sign in" button on YouTube
            sign_in_button = await self.browser.page.query_selector('a[href*="accounts.google.com"], button[aria-label*="Fazer login"]')
            
            if sign_in_button:
                activity_logger.log_activity("Login Check", "Clicking 'Sign in' button to restore session")
                await sign_in_button.click()
                await asyncio.sleep(5)
                
                # Check what happened: Avatar (success) or Login Page (needs credentials)
                avatar = await self.browser.page.query_selector('button#avatar-btn, img.style-scope.yt-img-shadow')
                if avatar:
                    self.is_logged_in = True
                    activity_logger.log_activity("Login Check", "Session restored successfully (Cookie auto-login)")
                    return True
                
                # Check for Email Input (Redirected to login)
                email_input = await self.browser.page.query_selector('input[type="email"]')
                if email_input:
                     activity_logger.log_activity("Login Check", "Redirected to login page. Performing full login...")
                     if hasattr(self, 'email') and hasattr(self, 'password'):
                         return await self.login(self.email, self.password)
                     else:
                         activity_logger.log_activity("Login Check", "Cannot login: No credentials saved", "error")
                         return False

            # If still not logged in, try full login if we have credentials
            if hasattr(self, 'email') and hasattr(self, 'password'):
                activity_logger.log_activity("Login Check", "Performing full re-login")
                return await self.login(self.email, self.password)
            
            return False
            
        except Exception as e:
            self.is_logged_in = False
            activity_logger.log_activity("Login Check", f"Failed to restore session: {str(e)}", "error")
            return False

    async def check_login_status(self) -> bool:
        try:
            # Don't navigate away if possible, just check current page element
            # But the original method navigated. Let's keep it for initial check, 
            # but use ensure_logged_in for in-flow checks.
            
            # If we are already on youtube, just check
            if "youtube.com" in self.browser.page.url:
                 return await self.ensure_logged_in()
            
            await self.browser.navigate("https://www.youtube.com/")
            await asyncio.sleep(2)
            
            return await self.ensure_logged_in()
                
        except Exception as e:
            activity_logger.log_activity(
                "Login Check", 
                f"Error: {str(e)}", 
                "error"
            )
            return False
