"""create products, sellers, offers

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("price_currency", sa.String(10), nullable=False, server_default="RUB"),
        sa.Column("stock", sa.Integer, nullable=False, server_default="0"),
        sa.Column("image_object_key", sa.String(500), nullable=True),
        sa.Column("thumbnail_object_key", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "product_attributes",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(200), nullable=False),
        sa.Column("value", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_product_attributes_product_id", "product_attributes", ["product_id"])

    op.create_table(
        "sellers",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("rating", sa.Numeric(3, 2), nullable=False, server_default="5.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "offers",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seller_id", sa.UUID(), sa.ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("price_currency", sa.String(10), nullable=False, server_default="RUB"),
        sa.Column("delivery_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_offers_product_id", "offers", ["product_id"])
    op.create_index("ix_offers_seller_id", "offers", ["seller_id"])


def downgrade() -> None:
    op.drop_table("offers")
    op.drop_table("sellers")
    op.drop_index("ix_product_attributes_product_id", table_name="product_attributes")
    op.drop_table("product_attributes")
    op.drop_table("products")
