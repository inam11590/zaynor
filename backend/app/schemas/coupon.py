"""Coupon Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CouponCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    discount_percent: float = Field(..., gt=0, le=100)
    min_order_amount: float = Field(0.0, ge=0)
    max_uses: Optional[int] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None


class CouponRead(BaseModel):
    id: int
    code: str
    discount_percent: float
    min_order_amount: float
    max_uses: Optional[int] = None
    times_used: int
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CouponValidate(BaseModel):
    code: str
    order_amount: float


class CouponValidateResponse(BaseModel):
    valid: bool
    code: str
    discount_percent: float
    discount_amount: float
    final_amount: float
    message: str
