# Marketplace Backend

REST API для маркетплейса на FastAPI. Построен на Clean Architecture + DDD + CQRS.

---

## Стек

| Категория | Технология |
|---|---|
| **Фреймворк** | FastAPI 0.135 |
| **Python** | 3.12 |
| **БД** | PostgreSQL 16 + SQLAlchemy 2.0 async + asyncpg |
| **Миграции** | Alembic |
| **Кэш / blacklist** | Redis 7 |
| **Хранилище файлов** | MinIO (S3-compatible) |
| **Аутентификация** | JWT (PyJWT + HS256) + bcrypt (passlib) |
| **Валидация / конфиг** | Pydantic v2 + pydantic-settings |
| **Мониторинг** | Prometheus (prometheus-fastapi-instrumentator) |
| **Зависимости** | Poetry |
| **Контейнеризация** | Docker (multi-stage build) |
| **CI** | GitHub Actions |

---

## Архитектура

Проект построен на **Clean Architecture** с разделением на четыре слоя. Каждый слой импортирует только вниз по иерархии.

```
src/
├── domain/          ← бизнес-сущности, правила, интерфейсы репозиториев и сервисов
├── application/     ← команды, запросы, обработчики (CQRS), DTO, сервисы приложения
├── infrastructure/  ← SQLAlchemy, Redis, MinIO, JWT, bcrypt — конкретные реализации
└── interfaces/      ← FastAPI endpoints, Depends-зависимости, обработчики ошибок
```

### Правила слоёв

- `domain` — не знает о FastAPI, SQLAlchemy, Redis или любом внешнем фреймворке
- `application` — зависит только от `domain`; работает с интерфейсами, не с реализациями
- `infrastructure` — реализует интерфейсы из `domain`, импортирует `domain` и `application`
- `interfaces` — вызывает только `application`-сервисы; прямой SQL в эндпоинтах запрещён

### CQRS

Команды изменяют состояние и возвращают DTO (или ничего). Запросы только читают и возвращают DTO.

```
Command → CommandHandler → Repository (write) → DTO
Query   → QueryHandler   → Repository (read)  → DTO
```

### Domain interfaces

Внешние зависимости скрыты за интерфейсами в `domain/services/`:

| Интерфейс | Реализация |
|---|---|
| `IPasswordService` | `PasswordServiceImpl` (bcrypt) |
| `ITokenService` | `TokenServiceImpl` (JWT + Redis blacklist) |
| `IImageService` | `ImageServiceImpl` (MinIO) |

Application-слой зависит от интерфейсов — замена bcrypt на argon2 или MinIO на S3 не затрагивает бизнес-логику.

---

## Быстрый старт

### Установка зависимостей

```bash
poetry install
```

### Переменные окружения

Скопируй `.env.example` в `.env` и заполни:

```bash
cp .env.example .env
```

Обязательные переменные:

| Переменная | Описание |
|---|---|
| `DB__HOST` | Хост PostgreSQL |
| `DB__PORT` | Порт PostgreSQL (default: 5432) |
| `DB__NAME` | Имя базы данных |
| `DB__USER` | Пользователь БД |
| `DB__PASSWORD` | Пароль БД |
| `REDIS__HOST` | Хост Redis |
| `REDIS__PORT` | Порт Redis (default: 6379) |
| `MINIO__ENDPOINT` | Адрес MinIO (`host:port`) |
| `MINIO__ACCESS_KEY` | MinIO access key |
| `MINIO__SECRET_KEY` | MinIO secret key |
| `JWT__SECRET_KEY` | Секрет для подписи токенов (`openssl rand -hex 32`) |

Опциональные:

