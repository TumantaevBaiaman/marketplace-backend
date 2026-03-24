"""remove logo_url from sellers

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-23
"""
from alembic import op

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('sellers', 'logo_url')


def downgrade() -> None:
    import sqlalchemy as sa
    op.add_column('sellers', sa.Column('logo_url', sa.String(500), nullable=True))
