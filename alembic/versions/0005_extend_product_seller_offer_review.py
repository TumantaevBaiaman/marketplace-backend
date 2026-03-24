"""extend product seller offer review fields

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── products ──────────────────────────────────────────────────────────────
    op.add_column("products", sa.Column("description", sa.Text, nullable=True))
    op.add_column("products", sa.Column("category", sa.String(200), nullable=True))
    op.add_column("products", sa.Column("sku", sa.String(100), nullable=True))
    op.add_column("products", sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"))
    op.add_column("products", sa.Column("views_count", sa.Integer, nullable=False, server_default="0"))
    op.create_index("ix_products_category", "products", ["category"])
    op.create_unique_constraint("uq_products_sku", "products", ["sku"])

    # ── sellers ───────────────────────────────────────────────────────────────
    op.add_column("sellers", sa.Column("description", sa.Text, nullable=True))
    op.add_column("sellers", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("sellers", sa.Column("phone", sa.String(50), nullable=True))
    op.add_column("sellers", sa.Column("website", sa.String(500), nullable=True))
    op.add_column("sellers", sa.Column("country", sa.String(100), nullable=True))
    op.add_column("sellers", sa.Column("logo_url", sa.String(500), nullable=True))
    op.add_column("sellers", sa.Column("review_count", sa.Integer, nullable=False, server_default="0"))
    op.add_column("sellers", sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"))

    # ── offers ────────────────────────────────────────────────────────────────
    offer_condition = sa.Enum("new", "used", "refurbished", name="offercondition")
    offer_condition.create(op.get_bind())
    op.add_column("offers", sa.Column(
        "condition",
        sa.Enum("new", "used", "refurbished", name="offercondition"),
        nullable=False,
        server_default="new",
    ))
    op.add_column("offers", sa.Column("quantity", sa.Integer, nullable=False, server_default="1"))
    op.add_column("offers", sa.Column("is_available", sa.Boolean, nullable=False, server_default="true"))
    op.add_column("offers", sa.Column("delivery_days_min", sa.Integer, nullable=True))
    op.add_column("offers", sa.Column("delivery_days_max", sa.Integer, nullable=True))

    # ── reviews ───────────────────────────────────────────────────────────────
    op.add_column("reviews", sa.Column("is_verified_purchase", sa.Boolean, nullable=False, server_default="false"))
    op.add_column("reviews", sa.Column("helpful_count", sa.Integer, nullable=False, server_default="0"))


def downgrade() -> None:
    # reviews
    op.drop_column("reviews", "helpful_count")
    op.drop_column("reviews", "is_verified_purchase")

    # offers
    op.drop_column("offers", "delivery_days_max")
    op.drop_column("offers", "delivery_days_min")
    op.drop_column("offers", "is_available")
    op.drop_column("offers", "quantity")
    op.drop_column("offers", "condition")
    sa.Enum(name="offercondition").drop(op.get_bind())

    # sellers
    op.drop_column("sellers", "is_verified")
    op.drop_column("sellers", "review_count")
    op.drop_column("sellers", "logo_url")
    op.drop_column("sellers", "country")
    op.drop_column("sellers", "website")
    op.drop_column("sellers", "phone")
    op.drop_column("sellers", "email")
    op.drop_column("sellers", "description")

    # products
    op.drop_constraint("uq_products_sku", "products", type_="unique")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_column("products", "views_count")
    op.drop_column("products", "is_active")
    op.drop_column("products", "sku")
    op.drop_column("products", "category")
    op.drop_column("products", "description")
