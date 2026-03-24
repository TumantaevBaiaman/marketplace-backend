# Marketplace Backend

REST API for a marketplace built with FastAPI. Designed on Clean Architecture + DDD + CQRS.

---

## Stack

| Category | Technology |
|---|---|
| **Framework** | FastAPI 0.135 |
| **Python** | 3.12 |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.0 async + asyncpg |
| **Migrations** | Alembic |
| **Cache / blacklist** | Redis 7 |
| **File storage** | MinIO (S3-compatible) |
| **Authentication** | JWT (PyJWT + HS256) + bcrypt (passlib) |
| **Validation / config** | Pydantic v2 + pydantic-settings |
| **Monitoring** | Prometheus (prometheus-fastapi-instrumentator) |
| **Dependencies** | Poetry |
| **Containerization** | Docker (multi-stage build) |
| **CI** | GitHub Actions |

---

## Architecture

Built on **Clean Architecture** with four layers. Each layer only imports downward in the hierarchy.

```
src/
├── domain/          ← business entities, rules, repository and service interfaces
├── application/     ← commands, queries, handlers (CQRS), DTOs, application services
├── infrastructure/  ← SQLAlchemy, Redis, MinIO, JWT, bcrypt — concrete implementations
└── interfaces/      ← FastAPI endpoints, Depends providers, error handlers
```

### Layer rules

- `domain` — no knowledge of FastAPI, SQLAlchemy, Redis, or any external framework
- `application` — depends only on `domain`; works with interfaces, not implementations
- `infrastructure` — implements `domain` interfaces; imports `domain` and `application`
- `interfaces` — calls `application` services only; direct SQL in endpoints is forbidden

### CQRS

Commands mutate state and return a DTO (or nothing). Queries only read and return a DTO.

```
Command → CommandHandler → Repository (write) → DTO
Query   → QueryHandler   → Repository (read)  → DTO
```

### Domain interfaces

External dependencies are hidden behind interfaces in `domain/services/`:

| Interface | Implementation |
|---|---|
| `IPasswordService` | `PasswordServiceImpl` (bcrypt) |
| `ITokenService` | `TokenServiceImpl` (JWT + Redis blacklist) |
| `IImageService` | `ImageServiceImpl` (MinIO) |

The application layer depends on interfaces — swapping bcrypt for argon2 or MinIO for S3 requires no changes to business logic.

---

## Quick start

### Install dependencies

```bash
poetry install
```

### Environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `DB__HOST` | PostgreSQL host |
| `DB__PORT` | PostgreSQL port (default: 5432) |
| `DB__NAME` | Database name |
| `DB__USER` | Database user |
| `DB__PASSWORD` | Database password |
| `REDIS__HOST` | Redis host |
| `REDIS__PORT` | Redis port (default: 6379) |
| `MINIO__ENDPOINT` | MinIO address (`host:port`) |
| `MINIO__ACCESS_KEY` | MinIO access key |
| `MINIO__SECRET_KEY` | MinIO secret key |
| `JWT__SECRET_KEY` | Token signing secret (`openssl rand -hex 32`) |

Optional variables:

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment (`development` / `production`) |
| `DEBUG` | `false` | Debug mode |
| `JWT__ALGORITHM` | `HS256` | JWT algorithm |
| `JWT__ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `DB__POOL_SIZE` | `10` | Connection pool size |
| `DB__ECHO` | `false` | SQL query logging |

### Migrations

```bash
make migrate
```

### Run

```bash
make dev     # with --reload
make run     # production
```

Server starts at `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`

---

## Docker

Multi-stage build: `builder` installs dependencies via Poetry, `runtime` is a minimal image without build tools.

```bash
docker build --target runtime -t marketplace-backend .
```

On container start, `entrypoint.sh` applies migrations and then starts uvicorn.

---

## Project structure

```
marketplace-backend/
├── src/
│   ├── domain/
│   │   ├── entities/        ← User, UserIdentity, Product, Review, Offer, Seller, Category
│   │   ├── value_objects/   ← Email
│   │   ├── enums/           ← UserRole, UserStatus, AuthProvider, Currency, OfferCondition
│   │   ├── repositories/    ← abstract repositories (ABC)
│   │   ├── services/        ← IPasswordService, ITokenService, IImageService
│   │   └── exceptions/      ← domain exceptions (EntityNotFound, BusinessRuleViolation, ...)
│   │
│   ├── application/
│   │   ├── commands/        ← commands (LoginCommand, RegisterCommand, CreateProductCommand, ...)
│   │   ├── queries/         ← queries (ListPublicProductsQuery, GetCurrentUserQuery, ...)
│   │   ├── handlers/
│   │   │   ├── command_handlers/   ← command handlers
│   │   │   └── query_handlers/     ← query handlers
│   │   ├── services/        ← AuthService, UserService, ProductService, ReviewService, ...
│   │   └── dto/             ← DTOs for all aggregates
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/      ← SQLAlchemy ORM models
│   │   │   ├── repositories/ ← repository implementations
│   │   │   └── pagination.py ← cursor-based pagination
│   │   ├── security/        ← PasswordServiceImpl, TokenServiceImpl
│   │   ├── storage/         ← ImageServiceImpl (MinIO)
│   │   ├── cache/           ← token blacklist (Redis)
│   │   └── logging/         ← JSON logging
│   │
│   ├── interfaces/
│   │   └── api/
│   │       ├── v1/
│   │       │   ├── endpoints/  ← FastAPI routers
│   │       │   └── dependencies.py ← Depends providers
│   │       └── errors/         ← domain exception handlers
│   │
│   └── config/              ← AppSettings + DatabaseSettings, JWTSettings, RedisSettings, MinioSettings
│
├── tests/
│   └── unit/
│       ├── domain/          ← entity tests
│       └── handlers/        ← command and query handler tests
│
├── alembic/                 ← database migrations
├── fixtures/                ← seed data
├── docs/
│   ├── architecture.md      ← detailed architecture description
│   └── ai/                  ← AI workflow and prompts
├── .github/workflows/ci.yml ← GitHub Actions CI
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## API

