"""
ShopGraph E-Commerce - FastAPI Application
app/main.py

Upgraded from a simple recommendation-only API to a complete
e-commerce backend with:
  - JWT Authentication
  - User behavior tracking
  - Shopping cart
  - Orders
  - Personalized recommendations via Neo4j Knowledge Graph
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.sqlite_db import init_db
from app.routers import auth, products, events, cart, orders, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (nothing needed)


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

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(events.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(recommendations.router)


# Keep legacy endpoint for backward compatibility
@app.get("/", tags=["Health"])
def root():
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Legacy recommendation endpoint (preserved)
@app.get("/recommend/{product_name}", tags=["Legacy"])
def recommend_legacy(product_name: str, top_k: int = 5):
    """Legacy endpoint for backward compatibility."""
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
