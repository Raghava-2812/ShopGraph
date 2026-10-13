"""
ShopGraph - Database Setup CLI Script
scripts/setup_database.py

This utility script connects to the configured Neo4j instance, tests connectivity,
and establishes uniqueness constraints for all node labels (Product, Category,
Feature, Brand, UseCase).

Run this script once during initial system setup prior to executing `load_kg.py`.

Usage:
    python scripts/setup_database.py
"""

import sys
import os

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.kg_loader import create_constraints


def main() -> None:
    """Verify Neo4j connectivity and create graph uniqueness constraints."""
    print("=" * 50)
    print("  ShopGraph — Database Setup")
    print("=" * 50)

    try:
        with get_db() as db:
            if not db.verify_connection():
                print("❌ Could not verify Neo4j connection.")
                sys.exit(1)

            print("Creating uniqueness constraints...")
            create_constraints(db)
            print("\n✅ Database setup complete!")
            print("You can now run:  python scripts/load_kg.py")

    except ConnectionError as e:
        print(f"\n❌ Connection failed:\n{e}")
        print("\nPlease check your .env file and make sure Neo4j is running.")
        sys.exit(1)


if __name__ == "__main__":
    main()

