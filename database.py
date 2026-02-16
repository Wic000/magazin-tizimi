"""Ma'lumotlar bazasi ulanishi - PostgreSQL (Render) yoki SQLite fallback"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Render uchun PORT va DATABASE_URL muhit o'zgaruvchisidan
# SQLite fallback - lokal ishlatish uchun
if os.getenv("DATABASE_URL"):
    db_url = os.getenv("DATABASE_URL")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url, pool_pre_ping=True, pool_size=1, max_overflow=0)
else:
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        f"sqlite:///./data/sklad.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Jadvallarni yaratish"""
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
