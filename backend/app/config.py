"""
ShopGraph - Configuration
app/config.py

Loads environment variables using python-dotenv.
All Neo4j credentials are read from the .env file — never hard-coded.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file from the backend directory (or project root)
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    # API settings
    APP_NAME: str = "ShopGraph Recommendation API"
    APP_VERSION: str = "1.0.0"
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20


settings = Settings()
