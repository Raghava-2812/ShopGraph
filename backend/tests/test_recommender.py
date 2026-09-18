"""
ShopGraph - Recommender Tests
tests/test_recommender.py

Tests the recommendation engine end-to-end:
  - Recommendations are returned
  - Purchased product is not in recommendations
  - Scores are numeric and in range 0–100
  - Recommendations contain explanations

Prerequisites:
  - Neo4j running with KG loaded

Run with:
    pytest tests/test_recommender.py -v
"""

import pytest
from app.database import get_db, Neo4jConnection
from app.recommender import ProductRecommender, RecommendationResult

TEST_PRODUCTS = [
    "Dell Inspiron 15",
    "HP Pavilion 15",
    "Lenovo IdeaPad Slim 5",
]


@pytest.fixture(scope="module")
def db() -> Neo4jConnection:
    conn = get_db()
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def recommender(db: Neo4jConnection) -> ProductRecommender:
    return ProductRecommender(db)


class TestRecommenderBasic:
    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_recommendations_returned(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """Recommender must return at least one recommendation."""
        results = recommender.recommend(product, top_k=5)
        assert len(results) >= 1, f"No recommendations for {product}"

    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_purchased_product_not_in_results(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """The purchased product must never appear in its own recommendations."""
        results = recommender.recommend(product, top_k=10)
        names = [r.product for r in results]
        assert product not in names, (
            f"'{product}' found in its own recommendations!"
        )

    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_scores_are_numeric(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """All scores must be numeric (int or float)."""
        results = recommender.recommend(product, top_k=5)
        for rec in results:
            assert isinstance(rec.score, (int, float)), (
                f"Score for {rec.product} is not numeric: {rec.score}"
            )

    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_scores_in_valid_range(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """All scores must be between 0 and 100."""
        results = recommender.recommend(product, top_k=10)
        for rec in results:
            assert 0 <= rec.score <= 100, (
                f"Score {rec.score} for {rec.product} is out of range 0–100"
            )

    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_recommendations_have_reasons(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """Every recommendation must have at least one reason."""
        results = recommender.recommend(product, top_k=5)
        for rec in results:
            assert len(rec.reasons) >= 1, (
                f"Recommendation for {rec.product} has no reasons!"
            )
            for reason in rec.reasons:
                assert isinstance(reason, str), "Reason must be a string"
                assert len(reason) > 0, "Reason must not be empty"

    @pytest.mark.parametrize("product", TEST_PRODUCTS)
    def test_results_sorted_by_score_descending(
        self,
        recommender: ProductRecommender,
        product: str,
    ) -> None:
        """Results must be sorted from highest to lowest score."""
        results = recommender.recommend(product, top_k=10)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True), (
            f"Results for {product} are not sorted by score descending"
        )

    def test_invalid_product_raises_value_error(
        self, recommender: ProductRecommender
    ) -> None:
        """Recommending an unknown product must raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            recommender.recommend("NonExistentProduct XYZ", top_k=5)


class TestRecommenderTopK:
    def test_top_k_respected(self, recommender: ProductRecommender) -> None:
        """Recommender must return at most top_k results."""
        results = recommender.recommend("Dell Inspiron 15", top_k=3)
        assert len(results) <= 3

    def test_top_k_one(self, recommender: ProductRecommender) -> None:
        """top_k=1 must return exactly one result."""
        results = recommender.recommend("Dell Inspiron 15", top_k=1)
        assert len(results) == 1


class TestRecommenderContent:
    def test_dell_inspiron_gets_hub_or_mouse(
        self, recommender: ProductRecommender
    ) -> None:
        """
        Dell Inspiron 15 should recommend a USB hub or mouse
        since they are directly COMPATIBLE_WITH the laptop.
        """
        results = recommender.recommend("Dell Inspiron 15", top_k=10)
        product_names = [r.product for r in results]
        expected = {"Dell USB-C Hub", "Logitech MX Master 3S", "Keychron K2"}
        found = expected.intersection(set(product_names))
        assert found, (
            f"Expected at least one of {expected} in recommendations "
            f"for Dell Inspiron 15, got: {product_names}"
        )
