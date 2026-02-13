from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional
from pathlib import Path
import asyncio

from config.settings import settings
from utils.logger import activity_logger


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
    
    async def start(self):
        activity_logger.log_activity("Browser", "Starting browser")
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=settings.headless_mode,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(settings.browser_timeout)
        
        activity_logger.log_activity("Browser", "Browser started successfully")
    
    async def navigate(self, url: str):
        if not self.page:
            raise RuntimeError("Browser not started")
        
        activity_logger.log_activity("Navigation", f"Navigating to {url}")
        await self.page.goto(url, wait_until='domcontentloaded')
    
    async def screenshot(self, name: str):
        if not self.page:
            return
        
        screenshot_path = self.session_dir / f"{name}.png"
        await self.page.screenshot(path=str(screenshot_path))
        activity_logger.log_activity("Screenshot", f"Saved to {screenshot_path}")
    
    async def save_session(self):
        if not self.context:
            return
        
        storage_state = await self.context.storage_state(
            path=str(self.session_dir / "session.json")
        )
        activity_logger.log_activity("Session", "Session saved")
    
    async def load_session(self):
        session_file = self.session_dir / "session.json"
        
        if not session_file.exists():
            return False
        
        if self.context:
            await self.context.close()
        
        self.context = await self.browser.new_context(
            storage_state=str(session_file),
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='pt-BR'
        )
        
        self.page = await self.context.new_page()
        activity_logger.log_activity("Session", "Session loaded")
        return True
    
    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        activity_logger.log_activity("Browser", "Browser closed")
    
    def is_healthy(self) -> bool:
        """Check if browser process is alive and connected."""
        if not self.browser:
            return False
            
        try:
            return self.browser.is_connected()
        except:
            return False
