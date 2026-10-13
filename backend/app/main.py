"""
ShopGraph E-Commerce - FastAPI Application Server
app/main.py

This is the main entry point for the ShopGraph backend service.
It sets up the FastAPI application instance, configures CORS middleware for frontend clients,
initializes the SQLite database during startup lifespan, and registers all API routers:
  - /auth: User registration, login, and profile
  - /products: Catalog browsing, search, category filtering, and product details
  - /events: Tracking user behavior (views, searches, cart actions, wishlists)
  - /cart: Shopping cart state management
  - /orders: Checkout, order placement, and history
  - /recommendations: Graph-driven personalized & context-aware recommendations
  - /wishlist: User wishlist management

Dual Route Registration:
  Each router is registered at the root prefix (e.g. `/products`) and also at the
  `/api` prefix (e.g. `/api/products`) to ensure full compatibility with diverse clients.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.sqlite_db import init_db
from app.routers import auth, products, events, cart, orders, recommendations, wishlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.
    
    Handles startup and shutdown events:
      - Startup: Initializes SQLite tables, migrations, and seeds the demo user account.
      - Shutdown: Performs any necessary resource cleanups upon server termination.
    """
    # Startup lifecycle
    init_db()
    yield
    # Shutdown lifecycle (connections close automatically)


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "ShopGraph: Knowledge Graph powered e-commerce recommendation system. "
        "Recommendations are automatically generated based on user behavior "
        "and Neo4j graph relationships."
    ),
    lifespan=lifespan,
)

# ── CORS Middleware Configuration ─────────────────────────────────────────────
# Allows local Vite dev servers, localhost ports, and production deploy origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://shopgraph-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler returning clean JSON error payloads with CORS headers."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal server error"},
    )


# ── Route Registrations ───────────────────────────────────────────────────────
# Standard routes
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(events.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(recommendations.router)
app.include_router(wishlist.router)

# Compatibility routes (/api/*) for frontend or proxy setups
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(wishlist.router, prefix="/api")


# ── Health & Diagnostic Endpoints ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Service health check and API entry point."""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# ── Legacy Recommendation Endpoint ───────────────────────────────────────────

@app.get("/recommend/{product_name}", tags=["Legacy"])
def recommend_legacy(product_name: str, top_k: int = 5):
    """Legacy recommendation endpoint preserved for backward compatibility.
    
    Generates recommendations directly from the Knowledge Graph using ProductRecommender.
    
    Args:
        product_name (str): Name of the purchased/context product.
        top_k (int): Number of recommendation items to return (default: 5).
        
    Returns:
        dict: Payload containing the purchased product name and ranked recommendations with scores and reasons.
    """
    from fastapi import HTTPException
    from app.database import get_db
    from app.recommender import ProductRecommender
    
    with get_db() as db:
        recommender = ProductRecommender(db)
        try:
            results = recommender.recommend(product_name, top_k=top_k)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No recommendations found for '{product_name}'")
    
    return {
        "purchased_product": product_name,
        "recommendations": [
            {"product": r.product, "score": r.score, "reasons": r.reasons}
            for r in results
        ]
    }

