"""Products API router — public read + admin CRUD endpoints."""

import json
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductRead, ProductSummary
from app.services.auth import require_admin

router = APIRouter(prefix="/products", tags=["Products"])

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[ProductSummary])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    db: Session = Depends(get_db),
):
    """List active products, optionally filtered by category slug."""
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.is_active == True)

    if category:
        query = query.join(Product.category).filter(
            Product.category.has(slug=category)
        )

    return query.all()


@router.get("/all", response_model=list[ProductSummary])
def list_all_products(
    db: Session = Depends(get_db),
):
    """List ALL products (including inactive) — admin only."""
    return db.query(Product).options(joinedload(Product.category)).all()


@router.get("/search", response_model=list[ProductSummary])
def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """Search active products by name or description."""
    term = f"%{q}%"
    query = db.query(Product).options(joinedload(Product.category)).filter(
        Product.is_active == True,
        (Product.name.ilike(term) | Product.short_description.ilike(term) | Product.description.ilike(term)),
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
# Admin-only endpoints
# ---------------------------------------------------------------------------
@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    slug: str = Query(...),
    name: str = Query(...),
    price: float = Query(...),
    image: str = Query(...),
    short_description: str = Query(...),
    description: str = Query(...),
    category_slug: str = Query(...),
    specs: str = Query("{}"),
    is_active: bool = Query(True),
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
        is_active=is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    slug: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    image: Optional[str] = Query(None),
    short_description: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    category_slug: Optional[str] = Query(None),
    specs: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Update an existing product. Admin only."""
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
    if is_active is not None:
        product.is_active = is_active
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


# ---------------------------------------------------------------------------
# Image Upload
# ---------------------------------------------------------------------------
@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    folder: str = Query("products", description="Subfolder: perfumes, skincare, or products"),
    admin=Depends(require_admin),
):
    """Upload a product image. Returns the relative path to use in the product."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}")

    save_dir = os.path.join(IMAGES_DIR, folder)
    os.makedirs(save_dir, exist_ok=True)

    filename = uuid.uuid4().hex[:12] + ext
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return {"path": f"images/{folder}/{filename}", "filename": filename}
