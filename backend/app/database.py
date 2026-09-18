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

    Usage:
        db = Neo4jConnection()
        results = db.run_query("MATCH (p:Product) RETURN p.name LIMIT 5")
        db.close()
    """

    def __init__(self) -> None:
        self._driver: Driver | None = None
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
            print(f"✅ Connected to Neo4j at {settings.NEO4J_URI}")
        except ServiceUnavailable as e:
            raise ConnectionError(
                f"Cannot reach Neo4j at {settings.NEO4J_URI}. "
                "Make sure Neo4j is running and the URI is correct.\n"
                f"Details: {e}"
            )
        except AuthError as e:
            raise ConnectionError(
                "Neo4j authentication failed. "
                "Check NEO4J_USERNAME and NEO4J_PASSWORD in your .env file.\n"
                f"Details: {e}"
            )

    def run_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dicts.

        Args:
            query:      A Cypher query string with $param placeholders.
            parameters: A dict of parameters to bind (prevents injection).

        Returns:
            A list of record dicts.
        """
        if self._driver is None:
            raise RuntimeError("Driver is not initialised. Call _connect() first.")

        parameters = parameters or {}
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def close(self) -> None:
        """Close the driver and release network resources."""
        if self._driver:
            self._driver.close()
            print("🔒 Neo4j connection closed.")

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
