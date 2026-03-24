"""remove brand and weight from products

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-23
"""
from alembic import op

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('products', 'brand')
    op.drop_column('products', 'weight')


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column('products', sa.Column('brand', sa.String(200), nullable=True))
    op.add_column('products', sa.Column('weight', sa.Numeric(10, 3), nullable=True))
