#!/bin/sh
set -e

echo "Checking migration state..."

ACTION=$(python3 - <<'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.config import get_settings

async def check():
    engine = create_async_engine(get_settings().db.url, echo=False)
    try:
        async with engine.connect() as conn:
            has_version = (await conn.execute(
                text("SELECT to_regclass('public.alembic_version')")
            )).scalar() is not None
            has_users = (await conn.execute(
                text("SELECT to_regclass('public.users')")
            )).scalar() is not None
            has_products = (await conn.execute(
                text("SELECT to_regclass('public.products')")
            )).scalar() is not None
    finally:
        await engine.dispose()

    if not has_version and has_users and not has_products:
        print("STAMP_0001")
    elif not has_version and has_users and has_products:
        print("STAMP_HEAD")
    else:
        print("UPGRADE")

asyncio.run(check())
EOF
)

if [ "$ACTION" = "STAMP_0001" ]; then
    echo "Partial schema found — stamping at 0001..."
    alembic stamp 0001
elif [ "$ACTION" = "STAMP_HEAD" ]; then
    echo "Full schema found — stamping at head..."
    alembic stamp head
fi

echo "Running migrations..."
alembic upgrade head
echo "Migrations complete."

echo "Starting server..."
exec "$@"
