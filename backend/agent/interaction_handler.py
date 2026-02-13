import asyncio
import random

from agent.browser_controller import BrowserController
from agent.comment_generator import CommentGenerator
from config.settings import settings
from utils.logger import activity_logger


class InteractionHandler:
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.comment_generator = CommentGenerator()
    
    async def like_video(self) -> bool:
        try:
            activity_logger.log_activity("Like", "Attempting to like video")
            
            # Strategy 1: Specific Like Button Containers (New Layouts)
            like_selectors = [
                '#segmented-like-button button', 
                'like-button-view-model button',
                'ytd-segmented-like-dislike-button-renderer button[aria-label*="Gostei"]',
                'ytd-segmented-like-dislike-button-renderer button[aria-label*="Like"]',
                'button[aria-label^="Gostei de"]',
                'button[aria-label^="Like this video"]',
                '#top-level-buttons-computed > ytd-toggle-button-renderer:first-child button', # Old layout
                'button[aria-label="Gosto"]' # PT-PT fallbak
            ]
            
            like_button = None
            for selector in like_selectors:
                try:
                    like_button = await self.browser.page.wait_for_selector(selector, timeout=2000)
                    if like_button:
                        activity_logger.log_activity("Like", f"Found like button: {selector}")
                        break
                except: continue
            
            if not like_button:
                # Strategy 2: XPath Fallback
                try:
                     xpath_selectors = [
                         '//button[contains(@aria-label, "Gostei")]',
                         '//button[contains(@aria-label, "like this video")]'
                     ]
                     for xpath in xpath_selectors:
                         try:
                             like_button = await self.browser.page.wait_for_selector(xpath, timeout=2000)
                             if like_button: break
                         except: continue
                except: pass

            if not like_button:
                activity_logger.log_activity("Like", "Like button not found", "warning")
                return False
            
            aria_pressed = await like_button.get_attribute('aria-pressed')
            
            if aria_pressed == 'true':
                activity_logger.log_activity("Like", "Already liked")
                return True
            
            await like_button.click()
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            activity_logger.log_activity("Like", "Successfully liked video")
            return True
            
        except Exception as e:
            activity_logger.log_activity(
                "Like", 
                f"Failed: {str(e)}", 
                "error"
            )
            return False
    
    async def post_comment(self, video_title: str = "", custom_comment: str = "") -> bool:
        try:
            activity_logger.log_activity("Comment", "Preparing to comment")
            
            await self.browser.page.evaluate("window.scrollTo(0, 800)")
            await asyncio.sleep(random.uniform(1, 2))
            
            comment_box = await self.browser.page.wait_for_selector(
                'ytd-comment-simplebox-renderer div#placeholder-area',
                timeout=5000
            )
            await comment_box.click()
            await asyncio.sleep(random.uniform(0.5, 1))
            
            text_area = await self.browser.page.wait_for_selector(
                'ytd-comment-simplebox-renderer div#contenteditable-root',
                timeout=5000
            )
            
            if custom_comment:
                comment = custom_comment
            else:
                comment = self.comment_generator.generate(video_title)
            
            await self._type_like_human(text_area, comment)
            
            await asyncio.sleep(random.uniform(1, 2))
            
            # Try multiple selectors for the submit check/button
            submit_selectors = [
                'ytd-comment-simplebox-renderer #submit-button',
                'ytd-comment-dialog-renderer #submit-button',
                '#submit-button',
                'button[aria-label="Comentar"]',
                'button[aria-label="Comment"]'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await self.browser.page.wait_for_selector(
                        selector,
                        timeout=2000,
                        state='visible'
                    )
                    if submit_button:
                        break
                except:
                    continue
            
            if not submit_button:
                activity_logger.log_activity("Comment", "Could not find submit button", "error")
                return False

            await submit_button.click()
            await asyncio.sleep(random.uniform(1, 2))
            
            activity_logger.log_activity("Comment", f"Posted: {comment[:50]}...")
            return True
            
        except Exception as e:
            activity_logger.log_activity(
                "Comment", 
                f"Failed: {str(e)}", 
                "error"
            )
            return False
    
    async def _type_like_human(self, element, text: str):
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def random_delay(self):
        delay = random.uniform(
            settings.action_delay_min,
            settings.action_delay_max
        )
        activity_logger.log_activity("Delay", f"Waiting {delay:.1f}s")
        await asyncio.sleep(delay)
