import asyncio
import random
from typing import List, Dict, Optional

from agent.browser_controller import BrowserController
from config.settings import settings
from utils.logger import activity_logger


class YouTubeNavigator:
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.current_channel_url = settings.target_channel_url
    
    async def navigate_to_channel(self, channel_url: Optional[str] = None):
        url = channel_url or self.current_channel_url
        
        activity_logger.log_activity("Navigation", f"Going to channel: {url}")
        await self.browser.navigate(url)
        await asyncio.sleep(random.uniform(2, 4))
        
        await self._handle_consent_popup()
    
    async def subscribe_to_channel(self) -> bool:
        try:
            activity_logger.log_activity("Subscribe", "Attempting to subscribe")
            
            # Strategy 1: Standard CSS Selectors
            subscribe_selectors = [
                'button[aria-label*="Inscrever"]',
                'button[aria-label*="Subscribe"]',
                'ytd-subscribe-button-renderer button',
                '.ytd-subscribe-button-renderer button',
                '#subscribe-button button',
                'iframe.ytd-subscribe-button-renderer' # Sometimes it's an iframe? Unlikely but possible
            ]
            
            subscribe_button = None
            for selector in subscribe_selectors:
                try:
                    subscribe_button = await self.browser.page.wait_for_selector(selector, timeout=2000)
                    if subscribe_button:
                        activity_logger.log_activity("Subscribe", f"Found button with selector: {selector}")
                        break
                except: continue
            
            # Strategy 2: XPath by text (Fallback)
            if not subscribe_button:
                activity_logger.log_activity("Subscribe", "CSS selectors failed, trying XPath...")
                try:
                    # Look for buttons containing "Inscrever" or "Subscribe"
                    xpath_selectors = [
                        '//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "inscrever")]',
                        '//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "subscribe")]',
                        '//div[@id="subscribe-button"]//button'
                    ]
                    for xpath in xpath_selectors:
                        try:
                            subscribe_button = await self.browser.page.wait_for_selector(xpath, timeout=2000)
                            if subscribe_button:
                                 activity_logger.log_activity("Subscribe", "Found button via XPath")
                                 break
                        except: continue
                except: pass

            if not subscribe_button:
                activity_logger.log_activity("Subscribe", "Subscribe button not found (all strategies failed)", "warning")
                # Take screenshot to debug
                try: await self.browser.screenshot("subscribe_debug") 
                except: pass
                return False
                
            button_text = await subscribe_button.inner_text()
            
            # Check if using the new design where "Inscrito" is a separate state visually
            is_subscribed = False
            
            if "inscrito" in button_text.lower() or "subscribed" in button_text.lower():
                is_subscribed = True
            
            # Also check aria-pressed or attributes
            aria_pressed = await subscribe_button.get_attribute("aria-pressed")
            if aria_pressed == "true":
                is_subscribed = True

            if is_subscribed:
                activity_logger.log_activity("Subscribe", "Already subscribed")
                return True
            
            await subscribe_button.click()
            await asyncio.sleep(random.uniform(2, 3))
            
            # Verification Logic (check for login modal or text change)
            # ... (Rest of existing verification logic matches what we have)
            
            # Check for login modal (if not logged in)
            login_modal = await self.browser.page.query_selector('ytd-modal-with-title-renderer, iframe[src*="accounts.google.com"]')
            if login_modal:
                 activity_logger.log_activity("Subscribe", "Failed: Login required", "error")
                 try:
                     close_btn = await self.browser.page.query_selector('button[aria-label="Fechar"], button[aria-label="Close"]')
                     if close_btn: await close_btn.click()
                 except: pass
                 return False

            # Re-check button status
            # Use JS to find button again by text to be sure
            is_now_subscribed = await self.browser.page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const subBtn = buttons.find(b => 
                        b.innerText.toLowerCase().includes('inscrito') || 
                        b.innerText.toLowerCase().includes('subscribed')
                    );
                    return !!subBtn;
                }
            """)
            
            if is_now_subscribed:
                activity_logger.log_activity("Subscribe", "Successfully subscribed")
                return True
            else:
                 activity_logger.log_activity("Subscribe", "Failed: Subscription status did not change", "warning")
                 return False
            
        except Exception as e:
            activity_logger.log_activity(
                "Subscribe", 
                f"Failed: {str(e)}", 
                "error"
            )
            return False
    
    async def get_channel_videos(self, limit: int = 10) -> List[Dict]:
        try:
            activity_logger.log_activity("Videos", f"Fetching up to {limit} videos")
            
            # Try to find "Videos" tab first, fallback to "Shorts"
            tabs_to_try = [
                {'text': 'Vídeos', 'selector': 'yt-tab-shape:has-text("Vídeos"), yt-tab-shape:has-text("Videos")'},
                {'text': 'Shorts', 'selector': 'yt-tab-shape:has-text("Shorts")'}
            ]
            
            videos = []
            for tab_info in tabs_to_try:
                try:
                    tab = await self.browser.page.wait_for_selector(tab_info['selector'], timeout=3000)
                    if tab:
                        activity_logger.log_activity("Videos", f"Switching to {tab_info['text']} tab")
                        await tab.click()
                        await asyncio.sleep(2)
                        
                        # Scroll to load more if needed
                        await self.browser.page.evaluate("window.scrollTo(0, 500)")
                        await asyncio.sleep(1)
                        
                        # Extract videos based on tab type
                        if tab_info['text'] == 'Shorts':
                            # Shorts selectors
                            video_elements = await self.browser.page.query_selector_all(
                                'ytd-rich-item-renderer a[href*="/shorts/"], ytd-reel-item-renderer a'
                            )
                        else:
                            # Standard video selectors
                            video_elements = await self.browser.page.query_selector_all(
                                'ytd-rich-item-renderer a#video-title-link'
                            )
                        
                        for element in video_elements[:limit]:
                            try:
                                # For shorts we might need to get the href and construct a title if title is missing
                                url = await element.get_attribute('href')
                                title = await element.get_attribute('title') or f"Short Video {url.split('/')[-1]}"
                                
                                if url:
                                    full_url = f"https://www.youtube.com{url}" if url.startswith('/') else url
                                    # Dedup
                                    if not any(v['url'] == full_url for v in videos):
                                        videos.append({
                                            'title': title,
                                            'url': full_url
                                        })
                            except: continue
                        
                        if videos:
                            break # Found videos in this tab
                except:
                    continue # Try next tab
            
            activity_logger.log_activity("Videos", f"Found {len(videos)} videos total")
            return videos
            
        except Exception as e:
            activity_logger.log_activity(
                "Videos", 
                f"Failed to fetch videos: {str(e)}", 
                "error"
            )
            return []
    
    async def _handle_consent_popup(self):
        try:
            accept_button = await self.browser.page.wait_for_selector(
                'button[aria-label*="Aceitar"], button[aria-label*="Accept"]',
                timeout=3000
            )
            await accept_button.click()
            await asyncio.sleep(1)
            activity_logger.log_activity("Popup", "Accepted consent")
        except:
            pass
