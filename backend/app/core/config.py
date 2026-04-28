from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLASSIFY_TIMEOUT_SECONDS: int = 8

    class Config:
        env_file = ".env"

settings = Settings()
