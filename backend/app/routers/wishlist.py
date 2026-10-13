"""
ShopGraph - User Wishlist Router
app/routers/wishlist.py

This module manages customer saved items / wishlists:
  - GET    /wishlist: Retrieves all saved items, enriching them with full product catalog data from Neo4j.
  - POST   /wishlist/{name}: Saves a product and logs a WISHLIST event for recommendation scoring.
  - DELETE /wishlist/{name}: Removes a product and logs a REMOVE_FROM_WISHLIST event.
  - GET    /wishlist/check/{name}: Verifies whether a product is currently saved by the active customer.
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
    """Retrieve all wishlisted products for the authenticated user, enriched with graph data.

    Workflow:
      1. Query WishlistItem table for user's saved product names, ordered by date added descending.
      2. Query Neo4j Knowledge Graph in batch to attach current price, ratings, images, and category.
      3. Return preserved chronological ordering.

    Args:
        db (Session): SQLite database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Total count and list of enriched product items.
    """
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
            # Retain user's insertion order
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
    """Add a product to the user's saved wishlist and record a WISHLIST telemetry event.

    Args:
        product_name (str): Title of the product to save.
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Status ('added' or 'already_in_wishlist') and product name.
    """
    existing = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_name == product_name,
    ).first()

    if existing:
        return {"status": "already_in_wishlist", "product_name": product_name}

    item = WishlistItem(user_id=current_user.id, product_name=product_name)
    db.add(item)

    # Ingest WISHLIST event to boost user interest scoring for this category/product
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
    """Remove a product from the user's wishlist and log a REMOVE_FROM_WISHLIST event.

    Args:
        product_name (str): Title of the product to remove.
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Status confirmation and product name.

    Raises:
        HTTPException: 404 Not Found if product is not in wishlist.
    """
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
    """Check whether a specific product is currently saved in the customer's wishlist.

    Args:
        product_name (str): Target product name.
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Boolean `is_wishlisted` flag and product name.
    """
    item = db.query(WishlistItem).filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.product_name == product_name,
    ).first()

    return {"is_wishlisted": item is not None, "product_name": product_name}

