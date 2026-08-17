"""Pydantic schemas for Review request/response."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    customer_name: str
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewRead(BaseModel):
    id: int
    product_id: int
    customer_name: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductRatingSummary(BaseModel):
    """Average rating + review count for a product."""
    average_rating: float = 0.0
    review_count: int = 0