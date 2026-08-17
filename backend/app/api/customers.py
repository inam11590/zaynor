"""Customers API router — public create/get + admin list."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerRead
from app.services.auth import require_admin

router = APIRouter(prefix="/customers", tags=["Customers"])


# ---------------------------------------------------------------------------
# Admin-only endpoints (placed before /{id} to avoid route conflicts)
# ---------------------------------------------------------------------------
@router.get("/", response_model=List[CustomerRead])
def list_customers(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """List all customers. Admin only."""
    return db.query(Customer).order_by(Customer.id).all()


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------
@router.post("/", response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    """Register a new customer (or return existing if email matches)."""
    existing = db.query(Customer).filter(Customer.email == payload.email).first()
    if existing:
        return existing

    customer = Customer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a customer by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
