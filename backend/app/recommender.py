"""
ShopGraph - Knowledge Graph Product Recommender
app/recommender.py

This module coordinates candidate product discovery, transparent multi-dimensional
scoring, ranking, and human-readable explanation generation.

Scoring Formula (Explainable, Rule-Based, No Black-Box ML):
  Final Score = (
      0.40 × Relationship Score  (direct graph edges: COMPATIBLE_WITH, ACCESSORY, WORKS_WITH, SIMILAR_TO)
    + 0.25 × Feature Score       (Jaccard-style feature overlap ratio)
    + 0.15 × Category Score      (same-category substitute boost)
    + 0.10 × Use Case Score      (shared practical application overlap)
    + 0.10 × Similarity Score    (direct SIMILAR_TO graph link)
  ) × 100 (normalized to a 0–100 scale)
"""

from dataclasses import dataclass
from app.database import Neo4jConnection
from app.candidate_generator import CandidateGenerator, CandidateInfo
from app.explanation import generate_reasons

# Relative weights applied to direct relationship types for the Relationship component
_REL_WEIGHTS: dict[str, float] = {
    "COMPATIBLE_WITH": 1.0,
    "ACCESSORY":       1.0,
    "WORKS_WITH":      0.9,
    "SIMILAR_TO":      0.6,
}


@dataclass
class RecommendationResult:
    """A scored and explained recommendation item.
    
    Attributes:
        product (str): Name of the recommended product.
        score (float): Normalized recommendation score (0–100).
        reasons (list[str]): List of human-readable explanation strings derived from the graph.
    """

    product: str
    score: float
    reasons: list[str]


