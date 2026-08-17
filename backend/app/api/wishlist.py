"""Wishlist API router — add, remove, list, check."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistAdd, WishlistCount, WishlistItem

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/", response_model=WishlistItem, status_code=201)
def add_to_wishlist(payload: WishlistAdd, db: Session = Depends(get_db)):
    """Add a product to a session's wishlist. Idempotent — returns existing if already saved."""
    # Verify product exists
    product = db.query(Product).filter(Product.slug == payload.product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already in wishlist
    existing = (
        db.query(Wishlist)
        .filter(Wishlist.session_key == payload.session_key, Wishlist.product_slug == payload.product_slug)
        .first()
    )
    if existing:
        return WishlistItem(
            id=existing.id,
            product_slug=existing.product_slug,
            product_name=product.name,
            product_price=product.price,
            product_image=product.image,
            created_at=existing.created_at,
        )

    item = Wishlist(session_key=payload.session_key, product_slug=payload.product_slug)
    db.add(item)
    db.commit()
    db.refresh(item)

    return WishlistItem(
        id=item.id,
        product_slug=item.product_slug,
        product_name=product.name,
        product_price=product.price,
        product_image=product.image,
        created_at=item.created_at,
    )


@router.delete("/{product_slug}", status_code=204)
def remove_from_wishlist(
    product_slug: str,
    session_key: str = Query(..., description="Session key"),
    db: Session = Depends(get_db),
):
    """Remove a product from a session's wishlist."""
    item = (
        db.query(Wishlist)
        .filter(Wishlist.session_key == session_key, Wishlist.product_slug == product_slug)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    db.delete(item)
    db.commit()


@router.get("/", response_model=List[WishlistItem])
def list_wishlist(
    session_key: str = Query(..., description="Session key"),
    db: Session = Depends(get_db),
):
    """List all items in a session's wishlist, with product details."""
    items = (
        db.query(Wishlist)
        .filter(Wishlist.session_key == session_key)
        .order_by(Wishlist.created_at.desc())
        .all()
    )

    result = []
    for item in items:
        product = db.query(Product).filter(Product.slug == item.product_slug).first()
        result.append(
            WishlistItem(
                id=item.id,
                product_slug=item.product_slug,
                product_name=product.name if product else item.product_slug,
                product_price=product.price if product else None,
                product_image=product.image if product else None,
                created_at=item.created_at,
            )
        )
    return result


@router.get("/count", response_model=WishlistCount)
def wishlist_count(
    session_key: str = Query(..., description="Session key"),
    db: Session = Depends(get_db),
):
    """Get the number of items in a session's wishlist."""
    count = db.query(Wishlist).filter(Wishlist.session_key == session_key).count()
    return WishlistCount(count=count)


@router.get("/check", response_model=dict)
def check_wishlist(
    session_key: str = Query(..., description="Session key"),
    product_slug: str = Query(..., description="Product slug"),
    db: Session = Depends(get_db),
):
    """Check if a product is in a session's wishlist."""
    exists = (
        db.query(Wishlist)
        .filter(Wishlist.session_key == session_key, Wishlist.product_slug == product_slug)
        .first()
        is not None
    )
    return {"in_wishlist": exists}
