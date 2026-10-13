"""
ShopGraph - Knowledge Graph ETL Loader
app/kg_loader.py

This module contains the extract-transform-load (ETL) pipeline that populates
the Neo4j Knowledge Graph with domain entities and semantic edges:
  - Node Labels: Product, Category, Feature, Brand, UseCase
  - Relationship Types:
      * Product -[:BELONGS_TO]-> Category
      * Product -[:MADE_BY]-> Brand
      * Product -[:HAS_FEATURE]-> Feature
      * Product -[:USED_FOR]-> UseCase
      * Product -[:COMPATIBLE_WITH]-> Product
      * Product -[:ACCESSORY]-> Product
      * Product -[:WORKS_WITH]-> Product
      * Product -[:SIMILAR_TO]-> Product

Idempotency:
  All Cypher operations use MERGE rather than CREATE, making this loader
  completely safe to run repeatedly without producing duplicate nodes or relationships.
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.database import Neo4jConnection

from app.expanded_data import (
    CATEGORIES,
    BRANDS,
    FEATURES,
    USE_CASES,
    PRODUCTS,
    PRODUCT_RELATIONS,
    PRODUCT_PRODUCT_RELATIONS,
)


def create_constraints(db: "Neo4jConnection") -> None:
    """Create uniqueness constraints for all node labels in Neo4j.
    
    Uniqueness constraints guarantee data integrity and build underlying indexes
    that dramatically accelerate MERGE operations and Cypher MATCH lookups.

    Args:
        db (Neo4jConnection): Active database connection.
    """
    constraints = [
        ("Product", "name", "product_name_unique"),
        ("Category", "name", "category_name_unique"),
        ("Feature", "name", "feature_name_unique"),
        ("Brand", "name", "brand_name_unique"),
        ("UseCase", "name", "usecase_name_unique"),
    ]
    for label, prop, constraint_name in constraints:
        db.run_query(
            f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
        )
    print("[OK] Constraints created")


def load_categories(db: "Neo4jConnection") -> int:
    """Merge Category nodes with descriptive metadata into the graph.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total number of Category nodes processed.
    """
    for cat in CATEGORIES:
        db.run_query(
            "MERGE (c:Category {name: $name}) SET c.description = $description",
            {"name": cat["name"], "description": cat["description"]},
        )
    print(f"[OK] Categories inserted: {len(CATEGORIES)}")
    return len(CATEGORIES)


def load_features(db: "Neo4jConnection") -> int:
    """Merge Feature nodes (e.g., 'ANC', 'USB-C', '4K OLED') into the graph.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total number of Feature nodes processed.
    """
    for feat in FEATURES:
        db.run_query(
            "MERGE (f:Feature {name: $name}) SET f.description = $description",
            {"name": feat["name"], "description": feat["description"]},
        )
    print(f"[OK] Features inserted: {len(FEATURES)}")
    return len(FEATURES)


def load_brands(db: "Neo4jConnection") -> int:
    """Merge Brand nodes (e.g., 'Apple', 'Dell', 'Sony') into the graph.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total number of Brand nodes processed.
    """
    for brand in BRANDS:
        db.run_query(
            "MERGE (b:Brand {name: $name}) SET b.country = $country",
            {"name": brand["name"], "country": brand["country"]},
        )
    print(f"[OK] Brands inserted: {len(BRANDS)}")
    return len(BRANDS)


def load_use_cases(db: "Neo4jConnection") -> int:
    """Merge UseCase nodes (e.g., 'Gaming', 'Remote Work', 'Fitness') into the graph.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total number of UseCase nodes processed.
    """
    for uc in USE_CASES:
        db.run_query(
            "MERGE (u:UseCase {name: $name}) SET u.description = $description",
            {"name": uc["name"], "description": uc["description"]},
        )
    print(f"[OK] Use cases inserted: {len(USE_CASES)}")
    return len(USE_CASES)


def load_products(db: "Neo4jConnection") -> int:
    """Merge Product nodes with complete e-commerce attributes into the graph.
    
    Attributes include pricing, discounts, stock, ratings, review counts,
    and image URLs.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total number of Product nodes processed.
    """
    for product in PRODUCTS:
        db.run_query(
            """
            MERGE (p:Product {name: $name})
            SET p.price = $price,
                p.original_price = $original_price,
                p.discount_percentage = $discount_percentage,
                p.description = $description,
                p.rating = $rating,
                p.review_count = $review_count,
                p.stock = $stock,
                p.image_url = $image_url,
                p.slug = $slug,
                p.brand = $brand,
                p.category = $category,
                p.model = $model,
                p.release_year = $release_year
            """,
            {
                "name": product["name"],
                "price": product["price"],
                "original_price": product.get("original_price", product["price"]),
                "discount_percentage": product.get("discount_percentage", 0),
                "description": product["description"],
                "rating": product.get("rating", 4.5),
                "review_count": product.get("review_count", 100),
                "stock": product.get("stock", 20),
                "image_url": product.get("image_url", ""),
                "slug": product.get("slug", ""),
                "brand": product.get("brand", ""),
                "category": product.get("category", ""),
                "model": product.get("model", ""),
                "release_year": product.get("release_year", 2023),
            },
        )
    print(f"[OK] Products inserted: {len(PRODUCTS)}")
    return len(PRODUCTS)


# Query templates for Product-to-Entity relationships
_REL_QUERY_TEMPLATES = {
    "BELONGS_TO": (
        "MATCH (p:Product {name: $src}), (t:Category {name: $tgt}) "
        "MERGE (p)-[:BELONGS_TO]->(t)"
    ),
    "MADE_BY": (
        "MATCH (p:Product {name: $src}), (t:Brand {name: $tgt}) "
        "MERGE (p)-[:MADE_BY]->(t)"
    ),
    "HAS_FEATURE": (
        "MATCH (p:Product {name: $src}), (t:Feature {name: $tgt}) "
        "MERGE (p)-[:HAS_FEATURE]->(t)"
    ),
    "USED_FOR": (
        "MATCH (p:Product {name: $src}), (t:UseCase {name: $tgt}) "
        "MERGE (p)-[:USED_FOR]->(t)"
    ),
}

# Query templates for Product-to-Product relationships
_PROD_PROD_TEMPLATES = {
    "COMPATIBLE_WITH": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:COMPATIBLE_WITH]->(b)"
    ),
    "ACCESSORY": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:ACCESSORY]->(b)"
    ),
    "WORKS_WITH": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:WORKS_WITH]->(b)"
    ),
    "SIMILAR_TO": (
        "MATCH (a:Product {name: $src}), (b:Product {name: $tgt}) "
        "MERGE (a)-[:SIMILAR_TO]->(b)"
    ),
}


def load_relationships(db: "Neo4jConnection") -> int:
    """Create all semantic and cross-product relationships in the graph.

    Args:
        db (Neo4jConnection): Active database connection.

    Returns:
        int: Total count of relationships created.
    """
    count = 0
    # Create product -> metadata entity edges
    for src, rel_type, tgt in PRODUCT_RELATIONS:
        if rel_type in _REL_QUERY_TEMPLATES:
            query = _REL_QUERY_TEMPLATES[rel_type]
            db.run_query(query, {"src": src, "tgt": tgt})
            count += 1

    # Create product -> product compatibility and accessory edges
    for src, rel_type, tgt in PRODUCT_PRODUCT_RELATIONS:
        if rel_type in _PROD_PROD_TEMPLATES:
            query = _PROD_PROD_TEMPLATES[rel_type]
            db.run_query(query, {"src": src, "tgt": tgt})
            count += 1

    print(f"[OK] Relationships created: {count}")
    return count


def load_all(db: "Neo4jConnection") -> None:
    """Full Knowledge Graph ETL load pipeline.
    
    Executes constraints, loads all entity nodes, and constructs all semantic relationships.
    Safe to run repeatedly on new or existing database instances.

    Args:
        db (Neo4jConnection): Active database connection.
    """
    print("\n[START] Loading ShopGraph Knowledge Graph into Neo4j...\n")
    create_constraints(db)
    load_categories(db)
    load_features(db)
    load_brands(db)
    load_use_cases(db)
    load_products(db)
    load_relationships(db)
    print("\n[DONE] Knowledge Graph loaded successfully!\n")

