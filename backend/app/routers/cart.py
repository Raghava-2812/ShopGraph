"""
ShopGraph - Shopping Cart Router
app/routers/cart.py

This module manages persistent customer shopping carts:
  - GET    /cart: Retrieves the active customer cart, calculating line subtotals and grand total.
  - POST   /cart/items: Adds a product or increments quantity if already present.
  - PATCH  /cart/items/{id}: Modifies line quantity (or removes item if quantity reaches 0).
  - DELETE /cart/items/{id}: Deletes a specific line item from the cart.
  - DELETE /cart: Empties all items from the current user's cart.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, Cart, CartItem, User
from app.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# ── Request Schemas ───────────────────────────────────────────────────────────

class AddItemRequest(BaseModel):
    """Payload schema for adding an item to the shopping cart."""
    product_name: str
    quantity: int = 1
    price: Optional[float] = None


class UpdateItemRequest(BaseModel):
    """Payload schema for altering the quantity of an existing cart item."""
    quantity: int


# ── Helper Functions ──────────────────────────────────────────────────────────

def get_or_create_cart(user_id: int, db: Session) -> Cart:
    """Retrieve an existing user cart, or create and persist a new one if none exists.

    Args:
        user_id (int): Foreign key identifier of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        Cart: Active Cart ORM instance.
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


# ── Route Handlers ────────────────────────────────────────────────────────────

@router.get("")
def get_cart(
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the current user's shopping cart, item breakdown, and total price.

    Args:
        db (Session): Database session.
        current_user (User): Authenticated customer context.

    Returns:
        dict: Cart ID, list of formatted items, total price, and item count.
    """
    cart = get_or_create_cart(current_user.id, db)
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    
    total = sum((item.price or 0) * item.quantity for item in items)
    
    return {
        "cart_id": cart.id,
        "items": [
            {
                "id": item.id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": (item.price or 0) * item.quantity,
            }
            for item in items
        ],
        "total": round(total, 2),
        "item_count": len(items),
    }


@router.post("/items", status_code=201)
def add_to_cart(
    req: AddItemRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Add a product item to the shopping cart, or increase quantity if already present.

    Args:
        req (AddItemRequest): Product name, quantity (min 1), and unit price.
        db (Session): Database session.
        current_user (User): Authenticated customer context.

    Returns:
        dict: Status ('added' or 'updated'), item id, and updated quantity.

    Raises:
        HTTPException: 400 Bad Request if requested quantity is less than 1.
    """
    if req.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    
    cart = get_or_create_cart(current_user.id, db)
    
    # Check if this product is already in the cart to increment quantity
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_name == req.product_name,
    ).first()
    
    if existing:
        existing.quantity += req.quantity
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "item_id": existing.id, "quantity": existing.quantity}
    
    # Otherwise create a new line item
    item = CartItem(
        cart_id=cart.id,
        product_name=req.product_name,
        quantity=req.quantity,
        price=req.price,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"status": "added", "item_id": item.id, "quantity": item.quantity}


@router.patch("/items/{item_id}")
def update_cart_item(
    item_id: int,
    req: UpdateItemRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Update line item quantity, automatically deleting the item if quantity is set to 0.

    Args:
        item_id (int): Primary key of the cart item.
        req (UpdateItemRequest): Updated quantity value.
        db (Session): Database session.
        current_user (User): Authenticated customer context.

    Returns:
        dict: Status ('updated' or 'removed') and current quantity.

    Raises:
        HTTPException: 400 if quantity is negative; 404 if item does not exist in cart.
    """
    if req.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    cart = get_or_create_cart(current_user.id, db)
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.cart_id == cart.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if req.quantity == 0:
        db.delete(item)
        db.commit()
        return {"status": "removed"}
    
    item.quantity = req.quantity
    db.commit()
    return {"status": "updated", "quantity": req.quantity}


@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a specific line item completely from the customer's cart.

    Args:
        item_id (int): Primary key of the cart item.
        db (Session): Database session.
        current_user (User): Authenticated customer context.

    Returns:
        dict: Status confirming removal.

    Raises:
        HTTPException: 404 if item not found.
    """
    cart = get_or_create_cart(current_user.id, db)
    item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.cart_id == cart.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(item)
    db.commit()
    return {"status": "removed"}


@router.delete("")
def clear_cart(
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Empty all items from the current user's shopping cart.

    Args:
        db (Session): Database session.
        current_user (User): Authenticated customer context.

    Returns:
        dict: Confirmation status.
    """
    cart = get_or_create_cart(current_user.id, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"status": "cleared"}