| Переменная | Default | Описание |
|---|---|---|
| `APP_ENV` | `development` | Окружение (`development` / `production`) |
| `DEBUG` | `false` | Режим отладки |
| `JWT__ALGORITHM` | `HS256` | Алгоритм JWT |
| `JWT__ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | TTL access-токена |
| `DB__POOL_SIZE` | `10` | Размер пула соединений |
| `DB__ECHO` | `false` | Логирование SQL-запросов |

### Миграции

```bash
make migrate
```

### Запуск

```bash
make dev     # с --reload
make run     # production
```

Сервер поднимается на `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`

---

## Docker

Многоэтапная сборка: `builder` устанавливает зависимости через Poetry, `runtime` — минимальный образ без лишних инструментов.

```bash
docker build --target runtime -t marketplace-backend .
```

При старте контейнера `entrypoint.sh` применяет миграции, затем запускает uvicorn.

---

## Структура проекта

```
marketplace-backend/
├── src/
│   ├── domain/
│   │   ├── entities/        ← User, UserIdentity, Product, Review, Offer, Seller, Category
│   │   ├── value_objects/   ← Email
│   │   ├── enums/           ← UserRole, UserStatus, AuthProvider, Currency, OfferCondition
│   │   ├── repositories/    ← абстрактные репозитории (ABC)
│   │   ├── services/        ← IPasswordService, ITokenService, IImageService
│   │   └── exceptions/      ← доменные исключения (EntityNotFound, BusinessRuleViolation, ...)
│   │
│   ├── application/
│   │   ├── commands/        ← команды (LoginCommand, RegisterCommand, CreateProductCommand, ...)
│   │   ├── queries/         ← запросы (ListPublicProductsQuery, GetCurrentUserQuery, ...)
│   │   ├── handlers/
│   │   │   ├── command_handlers/   ← обработчики команд
│   │   │   └── query_handlers/     ← обработчики запросов
│   │   ├── services/        ← AuthService, UserService, ProductService, ReviewService, ...
│   │   └── dto/             ← DTO для всех агрегатов
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/      ← SQLAlchemy ORM-модели
│   │   │   ├── repositories/ ← реализации репозиториев
│   │   │   └── pagination.py ← cursor-based пагинация
│   │   ├── security/        ← PasswordServiceImpl, TokenServiceImpl
│   │   ├── storage/         ← ImageServiceImpl (MinIO)
│   │   ├── cache/           ← token blacklist (Redis)
│   │   └── logging/         ← JSON-логирование
│   │
│   ├── interfaces/
│   │   └── api/
│   │       ├── v1/
│   │       │   ├── endpoints/  ← FastAPI-роутеры
│   │       │   └── dependencies.py ← Depends-провайдеры
│   │       └── errors/         ← обработка доменных исключений
│   │
│   └── config/              ← AppSettings + DatabaseSettings, JWTSettings, RedisSettings, MinioSettings
│
├── tests/
│   └── unit/
│       ├── domain/          ← тесты сущностей
│       └── handlers/        ← тесты обработчиков команд и запросов
│
├── alembic/                 ← миграции БД
├── fixtures/                ← seed-данные
├── docs/
│   ├── architecture.md      ← детальное описание архитектуры
│   └── ai/                  ← AI workflow и промпты
├── .github/workflows/ci.yml ← GitHub Actions CI
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## API

Все эндпоинты доступны под префиксом `/api/v1`.

### Auth

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/login` | Вход по email + password, возвращает JWT |
| `POST` | `/auth/register` | Регистрация + автоматический вход |
| `GET` | `/auth/me` | Профиль текущего пользователя |
| `POST` | `/auth/logout` | Инвалидация токена (blacklist в Redis) |

### Публичные

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/products` | Список товаров с cursor-пагинацией |
| `GET` | `/products/{id}` | Детали товара (атрибуты, офферы, рейтинг) |
| `GET` | `/sellers` | Список продавцов |
| `GET` | `/sellers/{id}` | Профиль продавца |

### Пользователи

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/users/me` | Профиль |
| `PATCH` | `/users/me` | Обновление профиля |
| `GET` | `/users/me/reviews` | Отзывы пользователя |
| `POST` | `/products/{id}/reviews` | Добавить отзыв (один на товар) |

### Admin

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/admin/auth/login` | Вход для администраторов |
| `GET/POST/PATCH/DELETE` | `/admin/products` | Управление товарами |
| `POST` | `/admin/products/{id}/image` | Загрузка изображения товара |
| `GET/POST/PATCH/DELETE` | `/admin/categories` | Управление категориями |
| `GET/POST/PATCH/DELETE` | `/admin/sellers` | Управление продавцами |
| `GET/POST/PATCH/DELETE` | `/admin/offers` | Управление офферами |

### Служебные

| Путь | Описание |
|---|---|
| `GET /health` | Health check |
| `GET /metrics` | Prometheus метрики |

---

## Пагинация

Все списковые эндпоинты используют cursor-based пагинацию.

```json
{
  "items": [...],
  "next_cursor": "018e1a2b-..."
}
```

Offset-пагинация ломается при вставке новых записей. Cursor стабилен и не зависит от нагрузки.

---

## Тесты

```bash
make test        # запустить тесты
make test-cov    # с отчётом по покрытию
```

64 unit-теста, запускаются за ~0.5 сек без БД, Redis и MinIO — всё мокируется через интерфейсы.

```
tests/unit/domain/
  test_user_entity.py     — 13 тестов: is_active, is_admin, activate/ban, full_name
  test_product_entity.py  — 13 тестов: дефолты, поля, равенство

tests/unit/handlers/
  test_auth_handlers.py    — 20 тестов: Login, Register, AdminLogin, Logout
  test_product_handlers.py — 13 тестов: Create, Update, Delete, UploadImage
  test_review_handlers.py  —  5 тестов: CreateReview (бизнес-правило: один отзыв на товар)
```

---

## Качество кода

```bash
make lint          # ruff check
make lint-fix      # ruff check --fix
make format        # ruff format
make format-check  # ruff format --check
make check         # lint + format-check
```

---

## CI

GitHub Actions запускается на push/PR в `main` и `develop`.

**Job `check`** — Lint · Unit tests:
- ruff check + ruff format --check
- pytest с coverage (не требует внешних сервисов)
- Артефакт `coverage.xml`

**Job `build`** (после `check`) — Docker build:
- Multi-stage docker build
- Верификация запуска: `python -c "import main"`

---

## Makefile

```bash
make help           # список всех команд
make install        # poetry install
make dev            # запуск с --reload
make run            # production запуск
make migrate        # alembic upgrade head
make migrate-create name=<name>   # новая миграция
make migrate-down   # откат последней миграции
make seed           # загрузка seed-данных
make test           # unit тесты
make test-cov       # тесты + coverage
make lint           # ruff check
make format         # ruff format
make check          # lint + format-check
```
