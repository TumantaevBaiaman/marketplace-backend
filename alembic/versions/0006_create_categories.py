"""create categories table and link products

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("parent_id", sa.UUID(),
                  sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_index("ix_categories_parent_id", "categories", ["parent_id"])

    # Заменяем строку category на FK
    op.drop_index("ix_products_category", table_name="products")
    op.drop_column("products", "category")
    op.add_column("products", sa.Column(
        "category_id", sa.UUID(),
        sa.ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    ))
    op.create_index("ix_products_category_id", "products", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_column("products", "category_id")
    op.add_column("products", sa.Column("category", sa.String(200), nullable=True))
    op.create_index("ix_products_category", "products", ["category"])

    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
