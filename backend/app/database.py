"""
ShopGraph - Database Connection
app/database.py

Manages the Neo4j driver lifecycle.
Provides a clean interface to run Cypher queries.
"""

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Any
from app.config import settings


class Neo4jConnection:
    """
    Manages connection to a Neo4j database.
    Automatically falls back to in-memory Knowledge Graph if Neo4j is offline.

    Usage:
        db = Neo4jConnection()
        results = db.run_query("MATCH (p:Product) RETURN p.name LIMIT 5")
        db.close()
    """

    def __init__(self) -> None:
        self._driver: Driver | None = None
        self._use_fallback: bool = False
        self._connect()

    def _connect(self) -> None:
        """Create the Neo4j driver using settings from environment."""
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            )
            # Verify the connection is live
            self._driver.verify_connectivity()
            print(f"[OK] Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            # When Neo4j AuraDB or local Neo4j is not reachable, fall back to in-memory graph
            self._driver = None
            self._use_fallback = True
            print(f"[INFO] Neo4j offline ({e.__class__.__name__}). Using In-Memory Knowledge Graph.")

    def run_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a Cypher query on Neo4j, or in-memory Knowledge Graph if Neo4j is offline.
        """
        parameters = parameters or {}
        if self._driver is not None and not self._use_fallback:
            try:
                with self._driver.session() as session:
                    result = session.run(query, parameters)
                    return [record.data() for record in result]
            except Exception as e:
                print(f"[WARN] Neo4j query error: {e}. Falling back to in-memory KG.")
                self._use_fallback = True

        from app.mock_kg import mock_kg
        return mock_kg.run_query(query, parameters)

    def close(self) -> None:
        """Close the driver and release network resources."""
        if self._driver:
            self._driver.close()
            print("[CLOSED] Neo4j connection closed.")

    def verify_connection(self) -> bool:
        """Return True if the database is reachable, False otherwise."""
        try:
            if self._driver:
                self._driver.verify_connectivity()
                return True
        except Exception:
            pass
        return False

    # ── Context manager support ──────────────────────────────
    def __enter__(self) -> "Neo4jConnection":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# Module-level singleton — imported by the rest of the app
def get_db() -> Neo4jConnection:
    """Create and return a new Neo4j connection."""
    return Neo4jConnection()
