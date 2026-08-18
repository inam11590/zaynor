"""Analytics API router — dashboard stats, revenue, top products, recent orders."""

from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderRead, OrderItemRead
from app.services.auth import require_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_overview(db=Depends(get_db), admin=Depends(require_admin)):
    """High-level stats: total orders, revenue, customers, products, avg order value."""
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    total_revenue = db.query(func.coalesce(func.sum(Order.total), 0.0)).scalar()
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_products = db.query(func.count(Product.id)).scalar() or 0

    pending = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
    confirmed = db.query(func.count(Order.id)).filter(Order.status == "confirmed").scalar() or 0
    shipped = db.query(func.count(Order.id)).filter(Order.status == "shipped").scalar() or 0
    delivered = db.query(func.count(Order.id)).filter(Order.status == "delivered").scalar() or 0

    avg_order = round(total_revenue / total_orders, 2) if total_orders else 0

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "total_customers": total_customers,
        "total_products": total_products,
        "avg_order_value": avg_order,
        "orders_by_status": {
            "pending": pending,
            "confirmed": confirmed,
            "shipped": shipped,
            "delivered": delivered,
        },
    }


@router.get("/revenue")
def get_revenue(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db=Depends(get_db),
    admin=Depends(require_admin),
):
    """Revenue grouped by day for the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.total), 0.0).label("revenue"),
        )
        .filter(Order.created_at >= since)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    return [
        {"date": str(row.day), "order_count": row.order_count, "revenue": round(row.revenue, 2)}
        for row in rows
    ]


@router.get("/top-products")
def get_top_products(
    limit: int = Query(5, ge=1, le=20),
    db=Depends(get_db),
    admin=Depends(require_admin),
):
    """Top selling products by total quantity sold."""
    rows = (
        db.query(
            Product.id,
            Product.name,
            Product.slug,
            Product.price,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("total_sold"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0.0).label("total_revenue"),
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.id,
            "name": row.name,
            "slug": row.slug,
            "price": row.price,
            "total_sold": int(row.total_sold),
            "total_revenue": round(row.total_revenue, 2),
        }
        for row in rows
    ]


@router.get("/recent-orders")
def get_recent_orders(
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_db),
    admin=Depends(require_admin),
):
    """Most recent orders with customer name and items."""
    orders = (
        db.query(Order)
        .options(joinedload(Order.customer), joinedload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for o in orders:
        items = [
            OrderItemRead(
                id=oi.id,
                product_id=oi.product_id,
                product_name=oi.product.name if oi.product else "",
                quantity=oi.quantity,
                unit_price=oi.unit_price,
            )
            for oi in o.items
        ]
        result.append(
            OrderRead(
                id=o.id,
                customer_id=o.customer_id,
                status=o.status,
                total=o.total,
                notes=o.notes,
                items=items,
                created_at=o.created_at,
            )
        )
    return result
