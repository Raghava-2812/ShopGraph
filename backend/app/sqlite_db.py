"""
ShopGraph - SQLite Database
app/sqlite_db.py

Manages SQLite database for application data:
  - users, carts, orders, order_items, user_events
Neo4j remains the Knowledge Graph (products, relationships).
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── ORM Models ────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=func.now())


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=True)
    added_at = Column(DateTime, default=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), default="Processing")
    total_amount = Column(Float, default=0.0)
    shipping_name = Column(String(200), nullable=True)
    shipping_address = Column(Text, nullable=True)
    shipping_city = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=True)


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    added_at = Column(DateTime, default=func.now())


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # VIEW, SEARCH, ADD_TO_CART, WISHLIST, etc.
    product_name = Column(String(200), nullable=True)
    search_query = Column(String(500), nullable=True)
    category_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())


# ── Init ──────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables if they don't exist and ensure demo user exists."""
    Base.metadata.create_all(bind=engine)

    # Safe migration: ensure category_name column exists in user_events
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE user_events ADD COLUMN category_name VARCHAR(100)"))
            conn.commit()
        except Exception:
            pass  # column already exists

    print("[OK] SQLite database initialized")

    # Ensure demo user exists
    db = SessionLocal()
    try:
        from app.auth import hash_password
        existing = db.query(User).filter(User.email == "demo@shopgraph.com").first()
        if not existing:
            demo_user = User(
                name="Demo User",
                email="demo@shopgraph.com",
                password_hash=hash_password("demo123"),
            )
            db.add(demo_user)
            db.commit()
            print("[OK] Demo user created: demo@shopgraph.com / demo123")
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def get_sqlite_db():
    """Dependency: yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
