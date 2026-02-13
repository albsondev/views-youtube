import sys
import asyncio

# Fix for Windows event loop policy with Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from agent.youtube_agent import YouTubeAgent
from config.settings import settings
from utils.logger import activity_logger


app = FastAPI(
    title="YouTube Automation Agent API",
    description="Educational project for web automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent: Optional[YouTubeAgent] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AutomationRequest(BaseModel):
    channel_url: Optional[str] = None
    video_limit: int = 5
    should_subscribe: bool = True
    should_like: bool = True
    should_comment: bool = True


@app.on_event("startup")
async def startup_event():
    try:
        global agent
        agent = YouTubeAgent()
        # await agent.initialize() - Moved to lazy init to prevent Windows event loop issues
        activity_logger.log_activity("API", "Server started")
    except Exception as e:
        activity_logger.log_activity("API", f"Startup failed: {str(e)}", "error")
        print(f"CRITICAL STARTUP ERROR: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    global agent
    if agent:
        await agent.shutdown()
    activity_logger.log_activity("API", "Server stopped")


@app.get("/")
async def root():
    return {
        "message": "YouTube Automation Agent API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/status")
async def get_status():
    if not agent:
        return {
            "status": "error",
            "is_running": False,
            "current_task": "Agent not initialized",
            "is_logged_in": False
        }
    
    return agent.get_status()


@app.post("/login")
async def login(request: LoginRequest):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent structure not created")
    
    # Lazy initialization
    if not agent.browser.playwright:
        await agent.initialize()
    
    success = await agent.login(request.email, request.password)
    
    if success:
        return {"message": "Login successful", "success": True}
    else:
        raise HTTPException(status_code=401, detail="Login failed")


@app.post("/start")
async def start_automation(
    request: AutomationRequest,
    background_tasks: BackgroundTasks
):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent structure not created")
    
    # Lazy initialization
    if not agent.browser.playwright:
        await agent.initialize()
    
    if agent.is_running:
        raise HTTPException(status_code=400, detail="Agent is already running")
    
    background_tasks.add_task(
        agent.run_automation,
        channel_url=request.channel_url,
        video_limit=request.video_limit,
        should_subscribe=request.should_subscribe,
        should_like=request.should_like,
        should_comment=request.should_comment
    )
    
    return {
        "message": "Automation started",
        "channel_url": request.channel_url or settings.target_channel_url,
        "video_limit": request.video_limit
    }


@app.post("/stop")
async def stop_automation():
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    await agent.stop()
    
    return {"message": "Automation stopped"}


@app.get("/activities")
async def get_activities(limit: int = 50):
    activities = activity_logger.get_recent_activities(limit)
    return {"activities": activities, "count": len(activities)}


@app.delete("/activities")
async def clear_activities():
    activity_logger.clear_activities()
    return {"message": "Activities cleared"}


if __name__ == "__main__":
    # Ensure policy is set if running directly
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False  # Disabled for stability on Windows/Playwright
    )
