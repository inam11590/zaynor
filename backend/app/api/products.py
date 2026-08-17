"""Products API router — public read + admin CRUD endpoints."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductRead, ProductSummary
from app.services.auth import require_admin

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------------------------------------------------------------------
# Public endpoints (Phase 2)
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[ProductSummary])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category slug (e.g. 'perfumes')"),
    db: Session = Depends(get_db),
):
    """List all products, optionally filtered by category slug."""
    query = db.query(Product).options(joinedload(Product.category))

    if category:
        query = query.join(Product.category).filter(
            Product.category.has(slug=category)
        )

    return query.all()


@router.get("/search", response_model=list[ProductSummary])
def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """Search products by name, short description, or description."""
    term = f"%{q}%"
    query = db.query(Product).options(joinedload(Product.category)).filter(
        Product.name.ilike(term)
        | Product.short_description.ilike(term)
        | Product.description.ilike(term)
    )
    return query.all()


@router.get("/{product_slug}", response_model=ProductRead)
def get_product(product_slug: str, db: Session = Depends(get_db)):
    """Get a single product by its slug."""
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.slug == product_slug)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---------------------------------------------------------------------------
# Admin-only endpoints (Phase 5)
# ---------------------------------------------------------------------------
@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    slug: str,
    name: str,
    price: float,
    image: str,
    short_description: str,
    description: str,
    category_slug: str,
    specs: str = "{}",
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Create a new product. Admin only."""
    if db.query(Product).filter(Product.slug == slug).first():
        raise HTTPException(status_code=400, detail="Product slug already exists")

    category = db.query(Category).filter(Category.slug == category_slug).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{category_slug}' not found")

    product = Product(
        slug=slug,
        name=name,
        price=price,
        image=image,
        short_description=short_description,
        description=description,
        specs=specs,
        category_id=category.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    slug: Optional[str] = None,
    name: Optional[str] = None,
    price: Optional[float] = None,
    image: Optional[str] = None,
    short_description: Optional[str] = None,
    description: Optional[str] = None,
    category_slug: Optional[str] = None,
    specs: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Update an existing product. Admin only. Only provided fields are changed."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if slug is not None:
        existing = db.query(Product).filter(Product.slug == slug, Product.id != product_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Product slug already exists")
        product.slug = slug

    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if image is not None:
        product.image = image
    if short_description is not None:
        product.short_description = short_description
    if description is not None:
        product.description = description
    if specs is not None:
        product.specs = specs
    if category_slug is not None:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category '{category_slug}' not found")
        product.category_id = category.id

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Delete a product. Admin only."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
