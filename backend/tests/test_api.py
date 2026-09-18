"""
ShopGraph - API Tests
tests/test_api.py

Tests the FastAPI endpoints using the httpx test client.

Endpoints tested:
  GET /
  GET /products
  GET /products/{product_name}
  GET /recommend/{product_name}

Prerequisites:
  - Neo4j running with KG loaded

Run with:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_root_returns_200(self) -> None:
        """GET / must return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_message(self) -> None:
        """GET / must contain a message field."""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "ShopGraph" in data["message"]

    def test_root_returns_version(self) -> None:
        """GET / must contain a version field."""
        response = client.get("/")
        data = response.json()
        assert "version" in data


class TestProductsEndpoint:
    def test_list_products_returns_200(self) -> None:
        """GET /products must return 200 OK."""
        response = client.get("/products")
        assert response.status_code == 200

    def test_list_products_returns_list(self) -> None:
        """GET /products must return a list."""
        response = client.get("/products")
        assert isinstance(response.json(), list)

    def test_list_products_not_empty(self) -> None:
        """GET /products must return at least one product."""
        response = client.get("/products")
        assert len(response.json()) >= 1

    def test_product_has_expected_fields(self) -> None:
        """Each product in the list must have name and category fields."""
        response = client.get("/products")
        products = response.json()
        first = products[0]
        assert "name" in first

    def test_get_product_detail_returns_200(self) -> None:
        """GET /products/Dell Inspiron 15 must return 200."""
        response = client.get("/products/Dell Inspiron 15")
        assert response.status_code == 200

    def test_get_product_detail_has_fields(self) -> None:
        """Product detail must include features, use_cases, compatible_with."""
        response = client.get("/products/Dell Inspiron 15")
        data = response.json()
        assert "name" in data
        assert "features" in data
        assert "use_cases" in data
        assert "compatible_with" in data
        assert "accessories" in data

    def test_get_product_detail_name_correct(self) -> None:
        """Product detail name must match the requested product."""
        response = client.get("/products/Dell Inspiron 15")
        data = response.json()
        assert data["name"] == "Dell Inspiron 15"

    def test_get_unknown_product_returns_404(self) -> None:
        """GET /products/Unknown must return 404."""
        response = client.get("/products/Unknown Product XYZ 999")
        assert response.status_code == 404


class TestRecommendEndpoint:
    def test_recommend_returns_200(self) -> None:
        """GET /recommend/Dell Inspiron 15 must return 200."""
        response = client.get("/recommend/Dell Inspiron 15")
        assert response.status_code == 200

    def test_recommend_has_purchased_product_field(self) -> None:
        """Response must echo back the purchased_product."""
        response = client.get("/recommend/Dell Inspiron 15")
        data = response.json()
        assert "purchased_product" in data
        assert data["purchased_product"] == "Dell Inspiron 15"

    def test_recommend_has_recommendations_list(self) -> None:
        """Response must contain a non-empty recommendations list."""
        response = client.get("/recommend/Dell Inspiron 15")
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 1

    def test_recommendation_has_required_fields(self) -> None:
        """Each recommendation must have product, score, and reasons."""
        response = client.get("/recommend/Dell Inspiron 15")
        rec = response.json()["recommendations"][0]
        assert "product" in rec
        assert "score" in rec
        assert "reasons" in rec

    def test_recommendation_score_in_range(self) -> None:
        """All recommendation scores must be between 0 and 100."""
        response = client.get("/recommend/Dell Inspiron 15")
        for rec in response.json()["recommendations"]:
            assert 0 <= rec["score"] <= 100

    def test_recommendation_reasons_not_empty(self) -> None:
        """Each recommendation must have at least one reason."""
        response = client.get("/recommend/Dell Inspiron 15")
        for rec in response.json()["recommendations"]:
            assert len(rec["reasons"]) >= 1

    def test_top_k_query_param(self) -> None:
        """?top_k=3 must return at most 3 recommendations."""
        response = client.get("/recommend/Dell Inspiron 15?top_k=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) <= 3

    def test_unknown_product_returns_404(self) -> None:
        """Recommending an unknown product must return 404."""
        response = client.get("/recommend/Unknown Product XYZ 999")
        assert response.status_code == 404

    def test_recommend_hp_pavilion(self) -> None:
        """HP Pavilion 15 must also return valid recommendations."""
        response = client.get("/recommend/HP Pavilion 15")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) >= 1

    def test_recommend_lenovo(self) -> None:
        """Lenovo IdeaPad Slim 5 must also return valid recommendations."""
        response = client.get("/recommend/Lenovo IdeaPad Slim 5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) >= 1
