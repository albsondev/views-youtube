import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import json


class ActivityLogger:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.activities: List[Dict] = []
        self._setup_logger()
    
    def _setup_logger(self):
        log_file = self.log_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("YouTubeAgent")
    
    def log_activity(self, action: str, details: str = "", status: str = "success"):
        activity = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status
        }
        
        self.activities.append(activity)
        self.logger.info(f"{action} - {details} [{status}]")
        
        return activity
    
    def get_recent_activities(self, limit: int = 50) -> List[Dict]:
        return self.activities[-limit:]
    
    def clear_activities(self):
        self.activities.clear()


activity_logger = ActivityLogger()
