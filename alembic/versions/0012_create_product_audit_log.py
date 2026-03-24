"""create product_audit_logs table

Revision ID: 0012
Revises: 0011
Create Date: 2026-03-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'product_audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'product_id', UUID(as_uuid=True),
            sa.ForeignKey('products.id', ondelete='CASCADE'),
            nullable=False,
            index=True,
        ),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column(
            'actor_id', UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
            index=True,
        ),
        sa.Column('actor_email', sa.String(255), nullable=True),
        sa.Column('diff', JSONB, nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index('ix_product_audit_logs_created_at', 'product_audit_logs', ['created_at'])


def downgrade() -> None:
    op.drop_table('product_audit_logs')
