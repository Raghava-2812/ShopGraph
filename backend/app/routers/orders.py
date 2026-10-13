"""
ShopGraph - Order Processing & Checkout Router
app/routers/orders.py

This module manages the checkout and order fulfillment lifecycle:
  - POST /orders: Converts active cart into a confirmed order, saves shipping details,
                  dispatches PURCHASE events into user telemetry, and clears the user's cart.
  - GET  /orders: Returns chronological order history for the authenticated customer.
  - GET  /orders/{order_id}: Fetches full order receipt and line items by formatted order ID (e.g. SG-0001).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, Order, OrderItem, Cart, CartItem, UserEvent, User
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


# ── Request Schemas ───────────────────────────────────────────────────────────

class ShippingInfo(BaseModel):
    """Customer shipping destination schema."""
    name: str
    address: str
    city: str


class CreateOrderRequest(BaseModel):
    """Checkout submission payload containing delivery information."""
    shipping: ShippingInfo


# ── Route Handlers ────────────────────────────────────────────────────────────

@router.post("", status_code=201)
def create_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Checkout workflow: convert cart into an order, record PURCHASE telemetry, and clear cart.

    Transaction Steps:
      1. Fetch and validate that the active cart contains items.
      2. Calculate final total order price from item prices and quantities.
      3. Create Order record with shipping details.
      4. Convert each CartItem into an OrderItem.
      5. Insert a PURCHASE UserEvent for each product to immediately feed recommendation signals.
      6. Delete items from CartItem table.
      7. Commit atomic transaction and return formatted order receipt ID.

    Args:
        req (CreateOrderRequest): Delivery name, address, and city.
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Formatted order ID (e.g. SG-0001), order status, and total amount.

    Raises:
        HTTPException: 400 Bad Request if cart is empty.
    """
    # 1. Validate cart contents
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = sum((item.price or 0) * item.quantity for item in items)
    
    # 2. Persist Order entity
    order = Order(
        user_id=current_user.id,
        status="Processing",
        total_amount=round(total, 2),
        shipping_name=req.shipping.name,
        shipping_address=req.shipping.address,
        shipping_city=req.shipping.city,
    )
    db.add(order)
    db.flush()  # Flushes SQL to populate generated order.id
    
    # 3. Create order line items and log PURCHASE events
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price,
        )
        db.add(order_item)
        
        # Ingest PURCHASE event for recommendation personalization
        event = UserEvent(
            user_id=current_user.id,
            event_type="PURCHASE",
            product_name=item.product_name,
        )
        db.add(event)
    
    # 4. Clear shopping cart
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
    """List all previous purchase orders for the authenticated customer.

    Args:
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        list[dict]: List of customer orders with item details, sorted newest first.
    """
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
    """Retrieve full order invoice including shipping address and item details by order ID.

    Args:
        order_id (str): Formatted order ID string (e.g. 'SG-0001' or '1').
        db (Session): Database session.
        current_user (User): Authenticated customer.

    Returns:
        dict: Detailed order invoice and item list.

    Raises:
        HTTPException: 400 for invalid ID format; 404 if order does not exist or belongs to another user.
    """
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

