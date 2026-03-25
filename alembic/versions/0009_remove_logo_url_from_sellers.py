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
    pass  # logo_url was removed before this migration was created


def downgrade() -> None:
    pass
