"""
ShopGraph - Database Tests
tests/test_database.py

Tests Neo4j connection and verifies the knowledge graph
nodes and relationships are correctly loaded.

Prerequisites:
  - Neo4j running with the KG loaded (run scripts/load_kg.py first)
  - .env file with correct credentials

Run with:
    pytest tests/test_database.py -v
"""

import pytest
from app.database import get_db, Neo4jConnection


@pytest.fixture(scope="module")
def db() -> Neo4jConnection:
    """Create a single DB connection for all tests in this module."""
    conn = get_db()
    yield conn
    conn.close()


class TestConnection:
    def test_connection_is_alive(self, db: Neo4jConnection) -> None:
        """The driver must be able to reach Neo4j."""
        assert db.verify_connection() is True

    def test_run_simple_query(self, db: Neo4jConnection) -> None:
        """A basic query must return results without raising."""
        rows = db.run_query("RETURN 1 AS n")
        assert rows == [{"n": 1}]


class TestNodes:
    def test_products_exist(self, db: Neo4jConnection) -> None:
        """Knowledge graph must contain Product nodes."""
        rows = db.run_query("MATCH (p:Product) RETURN count(p) AS n")
        assert rows[0]["n"] >= 20, "Expected at least 20 Product nodes"

    def test_categories_exist(self, db: Neo4jConnection) -> None:
        """Knowledge graph must contain Category nodes."""
        rows = db.run_query("MATCH (c:Category) RETURN count(c) AS n")
        assert rows[0]["n"] >= 10, "Expected at least 10 Category nodes"

    def test_features_exist(self, db: Neo4jConnection) -> None:
        """Knowledge graph must contain Feature nodes."""
        rows = db.run_query("MATCH (f:Feature) RETURN count(f) AS n")
        assert rows[0]["n"] >= 10, "Expected at least 10 Feature nodes"

    def test_brands_exist(self, db: Neo4jConnection) -> None:
        """Knowledge graph must contain Brand nodes."""
        rows = db.run_query("MATCH (b:Brand) RETURN count(b) AS n")
        assert rows[0]["n"] >= 12, "Expected at least 12 Brand nodes"

    def test_use_cases_exist(self, db: Neo4jConnection) -> None:
        """Knowledge graph must contain UseCase nodes."""
        rows = db.run_query("MATCH (u:UseCase) RETURN count(u) AS n")
        assert rows[0]["n"] >= 8, "Expected at least 8 UseCase nodes"

    def test_specific_product_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must exist."""
        rows = db.run_query(
            "MATCH (p:Product {name: $name}) RETURN p.name AS name",
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) == 1
        assert rows[0]["name"] == "Dell Inspiron 15"

    def test_specific_category_exists(self, db: Neo4jConnection) -> None:
        """Laptop category must exist."""
        rows = db.run_query(
            "MATCH (c:Category {name: $name}) RETURN c.name AS name",
            {"name": "Laptop"},
        )
        assert len(rows) == 1


class TestRelationships:
    def test_belongs_to_relationship_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must belong to Laptop category."""
        rows = db.run_query(
            """
            MATCH (p:Product {name: $name})-[:BELONGS_TO]->(c:Category)
            RETURN c.name AS category
            """,
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) == 1
        assert rows[0]["category"] == "Laptop"

    def test_has_feature_relationship_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must have at least one feature."""
        rows = db.run_query(
            """
            MATCH (p:Product {name: $name})-[:HAS_FEATURE]->(f:Feature)
            RETURN f.name AS feature
            """,
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) > 0

    def test_compatible_with_relationship_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must have compatible products."""
        rows = db.run_query(
            """
            MATCH (p:Product {name: $name})-[:COMPATIBLE_WITH]->(c:Product)
            RETURN c.name AS product
            """,
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) > 0

    def test_accessory_relationship_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must have accessory relationships."""
        rows = db.run_query(
            """
            MATCH (p:Product {name: $name})-[:ACCESSORY]->(a:Product)
            RETURN a.name AS product
            """,
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) > 0

    def test_works_with_relationship_exists(self, db: Neo4jConnection) -> None:
        """Dell Inspiron 15 must have WORKS_WITH relationships."""
        rows = db.run_query(
            """
            MATCH (p:Product {name: $name})-[:WORKS_WITH]->(w:Product)
            RETURN w.name AS product
            """,
            {"name": "Dell Inspiron 15"},
        )
        assert len(rows) > 0
