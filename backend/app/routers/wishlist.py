"""
ShopGraph - Wishlist Router
app/routers/wishlist.py

Routes:
  GET    /wishlist
  POST   /wishlist/{product_name}
  DELETE /wishlist/{product_name}
  GET    /wishlist/check/{product_name}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.sqlite_db import get_sqlite_db, WishlistItem, UserEvent, User
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("")
def get_wishlist(
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all wishlisted products for the current user."""
    items = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).order_by(WishlistItem.added_at.desc()).all()

    product_names = [item.product_name for item in items]
    products_info = []

    if product_names:
        with get_db() as neo4j_db:
            rows = neo4j_db.run_query(
                """
                MATCH (p:Product)
                WHERE p.name IN $names
                RETURN p.name AS name, p.price AS price, p.original_price AS original_price,
                       p.discount_percentage AS discount_percentage, p.description AS description,
                       p.rating AS rating, p.review_count AS review_count, p.stock AS stock,
                       p.image_url AS image_url, p.category AS category, p.brand AS brand
                """,
                {"names": product_names},
            )
            # Retain insertion order
            row_map = {r["name"]: r for r in rows}
            products_info = [row_map.get(name) for name in product_names if name in row_map]

    return {
        "count": len(products_info),
        "items": products_info,
    }


@router.post("/{product_name}", status_code=201)
def add_to_wishlist(
    product_name: str,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Add a product to the user's wishlist and track the event."""
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_name == product_name,
    ).first()

    if existing:
        return {"status": "already_in_wishlist", "product_name": product_name}

    item = WishlistItem(user_id=current_user.id, product_name=product_name)
    db.add(item)

    # Track WISHLIST event
    event = UserEvent(
        user_id=current_user.id,
        event_type="WISHLIST",
        product_name=product_name,
    )
    db.add(event)
    db.commit()

    return {"status": "added", "product_name": product_name}


@router.delete("/{product_name}")
def remove_from_wishlist(
    product_name: str,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a product from the user's wishlist."""
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_name == product_name,
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not in wishlist")

    db.delete(item)

    # Track REMOVE_FROM_WISHLIST event
    event = UserEvent(
        user_id=current_user.id,
        event_type="REMOVE_FROM_WISHLIST",
        product_name=product_name,
    )
    db.add(event)
    db.commit()

    return {"status": "removed", "product_name": product_name}


@router.get("/check/{product_name}")
def check_wishlist(
    product_name: str,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Check if a product is in the user's wishlist."""
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_name == product_name,
    ).first()

    return {"is_wishlisted": item is not None, "product_name": product_name}
