from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


@dataclass
class CursorPage:
    items: list
    next_cursor: Any | None  # raw value from cursor field (e.g. uuid.UUID, datetime)


async def cursor_paginate(
    session: AsyncSession,
    query: Select,
    limit: int,
    cursor_value: Any | None,
    cursor_field: InstrumentedAttribute,
) -> CursorPage:
    """
    Cursor-based pagination using limit+1 trick.

    Args:
        session:      AsyncSession
        query:        SELECT query with ordering already applied
        limit:        page size
        cursor_value: raw cursor value (e.g. uuid.UUID) or None for first page
        cursor_field: model column used as cursor (e.g. ProductModel.id)

    Returns:
        CursorPage with items and next_cursor (raw field value, or None if last page)

    Usage:
        q = select(ProductModel).order_by(ProductModel.id.asc())
        page = await cursor_paginate(session, q, limit=20, cursor_value=cursor_uuid, cursor_field=ProductModel.id)
        # page.items        → list of ORM models
        # page.next_cursor  → uuid.UUID | None
    """
    if cursor_value is not None:
        query = query.where(cursor_field > cursor_value)

    query = query.limit(limit + 1)
    result = await session.execute(query)
    rows = result.scalars().all()

    has_next = len(rows) > limit
    items = rows[:limit]
    next_cursor = getattr(items[-1], cursor_field.key) if has_next and items else None

    return CursorPage(items=list(items), next_cursor=next_cursor)
