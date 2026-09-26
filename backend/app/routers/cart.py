"""
ShopGraph - Cart Router
app/routers/cart.py

Routes:
  GET    /cart
  POST   /cart/items
  PATCH  /cart/items/{id}
  DELETE /cart/items/{id}
  DELETE /cart
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, Cart, CartItem, User
from app.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


class AddItemRequest(BaseModel):
    product_name: str
    quantity: int = 1
    price: Optional[float] = None


class UpdateItemRequest(BaseModel):
    quantity: int


def get_or_create_cart(user_id: int, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("")
def get_cart(
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's cart with all items."""
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
    """Add a product to the cart. If already present, increase quantity."""
    if req.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    
    cart = get_or_create_cart(current_user.id, db)
    
    # Check if product is already in cart
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_name == req.product_name,
    ).first()
    
    if existing:
        existing.quantity += req.quantity
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "item_id": existing.id, "quantity": existing.quantity}
    
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
    """Update cart item quantity."""
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
    """Remove a specific item from the cart."""
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
    """Clear all items from the cart."""
    cart = get_or_create_cart(current_user.id, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"status": "cleared"}
