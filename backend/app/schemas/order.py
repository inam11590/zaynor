"""Pydantic schemas for Order and OrderItem request/response."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Order Items
# ---------------------------------------------------------------------------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str = ""
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    notes: Optional[str] = None


class OrderRead(BaseModel):
    id: int
    customer_id: int
    status: str
    total: float
    notes: Optional[str] = None
    items: List[OrderItemRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderTrackingRead(BaseModel):
    """Public order tracking response — includes customer name but no email/address."""
    id: int
    status: str
    total: float
    items: List[OrderItemRead] = []
    created_at: datetime
    customer_name: str = ""

    model_config = {"from_attributes": True}
