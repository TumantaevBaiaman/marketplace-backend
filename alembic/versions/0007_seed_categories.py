"""seed initial categories

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-23
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

FIXTURES_PATH = Path(__file__).parent.parent.parent / "fixtures" / "categories.json"

categories_table = table(
    "categories",
    column("id", sa.UUID),
    column("name", sa.String),
    column("slug", sa.String),
    column("description", sa.Text),
    column("icon_url", sa.String),
    column("parent_id", sa.UUID),
    column("created_at", sa.DateTime),
    column("updated_at", sa.DateTime),
)


def _load_rows() -> list[dict]:
    now = datetime.utcnow()
    data = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    rows = []
    for parent in data:
        rows.append({
            "id": uuid.UUID(parent["id"]),
            "name": parent["name"],
            "slug": parent["slug"],
            "description": parent.get("description"),
            "icon_url": parent.get("icon_url"),
            "parent_id": None,
            "created_at": now,
            "updated_at": now,
        })
        for child in parent.get("children", []):
            rows.append({
                "id": uuid.UUID(child["id"]),
                "name": child["name"],
                "slug": child["slug"],
                "description": child.get("description"),
                "icon_url": child.get("icon_url"),
                "parent_id": uuid.UUID(parent["id"]),
                "created_at": now,
                "updated_at": now,
            })
    return rows


def upgrade() -> None:
    op.bulk_insert(categories_table, _load_rows())


def downgrade() -> None:
    data = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    slugs = []
    for parent in data:
        slugs.append(parent["slug"])
        for child in parent.get("children", []):
            slugs.append(child["slug"])
    slugs_sql = ", ".join(f"'{s}'" for s in slugs)
    op.execute(f"DELETE FROM categories WHERE slug IN ({slugs_sql})")
