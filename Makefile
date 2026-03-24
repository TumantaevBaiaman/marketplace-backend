.PHONY: help install run dev check-services \
        migrate migrate-create migrate-down migrate-history \
        lint format check seed \
        test test-cov

# ── Config ────────────────────────────────────────────────────────────────────
include .env
export

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  App"
	@echo "    make install          — установить зависимости"
	@echo "    make run              — запустить сервер (production)"
	@echo "    make dev              — запустить сервер с --reload"
	@echo ""
	@echo "  Migrations"
	@echo "    make migrate                      — применить миграции"
	@echo "    make migrate-create name=<name>   — создать новую миграцию"
	@echo "    make migrate-down                 — откатить последнюю"
	@echo "    make migrate-history              — история миграций"
	@echo ""
	@echo "  Tests"
	@echo "    make test             — unit tests"
	@echo "    make test-cov         — unit tests + coverage report"
	@echo ""
	@echo "  Code quality"
	@echo "    make lint             — ruff check"
	@echo "    make lint-fix         — ruff check --fix"
	@echo "    make format           — ruff format"
	@echo "    make format-check     — ruff format --check"
	@echo "    make check            — lint + format-check"
	@echo ""

# ── Service health checks ─────────────────────────────────────────────────────
check-services:
	@echo "Проверка сервисов..."
	@nc -z $(DB__HOST) $(DB__PORT) 2>/dev/null \
		&& echo "  [OK] PostgreSQL $(DB__HOST):$(DB__PORT)" \
		|| (echo "  [ERROR] PostgreSQL недоступен на $(DB__HOST):$(DB__PORT)" && exit 1)
	@nc -z $(REDIS__HOST) $(REDIS__PORT) 2>/dev/null \
		&& echo "  [OK] Redis $(REDIS__HOST):$(REDIS__PORT)" \
		|| (echo "  [ERROR] Redis недоступен на $(REDIS__HOST):$(REDIS__PORT)" && exit 1)
	@nc -z $(shell echo $(MINIO__ENDPOINT) | cut -d: -f1) $(shell echo $(MINIO__ENDPOINT) | cut -d: -f2) 2>/dev/null \
		&& echo "  [OK] MinIO $(MINIO__ENDPOINT)" \
		|| (echo "  [ERROR] MinIO недоступен на $(MINIO__ENDPOINT)" && exit 1)
	@echo "Все сервисы доступны"

# ── App ───────────────────────────────────────────────────────────────────────
install:
	poetry install

run: check-services
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000

dev: check-services
	poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# ── Migrations ────────────────────────────────────────────────────────────────
migrate: check-services
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "$(name)"

migrate-down: check-services
	poetry run alembic downgrade -1

migrate-history:
	poetry run alembic history --verbose

seed: check-services
	poetry run python -m src.infrastructure.database.seed

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ -v --tb=short \
		--cov=src --cov-report=term-missing --cov-report=html

# ── Code quality ──────────────────────────────────────────────────────────────
lint:
	poetry run ruff check src

lint-fix:
	poetry run ruff check src --fix

format:
	poetry run ruff format src

format-check:
	poetry run ruff format src --check

check: lint format-check
