"""
ShopGraph - Load Knowledge Graph
scripts/load_kg.py

Loads all nodes and relationships into Neo4j.
Safe to run multiple times — uses MERGE throughout.

Usage:
    python scripts/load_kg.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.kg_loader import load_all


def print_statistics(db) -> None:
    """Print a summary of what is in the graph after loading."""
    print("\n📊 Knowledge Graph Statistics:")
    print("-" * 40)

    node_query = """
    MATCH (n)
    RETURN labels(n)[0] AS label, count(n) AS count
    ORDER BY count DESC
    """
    rel_query = """
    MATCH ()-[r]->()
    RETURN type(r) AS type, count(r) AS count
    ORDER BY count DESC
    """

    rows = db.run_query(node_query)
    print("  Nodes:")
    for row in rows:
        print(f"    {row['label']:20s} {row['count']:4d}")

    print("  Relationships:")
    rows = db.run_query(rel_query)
    for row in rows:
        print(f"    {row['type']:20s} {row['count']:4d}")
    print("-" * 40)


def main() -> None:
    print("=" * 50)
    print("  ShopGraph — Knowledge Graph Loader")
    print("=" * 50)

    start = time.time()
    try:
        with get_db() as db:
            load_all(db)
            print_statistics(db)

    except ConnectionError as e:
        print(f"\n❌ Could not connect to Neo4j:\n{e}")
        print("\nPlease check your .env file and make sure Neo4j is running.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

    elapsed = time.time() - start
    print(f"⏱  Completed in {elapsed:.1f}s")
    print("\nYou can now run the API:")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
