"""Konfiguratsiya - PostgreSQL yoki SQLite fallback"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/sklad_db"
    )
    # SQLite fallback
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "data/sklad.db")
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sklad-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 soat
    # Backup
    BACKUP_DIR: str = "backups"
    
    class Config:
        env_file = ".env"


settings = Settings()
