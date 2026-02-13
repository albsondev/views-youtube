import asyncio
from typing import Optional, List, Dict
from enum import Enum

from agent.browser_controller import BrowserController
from agent.account_manager import AccountManager
from agent.youtube_navigator import YouTubeNavigator
from agent.video_watcher import VideoWatcher
from agent.interaction_handler import InteractionHandler
from config.settings import settings
from utils.logger import activity_logger


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class YouTubeAgent:
    def __init__(self):
        self.browser = BrowserController()
        self.account_manager: Optional[AccountManager] = None
        self.navigator: Optional[YouTubeNavigator] = None
        self.watcher: Optional[VideoWatcher] = None
        self.interaction: Optional[InteractionHandler] = None
        
        self.status = AgentStatus.IDLE
        self.current_task = ""
        self.is_running = False
    
    async def initialize(self):
        activity_logger.log_activity("Agent", "Initializing agent")
        
        await self.browser.start()
        
        self.account_manager = AccountManager(self.browser)
        self.navigator = YouTubeNavigator(self.browser)
        self.watcher = VideoWatcher(self.browser)
        self.interaction = InteractionHandler(self.browser)
        
        loaded = await self.browser.load_session()
        
        if loaded:
            is_logged_in = await self.account_manager.check_login_status()
            if not is_logged_in:
                activity_logger.log_activity(
                    "Agent", 
                    "Session expired, login required", 
                    "warning"
                )
        
        self.status = AgentStatus.IDLE
        activity_logger.log_activity("Agent", "Agent initialized successfully")
    
    async def login(self, email: Optional[str] = None, password: Optional[str] = None):
        if not self.browser.is_healthy():
            activity_logger.log_activity("Agent", "Browser unhealthy, restarting...", "warning")
            await self.shutdown()
            await self.initialize()
            
        if not self.account_manager:
            await self.initialize()
        
        success = await self.account_manager.login(email, password)
        return success
    
    async def run_automation(
        self,
        channel_url: Optional[str] = None,
        video_limit: int = 5,
        should_subscribe: bool = True,
        should_like: bool = True,
        should_comment: bool = True
    ):
        if self.is_running:
            activity_logger.log_activity(
                "Agent", 
                "Already running", 
                "warning"
            )
            return
        
        self.is_running = True
        self.status = AgentStatus.RUNNING
        
        try:
            if not self.account_manager.is_logged_in:
                activity_logger.log_activity(
                    "Agent", 
                    "Not logged in, please login first", 
                    "error"
                )
                self.status = AgentStatus.ERROR
                return
            
            # Verify login BEFORE starting any navigation
            if not await self.account_manager.ensure_logged_in():
                 activity_logger.log_activity(
                    "Agent", 
                    "Not logged in. Attempting to restore session...", 
                    "warning"
                )
                 # Give it one more try with full login if needed inside ensure_logged_in
            
            if not self.account_manager.is_logged_in:
                 activity_logger.log_activity("Agent", "Critical: Could not log in. Aborting.", "error")
                 self.status = AgentStatus.ERROR
                 return

            self.current_task = "Navigating to channel"
            await self.navigator.navigate_to_channel(channel_url)
            
            if should_subscribe:
                self.current_task = "Subscribing to channel"
                await self.navigator.subscribe_to_channel()
            
            self.current_task = "Fetching videos"
            videos = await self.navigator.get_channel_videos(limit=video_limit)
            
            if not videos:
                activity_logger.log_activity(
                    "Agent", 
                    "No videos found", 
                    "warning"
                )
                return
            
            for idx, video in enumerate(videos, 1):
                if not self.is_running:
                    activity_logger.log_activity("Agent", "Automation stopped by user")
                    break
                
                # Health Check
                if not self.browser.is_healthy():
                    activity_logger.log_activity("Agent", "Browser crashed, attempting to recover...", "error")
                    # We could try to restart, but it breaks the flow. Better to abort cleanly.
                    self.status = AgentStatus.ERROR 
                    return
                
                self.current_task = f"Processing video {idx}/{len(videos)}"
                
                # Verify login BEFORE starting any navigation
                # ... (rest of code)
                
                # Ensure we are still logged in before starting actions
                if not await self.account_manager.ensure_logged_in():
                    activity_logger.log_activity("Agent", "Lost login session and failed to restore. Skipping actions.", "error")
                    continue
                
                await self.watcher.watch_video(video['url'])
                
                if should_like:
                    await self.interaction.random_delay()
                    await self.interaction.like_video()
                
                if should_comment:
                    await self.interaction.random_delay()
                    video_info = await self.watcher.get_video_info()
                    await self.interaction.post_comment(video_info.get('title', ''))
                
                await self.interaction.random_delay()
            
            activity_logger.log_activity(
                "Agent", 
                f"Completed automation for {len(videos)} videos"
            )
            
        except Exception as e:
            activity_logger.log_activity(
                "Agent", 
                f"Error during automation: {str(e)}", 
                "error"
            )
            self.status = AgentStatus.ERROR
            
        finally:
            self.is_running = False
            self.status = AgentStatus.IDLE
            self.current_task = ""
    
    async def stop(self):
        activity_logger.log_activity("Agent", "Stopping automation")
        self.is_running = False
        self.status = AgentStatus.IDLE
    
    async def shutdown(self):
        activity_logger.log_activity("Agent", "Shutting down agent")
        self.is_running = False
        await self.browser.close()
        self.status = AgentStatus.IDLE
    
    def get_status(self) -> Dict:
        return {
            "status": self.status.value,
            "is_running": self.is_running,
            "current_task": self.current_task,
            "is_logged_in": self.account_manager.is_logged_in if self.account_manager else False
        }
