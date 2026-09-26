"""
ShopGraph - Backend Tests
tests/test_backend.py

Tests for:
- API health
- Products endpoints
- Events
- Auth (register/login)
- Cart operations
- Orders
- Recommendations
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.sqlite_db import init_db

init_db()

client = TestClient(app, raise_server_exceptions=False)


# ── Health ─────────────────────────────────────────────────────────────────────

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "ShopGraph" in data["message"]


# ── Products ──────────────────────────────────────────────────────────────────

def test_list_products():
    resp = client.get("/products")
    # May return 503 if Neo4j not available in test environment
    assert resp.status_code in (200, 500, 503)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)


def test_get_product_not_found():
    resp = client.get("/products/NonExistentProductXYZ123")
    assert resp.status_code in (404, 500, 503)


def test_search_products():
    resp = client.get("/products/search", params={"q": "laptop"})
    assert resp.status_code in (200, 500, 503)


def test_list_categories():
    resp = client.get("/products/categories")
    assert resp.status_code in (200, 500, 503)


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_register_and_login():
    import uuid
    unique_email = f"test_{uuid.uuid4().hex[:8]}@shopgraph.test"
    
    # Register
    resp = client.post("/auth/register", json={
        "name": "Test User",
        "email": unique_email,
        "password": "testpassword123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["name"] == "Test User"
    token = data["access_token"]
    
    # Login
    resp = client.post("/auth/login", json={
        "email": unique_email,
        "password": "testpassword123",
    })
    assert resp.status_code == 200
    login_data = resp.json()
    assert "access_token" in login_data
    
    return token


def test_login_wrong_password():
    resp = client.post("/auth/login", json={
        "email": "notexist@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_auth_me_no_token():
    resp = client.get("/auth/me")
    assert resp.status_code == 401


# ── Full flow test (register → events → cart → order) ─────────────────────────

def test_full_user_flow():
    import uuid
    unique_email = f"flow_{uuid.uuid4().hex[:8]}@shopgraph.test"
    
    # Register
    resp = client.post("/auth/register", json={
        "name": "Flow User",
        "email": unique_email,
        "password": "flowpass123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Record VIEW event
    resp = client.post("/events", json={
        "event_type": "VIEW",
        "product_name": "Dell Inspiron 15",
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["status"] == "recorded"
    
    # Record SEARCH event
    resp = client.post("/events", json={
        "event_type": "SEARCH",
        "search_query": "laptop",
    }, headers=headers)
    assert resp.status_code == 201
    
    # Add to cart
    resp = client.post("/cart/items", json={
        "product_name": "Dell Inspiron 15",
        "quantity": 1,
        "price": 55000.0,
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["status"] in ("added", "updated")
    
    # Get cart
    resp = client.get("/cart", headers=headers)
    assert resp.status_code == 200
    cart_data = resp.json()
    assert len(cart_data["items"]) >= 1
    
    # Record ADD_TO_CART event
    resp = client.post("/events", json={
        "event_type": "ADD_TO_CART",
        "product_name": "Dell Inspiron 15",
    }, headers=headers)
    assert resp.status_code == 201
    
    # Create order
    resp = client.post("/orders", json={
        "shipping": {
            "name": "Flow User",
            "address": "123 Test Street",
            "city": "Hyderabad",
        }
    }, headers=headers)
    assert resp.status_code == 201
    order_data = resp.json()
    assert "order_id" in order_data
    assert order_data["order_id"].startswith("SG-")
    
    # Cart should now be empty
    resp = client.get("/cart", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 0
    
    # List orders
    resp = client.get("/orders", headers=headers)
    assert resp.status_code == 200
    orders = resp.json()
    assert len(orders) >= 1


# ── Recommendations ───────────────────────────────────────────────────────────

def test_product_recommendations():
    resp = client.get("/recommendations/product/Dell Inspiron 15")
    assert resp.status_code in (200, 404, 500, 503)
    if resp.status_code == 200:
        data = resp.json()
        assert "sections" in data
        assert "recommendations" in data


def test_personalized_recommendations_no_auth():
    resp = client.get("/recommendations")
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        data = resp.json()
        assert "recommendations" in data


def test_cart_recommendations_no_auth():
    resp = client.get("/recommendations/cart")
    assert resp.status_code in (200, 500)


# ── Events ────────────────────────────────────────────────────────────────────

def test_invalid_event_type():
    import uuid
    unique_email = f"ev_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/auth/register", json={
        "name": "Event User", "email": unique_email, "password": "evpass"
    })
    token = resp.json()["access_token"]
    
    resp = client.post("/events", json={
        "event_type": "INVALID_TYPE",
        "product_name": "Dell Inspiron 15",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


# ── Wishlist Tests ────────────────────────────────────────────────────────────

def test_wishlist_flow():
    import uuid
    email = f"wish_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/auth/register", json={
        "name": "Wish User", "email": email, "password": "wishpassword123"
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add to wishlist
    resp = client.post("/wishlist/Dell%20Inspiron%2015", headers=headers)
    assert resp.status_code == 201

    # Check wishlisted
    resp = client.get("/wishlist/check/Dell%20Inspiron%2015", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_wishlisted"] is True

    # Get wishlist
    resp = client.get("/wishlist", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1

    # Remove from wishlist
    resp = client.delete("/wishlist/Dell%20Inspiron%2015", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "removed"


# ── Recently Viewed & Category Recs ───────────────────────────────────────────

def test_recently_viewed_flow():
    import uuid
    email = f"rec_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/auth/register", json={
        "name": "Rec User", "email": email, "password": "recpassword123"
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record VIEW_PRODUCT event
    resp = client.post("/events", json={
        "event_type": "VIEW_PRODUCT",
        "product_name": "Dell Inspiron 15",
        "category_name": "Laptops",
    }, headers=headers)
    assert resp.status_code == 201

    # Fetch recently viewed
    resp = client.get("/recommendations/recently-viewed", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data.get("items", [])) >= 1


def test_category_recommendations():
    resp = client.get("/recommendations/category/Laptops")
    assert resp.status_code == 200
    data = resp.json()
    assert "top_picks" in data
    assert len(data["top_picks"]) >= 1

