"""
ShopGraph - User Behavioral Interaction Events Router
app/routers/events.py

This module ingests telemetry on user browsing and shopping behavior:
  - POST /events: Ingests user actions to drive the personalization scoring dimension.

Tracked Event Types:
  - VIEW / VIEW_PRODUCT: Customer browsed a product detail page.
  - SEARCH / SEARCH_PRODUCT: Customer performed a text query.
  - VIEW_CATEGORY: Customer explored a specific category catalog.
  - ADD_TO_CART / REMOVE_FROM_CART: Items added or removed from shopping bag.
  - WISHLIST / WISHLIST_PRODUCT: Items saved to personal wishlist.
  - PURCHASE / PURCHASE_PRODUCT: Checkout orders placed.
  - CLICK_RECOMMENDATION: Interactions on recommended product cards.

Normalization:
  Event names are canonicalized to standard internal representations (e.g. VIEW_PRODUCT -> VIEW)
  to ensure consistent scoring in the recommendation engine.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, UserEvent, User
from app.auth import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])

# Set of allowed event names supported by the telemetry receiver
ALLOWED_EVENTS = {
    "VIEW", "VIEW_PRODUCT",
    "SEARCH", "SEARCH_PRODUCT",
    "VIEW_CATEGORY",
    "ADD_TO_CART", "REMOVE_FROM_CART",
    "PURCHASE", "PURCHASE_PRODUCT",
    "WISHLIST", "WISHLIST_PRODUCT", "REMOVE_FROM_WISHLIST",
    "CLICK_RECOMMENDATION",
}


class EventRequest(BaseModel):
    """Payload schema representing a recorded user action."""
    event_type: str
    product_name: Optional[str] = None
    search_query: Optional[str] = None
    category_name: Optional[str] = None


@router.post("", status_code=201)
def record_event(
    req: EventRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest and record a customer behavioral event in the SQLite database.

    Args:
        req (EventRequest): Event parameters (event_type, product_name, search_query, category_name).
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated customer associated with the event.

    Returns:
        dict: Confirmation status and standardized event type.

    Raises:
        HTTPException: 400 Bad Request if the event type is unapproved.
    """
    # Normalize event names to uppercase and strip whitespace
    norm_type = req.event_type.upper().strip()
    if norm_type not in ALLOWED_EVENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type. Allowed: {', '.join(sorted(ALLOWED_EVENTS))}",
        )

    # Standardize alias event names to internal canonical forms
    std_type = norm_type
    if norm_type == "VIEW_PRODUCT":
        std_type = "VIEW"
    elif norm_type == "SEARCH_PRODUCT":
        std_type = "SEARCH"
    elif norm_type == "WISHLIST_PRODUCT":
        std_type = "WISHLIST"
    elif norm_type == "PURCHASE_PRODUCT":
        std_type = "PURCHASE"

    # Persist the event record
    event = UserEvent(
        user_id=current_user.id,
        event_type=std_type,
        product_name=req.product_name,
        search_query=req.search_query,
        category_name=req.category_name,
    )
    db.add(event)
    db.commit()
    return {"status": "recorded", "event_type": std_type}

