"""
ShopGraph - Candidate Generator
app/candidate_generator.py

Queries Neo4j to find candidate products for recommendation.
Uses four discovery strategies:
  A. Direct relationships (COMPATIBLE_WITH, ACCESSORY, WORKS_WITH, SIMILAR_TO)
  B. Shared features
  C. Shared use cases
  D. Same category (similar products)
"""

from dataclasses import dataclass, field
from app.database import Neo4jConnection


@dataclass
class CandidateInfo:
    """Holds a candidate product and the signals that led to its discovery."""

    name: str
    direct_relationships: list[str] = field(default_factory=list)
    shared_features: list[str] = field(default_factory=list)
    shared_use_cases: list[str] = field(default_factory=list)
    same_category: bool = False


class CandidateGenerator:
    """
    Traverses the Neo4j knowledge graph to find candidate products
    that could be recommended alongside a given purchased product.
    """

    def __init__(self, db: Neo4jConnection) -> None:
        self.db = db

    # ── A. Direct Relationships ──────────────────────────────────────────────

    def get_direct_candidates(self, product_name: str) -> dict[str, list[str]]:
        """
        Find products directly connected via graph relationships.
        Returns a dict: {product_name -> [relationship_types]}
        """
        query = """
        MATCH (p:Product {name: $name})
        -[r:COMPATIBLE_WITH|ACCESSORY|WORKS_WITH|SIMILAR_TO]->
        (c:Product)
        RETURN c.name AS candidate, type(r) AS rel_type
        """
        rows = self.db.run_query(query, {"name": product_name})
        result: dict[str, list[str]] = {}
        for row in rows:
            candidate = row["candidate"]
            rel = row["rel_type"]
            result.setdefault(candidate, []).append(rel)
        return result

    # ── B. Shared Features ───────────────────────────────────────────────────

    def get_feature_candidates(self, product_name: str) -> dict[str, list[str]]:
        """
        Find products that share at least one feature with the input product.
        Returns a dict: {product_name -> [shared_feature_names]}
        """
        query = """
        MATCH (p:Product {name: $name})-[:HAS_FEATURE]->(f:Feature)
              <-[:HAS_FEATURE]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate, collect(DISTINCT f.name) AS shared_features
        """
        rows = self.db.run_query(query, {"name": product_name})
        return {row["candidate"]: row["shared_features"] for row in rows}

    # ── C. Shared Use Cases ──────────────────────────────────────────────────

    def get_use_case_candidates(self, product_name: str) -> dict[str, list[str]]:
        """
        Find products that share at least one use case with the input product.
        Returns a dict: {product_name -> [shared_use_case_names]}
        """
        query = """
        MATCH (p:Product {name: $name})-[:USED_FOR]->(u:UseCase)
              <-[:USED_FOR]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate, collect(DISTINCT u.name) AS shared_use_cases
        """
        rows = self.db.run_query(query, {"name": product_name})
        return {row["candidate"]: row["shared_use_cases"] for row in rows}

    # ── D. Same Category ─────────────────────────────────────────────────────

    def get_same_category_candidates(self, product_name: str) -> list[str]:
        """
        Find products in the same category as the input product.
        Useful for surfacing alternatives.
        """
        query = """
        MATCH (p:Product {name: $name})-[:BELONGS_TO]->(cat:Category)
              <-[:BELONGS_TO]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate
        """
        rows = self.db.run_query(query, {"name": product_name})
        return [row["candidate"] for row in rows]

    # ── Combined ─────────────────────────────────────────────────────────────

    def generate_candidates(self, product_name: str) -> dict[str, CandidateInfo]:
        """
        Run all four discovery strategies and merge results.

        Args:
            product_name: The exact name of the purchased product.

        Returns:
            A dict mapping candidate product name → CandidateInfo.
        """
        direct   = self.get_direct_candidates(product_name)
        features = self.get_feature_candidates(product_name)
        use_cases = self.get_use_case_candidates(product_name)
        same_cat = set(self.get_same_category_candidates(product_name))

        # Collect every unique candidate name
        all_names: set[str] = (
            set(direct.keys())
            | set(features.keys())
            | set(use_cases.keys())
            | same_cat
        )
        # Remove the source product itself (safety check)
        all_names.discard(product_name)

        candidates: dict[str, CandidateInfo] = {}
        for name in all_names:
            candidates[name] = CandidateInfo(
                name=name,
                direct_relationships=direct.get(name, []),
                shared_features=features.get(name, []),
                shared_use_cases=use_cases.get(name, []),
                same_category=(name in same_cat),
            )

        return candidates
