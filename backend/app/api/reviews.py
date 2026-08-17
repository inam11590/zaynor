"""Reviews API router — public read + create, admin delete."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.product import Product
from app.models.review import Review
from app.schemas.review import ProductRatingSummary, ReviewCreate, ReviewRead
from app.services.auth import require_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)


@router.get("/", response_model=List[ReviewRead])
def list_reviews(
    product_id: int = Query(..., description="Filter by product ID"),
    db: Session = Depends(get_db),
):
    """List all reviews for a product, newest first."""
    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.get("/summary", response_model=ProductRatingSummary)
def get_rating_summary(
    product_id: int = Query(..., description="Product ID"),
    db: Session = Depends(get_db),
):
    """Get average rating and review count for a product."""
    result = (
        db.query(
            func.coalesce(func.avg(Review.rating), 0.0),
            func.count(Review.id),
        )
        .filter(Review.product_id == product_id)
        .one()
    )
    return ProductRatingSummary(
        average_rating=round(float(result[0]), 1),
        review_count=result[1],
    )


@router.post("/", response_model=ReviewRead, status_code=201)
@limiter.limit(settings.RATE_LIMIT_REVIEWS)
def create_review(
    request: Request,
    product_id: int = Query(..., description="Product ID"),
    payload: ReviewCreate = ...,
    db: Session = Depends(get_db),
):
    """Submit a review for a product. No auth required."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review = Review(
        product_id=product_id,
        customer_name=payload.customer_name,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Delete a review. Admin only."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()