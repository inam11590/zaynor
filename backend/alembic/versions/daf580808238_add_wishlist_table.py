"""add wishlist table

Revision ID: daf580808238
Revises: e8b93123fec8
Create Date: 2026-08-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'daf580808238'
down_revision: Union[str, Sequence[str], None] = 'e8b93123fec8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'wishlist',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_key', sa.String(length=64), nullable=False),
        sa.Column('product_slug', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('session_key', 'product_slug', name='uq_wishlist_session_product'),
    )
    op.create_index('ix_wishlist_id', 'wishlist', ['id'])
    op.create_index('ix_wishlist_session_key', 'wishlist', ['session_key'])


def downgrade() -> None:
    op.drop_index('ix_wishlist_session_key', table_name='wishlist')
    op.drop_index('ix_wishlist_id', table_name='wishlist')
    op.drop_table('wishlist')
