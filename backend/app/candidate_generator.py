"""
ShopGraph - Knowledge Graph Candidate Generator
app/candidate_generator.py

This module queries the Neo4j Knowledge Graph to find candidate products
for recommendations based on a seed/purchased product.

Candidate Discovery Strategies:
  A. Direct Graph Relationships:
     - COMPATIBLE_WITH: Hardware/accessories explicitly verified to work together.
     - ACCESSORY: Complementary add-on products (e.g. mouse for a laptop).
     - WORKS_WITH: Functional synergy (e.g. docking station for a laptop).
     - SIMILAR_TO: Alternative or competitor products in the same domain.
  B. Shared Features:
     - Products that have matching Feature nodes (e.g. USB-C, 4K Display, ANC).
  C. Shared Use Cases:
     - Products sharing target user scenarios (e.g. Remote Work, Gaming, Video Editing).
  D. Same Category:
     - Products belonging to the identical Category node (substitutes / alternatives).
"""

from dataclasses import dataclass, field
from app.database import Neo4jConnection


@dataclass
class CandidateInfo:
    """Encapsulates a candidate product and the graph signals discovered for it.
    
    Attributes:
        name (str): Product identifier name.
        direct_relationships (list[str]): Types of direct relationships pointing to/from the seed product.
        shared_features (list[str]): Feature node names shared in common with the seed product.
        shared_use_cases (list[str]): UseCase node names shared in common with the seed product.
        same_category (bool): True if candidate shares the same Category node as the seed product.
    """

    name: str
    direct_relationships: list[str] = field(default_factory=list)
    shared_features: list[str] = field(default_factory=list)
    shared_use_cases: list[str] = field(default_factory=list)
    same_category: bool = False


class CandidateGenerator:
    """Traverses the Neo4j knowledge graph to discover candidate products for recommendation."""

    def __init__(self, db: Neo4jConnection) -> None:
        """Initialize the generator with an active database connection.
        
        Args:
            db (Neo4jConnection): Database connection instance.
        """
        self.db = db

    # ── Strategy A: Direct Graph Relationships ────────────────────────────────

    def get_direct_candidates(self, product_name: str) -> dict[str, list[str]]:
        """Query direct graph edges (COMPATIBLE_WITH, ACCESSORY, WORKS_WITH, SIMILAR_TO).
        
        Args:
            product_name (str): Seed product name.

        Returns:
            dict[str, list[str]]: Mapping from candidate product name to list of relationship types.
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

    # ── Strategy B: Shared Features ───────────────────────────────────────────

    def get_feature_candidates(self, product_name: str) -> dict[str, list[str]]:
        """Find candidate products sharing at least one Feature node with the input product.
        
        Args:
            product_name (str): Seed product name.

        Returns:
            dict[str, list[str]]: Mapping from candidate product name to list of shared feature names.
        """
        query = """
        MATCH (p:Product {name: $name})-[:HAS_FEATURE]->(f:Feature)
              <-[:HAS_FEATURE]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate, collect(DISTINCT f.name) AS shared_features
        """
        rows = self.db.run_query(query, {"name": product_name})
        return {row["candidate"]: row["shared_features"] for row in rows}

    # ── Strategy C: Shared Use Cases ──────────────────────────────────────────

    def get_use_case_candidates(self, product_name: str) -> dict[str, list[str]]:
        """Find candidate products sharing at least one UseCase node with the input product.
        
        Args:
            product_name (str): Seed product name.

        Returns:
            dict[str, list[str]]: Mapping from candidate product name to list of shared use-case names.
        """
        query = """
        MATCH (p:Product {name: $name})-[:USED_FOR]->(u:UseCase)
              <-[:USED_FOR]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate, collect(DISTINCT u.name) AS shared_use_cases
        """
        rows = self.db.run_query(query, {"name": product_name})
        return {row["candidate"]: row["shared_use_cases"] for row in rows}

    # ── Strategy D: Same Category ─────────────────────────────────────────────

    def get_same_category_candidates(self, product_name: str) -> list[str]:
        """Find products belonging to the same Category node (substitutes/alternatives).
        
        Args:
            product_name (str): Seed product name.

        Returns:
            list[str]: List of candidate product names in the same category.
        """
        query = """
        MATCH (p:Product {name: $name})-[:BELONGS_TO]->(cat:Category)
              <-[:BELONGS_TO]-(c:Product)
        WHERE c.name <> $name
        RETURN c.name AS candidate
        """
        rows = self.db.run_query(query, {"name": product_name})
        return [row["candidate"] for row in rows]

    # ── Aggregated Multi-Strategy Candidate Generation ────────────────────────

    def generate_candidates(self, product_name: str) -> dict[str, CandidateInfo]:
        """Execute all four graph discovery strategies and consolidate signals into CandidateInfo objects.

        Args:
            product_name (str): The exact name of the purchased/context product.

        Returns:
            dict[str, CandidateInfo]: Mapping of candidate product names to their accumulated graph signals.
        """
        # Execute individual traversal queries
        direct = self.get_direct_candidates(product_name)
        features = self.get_feature_candidates(product_name)
        use_cases = self.get_use_case_candidates(product_name)
        same_cat = set(self.get_same_category_candidates(product_name))

        # Union of all candidate names surfaced by any strategy
        all_names: set[str] = (
            set(direct.keys())
            | set(features.keys())
            | set(use_cases.keys())
            | same_cat
        )
        # Exclude the seed product itself from candidate recommendations
        all_names.discard(product_name)

        # Build structured signal containers in deterministic order
        candidates: dict[str, CandidateInfo] = {}
        for name in sorted(all_names):
            candidates[name] = CandidateInfo(
                name=name,
                direct_relationships=direct.get(name, []),
                shared_features=features.get(name, []),
                shared_use_cases=use_cases.get(name, []),
                same_category=(name in same_cat),
            )

        return candidates

