"""
ShopGraph - Orders Router
app/routers/orders.py

Routes:
  POST /orders
  GET  /orders
  GET  /orders/{order_id}
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, Order, OrderItem, Cart, CartItem, UserEvent, User
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


class ShippingInfo(BaseModel):
    name: str
    address: str
    city: str


class CreateOrderRequest(BaseModel):
    shipping: ShippingInfo


@router.post("", status_code=201)
def create_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Checkout: create order from cart, record PURCHASE events, clear cart."""
    # Get cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = sum((item.price or 0) * item.quantity for item in items)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        status="Processing",
        total_amount=round(total, 2),
        shipping_name=req.shipping.name,
        shipping_address=req.shipping.address,
        shipping_city=req.shipping.city,
    )
    db.add(order)
    db.flush()  # get order.id
    
    # Create order items + PURCHASE events
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price,
        )
        db.add(order_item)
        
        # Record PURCHASE event
        event = UserEvent(
            user_id=current_user.id,
            event_type="PURCHASE",
            product_name=item.product_name,
        )
        db.add(event)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return {
        "order_id": f"SG-{order.id:04d}",
        "status": order.status,
        "total_amount": order.total_amount,
        "message": f"Order placed successfully! Order ID: SG-{order.id:04d}",
    }


@router.get("")
def list_orders(
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """List all orders for the current user."""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(
        Order.created_at.desc()
    ).all()
    
    result = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        result.append({
            "order_id": f"SG-{order.id:04d}",
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": [
                {"product_name": i.product_name, "quantity": i.quantity, "price": i.price}
                for i in items
            ],
        })
    return result


@router.get("/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific order by ID."""
    try:
        numeric_id = int(order_id.replace("SG-", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    order = db.query(Order).filter(
        Order.id == numeric_id, Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return {
        "order_id": f"SG-{order.id:04d}",
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_name": order.shipping_name,
        "shipping_address": order.shipping_address,
        "shipping_city": order.shipping_city,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [
            {"product_name": i.product_name, "quantity": i.quantity, "price": i.price}
            for i in items
        ],
    }
