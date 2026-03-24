# Архитектура

## Обзор

Проект построен на **Clean Architecture + DDD + CQRS**. Каждый слой имеет чёткую зону ответственности и зависит только от слоёв ниже.

```
┌────────────────────────────────────────────┐
│              interfaces/                   │  FastAPI, HTTP, Depends
├────────────────────────────────────────────┤
│             application/                   │  CQRS, Services, DTO
├────────────────────────────────────────────┤
│               domain/                      │  Entities, Rules, Interfaces
├────────────────────────────────────────────┤
│            infrastructure/                 │  SQLAlchemy, Redis, MinIO, JWT
└────────────────────────────────────────────┘
```

**Правило импортов:** стрелки идут только вниз. `domain` не импортирует ничего из других слоёв. `application` не знает о SQLAlchemy или FastAPI.

---

## Слои

### domain/

Ядро системы. Не зависит ни от каких фреймворков.

**entities/** — агрегаты и сущности:

| Класс | Описание |
|---|---|
| `BaseEntity` | Базовый класс с `id: UUID`, `__eq__` по id, `__hash__` |
| `User` | Пользователь: email, роль, статус, методы `activate()`, `ban()`, `deactivate()` |
| `UserIdentity` | Хранит провайдер аутентификации и хэш пароля |
| `Product` | Товар: название, цена, склад, изображение, категория |
| `ProductAttribute` | Атрибут товара (key–value) |
| `Review` | Отзыв: оценка, текст, привязка к пользователю и товару |
| `Offer` | Оффер продавца: цена, дата доставки, условие |
| `Seller` | Продавец: имя, рейтинг |
| `Category` | Категория товаров |
| `ProductAuditLog` | Лог изменений товара |

**value_objects/** — иммутабельные объекты-значения:
- `Email` — валидированный email

**repositories/** — абстрактные интерфейсы (ABC):
- `UserRepository`, `UserIdentityRepository`
- `ProductRepository`, `ProductAttributeRepository`
- `ReviewRepository`, `OfferRepository`
- `SellerRepository`, `CategoryRepository`
- `ProductAuditLogRepository`

**services/** — domain-интерфейсы для внешних зависимостей:
- `IPasswordService` — `hash_password()`, `verify_password()`
- `ITokenService` — `create_access_token()`, `blacklist_token()`
- `IImageService` — `upload_product_image()`, `get_object_url()`

**exceptions/** — доменные исключения:
- `EntityNotFound`, `BusinessRuleViolation`, `AlreadyExists`, `PermissionDenied`

---

### application/

Оркестрирует домен. Не знает о конкретных реализациях — работает с интерфейсами.

#### CQRS

Разделение операций на команды (запись) и запросы (чтение):

```
Command → CommandHandler → Repository.save() → DTO | None
Query   → QueryHandler   → Repository.get()  → DTO
```

**commands/** — описывают намерение изменить состояние:
```python
@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str
```

**queries/** — описывают что прочитать:
```python
@dataclass(frozen=True)
class ListPublicProductsQuery:
    limit: int
    cursor: str | None
    in_stock: bool | None
    sort: str
```

**handlers/** — обрабатывают команды и запросы, зависят только от абстракций:
```python
class LoginHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        identity_repo: UserIdentityRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ): ...
```

**services/** — фасады для эндпоинтов. Принимают команду/запрос, делегируют обработчику:
```python
class AuthService:
    async def login(self, cmd: LoginCommand) -> str:
        return await self._login_handler.handle(cmd)
```

**dto/** — Data Transfer Objects. Отделяют API-контракт от доменных сущностей. Обработчики никогда не возвращают entity напрямую.

---

### infrastructure/

Конкретные реализации всего, что работает с внешними системами.

**database/**
- `models/` — SQLAlchemy ORM-модели (декларативный стиль, async)
- `repositories/` — реализации `*RepositoryImpl` через `AsyncSession`
- `pagination.py` — cursor-based пагинация

Пагинация по cursor вместо offset:
```python
# Offset ломается при вставке новых записей
# Cursor стабилен: WHERE id > cursor ORDER BY id LIMIT n
products, next_cursor = await repo.get_list(limit=20, cursor=uuid)
```

**security/**
- `PasswordServiceImpl` — bcrypt через passlib
- `TokenServiceImpl` — JWT через PyJWT + Redis blacklist

**storage/**
- `ImageServiceImpl` — загрузка и получение URL изображений через MinIO

**cache/**
- `token_blacklist.py` — инвалидация токенов через Redis TTL

**logging/**
- JSON-логирование через `python-json-logger`

---

### interfaces/

Точка входа HTTP. Обращается только к `application/services/`.

**api/v1/endpoints/** — FastAPI-роутеры. Каждый эндпоинт:
1. Получает данные запроса через Pydantic-схему
2. Получает сервис через `Depends`
3. Вызывает один метод сервиса
4. Возвращает DTO

```python
@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    token = await service.login(LoginCommand(email=body.email, password=body.password))
    return TokenResponse(access_token=token)
```

**api/v1/dependencies.py** — провайдеры зависимостей. Собирает граф зависимостей: репозитории + сервисы + обработчики:
```python
async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repo = UserRepositoryImpl(session)
    identity_repo = UserIdentityRepositoryImpl(session)
    password_service = PasswordServiceImpl()
    token_service = TokenServiceImpl(redis, settings)
    login_handler = LoginHandler(user_repo, identity_repo, password_service, token_service)
    return AuthService(login_handler, ...)
```

**api/errors/** — перехват доменных исключений и маппинг в HTTP-ответы:
```
EntityNotFound      → 404 Not Found
BusinessRuleViolation → 422 Unprocessable Entity
AlreadyExists       → 409 Conflict
PermissionDenied    → 403 Forbidden
```

---

## Аутентификация

1. Клиент отправляет `POST /api/v1/auth/login` с `{email, password}`
2. `LoginHandler` проверяет пароль через `IPasswordService`
3. `ITokenService` создаёт JWT с payload `{sub, jti, exp, role}`
4. Токен возвращается клиенту
5. При каждом запросе `get_current_user` (Depends) декодирует токен и проверяет blacklist в Redis
6. `POST /auth/logout` добавляет `jti` токена в Redis с TTL = оставшееся время жизни токена

---

## Конфигурация

Конфигурация загружается из `.env` через `pydantic-settings`. Вложенные настройки через разделитель `__`:

```
DB__HOST=localhost
JWT__SECRET_KEY=your-secret
MINIO__ENDPOINT=localhost:9000
```

Класс `AppSettings` агрегирует все вложенные конфиги:
```python
class AppSettings(BaseSettings):
    db: DatabaseSettings
    redis: RedisSettings
    jwt: JWTSettings
    minio: MinioSettings
    logging: LoggingSettings
```

`get_settings()` кэшируется через `@lru_cache` — один инстанс на весь процесс.

---

## Тестируемость

Правильная архитектура делает тесты простыми. Обработчики получают всё через конструктор → в тестах передаём моки:

```python
async def test_login_success():
    user_repo = AsyncMock(spec=UserRepository)
    identity_repo = AsyncMock(spec=UserIdentityRepository)
    password_service = MagicMock(spec=IPasswordService)
    token_service = AsyncMock(spec=ITokenService)

    user_repo.get_by_email.return_value = make_user()
    password_service.verify_password.return_value = True
    token_service.create_access_token.return_value = "test.jwt.token"

    handler = LoginHandler(user_repo, identity_repo, password_service, token_service)
    result = await handler.handle(LoginCommand(email="user@test.com", password="pass"))

    assert result == "test.jwt.token"
```

64 теста, 0 внешних зависимостей, ~0.5 сек.

---

## Инварианты

Архитектурные правила, которые не должны нарушаться:

```python
# application не импортирует infrastructure
for file in Path("src/application").rglob("*.py"):
    assert "from src.infrastructure" not in file.read_text()

# endpoints не используют session.execute напрямую
for file in Path("src/interfaces").rglob("*.py"):
    assert "session.execute" not in file.read_text()

# query handlers возвращают DTO, не entity
# command handlers возвращают DTO | None, не entity
```
