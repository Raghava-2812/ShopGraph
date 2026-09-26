"""
ShopGraph - Configuration
app/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopgraph.db")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "shopgraph-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    APP_NAME: str = "ShopGraph E-Commerce API"
    APP_VERSION: str = "2.0.0"
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20


settings = Settings()
