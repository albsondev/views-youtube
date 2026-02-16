import sys
import asyncio
import uvicorn
import traceback

if sys.platform == "win32":
    # Critical for Playwright on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from main import app
except Exception as e:
    print("Failed to import app from main:")
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    try:
        print("Starting Uvicorn server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print("Failed to start server:")
        traceback.print_exc()