class ProductRecommender:
    """Knowledge-Graph powered recommendation engine.

    Pipeline Steps:
      1. Validation: Ensure the context product exists in the Neo4j Knowledge Graph.
      2. Metadata Retrieval: Extract product features, use cases, category, and brand.
      3. Candidate Generation: Traverse graph relationships via CandidateGenerator.
      4. Multi-Factor Scoring: Evaluate each candidate across the 5 defined scoring dimensions.
      5. Ranking & Explanation: Sort descending by score and attach transparent explanations.
    """

    def __init__(self, db: Neo4jConnection) -> None:
        """Initialize the recommender with a database connection and candidate generator.
        
        Args:
            db (Neo4jConnection): Database connection instance.
        """
        self.db = db
        self.generator = CandidateGenerator(db)


    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_product_info(self, product_name: str) -> dict:
        """Fetch product metadata, linked features, use cases, category, and brand from Neo4j.

        Args:
            product_name (str): Exact product title string.

        Returns:
            dict: Dictionary with keys 'exists', 'features', 'use_cases', 'category', 'brand'.
        """
        query = """
        MATCH (p:Product {name: $name})
        OPTIONAL MATCH (p)-[:HAS_FEATURE]->(f:Feature)
        OPTIONAL MATCH (p)-[:USED_FOR]->(u:UseCase)
        OPTIONAL MATCH (p)-[:BELONGS_TO]->(cat:Category)
        OPTIONAL MATCH (p)-[:MADE_BY]->(b:Brand)
        RETURN
          p.name AS name,
          collect(DISTINCT f.name) AS features,
          collect(DISTINCT u.name) AS use_cases,
          cat.name AS category,
          b.name AS brand
        """
        rows = self.db.run_query(query, {"name": product_name})
        if not rows or rows[0]["name"] is None:
            return {"exists": False}

        row = rows[0]
        return {
            "exists": True,
            "features":  row["features"]  or [],
            "use_cases": row["use_cases"] or [],
            "category":  row["category"],
            "brand":     row["brand"],
        }

    # ── Scoring Components ───────────────────────────────────────────────────

    def _relationship_score(self, candidate: CandidateInfo) -> float:
        """Compute score (0.0 to 1.0) based on direct Knowledge Graph edges.
        
        Evaluates relationships against weighted priorities (e.g. COMPATIBLE_WITH = 1.0,
        ACCESSORY = 1.0, WORKS_WITH = 0.9, SIMILAR_TO = 0.6) taking the highest weight
        to avoid redundant double-counting.

        Args:
            candidate (CandidateInfo): Discovered candidate container.

        Returns:
            float: Relationship score component between 0.0 and 1.0.
        """
        if not candidate.direct_relationships:
            return 0.0
        best = max(_REL_WEIGHTS.get(r, 0.3) for r in candidate.direct_relationships)
        return best

    def _feature_score(
        self,
        purchased_features: list[str],
        candidate: CandidateInfo,
    ) -> float:
        """Compute score (0.0 to 1.0) based on shared feature specifications overlap.

        Args:
            purchased_features (list[str]): Features possessed by the seed product.
            candidate (CandidateInfo): Candidate product with its shared feature list.

        Returns:
            float: Overlap ratio capped at 1.0.
        """
        if not purchased_features or not candidate.shared_features:
            return 0.0
        overlap = len(candidate.shared_features)
        max_possible = len(purchased_features)
        return min(overlap / max_possible, 1.0)

    def _category_score(
        self,
        purchased_category: str | None,
        candidate_name: str,
    ) -> float:
        """Evaluate category alignment; awards 0.6 if candidate is in the same category.

        Args:
            purchased_category (str | None): Category of the purchased product.
            candidate_name (str): Name of the candidate product.

        Returns:
            float: Category affinity score (0.6 for same-category alternative, 0.0 otherwise).
        """
        query = """
        MATCH (p:Product {name: $name})-[:BELONGS_TO]->(c:Category)
        RETURN c.name AS category
        """
        rows = self.db.run_query(query, {"name": candidate_name})
        if not rows:
            return 0.0
        candidate_category = rows[0]["category"]
        if purchased_category and candidate_category == purchased_category:
            return 0.6  # Alternative in the same category
        return 0.0

    def _use_case_score(
        self,
        purchased_use_cases: list[str],
        candidate: CandidateInfo,
    ) -> float:
        """Compute score (0.0 to 1.0) based on shared practical application/use-case overlap.

        Args:
            purchased_use_cases (list[str]): Use cases associated with seed product.
            candidate (CandidateInfo): Candidate product with its shared use-case list.

        Returns:
            float: Use-case overlap ratio capped at 1.0.
        """
        if not purchased_use_cases or not candidate.shared_use_cases:
            return 0.0
        overlap = len(candidate.shared_use_cases)
        max_possible = len(purchased_use_cases)
        return min(overlap / max_possible, 1.0)

    def _similarity_score(self, candidate: CandidateInfo) -> float:
        """Check whether explicit SIMILAR_TO relationship exists in the knowledge graph.

        Args:
            candidate (CandidateInfo): Candidate product information.

        Returns:
            float: 1.0 if SIMILAR_TO edge is present, otherwise 0.0.
        """
        return 1.0 if "SIMILAR_TO" in candidate.direct_relationships else 0.0

    def _compute_final_score(
        self,
        rel_score: float,
        feat_score: float,
        cat_score: float,
        uc_score: float,
        sim_score: float,
    ) -> float:
        """Calculate weighted composite score and normalize to a 0–100 scale.

        Formula:
          raw = 0.40 * rel_score + 0.25 * feat_score + 0.15 * cat_score + 0.10 * uc_score + 0.10 * sim_score
          final = round(raw * 100, 2)

        Args:
            rel_score (float): Direct relationship score (0–1).
            feat_score (float): Feature overlap score (0–1).
            cat_score (float): Category affinity score (0–1).
            uc_score (float): Use-case overlap score (0–1).
            sim_score (float): Direct similarity score (0–1).

        Returns:
            float: Composite score rounded to two decimal places (0.0 to 100.0).
        """
        raw = (
            0.40 * rel_score
            + 0.25 * feat_score
            + 0.15 * cat_score
            + 0.10 * uc_score
            + 0.10 * sim_score
        )
        return round(raw * 100, 2)

    # ── Public API ────────────────────────────────────────────────────────────

    def recommend(
        self,
        purchased_product: str,
        top_k: int = 5,
    ) -> list[RecommendationResult]:
        """Generate ranked, explainable product recommendations for a seed product.

        Execution Flow:
          1. Validate product exists in Neo4j.
          2. Extract seed product metadata (features, use cases, category).
          3. Generate candidate set using graph traversal.
          4. Score each candidate across the 5 dimensions.
          5. Synthesize natural-language explanations from graph edges.
          6. Rank descending by score and return top K results.

        Args:
            purchased_product (str): Exact title of seed/purchased product.
            top_k (int): Maximum number of recommendations to return (default: 5).

        Returns:
            list[RecommendationResult]: Sorted recommendations with scores and explanations.

        Raises:
            ValueError: If purchased_product does not exist in the knowledge graph.
        """
        # 1. Validate existence and fetch metadata
        product_info = self._get_product_info(purchased_product)
        if not product_info["exists"]:
            raise ValueError(
                f"Product '{purchased_product}' not found in the knowledge graph."
            )

        purchased_features  = product_info["features"]
        purchased_use_cases = product_info["use_cases"]
        purchased_category  = product_info["category"]

        # 2. Generate candidate products via graph traversal
        candidates: dict[str, CandidateInfo] = self.generator.generate_candidates(
            purchased_product
        )

        # 3. Score each candidate across dimensions
        results: list[RecommendationResult] = []
        for candidate_name, candidate in candidates.items():
            rel_score  = self._relationship_score(candidate)
            feat_score = self._feature_score(purchased_features, candidate)
            cat_score  = self._category_score(purchased_category, candidate_name)
            uc_score   = self._use_case_score(purchased_use_cases, candidate)
            sim_score  = self._similarity_score(candidate)

            final_score = self._compute_final_score(
                rel_score, feat_score, cat_score, uc_score, sim_score
            )

            # Defensive check: skip items with 0 score
            if final_score <= 0:
                continue

            # Generate natural language reasons
            reasons = generate_reasons(purchased_product, candidate)

            results.append(
                RecommendationResult(
                    product=candidate_name,
                    score=final_score,
                    reasons=reasons,
                )
            )

        # 4. Sort descending by score and return top K
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

