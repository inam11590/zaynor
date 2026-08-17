"""Pydantic schemas for Category responses."""

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    slug: str


class CategoryRead(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
