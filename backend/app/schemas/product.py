"""Pydantic schemas for Product responses."""

import json
from typing import Any, Dict

from pydantic import BaseModel, field_validator


class ProductBase(BaseModel):
    slug: str
    name: str
    price: float
    image: str
    short_description: str
    description: str
    category_id: int


class ProductRead(ProductBase):
    id: int
    specs: Dict[str, Any] = {}

    model_config = {"from_attributes": True}

    @field_validator("specs", mode="before")
    @classmethod
    def parse_specs_json(cls, v: Any) -> Dict[str, Any]:
        """Convert the JSON string stored in the DB into a dict."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v


class ProductSummary(BaseModel):
    """Lighter response — used in product list endpoints."""

    id: int
    slug: str
    name: str
    price: float
    image: str
    short_description: str
    category_id: int

    model_config = {"from_attributes": True}
