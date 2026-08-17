"""Wishlist Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WishlistAdd(BaseModel):
    session_key: str = Field(..., min_length=1, max_length=64)
    product_slug: str = Field(..., min_length=1, max_length=255)


class WishlistItem(BaseModel):
    id: int
    product_slug: str
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WishlistCount(BaseModel):
    count: int
