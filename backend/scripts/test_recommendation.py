"""
ShopGraph - CLI Recommendation Test Script
scripts/test_recommendation.py

Demonstrates the recommendation engine from the command line.
Run this after loading the knowledge graph.

Usage:
    python scripts/test_recommendation.py
    python scripts/test_recommendation.py "HP Pavilion 15" 3
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.recommender import ProductRecommender

# Products to test
DEFAULT_TEST_PRODUCTS = [
    "Dell Inspiron 15",
    "HP Pavilion 15",
    "Lenovo IdeaPad Slim 5",
]


def print_recommendations(product_name: str, top_k: int = 5) -> None:
    """Run the recommender and pretty-print results to the terminal."""
    print("\n" + "=" * 60)
    print(f"  🛒  Purchased Product: {product_name}")
    print("=" * 60)

    try:
        with get_db() as db:
            recommender = ProductRecommender(db)
            results = recommender.recommend(product_name, top_k=top_k)

    except ConnectionError as e:
        print(f"❌ Neo4j connection failed: {e}")
        return
    except ValueError as e:
        print(f"❌ {e}")
        return

    if not results:
        print("  No recommendations found.")
        return

    print(f"\n  Top {len(results)} Recommendations:\n")
    for i, rec in enumerate(results, start=1):
        print(f"  {i}. {rec.product}")
        print(f"     Score: {rec.score:.1f} / 100")
        print("     Why:")
        for reason in rec.reasons:
            print(f"       • {reason}")
        print()


def main() -> None:
    # Allow overriding from command line
    if len(sys.argv) >= 2:
        product = sys.argv[1]
        top_k = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
        print_recommendations(product, top_k)
    else:
        print("\n🚀 Running recommendation tests for sample products...\n")
        for product in DEFAULT_TEST_PRODUCTS:
            print_recommendations(product, top_k=5)


if __name__ == "__main__":
    main()
