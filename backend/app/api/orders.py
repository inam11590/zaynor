"""Orders API router — create, list, retrieve, track, and admin status update."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderRead, OrderItemRead, OrderTrackingRead
from app.services.auth import require_admin

router = APIRouter(prefix="/orders", tags=["Orders"])
limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)


def _build_order_item_read(item: OrderItem) -> OrderItemRead:
    """Build an OrderItemRead with the product name resolved."""
    return OrderItemRead(
        id=item.id,
        product_id=item.product_id,
        product_name=item.product.name if item.product else "",
        quantity=item.quantity,
        unit_price=item.unit_price,
    )


@router.post("/", response_model=OrderRead, status_code=201)
@limiter.limit(settings.RATE_LIMIT_ORDERS)
def create_order(request: Request, payload: OrderCreate, db: Session = Depends(get_db)):
    """Place a new order.

    Validates that the customer and all products exist, calculates the
    total from current product prices, and stores the order with items.
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Validate products and calculate total
    total = 0.0
    order_items: List[OrderItem] = []
    for item_in in payload.items:
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with id {item_in.product_id} not found",
            )
        if item_in.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")

        total += product.price * item_in.quantity
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item_in.quantity,
                unit_price=product.price,
            )
        )

    order = Order(
        customer_id=payload.customer_id,
        status="pending",
        total=round(total, 2),
        notes=payload.notes,
    )
    db.add(order)
    db.flush()  # get order.id before adding items

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    db.commit()
    db.refresh(order)

    # Re-fetch with relationships loaded
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order.id)
        .first()
    )

    # Send emails (best-effort — never block the response)
    try:
        from app.services.email import send_order_confirmation, send_admin_new_order

        email_items = [
            {"product_name": oi.product.name, "quantity": oi.quantity, "unit_price": oi.unit_price}
            for oi in order.items
        ]
        send_order_confirmation(
            customer_name=customer.name,
            customer_email=customer.email,
            order_id=order.id,
            items=email_items,
            total=order.total,
            notes=order.notes,
        )
        send_admin_new_order(
            customer_name=customer.name,
            customer_email=customer.email,
            order_id=order.id,
            items=email_items,
            total=order.total,
            notes=order.notes,
        )
    except Exception:
        pass  # never fail an order because email sending failed

    return order


@router.get("/", response_model=List[OrderRead])
def list_orders(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all orders, with optional filters."""
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    )

    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)
    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).all()


@router.get("/track", response_model=OrderTrackingRead)
def track_order(
    order_id: int = Query(..., description="Order ID"),
    email: str = Query(..., description="Customer email"),
    db: Session = Depends(get_db),
):
    """Track an order by ID and customer email.

    Public endpoint — no auth required. Validates that the email matches
    the customer who placed the order.
    """
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="No customer found with that email")

    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id, Order.customer_id == customer.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found for this email")

    items = [
        OrderItemRead(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else "",
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in order.items
    ]

    return OrderTrackingRead(
        id=order.id,
        status=order.status,
        total=order.total,
        items=items,
        created_at=order.created_at,
        customer_name=customer.name,
    )


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order by ID."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ---------------------------------------------------------------------------
# Admin-only endpoints (Phase 5)
# ---------------------------------------------------------------------------
VALID_ORDER_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"]


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    new_status: str = Query(..., description=f"New status: {VALID_ORDER_STATUSES}"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Update an order's status. Admin only."""
    if new_status not in VALID_ORDER_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_ORDER_STATUSES)}",
        )

    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
