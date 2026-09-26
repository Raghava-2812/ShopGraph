"""
ShopGraph - Products Router
app/routers/products.py

Routes:
  GET /products
  GET /products/{product_name}
  GET /products/search?q=...
  GET /products/categories
  GET /products/brands
  GET /categories/{category_name}/products
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[dict])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    sort: Optional[str] = Query(None, description="Sort order: price_asc, price_desc, rating, popular"),
):
    """List all products from the Knowledge Graph with optional filtering and sorting."""
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)", {"category": category, "brand": brand})

    if not rows:
        return []

    # Apply in-memory sorting if requested
    if sort == "price_asc":
        rows.sort(key=lambda x: x.get("price") or 0)
    elif sort == "price_desc":
        rows.sort(key=lambda x: x.get("price") or 0, reverse=True)
    elif sort == "rating":
        rows.sort(key=lambda x: x.get("rating") or 0, reverse=True)
    elif sort == "popular":
        rows.sort(key=lambda x: x.get("review_count") or 0, reverse=True)

    return rows


@router.get("/search", response_model=list[dict])
def search_products(q: str = Query(..., description="Search query")):
    """Full-text product search across name, description, category, brand."""
    with get_db() as db:
        rows = db.run_query(
            """
            MATCH (p:Product)
            WHERE toLower(p.name) CONTAINS toLower($q)
               OR toLower(p.description) CONTAINS toLower($q)
               OR toLower(cat.name) CONTAINS toLower($q)
               OR toLower(b.name) CONTAINS toLower($q)
            """,
            {"q": q},
        )
    return rows


@router.get("/categories", response_model=list[str])
def list_categories():
    """List all product categories from the Knowledge Graph."""
    query = "MATCH (c:Category) RETURN c.name AS name ORDER BY c.name"
    with get_db() as db:
        rows = db.run_query(query)
    return [r["name"] for r in rows]


@router.get("/brands", response_model=list[str])
def list_brands():
    """List all product brands from the Knowledge Graph."""
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)")
    brands = sorted(list(set(r.get("brand") for r in rows if r.get("brand"))))
    return brands


@router.get("/category/{category_name}/products", response_model=list[dict])
def list_products_by_category(category_name: str):
    """List products in a specific category."""
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)", {"category": category_name})
    return rows


@router.get("/{product_name}", response_model=dict)
def get_product(product_name: str):
    """Return full product details including graph relationships, specs, ratings, and gallery."""
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
      collect(DISTINCT comp.name) AS compatible_with,
      collect(DISTINCT acc.name)  AS accessories,
      collect(DISTINCT ww.name)   AS works_with,
      collect(DISTINCT sim.name)  AS similar_to
    """
    with get_db() as db:
        rows = db.run_query(query, {"name": product_name})

    if not rows or rows[0].get("name") is None:
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")

    return rows[0]
