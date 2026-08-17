"""add coupons table

Revision ID: 75ef7c539dd0
Revises: daf580808238
Create Date: 2026-08-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '75ef7c539dd0'
down_revision: Union[str, Sequence[str], None] = 'daf580808238'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), unique=True, nullable=False),
        sa.Column('discount_percent', sa.Float(), nullable=False),
        sa.Column('min_order_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('times_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_coupons_id', 'coupons', ['id'])
    op.create_index('ix_coupons_code', 'coupons', ['code'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_coupons_code', table_name='coupons')
    op.drop_index('ix_coupons_id', table_name='coupons')
    op.drop_table('coupons')
