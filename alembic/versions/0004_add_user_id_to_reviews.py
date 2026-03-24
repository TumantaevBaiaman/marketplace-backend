"""add user_id to reviews

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Старые строки без user_id — удаляем, они всё равно тестовые
    op.execute("TRUNCATE reviews RESTART IDENTITY CASCADE")

    op.add_column(
        "reviews",
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"),
                  nullable=False),
    )
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])
    op.create_unique_constraint(
        "uq_review_user_product", "reviews", ["user_id", "product_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_review_user_product", "reviews", type_="unique")
    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_column("reviews", "user_id")
