from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    target_channel_url: str = "https://www.youtube.com/@example"
    headless_mode: bool = False
    browser_timeout: int = 30000
    
    min_watch_time: int = 30
    max_watch_time: int = 180
    action_delay_min: int = 2
    action_delay_max: int = 5
    
    openai_api_key: Optional[str] = None
    use_ai_comments: bool = False
    
    google_email: Optional[str] = None
    google_password: Optional[str] = None
    
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
