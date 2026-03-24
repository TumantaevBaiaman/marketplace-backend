"""create users and user_identities

Revision ID: 0001
Revises: 
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "role",
            sa.Enum("admin", "moderator", "user", name="userrole"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "banned", "pending_verification", name="userstatus"),
            nullable=False,
            server_default="pending_verification",
        ),
        sa.Column("first_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("last_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_identities",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "provider",
            sa.Enum("email", "google", "apple", "phone", name="authprovider"),
            nullable=False,
        ),
        sa.Column("provider_id", sa.String(255), nullable=False),
        sa.Column("credential_hash", sa.String(255), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("provider", "provider_id", name="uq_identity_provider_provider_id"),
    )

    op.create_index("ix_user_identities_user_id", "user_identities", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_identities_user_id", table_name="user_identities")
    op.drop_table("user_identities")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS authprovider")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
