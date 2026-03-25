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
    pass  # columns brand/weight were removed before this migration was created


def downgrade() -> None:
    pass
