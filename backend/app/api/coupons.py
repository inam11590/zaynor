"""Coupons API router — validate, apply, admin CRUD."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponRead, CouponValidate, CouponValidateResponse
from app.services.auth import require_admin

router = APIRouter(prefix="/coupons", tags=["Coupons"])
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)


def _validate_coupon(coupon: Coupon, order_amount: float) -> CouponValidateResponse:
    """Validate a coupon and return the discount breakdown."""
    now = datetime.now(timezone.utc)

    if not coupon.is_active:
        return CouponValidateResponse(
            valid=False, code=coupon.code, discount_percent=coupon.discount_percent,
            discount_amount=0, final_amount=order_amount,
            message="This coupon is no longer active.",
        )

    if coupon.expires_at and coupon.expires_at.replace(tzinfo=timezone.utc) < now:
        return CouponValidateResponse(
            valid=False, code=coupon.code, discount_percent=coupon.discount_percent,
            discount_amount=0, final_amount=order_amount,
            message="This coupon has expired.",
        )

    if coupon.max_uses is not None and coupon.times_used >= coupon.max_uses:
        return CouponValidateResponse(
            valid=False, code=coupon.code, discount_percent=coupon.discount_percent,
            discount_amount=0, final_amount=order_amount,
            message="This coupon has reached its usage limit.",
        )

    if order_amount < coupon.min_order_amount:
        return CouponValidateResponse(
            valid=False, code=coupon.code, discount_percent=coupon.discount_percent,
            discount_amount=0, final_amount=order_amount,
            message=f"Minimum order amount is Rs. {coupon.min_order_amount:,.0f}.",
        )

    discount = round(order_amount * coupon.discount_percent / 100, 2)
    final = round(order_amount - discount, 2)

    return CouponValidateResponse(
        valid=True, code=coupon.code, discount_percent=coupon.discount_percent,
        discount_amount=discount, final_amount=final,
        message=f"{coupon.discount_percent}% discount applied!",
    )


@router.post("/validate", response_model=CouponValidateResponse)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def validate_coupon(request: Request, payload: CouponValidate, db: Session = Depends(get_db)):
    """Validate a coupon code against an order amount. Does NOT consume uses."""
    coupon = db.query(Coupon).filter(Coupon.code == payload.code.upper()).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return _validate_coupon(coupon, payload.order_amount)


@router.get("/", response_model=List[CouponRead])
def list_coupons(
    active_only: bool = Query(False, description="Show only active coupons"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """List all coupons. Admin only."""
    query = db.query(Coupon)
    if active_only:
        query = query.filter(Coupon.is_active == True)
    return query.order_by(Coupon.created_at.desc()).all()


@router.post("/", response_model=CouponRead, status_code=201)
def create_coupon(
    payload: CouponCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Create a new coupon. Admin only."""
    existing = db.query(Coupon).filter(Coupon.code == payload.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(
        code=payload.code.upper(),
        discount_percent=payload.discount_percent,
        min_order_amount=payload.min_order_amount,
        max_uses=payload.max_uses,
        is_active=payload.is_active,
        expires_at=payload.expires_at,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.put("/{coupon_id}", response_model=CouponRead)
def update_coupon(
    coupon_id: int,
    payload: CouponCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Update a coupon. Admin only."""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    # Check code uniqueness if changed
    if payload.code.upper() != coupon.code:
        existing = db.query(Coupon).filter(Coupon.code == payload.code.upper()).first()
        if existing:
            raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon.code = payload.code.upper()
    coupon.discount_percent = payload.discount_percent
    coupon.min_order_amount = payload.min_order_amount
    coupon.max_uses = payload.max_uses
    coupon.is_active = payload.is_active
    coupon.expires_at = payload.expires_at
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}", status_code=204)
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Delete a coupon. Admin only."""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    db.delete(coupon)
    db.commit()
