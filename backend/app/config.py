from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/news_analyzer"
    gnews_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-nano"
    cors_origins: str = "http://localhost:5173"
    gnews_base_url: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
