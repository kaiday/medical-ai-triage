from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "dummy"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLASSIFY_TIMEOUT_SECONDS: int = 8

    model_config = {"env_file": ".env"}

settings = Settings()
