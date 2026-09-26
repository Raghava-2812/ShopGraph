"""
ShopGraph - Events Router
app/routers/events.py

Routes:
  POST /events

Records user behavior events:
  VIEW, SEARCH, ADD_TO_CART, REMOVE_FROM_CART, PURCHASE, WISHLIST
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.sqlite_db import get_sqlite_db, UserEvent
from app.auth import get_current_user
from app.sqlite_db import User

router = APIRouter(prefix="/events", tags=["Events"])

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
    """Record a user behavior event."""
    # Normalize event names
    norm_type = req.event_type.upper().strip()
    if norm_type not in ALLOWED_EVENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type. Allowed: {', '.join(sorted(ALLOWED_EVENTS))}",
        )

    # Standardize internal representation
    std_type = norm_type
    if norm_type == "VIEW_PRODUCT":
        std_type = "VIEW"
    elif norm_type == "SEARCH_PRODUCT":
        std_type = "SEARCH"
    elif norm_type == "WISHLIST_PRODUCT":
        std_type = "WISHLIST"
    elif norm_type == "PURCHASE_PRODUCT":
        std_type = "PURCHASE"

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
