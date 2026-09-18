"""
ShopGraph - Pydantic Models
app/models.py

Data models for API request/response validation.
"""

from pydantic import BaseModel, Field


class ProductDetail(BaseModel):
    """Full product information with graph relationships."""

    name: str
    price: float | None = None
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    features: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    compatible_with: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)
    works_with: list[str] = Field(default_factory=list)
    similar_to: list[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    """A single recommended product with its score and explanation."""

    product: str
    score: float = Field(ge=0.0, le=100.0, description="Score between 0 and 100")
    reasons: list[str] = Field(description="Human-readable reasons for recommendation")


class RecommendationResponse(BaseModel):
    """Full recommendation response."""

    purchased_product: str
    recommendations: list[RecommendationItem]


class HealthResponse(BaseModel):
    """API health/welcome response."""

    message: str
    version: str
