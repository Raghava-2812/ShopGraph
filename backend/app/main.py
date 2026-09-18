"""
ShopGraph - FastAPI Application
app/main.py

Exposes the recommendation engine as a REST API.

Endpoints:
  GET /                          → Health / welcome
  GET /products                  → List all products
  GET /products/{product_name}   → Product detail with graph relationships
  GET /recommend/{product_name}  → Recommendations (optional ?top_k=N)
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import get_db
from app.models import (
    HealthResponse,
    ProductDetail,
    RecommendationResponse,
    RecommendationItem,
)
from app.recommender import ProductRecommender

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Knowledge Graph based product recommendation system using Neo4j. "
        "Every recommendation includes a transparent explanation."
    ),
)

# Enable CORS for Vite frontend
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


# ── GET / ────────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse, tags=["Health"])
def root() -> HealthResponse:
    """Welcome endpoint — confirms the API is running."""
    return HealthResponse(
        message=settings.APP_NAME,
        version=settings.APP_VERSION,
    )


# ── GET /products ─────────────────────────────────────────────────────────────

@app.get("/products", response_model=list[dict], tags=["Products"])
def list_products() -> list[dict]:
    """
    Return a list of all products stored in the knowledge graph,
    including their category, brand, and price.
    """
    query = """
    MATCH (p:Product)
    OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
    OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
    RETURN p.name AS name,
           p.price AS price,
           p.description AS description,
           cat.name AS category,
           b.name AS brand
    ORDER BY cat.name, p.name
    """
    with get_db() as db:
        rows = db.run_query(query)

    if not rows:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve products. Is the knowledge graph loaded?",
        )
    return rows


# ── GET /products/{product_name} ──────────────────────────────────────────────

@app.get(
    "/products/{product_name}",
    response_model=ProductDetail,
    tags=["Products"],
)
def get_product(
    product_name: str = Path(..., description="Exact product name, e.g. Dell Inspiron 15"),
) -> ProductDetail:
    """
    Return full product details including all graph relationships:
    features, use cases, compatible products, accessories, etc.
    """
    query = """
    MATCH (p:Product {name: $name})
    OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
    OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
    OPTIONAL MATCH (p)-[:HAS_FEATURE]->(f:Feature)
    OPTIONAL MATCH (p)-[:USED_FOR]->(u:UseCase)
    OPTIONAL MATCH (p)-[:COMPATIBLE_WITH]->(comp:Product)
    OPTIONAL MATCH (p)-[:ACCESSORY]->(acc:Product)
    OPTIONAL MATCH (p)-[:WORKS_WITH]->(ww:Product)
    OPTIONAL MATCH (p)-[:SIMILAR_TO]->(sim:Product)
    RETURN
      p.name AS name,
      p.price AS price,
      p.description AS description,
      cat.name AS category,
      b.name AS brand,
      collect(DISTINCT f.name)    AS features,
      collect(DISTINCT u.name)    AS use_cases,
      collect(DISTINCT comp.name) AS compatible_with,
      collect(DISTINCT acc.name)  AS accessories,
      collect(DISTINCT ww.name)   AS works_with,
      collect(DISTINCT sim.name)  AS similar_to
    """
    with get_db() as db:
        rows = db.run_query(query, {"name": product_name})

    if not rows or rows[0]["name"] is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product '{product_name}' not found in the knowledge graph.",
        )

    row = rows[0]
    return ProductDetail(
        name=row["name"],
        price=row["price"],
        description=row["description"],
        category=row["category"],
        brand=row["brand"],
        features=row["features"] or [],
        use_cases=row["use_cases"] or [],
        compatible_with=row["compatible_with"] or [],
        accessories=row["accessories"] or [],
        works_with=row["works_with"] or [],
        similar_to=row["similar_to"] or [],
    )


# ── GET /recommend/{product_name} ─────────────────────────────────────────────

@app.get(
    "/recommend/{product_name}",
    response_model=RecommendationResponse,
    tags=["Recommendations"],
)
def recommend(
    product_name: str = Path(
        ..., description="The product the user has purchased, e.g. Dell Inspiron 15"
    ),
    top_k: int = Query(
        default=settings.DEFAULT_TOP_K,
        ge=1,
        le=settings.MAX_TOP_K,
        description="Number of recommendations to return (1–20)",
    ),
) -> RecommendationResponse:
    """
    Generate explainable product recommendations for a purchased product.

    The engine:
    1. Finds the product in Neo4j.
    2. Traverses graph relationships to generate candidates.
    3. Scores each candidate across 5 dimensions.
    4. Returns the top-K recommendations with explanations.

    Returns 404 if the product does not exist in the knowledge graph.
    """
    with get_db() as db:
        recommender = ProductRecommender(db)
        try:
            results = recommender.recommend(product_name, top_k=top_k)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    if not results:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No recommendations found for '{product_name}'. "
                "Make sure the knowledge graph is loaded."
            ),
        )

    recommendations = [
        RecommendationItem(
            product=r.product,
            score=r.score,
            reasons=r.reasons,
        )
        for r in results
    ]

    return RecommendationResponse(
        purchased_product=product_name,
        recommendations=recommendations,
    )
