"""
ShopGraph - Pydantic Request/Response Data Validation Schemas
app/models.py

This module defines Pydantic schemas used across FastAPI routes for strict
data parsing, JSON serialization, OpenAPI specification documentation, and type safety.
"""

from pydantic import BaseModel, Field


class ProductDetail(BaseModel):
    """Rich product data model including attributes and Knowledge Graph relationship sets.
    
    Attributes:
        name (str): Unique product title/name.
        price (float | None): Current sale price in USD.
        description (str | None): Marketing and technical product description.
        category (str | None): Primary product category node name.
        brand (str | None): Manufacturer / brand node name.
        features (list[str]): Names of connected Feature nodes (via HAS_FEATURE).
        use_cases (list[str]): Names of connected UseCase nodes (via USED_FOR).
        compatible_with (list[str]): Related products that are hardware/software compatible.
        accessories (list[str]): Recommended complementary accessory products.
        works_with (list[str]): Products that synergize or integrate together.
        similar_to (list[str]): Direct alternative or substitute products.
    """

    name: str
    price: float | None = None
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    features: list[str] = Field(default_factory=list, description="Connected feature names")
    use_cases: list[str] = Field(default_factory=list, description="Target use-case scenarios")
    compatible_with: list[str] = Field(default_factory=list, description="Directly compatible products")
    accessories: list[str] = Field(default_factory=list, description="Recommended accessories")
    works_with: list[str] = Field(default_factory=list, description="Functional companion products")
    similar_to: list[str] = Field(default_factory=list, description="Direct product alternatives")


class RecommendationItem(BaseModel):
    """Individual scored and explained recommendation item.
    
    Attributes:
        product (str): Name of the recommended product.
        score (float): Calculated recommendation score between 0.0 and 100.0.
        reasons (list[str]): Human-readable bullet points explaining WHY this product was chosen.
    """

    product: str
    score: float = Field(ge=0.0, le=100.0, description="Confidence score between 0 and 100")
    reasons: list[str] = Field(description="Human-readable transparent explanations")


class RecommendationResponse(BaseModel):
    """Top-level recommendation API response payload.
    
    Attributes:
        purchased_product (str): Name of the context/seed product.
        recommendations (list[RecommendationItem]): Ranked list of recommendation items.
    """

    purchased_product: str
    recommendations: list[RecommendationItem]


class HealthResponse(BaseModel):
    """Application health and API metadata response.
    
    Attributes:
        message (str): Welcome or status message.
        version (str): Deployed service version.
    """

    message: str
    version: str

