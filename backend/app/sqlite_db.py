"""
ShopGraph - Relational SQLite Database & ORM Models
app/sqlite_db.py

This module manages the SQLite relational database using SQLAlchemy.
Architecture division:
  - Neo4j stores the product Knowledge Graph (nodes, categories, features, semantic relationships).
  - SQLite stores dynamic user and e-commerce transactional data:
      * User accounts and password hashes
      * Persistent shopping carts and items
      * Customer orders and line items
      * User wishlists
      * User behavioral interaction events (VIEW, SEARCH, ADD_TO_CART, PURCHASE, WISHLIST)
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from app.config import settings

# Engine configuration: check_same_thread=False allows FastAPI multi-threaded request workers to access SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory for generating request-scoped database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for SQLAlchemy models
Base = declarative_base()


# ── ORM Models ────────────────────────────────────────────────────────────────

class User(Base):
    """User account entity for authentication and personalization.
    
    Attributes:
        id (int): Primary key.
        name (str): Full display name of the customer.
        email (str): Unique login email address.
        password_hash (str): Bcrypt hash of the user password.
        created_at (datetime): Timestamp of account creation.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=func.now())


class Cart(Base):
    """Shopping cart entity associated with a single user account.
    
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing users.id.
        created_at (datetime): Cart initialization timestamp.
        updated_at (datetime): Timestamp of last item addition or modification.
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CartItem(Base):
    """Individual product line item inside a user's shopping cart.
    
    Attributes:
        id (int): Primary key.
        cart_id (int): Foreign key referencing carts.id.
        product_name (str): Product identifier name corresponding to Knowledge Graph product.
        quantity (int): Number of units requested.
        price (float): Unit price snapshot at time of addition.
        added_at (datetime): Timestamp when added to cart.
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=True)
    added_at = Column(DateTime, default=func.now())


class Order(Base):
    """Placed order entity representing completed customer checkout.
    
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing users.id.
        status (str): Processing state (e.g. 'Processing', 'Shipped', 'Delivered').
        total_amount (float): Total order monetary amount.
        shipping_name (str): Recipient name.
        shipping_address (str): Delivery street address.
        shipping_city (str): Delivery destination city.
        created_at (datetime): Order submission timestamp.
    """
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
    """Product line item record within a submitted order.
    
    Attributes:
        id (int): Primary key.
        order_id (int): Foreign key referencing orders.id.
        product_name (str): Purchased product name.
        quantity (int): Ordered quantity.
        price (float): Purchase price per item.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=True)


class WishlistItem(Base):
    """Saved product item representing user interest without immediate purchase intent.
    
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing users.id.
        product_name (str): Saved product name.
        added_at (datetime): Timestamp saved to wishlist.
    """
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    added_at = Column(DateTime, default=func.now())


class UserEvent(Base):
    """Behavioral interaction event tracked for personalized recommendation scoring.
    
    Events tracked include:
      - VIEW: Customer viewed a product detail page.
      - SEARCH: Customer queried products via search bar.
      - ADD_TO_CART: Customer added an item to cart.
      - WISHLIST: Customer saved an item to wishlist.
      - PURCHASE: Customer completed purchase during checkout.
    
    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key referencing users.id.
        event_type (str): Type of user action.
        product_name (str | None): Target product name for product-specific events.
        search_query (str | None): Query string for search events.
        category_name (str | None): Category context associated with the action.
        created_at (datetime): Timestamp of occurrence.
    """
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=True)
    search_query = Column(String(500), nullable=True)
    category_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())


# ── Initialization & Database Lifecycle ───────────────────────────────────────

def init_db() -> None:
    """Initialize database tables, apply backward-compatible migrations, and create demo user.
    
    This function:
      1. Creates any missing SQLite tables via SQLAlchemy metadata.
      2. Runs an idempotent column migration for `category_name` in `user_events`.
      3. Automatically seeds the standard demo account (`demo@shopgraph.com` / `demo123`).
    """
    Base.metadata.create_all(bind=engine)

    # Safe migration: ensure category_name column exists in user_events table
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE user_events ADD COLUMN category_name VARCHAR(100)"))
            conn.commit()
        except Exception:
            pass  # column already exists in schema

    print("[OK] SQLite database initialized")

    # Ensure demo user exists for out-of-the-box evaluation and testing
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
    """FastAPI dependency yielding an isolated SQLAlchemy database session.
    
    Closes the session deterministically when the HTTP request completes.
    
    Yields:
        Session: Active SQLAlchemy session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

