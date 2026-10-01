from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    app_name: str = "Service AD System"
    app_version: str = "0.0.1"
    log_level: str = "INFO"
    log_json: bool = False
    
    # 서버 및 CORS 설정
    cors_origins: List[str] = ["*"]
    
    # 데이터베이스 및 작업 저장소 설정
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"
    job_ttl_seconds: int = 3600
    
    # AI 모델 및 API 제공자 설정 (OpenAI 및 HuggingFace)
    copy_provider: str = "openai"
    image_provider: str = "huggingface"
    openai_api_key: str = "OPENAI_API_KEY"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Settings:
    return Settings()
