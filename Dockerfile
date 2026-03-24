# ============================================================
# Stage 1: builder — устанавливаем зависимости
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.1

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# ============================================================
# Stage 2: runtime — финальный образ без poetry и build tools
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY src ./src
COPY main.py ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY fixtures ./fixtures
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
