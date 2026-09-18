"""
ShopGraph - Product Recommender
app/recommender.py

Orchestrates candidate generation, scoring, ranking, and explanation.

Scoring formula (transparent, no ML):
  Final Score = 0.40 × Relationship Score
              + 0.25 × Feature Score
              + 0.15 × Category Score
              + 0.10 × Use Case Score
              + 0.10 × Similarity Score
  Normalised to 0–100.
"""

from dataclasses import dataclass
from app.database import Neo4jConnection
from app.candidate_generator import CandidateGenerator, CandidateInfo
from app.explanation import generate_reasons


# Relationship type weights for the Relationship component
_REL_WEIGHTS: dict[str, float] = {
    "COMPATIBLE_WITH": 1.0,
    "ACCESSORY":       1.0,
    "WORKS_WITH":      0.9,
    "SIMILAR_TO":      0.6,
}


@dataclass
class RecommendationResult:
    """A single scored and explained recommendation."""

    product: str
    score: float
    reasons: list[str]


class ProductRecommender:
    """
    Knowledge-Graph based product recommender.

    Steps:
      1. Validate the purchased product exists in Neo4j.
      2. Retrieve product metadata (features, use cases, category).
      3. Generate candidate products via graph traversal.
      4. Score each candidate across five dimensions.
      5. Sort by score and return top K with explanations.
    """

    def __init__(self, db: Neo4jConnection) -> None:
        self.db = db
        self.generator = CandidateGenerator(db)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_product_info(self, product_name: str) -> dict:
        """
        Fetch product metadata from Neo4j.

        Returns a dict with keys:
          - exists (bool)
          - features (list[str])
          - use_cases (list[str])
          - category (str | None)
          - brand (str | None)
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

    # ── Scoring ───────────────────────────────────────────────────────────────

    def _relationship_score(self, candidate: CandidateInfo) -> float:
        """
        Score based on direct graph relationships.
        Each relationship type has a weight; take the max (don't double-count).
        Returns 0–1.
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
        """
        Score based on shared feature overlap.
        Returns 0–1.  (overlap / max_possible capped at 1)
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
        """
        Score based on category relationship.
        Same-category products (alternatives) score 0.6.
        Different categories score 0 here (candidate from other categories
        still score via other dimensions).
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
        """
        Score based on shared use-case overlap.
        Returns 0–1.
        """
        if not purchased_use_cases or not candidate.shared_use_cases:
            return 0.0
        overlap = len(candidate.shared_use_cases)
        max_possible = len(purchased_use_cases)
        return min(overlap / max_possible, 1.0)

    def _similarity_score(self, candidate: CandidateInfo) -> float:
        """
        Score 1.0 if SIMILAR_TO relationship exists, else 0.
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
        """
        Weighted combination → normalised to 0–100.

        Weights:
          Relationship  40%
          Feature       25%
          Category      15%
          Use Case      10%
          Similarity    10%
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
        """
        Generate ranked recommendations for a purchased product.

        Args:
            purchased_product: Exact product name as stored in Neo4j.
            top_k:             Maximum number of recommendations to return.

        Returns:
            A sorted list of RecommendationResult objects (highest score first).

        Raises:
            ValueError: If the product is not found in Neo4j.
        """
        # 1. Validate
        product_info = self._get_product_info(purchased_product)
        if not product_info["exists"]:
            raise ValueError(
                f"Product '{purchased_product}' not found in the knowledge graph."
            )

        purchased_features  = product_info["features"]
        purchased_use_cases = product_info["use_cases"]
        purchased_category  = product_info["category"]

        # 2. Generate candidates via graph traversal
        candidates: dict[str, CandidateInfo] = self.generator.generate_candidates(
            purchased_product
        )

        # 3. Score each candidate
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

            # Skip zero-scored items (very unlikely but defensive)
            if final_score <= 0:
                continue

            reasons = generate_reasons(purchased_product, candidate)

            results.append(
                RecommendationResult(
                    product=candidate_name,
                    score=final_score,
                    reasons=reasons,
                )
            )

        # 4. Sort by score descending and return top K
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
