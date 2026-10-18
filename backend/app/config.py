from typing import List, Set
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResumeIQ ATS Analyzer"
    app_version: str = "1.0.0"
    debug: bool | str = False
    
    # Upload limits & constraints
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: Set[str] = {".pdf", ".docx"}
    min_scanned_char_threshold: int = 80  # Minimum characters to consider a page non-scanned
    
    # Security & CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # AI Layer settings
    ai_provider: str = "local"  # "local", "gemini", "mock"
    gemini_api_key: str | None = None
    ai_request_timeout_seconds: int = 30
    
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
