"""convert price_currency to enum in products and offers

Revision ID: 0010
Revises: 0009
Create Date: 2026-03-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None

currency_enum = sa.Enum('USD', 'EUR', 'RUB', 'KZT', 'KGZ', name='currency')


def upgrade() -> None:
    currency_enum.create(op.get_bind(), checkfirst=True)

    op.execute("ALTER TABLE products ALTER COLUMN price_currency DROP DEFAULT")
    op.execute("ALTER TABLE products ALTER COLUMN price_currency TYPE currency USING price_currency::currency")

    op.execute("ALTER TABLE offers ALTER COLUMN price_currency DROP DEFAULT")
    op.execute("ALTER TABLE offers ALTER COLUMN price_currency TYPE currency USING price_currency::currency")


def downgrade() -> None:
    op.execute("ALTER TABLE products ALTER COLUMN price_currency TYPE VARCHAR(10) USING price_currency::text")
    op.execute("ALTER TABLE offers ALTER COLUMN price_currency TYPE VARCHAR(10) USING price_currency::text")

    currency_enum.drop(op.get_bind())
