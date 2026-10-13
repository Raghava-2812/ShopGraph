"""
ShopGraph - Application Configuration Module
app/config.py

This module centralizes application configuration using Pydantic-style or environment-driven
settings. It loads environment variables from .env files and exposes typed configurations for:
  - Neo4j Knowledge Graph connectivity (bolt URI, authentication)
  - SQLite Relational Database connectivity (users, orders, events)
  - JSON Web Token (JWT) authentication & expiration
  - Knowledge Graph recommendation scoring weights
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project backend directory to load the correct .env file
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv()


class Settings:
    """Application settings loaded from environment variables with safe defaults.
    
    Attributes:
        NEO4J_URI (str): Connection URI for Neo4j instance (AuraDB or local bolt protocol).
        NEO4J_USERNAME (str): Authentication username for Neo4j.
        NEO4J_PASSWORD (str): Authentication password for Neo4j.
        DATABASE_URL (str): Connection string for relational application database (SQLite).
        JWT_SECRET (str): Secret key used for signing JWT access tokens.
        JWT_ALGORITHM (str): Cryptographic algorithm for JWT encoding/decoding (HS256).
        JWT_EXPIRE_MINUTES (int): Lifetime of issued authentication tokens (default 7 days).
        APP_NAME (str): Application display name.
        APP_VERSION (str): API version string.
        DEFAULT_TOP_K (int): Default number of recommendations to return if unspecified.
        MAX_TOP_K (int): Upper bound limit for recommendation items per request.
        WEIGHT_*: Dimension weights for the explainable 7-factor recommendation formula.
    """

    # ── Database Connections ──────────────────────────────────────────────────
    # Neo4j Graph Database Configuration (Knowledge Graph)
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    # SQLite Relational Database Configuration (User accounts, carts, orders, events)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopgraph.db")

    # ── Security & Authentication ─────────────────────────────────────────────
    # Secret key for JWT generation; in production this should be provided via environment variables
    JWT_SECRET: str = os.getenv("JWT_SECRET", "shopgraph-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days token expiration

    # ── Application Metadata & Defaults ───────────────────────────────────────
    APP_NAME: str = "ShopGraph E-Commerce API"
    APP_VERSION: str = "2.0.0"
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20

    # ── Recommendation Scoring Dimension Weights ─────────────────────────────
    # Transparent multi-factor recommendation formula weights (sum = 1.0)
    WEIGHT_RELATIONSHIP: float = 0.30     # Direct KG edges: COMPATIBLE_WITH, ACCESSORY, etc.
    WEIGHT_FEATURE: float = 0.20          # Shared product specifications/features overlap
    WEIGHT_CATEGORY: float = 0.15         # Category affinity / same-category alternatives
    WEIGHT_USE_CASE: float = 0.10         # Shared practical use cases (e.g. Gaming, Office Work)
    WEIGHT_USER_INTEREST: float = 0.15    # Personalized signals (view history, search, wishlist)
    WEIGHT_POPULARITY: float = 0.05       # Product rating and review volume baseline
    WEIGHT_RECENCY: float = 0.05          # Recency freshness factor


# Singleton settings instance accessible across all backend modules
settings = Settings()
