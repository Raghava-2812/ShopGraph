"""
ShopGraph - Database & Knowledge Graph Seed Script
app/seed.py

Usage:
    python -m app.seed
    or
    python scripts/seed_expanded_kg.py

Initializes:
  1. Neo4j Knowledge Graph with 83 products, 19 categories, 26 brands, 36 features, 13 use cases, 270+ relationships
  2. SQLite Database with tables, demo user (demo@shopgraph.com / demo123), and sample interaction history
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.config import settings
from app.sqlite_db import init_db, SessionLocal, User, UserEvent, Cart, CartItem, Order, OrderItem, WishlistItem
from app.auth import hash_password
from app.database import get_db
from app.kg_loader import load_all


def seed_demo_user_history():
    """Seeds rich interaction history for demo@shopgraph.com for demonstration."""
    print("\n[START] Seeding demo user and interaction history into SQLite...")
    init_db()
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@shopgraph.com").first()
        if not demo_user:
            demo_user = User(
                name="Demo User",
                email="demo@shopgraph.com",
                password_hash=hash_password("demo123"),
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("[OK] Created demo user: demo@shopgraph.com")
        else:
            print("[OK] Found existing demo user: demo@shopgraph.com")

        # Clear existing demo events to avoid duplicates on re-seed
        db.query(UserEvent).filter(UserEvent.user_id == demo_user.id).delete()
        db.query(CartItem).filter(CartItem.cart_id.in_(
            db.query(Cart.id).filter(Cart.user_id == demo_user.id)
        )).delete()
        db.query(WishlistItem).filter(WishlistItem.user_id == demo_user.id).delete()

        # Seed realistic interactions:
        # 1. VIEW events (Laptops & Tech)
        view_products = [
            ("Dell Inspiron 15", "Laptops"),
            ("HP Pavilion 15", "Laptops"),
            ("Logitech MX Master 3S", "Mice"),
            ("Apple MacBook Air M3", "Laptops"),
        ]
        for prod, cat in view_products:
            ev = UserEvent(
                user_id=demo_user.id,
                event_type="VIEW",
                product_name=prod,
                search_query=None,
                category_name=cat,
            )
            db.add(ev)

        # 2. SEARCH events
        searches = ["laptop", "mouse", "dell"]
        for q in searches:
            ev = UserEvent(
                user_id=demo_user.id,
                event_type="SEARCH",
                product_name=None,
                search_query=q,
                category_name=None,
            )
            db.add(ev)

        # 3. ADD_TO_CART event + Cart Item (Dell USB-C Hub)
        cart = db.query(Cart).filter(Cart.user_id == demo_user.id).first()
        if not cart:
            cart = Cart(user_id=demo_user.id)
            db.add(cart)
            db.commit()
            db.refresh(cart)

        cart_item = CartItem(
            cart_id=cart.id,
            product_name="Dell USB-C Hub",
            quantity=1,
            price=4499.0,
        )
        db.add(cart_item)
        db.add(UserEvent(
            user_id=demo_user.id,
            event_type="ADD_TO_CART",
            product_name="Dell USB-C Hub",
            category_name="USB Hubs",
        ))

        # 4. WISHLIST item + event (Sony WH-1000XM5)
        wish = WishlistItem(
            user_id=demo_user.id,
            product_name="Sony WH-1000XM5",
        )
        db.add(wish)
        db.add(UserEvent(
            user_id=demo_user.id,
            event_type="WISHLIST",
            product_name="Sony WH-1000XM5",
            category_name="Headphones",
        ))

        db.commit()
        print("[OK] Seeded demo history: 4 Views, 3 Searches, 1 Cart item, 1 Wishlist item")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to seed demo user history: {e}")
    finally:
        db.close()


def seed_neo4j_kg():
    """Seeds the full expanded Knowledge Graph into Neo4j if reachable."""
    print("\n[START] Connecting to Neo4j to seed Knowledge Graph...")
    try:
        with get_db() as db:
            if getattr(db, "_use_fallback", False):
                print("[INFO] Neo4j is offline. Using in-memory Knowledge Graph fallback.")
                return
            load_all(db)
    except Exception as e:
        print(f"[WARN] Neo4j seeding skipped (connection offline: {e}). In-memory KG will be used automatically.")


def main():
    print("=" * 60)
    print("  ShopGraph - Knowledge Graph & App Seeder")
    print("=" * 60)
    seed_demo_user_history()
    seed_neo4j_kg()
    print("\n[DONE] ShopGraph seeding complete!\n")


if __name__ == "__main__":
    main()
