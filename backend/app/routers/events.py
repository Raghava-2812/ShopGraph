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

ALLOWED_EVENTS = {"VIEW", "SEARCH", "ADD_TO_CART", "REMOVE_FROM_CART", "PURCHASE", "WISHLIST"}


class EventRequest(BaseModel):
    event_type: str
    product_name: Optional[str] = None
    search_query: Optional[str] = None


@router.post("", status_code=201)
def record_event(
    req: EventRequest,
    db: Session = Depends(get_sqlite_db),
    current_user: User = Depends(get_current_user),
):
    """Record a user behavior event."""
    if req.event_type not in ALLOWED_EVENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type. Allowed: {', '.join(ALLOWED_EVENTS)}",
        )
    
    event = UserEvent(
        user_id=current_user.id,
        event_type=req.event_type,
        product_name=req.product_name,
        search_query=req.search_query,
    )
    db.add(event)
    db.commit()
    return {"status": "recorded", "event_type": req.event_type}
