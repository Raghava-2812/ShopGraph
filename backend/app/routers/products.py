"""
ShopGraph - Product Catalog & Graph Traversal Router
app/routers/products.py

This module serves catalog queries directly backed by the Neo4j Knowledge Graph:
  - GET /products: Catalog list with optional category/brand filtering and sorting.
  - GET /products/search: Full-text search across product titles, descriptions, categories, and brands.
  - GET /products/categories: List of unique product category nodes.
  - GET /products/brands: List of unique manufacturer brand nodes.
  - GET /products/category/{name}/products: Category-specific product listing.
  - GET /products/{name}: Complete product dossier including rich specs and all connected graph edges
                          (compatible_with, accessories, works_with, similar_to).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[dict])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category name"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    sort: Optional[str] = Query(None, description="Sort order: price_asc, price_desc, rating, popular"),
):
    """List products from the Knowledge Graph with optional filtering and sorting.

    Args:
        category (str | None): Optional category filter.
        brand (str | None): Optional brand filter.
        sort (str | None): Optional sort criteria ('price_asc', 'price_desc', 'rating', 'popular').

    Returns:
        list[dict]: List of matching product records with full attributes.
    """
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)", {"category": category, "brand": brand})

    if not rows:
        return []

    # Apply sorting in-memory based on requested criteria
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
def search_products(q: str = Query(..., description="Search query string")):
    """Full-text case-insensitive product search across titles, descriptions, and categories.

    Args:
        q (str): Case-insensitive search query.

    Returns:
        list[dict]: Products matching the query across any text field.
    """
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
    """Retrieve all unique product category names from Category nodes in the graph.

    Returns:
        list[str]: Sorted list of category names.
    """
    query = "MATCH (c:Category) RETURN c.name AS name ORDER BY c.name"
    with get_db() as db:
        rows = db.run_query(query)
    return [r["name"] for r in rows]


@router.get("/brands", response_model=list[str])
def list_brands():
    """Retrieve all distinct manufacturer brand names present in the product catalog.

    Returns:
        list[str]: Sorted list of brand names.
    """
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)")
    brands = sorted(list(set(r.get("brand") for r in rows if r.get("brand"))))
    return brands


@router.get("/category/{category_name}/products", response_model=list[dict])
def list_products_by_category(category_name: str):
    """Retrieve all product records assigned to a specific category.

    Args:
        category_name (str): Exact category title.

    Returns:
        list[dict]: Catalog items belonging to the category.
    """
    with get_db() as db:
        rows = db.run_query("MATCH (p:Product)", {"category": category_name})
    return rows


@router.get("/{product_name}", response_model=dict)
def get_product(product_name: str):
    """Retrieve full product details along with all first-degree Knowledge Graph connections.

    Fetches:
      - Pricing, discount percentage, specs, and stock
      - Category and Brand nodes
      - Connected Features (HAS_FEATURE) and Use Cases (USED_FOR)
      - Direct Cross-Product Edges:
          * COMPATIBLE_WITH
          * ACCESSORY
          * WORKS_WITH
          * SIMILAR_TO

    Args:
        product_name (str): Name of the product to query.

    Returns:
        dict: Full product record and connected graph lists.

    Raises:
        HTTPException: 404 Not Found if product does not exist in the graph.
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

