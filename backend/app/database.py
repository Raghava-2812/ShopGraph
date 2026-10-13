"""
ShopGraph - Graph Database Connection Manager
app/database.py

This module manages the lifecycle of the Neo4j graph database driver and provides
a unified execution interface for Cypher queries.

Key Architectural Feature:
  Automatic In-Memory Fallback: If Neo4j (local or AuraDB) is offline or unreachable,
  the connection manager gracefully fails over to the in-memory mock knowledge graph
  (`app.mock_kg.mock_kg`). This guarantees zero downtime and enables tests and frontend
  exploration to run seamlessly without requiring a local Neo4j container.
"""

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Any
from app.config import settings


class Neo4jConnection:
    """Manages connection pooling and query execution against Neo4j.
    
    Provides automatic fallback to an in-memory knowledge graph if Neo4j
    cannot be reached or encounters network timeouts. Implements the Python
    Context Manager protocol (`__enter__` / `__exit__`) for deterministic resource cleanup.

    Usage:
        with Neo4jConnection() as db:
            results = db.run_query(
                "MATCH (p:Product {name: $name}) RETURN p.price AS price",
                {"name": "Dell Inspiron 15"}
            )
    """

    def __init__(self) -> None:
        """Initialize the connection manager and attempt to establish driver connection."""
        self._driver: Driver | None = None
        self._use_fallback: bool = False
        self._connect()

    def _connect(self) -> None:
        """Create the Neo4j driver using environment settings and verify connectivity.
        
        If connectivity verification fails (e.g. database offline or credentials invalid),
        the instance sets `_use_fallback = True` to seamlessly redirect Cypher queries
        to the in-memory knowledge graph.
        """
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
            )
            # Verify that the database is active and accepting connections
            self._driver.verify_connectivity()
            print(f"[OK] Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            # Fall back to in-memory graph if remote or local Neo4j instance is unreachable
            self._driver = None
            self._use_fallback = True
            print(f"[INFO] Neo4j offline ({e.__class__.__name__}). Using In-Memory Knowledge Graph.")

    def run_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query on Neo4j, falling back to the in-memory graph if offline.

        Args:
            query (str): Cypher query string to execute.
            parameters (dict[str, Any] | None): Parameter dictionary for query interpolation.

        Returns:
            list[dict[str, Any]]: List of dictionary records representing returned rows.
        """
        parameters = parameters or {}
        # Try active Neo4j driver first if available
        if self._driver is not None and not self._use_fallback:
            try:
                with self._driver.session() as session:
                    result = session.run(query, parameters)
                    return [record.data() for record in result]
            except Exception as e:
                print(f"[WARN] Neo4j query error: {e}. Falling back to in-memory KG.")
                self._use_fallback = True

        # Fallback: evaluate Cypher query using the in-memory graph engine
        from app.mock_kg import mock_kg
        return mock_kg.run_query(query, parameters)

    def close(self) -> None:
        """Close the underlying Neo4j driver connection and release pool resources."""
        if self._driver:
            self._driver.close()
            print("[CLOSED] Neo4j connection closed.")

    def verify_connection(self) -> bool:
        """Check whether the active Neo4j database connection is healthy and responsive.

        Returns:
            bool: True if Neo4j is reachable and authenticated; False otherwise.
        """
        try:
            if self._driver:
                self._driver.verify_connectivity()
                return True
        except Exception:
            pass
        return False

    # ── Context Manager Support ───────────────────────────────────────────────
    def __enter__(self) -> "Neo4jConnection":
        """Enter context manager, returning connection instance."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager and cleanly close driver connections."""
        self.close()


# Module-level factory function — used across API routers and services
def get_db() -> Neo4jConnection:
    """Factory dependency to create a new Neo4jConnection instance.
    
    Returns:
        Neo4jConnection: Configured connection instance ready for Cypher queries.
    """
    return Neo4jConnection()

