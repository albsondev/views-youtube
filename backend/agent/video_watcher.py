import asyncio
import random

from agent.browser_controller import BrowserController
from config.settings import settings
from utils.logger import activity_logger


class VideoWatcher:
    def __init__(self, browser: BrowserController):
        self.browser = browser
    
    async def watch_video(self, video_url: str) -> bool:
        try:
            activity_logger.log_activity("Watch", f"Opening video: {video_url}")
            
            await self.browser.navigate(video_url)
            await asyncio.sleep(random.uniform(2, 4))
            
            await self._skip_ads()
            
            await self._play_video()
            
            watch_duration = random.randint(
                settings.min_watch_time,
                settings.max_watch_time
            )
            
            activity_logger.log_activity(
                "Watch", 
                f"Watching for {watch_duration} seconds"
            )
            
            await self._simulate_watching(watch_duration)
            
            activity_logger.log_activity("Watch", "Finished watching video")
            return True
            
        except Exception as e:
            activity_logger.log_activity(
                "Watch", 
                f"Failed: {str(e)}", 
                "error"
            )
            return False
    
    async def _play_video(self):
        try:
            video_element = await self.browser.page.wait_for_selector(
                'video',
                timeout=10000
            )
            
            is_playing = await self.browser.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    return video && !video.paused;
                }
            """)
            
            if not is_playing:
                play_button = await self.browser.page.query_selector(
                    'button.ytp-large-play-button'
                )
                if play_button:
                    await play_button.click()
                    await asyncio.sleep(1)
            
            activity_logger.log_activity("Watch", "Video playing")
            
        except Exception as e:
            activity_logger.log_activity(
                "Watch", 
                f"Play error: {str(e)}", 
                "warning"
            )
    
    async def _skip_ads(self):
        try:
            skip_button = await self.browser.page.wait_for_selector(
                'button.ytp-ad-skip-button, button.ytp-skip-ad-button',
                timeout=5000
            )
            await skip_button.click()
            await asyncio.sleep(1)
            activity_logger.log_activity("Watch", "Skipped ad")
        except:
            pass
    
    async def _simulate_watching(self, duration: int):
        intervals = random.randint(3, 6)
        interval_duration = duration / intervals
        
        for i in range(intervals):
            await asyncio.sleep(interval_duration)
            
            if random.random() < 0.3:
                scroll_amount = random.randint(100, 300)
                await self.browser.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            if random.random() < 0.2:
                await self.browser.page.evaluate("window.scrollBy(0, -200)")
                await asyncio.sleep(random.uniform(0.5, 1))
    
    async def get_video_info(self) -> dict:
        try:
            # Try standard layout
            title_selector = 'h1.ytd-video-primary-info-renderer, yt-formatted-string.ytd-video-primary-info-renderer'
            title_element = await self.browser.page.query_selector(title_selector)
            
            # Try Shorts layout fallback
            if not title_element:
                title_element = await self.browser.page.query_selector('ytd-reel-player-overlay-renderer h2.title, ytd-reel-player-overlay-renderer yt-formatted-string.title')
            
            title = await title_element.text_content() if title_element else ""
            
            description_element = await self.browser.page.query_selector(
                'ytd-text-inline-expander#description-inline-expander, ytd-reel-player-overlay-renderer #description'
            )
            description = await description_element.text_content() if description_element else ""
            
            return {
                'title': title.strip(),
                'description': description.strip()
            }
            
        except Exception as e:
            activity_logger.log_activity(
                "Video Info", 
                f"Failed to get info: {str(e)}", 
                "warning"
            )
            return {'title': "", 'description': ""}
