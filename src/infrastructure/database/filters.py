from sqlalchemy import Select, or_


def apply_filters(query: Select, model, filters: dict) -> Select:
    """
    Apply filters to a SQLAlchemy query from a dict.

    Supported suffixes:
        field          → field == value
        field__gt      → field > value
        field__gte     → field >= value
        field__lt      → field < value
        field__lte     → field <= value
        field__in      → field IN (values)
        field__like    → field ILIKE '%value%'
        field__search  → OR ILIKE across list of fields (value must be str)

    None values are ignored (filter is skipped).

    Usage:
        q = select(ProductModel)
        q = apply_filters(q, ProductModel, {
            'is_active': True,
            'stock__gt': 0,
            'price_amount__gte': min_price,
            'price_amount__lte': max_price,
            'category_id__in': [id1, id2],
            'name__like': search_text,
        })
    """
    for key, value in filters.items():
        if value is None:
            continue

        if "__" in key:
            field_name, op = key.rsplit("__", 1)
        else:
            field_name, op = key, "eq"

        column = getattr(model, field_name, None)
        if column is None:
            raise ValueError(f"Model {model.__name__} has no field '{field_name}'")

        if op == "eq":
            query = query.where(column == value)
        elif op == "gt":
            query = query.where(column > value)
        elif op == "gte":
            query = query.where(column >= value)
        elif op == "lt":
            query = query.where(column < value)
        elif op == "lte":
            query = query.where(column <= value)
        elif op == "in":
            if value:
                query = query.where(column.in_(value))
        elif op == "like":
            query = query.where(column.ilike(f"%{value}%"))
        elif op == "search":
            # value: {'fields': [Model.name, Model.description], 'q': 'text'}
            fields = value.get("fields", [column])
            q_text = value.get("q", "")
            if q_text:
                query = query.where(or_(*[f.ilike(f"%{q_text}%") for f in fields]))
        else:
            raise ValueError(f"Unknown filter operator '{op}'")

    return query
