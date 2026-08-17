"""Wishlist model — stores products saved by anonymous sessions."""

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func

from app.database import Base


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True)
    session_key = Column(String(64), nullable=False, index=True)
    product_slug = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("session_key", "product_slug", name="uq_wishlist_session_product"),
    )