All endpoints are available under the `/api/v1` prefix.

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Login with email + password, returns JWT |
| `POST` | `/auth/register` | Registration + automatic login |
| `GET` | `/auth/me` | Current user profile |
| `POST` | `/auth/logout` | Token invalidation (Redis blacklist) |

### Public

| Method | Path | Description |
|---|---|---|
| `GET` | `/products` | Product list with cursor pagination |
| `GET` | `/products/{id}` | Product details (attributes, offers, rating) |
| `GET` | `/sellers` | Seller list |
| `GET` | `/sellers/{id}` | Seller profile |

### Users

| Method | Path | Description |
|---|---|---|
| `GET` | `/users/me` | Profile |
| `PATCH` | `/users/me` | Update profile |
| `GET` | `/users/me/reviews` | User reviews |
| `POST` | `/products/{id}/reviews` | Add a review (one per product) |

### Admin

| Method | Path | Description |
|---|---|---|
| `POST` | `/admin/auth/login` | Admin login |
| `GET/POST/PATCH/DELETE` | `/admin/products` | Product management |
| `POST` | `/admin/products/{id}/image` | Upload product image |
| `GET/POST/PATCH/DELETE` | `/admin/categories` | Category management |
| `GET/POST/PATCH/DELETE` | `/admin/sellers` | Seller management |
| `GET/POST/PATCH/DELETE` | `/admin/offers` | Offer management |

### Service

| Path | Description |
|---|---|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus metrics |

---

## Pagination

All list endpoints use cursor-based pagination.

```json
{
  "items": [...],
  "next_cursor": "018e1a2b-..."
}
```

Offset pagination breaks when new records are inserted mid-page. Cursor pagination is stable under any load.

---

## Tests

```bash
make test        # run tests
make test-cov    # with coverage report
```

64 unit tests, run in ~0.5s with no DB, Redis, or MinIO — everything is mocked through interfaces.

```
tests/unit/domain/
  test_user_entity.py     — 13 tests: is_active, is_admin, activate/ban, full_name
  test_product_entity.py  — 13 tests: defaults, fields, equality

tests/unit/handlers/
  test_auth_handlers.py    — 20 tests: Login, Register, AdminLogin, Logout
  test_product_handlers.py — 13 tests: Create, Update, Delete, UploadImage
  test_review_handlers.py  —  5 tests: CreateReview (one review per product business rule)
```

---

## Code quality

```bash
make lint          # ruff check
make lint-fix      # ruff check --fix
make format        # ruff format
make format-check  # ruff format --check
make check         # lint + format-check
```

---

## CI

GitHub Actions runs on push/PR to `main` and `develop`.

**Job `check`** — Lint · Unit tests:
- ruff check + ruff format --check
- pytest with coverage (no external services required)
- Artifact: `coverage.xml`

**Job `build`** (after `check`) — Docker build:
- Multi-stage docker build
- Startup verification: `python -c "import main"`

---

## Makefile

```bash
make help           # list all commands
make install        # poetry install
make dev            # run with --reload
make run            # production run
make migrate        # alembic upgrade head
make migrate-create name=<name>   # create new migration
make migrate-down   # roll back last migration
make seed           # load seed data
make test           # unit tests
make test-cov       # tests + coverage
make lint           # ruff check
make format         # ruff format
make check          # lint + format-check
```
