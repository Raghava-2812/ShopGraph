"""
ShopGraph - Setup Database
scripts/setup_database.py

Verifies Neo4j connection and creates all constraints.
Run this once before loading any data.

Usage:
    python scripts/setup_database.py
"""

import sys
import os

# Make sure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.kg_loader import create_constraints


def main() -> None:
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
