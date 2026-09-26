"""
ShopGraph - Products Router
app/routers/products.py

Routes:
  GET /products
  GET /products/{product_name}
  GET /categories
  GET /products/search?q=...
"""

from fastapi import APIRouter, HTTPException, Query
from app.database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[dict])
def list_products(category: str = Query(None, description="Filter by category")):
    """List all products from the Knowledge Graph, optionally filtered by category."""
    if category:
        query = """
        MATCH (p:Product)-[:BELONGS_TO]->(cat:Category {name: $category})
        OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
        RETURN p.name AS name,
               p.price AS price,
               p.description AS description,
               cat.name AS category,
               b.name AS brand
        ORDER BY p.name
        """
        params = {"category": category}
    else:
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
        params = {}
    
    with get_db() as db:
        rows = db.run_query(query, params)
    
    if not rows:
        raise HTTPException(status_code=503, detail="Could not retrieve products. Is the knowledge graph loaded?")
    return rows


@router.get("/search", response_model=list[dict])
def search_products(q: str = Query(..., description="Search query")):
    """Full-text product search across name, description, category, brand."""
    query = """
    MATCH (p:Product)
    OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
    OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
    WHERE toLower(p.name) CONTAINS toLower($q)
       OR toLower(p.description) CONTAINS toLower($q)
       OR toLower(cat.name) CONTAINS toLower($q)
       OR toLower(b.name) CONTAINS toLower($q)
    RETURN p.name AS name,
           p.price AS price,
           p.description AS description,
           cat.name AS category,
           b.name AS brand
    ORDER BY p.name
    """
    with get_db() as db:
        rows = db.run_query(query, {"q": q})
    return rows


@router.get("/categories", response_model=list[str])
def list_categories():
    """List all product categories from the Knowledge Graph."""
    query = "MATCH (c:Category) RETURN c.name AS name ORDER BY c.name"
    with get_db() as db:
        rows = db.run_query(query)
    return [r["name"] for r in rows]


@router.get("/{product_name}", response_model=dict)
def get_product(product_name: str):
    """Return full product details including graph relationships."""
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
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
    
    row = rows[0]
    return {
        "name": row["name"],
        "price": row["price"],
        "description": row["description"],
        "category": row["category"],
        "brand": row["brand"],
        "features": row["features"] or [],
        "use_cases": row["use_cases"] or [],
        "compatible_with": row["compatible_with"] or [],
        "accessories": row["accessories"] or [],
        "works_with": row["works_with"] or [],
        "similar_to": row["similar_to"] or [],
    }
