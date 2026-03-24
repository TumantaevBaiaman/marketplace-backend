# PROMPTS.md — Промпты разработки бэкенда

> Промпты которые я использовал при разработке.
> Организованы по этапам: проектирование → реализация → аудит → исправления → тесты.
> Каждый промпт на EN и RU.

---

## Проектирование архитектуры

### Начальный каркас Clean Architecture + DDD + CQRS

```
Scaffold a Python backend for a marketplace platform following
Clean Architecture + DDD + CQRS.

Tech stack: FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis, MinIO, Poetry.

Layer structure:
- domain/        — entities, value objects, repository interfaces, domain exceptions
- application/   — commands, queries, handlers, DTOs, services
- infrastructure/— SQLAlchemy models + repos, Redis, MinIO, JWT, bcrypt
- interfaces/    — FastAPI routers, endpoints, dependency injection

Domain entities: User, UserIdentity (auth providers), Product, ProductAttribute,
Offer, Seller, Review, Category, ProductAuditLog.

Rules that must be enforced:
1. Domain imports nothing from application/infrastructure/interfaces
2. Application imports only from domain (no infrastructure imports)
3. All repository interfaces are abstract classes in domain/repositories/
4. Infrastructure implements domain interfaces
5. Endpoints call only application services — no direct DB access
6. CQRS: command handlers return None or DTO, query handlers return DTOs only
7. All cross-layer calls go through public __init__.py exports

Generate the complete folder structure with all __init__.py files,
then implement the most critical files: base entity, domain exceptions,
User entity, UserRepository interface, Axios-equivalent (Axios instance for Python).
```

**RU:**
```
Создай каркас Python бэкенда для маркетплейса по паттернам
Clean Architecture + DDD + CQRS.

Стек: FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis, MinIO, Poetry.

Структура слоёв:
- domain/        — entities, value objects, интерфейсы репозиториев, domain exceptions
- application/   — commands, queries, handlers, DTO, services
- infrastructure/— SQLAlchemy модели + репозитории, Redis, MinIO, JWT, bcrypt
- interfaces/    — FastAPI роутеры, endpoints, dependency injection

Доменные сущности: User, UserIdentity (auth providers), Product, ProductAttribute,
Offer, Seller, Review, Category, ProductAuditLog.

Правила которые должны соблюдаться:
1. Domain не импортирует ничего из application/infrastructure/interfaces
2. Application импортирует только из domain (без импортов infrastructure)
3. Все интерфейсы репозиториев — абстрактные классы в domain/repositories/
4. Infrastructure реализует domain-интерфейсы
5. Endpoints вызывают только application services — без прямого доступа к БД
6. CQRS: command handlers возвращают None или DTO, query handlers только DTO
7. Все межслойные вызовы через публичные __init__.py

Сгенерируй полную структуру папок с __init__.py файлами,
затем реализуй критичные файлы: base entity, domain exceptions,
User entity, UserRepository интерфейс.
```

---

### Проектирование доменной модели User + UserIdentity

```
Design the User aggregate for a marketplace with multi-provider auth.

Requirements:
- User entity stores profile only: first_name, last_name, role, status, avatar_url
- User does NOT store email or password directly (that's UserIdentity's job)
- UserIdentity stores: user_id, provider (EMAIL/GOOGLE/PHONE), provider_id, credential_hash, is_verified
- One user can have multiple identities (email + google login)
- UserRole enum: ADMIN, MODERATOR, USER
- UserStatus enum: ACTIVE, INACTIVE, BANNED, PENDING_VERIFICATION
- User entity must have: is_active property, is_admin property, activate(), ban(), deactivate() methods
- BaseEntity has uuid id, __eq__ and __hash__ based on id only

Show complete implementation of: BaseEntity, User, UserIdentity, UserRole, UserStatus,
UserRepository (abstract), UserIdentityRepository (abstract).
```

**RU:**
```
Спроектируй User-агрегат для маркетплейса с мультипровайдерной аутентификацией.

Требования:
- User entity хранит только профиль: first_name, last_name, role, status, avatar_url
- User НЕ хранит email или пароль напрямую (это задача UserIdentity)
- UserIdentity хранит: user_id, provider (EMAIL/GOOGLE/PHONE), provider_id, credential_hash, is_verified
- Один пользователь может иметь несколько identity (email + google логин)
- UserRole enum: ADMIN, MODERATOR, USER
- UserStatus enum: ACTIVE, INACTIVE, BANNED, PENDING_VERIFICATION
- User entity должен иметь: свойства is_active, is_admin, методы activate(), ban(), deactivate()
- BaseEntity имеет uuid id, __eq__ и __hash__ только по id

Покажи полную реализацию: BaseEntity, User, UserIdentity, UserRole, UserStatus,
UserRepository (abstract), UserIdentityRepository (abstract).
```

---

### CQRS: Auth команды и хэндлеры

```
Implement CQRS auth handlers for a FastAPI + Clean Architecture backend.

Commands needed: LoginCommand, AdminLoginCommand, RegisterCommand, LogoutCommand
All are plain dataclasses with no logic.

Handler rules:
- LoginHandler: verify identity exists → verify password → check email verified →
  check user is_active → create JWT token
- AdminLoginHandler: same as Login + check role is ADMIN or MODERATOR
- RegisterHandler: check email not taken → create User → create UserIdentity with hashed password
- LogoutHandler: blacklist the JWT token in Redis

Critical constraint: handlers must NOT import from infrastructure directly.
Instead, accept IPasswordService and ITokenService interfaces via constructor injection.
These interfaces are defined in domain/services/.

IPasswordService: hash_password(plain) → str, verify_password(plain, hashed) → bool
ITokenService: create_access_token(data) → str, blacklist_token(jti, ttl) → None

Raise AccessDenied for auth failures, EntityAlreadyExists for duplicate email.
```

**RU:**
```
Реализуй CQRS auth-хэндлеры для FastAPI + Clean Architecture бэкенда.

Команды: LoginCommand, AdminLoginCommand, RegisterCommand, LogoutCommand
Все — простые dataclass'ы без логики.

Правила хэндлеров:
- LoginHandler: проверить identity → проверить пароль → проверить email verified →
  проверить is_active → создать JWT токен
- AdminLoginHandler: то же что Login + проверить роль ADMIN или MODERATOR
- RegisterHandler: проверить что email не занят → создать User → создать UserIdentity с хешем пароля
- LogoutHandler: добавить JWT токен в blacklist Redis

Критическое ограничение: хэндлеры НЕ должны импортировать infrastructure напрямую.
Принимать IPasswordService и ITokenService через constructor injection.
Интерфейсы определены в domain/services/.

IPasswordService: hash_password(plain) → str, verify_password(plain, hashed) → bool
ITokenService: create_access_token(data) → str, blacklist_token(jti, ttl) → None

Кидать AccessDenied при ошибках авторизации, EntityAlreadyExists при дубликате email.
```

---

### Cursor-based pagination для product listing

```
Implement cursor-based pagination for the product listing query handler.

Why cursor not offset: offset breaks when new records are inserted during browsing.
Cursor is stable — it references a specific record.

Query: ListPublicProductsQuery(cursor: str | None, limit: int, category_id, search)
Response: ProductListResponseDTO(items: list[ProductListItemDTO], next_cursor: str | None)

Cursor encoding: base64(product_id) — simple, opaque to clients.

ProductRepository must have:
  list_public(cursor, limit, category_id, search) → tuple[list[Product], str | None]

The handler must:
1. Call repo to get items + next_cursor
2. For each product: get offers sorted by delivery_date, get ratings
3. Map to ProductListItemDTO — never return raw domain entities
4. Return ProductListResponseDTO with next_cursor

Show: the query, the DTO, the handler, and the abstract repository method signature.
```

**RU:**
```
Реализуй курсорную пагинацию для хэндлера листинга товаров.

Почему cursor, а не offset: offset ломается при вставке новых записей во время просмотра.
Cursor стабилен — он ссылается на конкретную запись.

Query: ListPublicProductsQuery(cursor: str | None, limit: int, category_id, search)
Response: ProductListResponseDTO(items: list[ProductListItemDTO], next_cursor: str | None)

Кодирование курсора: base64(product_id) — простой, непрозрачный для клиентов.

ProductRepository должен иметь:
  list_public(cursor, limit, category_id, search) → tuple[list[Product], str | None]

Хэндлер должен:
1. Вызвать repo для получения items + next_cursor
2. Для каждого товара: получить офферы отсортированные по delivery_date, получить рейтинги
3. Смаппировать в ProductListItemDTO — никогда не возвращать сырые domain entities
4. Вернуть ProductListResponseDTO с next_cursor

Покажи: query, DTO, хэндлер и сигнатуру абстрактного метода репозитория.
```

---

## Аудит и исправления

### Полный архитектурный аудит

```
Perform a full Clean Architecture compliance audit of this Python backend.

Check every file in src/ and report violations of these rules:

1. Layer isolation:
   - domain/ must not import from application/, infrastructure/, or interfaces/
   - application/ must not import from infrastructure/ or interfaces/
   - Any direct infrastructure import in application handlers is a CRITICAL violation

2. Direct DB access in endpoints:
   - interfaces/api/ endpoints must not call session.execute(), session.get(), session.add()
   - All data access must go through application services and handlers

3. CQRS compliance:
   - Query handlers must return DTOs, not domain entities
   - Command handlers must return None, DTO, or primitive (not domain entities)

4. Repository contract:
   - Every method used by application handlers must be declared in the abstract repository in domain/

5. Dead code:
   - Any module defined but never imported anywhere

For each violation: file path, line number, violation type, and suggested fix.
Return as a prioritized list: CRITICAL → HIGH → MEDIUM → LOW.
```

**RU:**
```
Выполни полный аудит соответствия Clean Architecture для этого Python бэкенда.

Проверь каждый файл в src/ и сообщи о нарушениях этих правил:

1. Изоляция слоёв:
   - domain/ не должен импортировать из application/, infrastructure/, interfaces/
   - application/ не должен импортировать из infrastructure/ или interfaces/
   - Любой прямой import infrastructure в application handlers — КРИТИЧЕСКОЕ нарушение

2. Прямой доступ к БД в endpoints:
   - endpoints в interfaces/api/ не должны вызывать session.execute(), session.get(), session.add()
   - Весь доступ к данным через application services и handlers

3. Соответствие CQRS:
   - Query handlers должны возвращать DTO, не domain entities
   - Command handlers должны возвращать None, DTO или примитив (не domain entities)

4. Контракт репозитория:
   - Каждый метод используемый application handlers должен быть объявлен в абстрактном репозитории в domain/

5. Мёртвый код:
   - Любой модуль который определён но нигде не импортируется

Для каждого нарушения: путь к файлу, номер строки, тип нарушения, предложение по исправлению.
Вернуть приоритизированным списком: CRITICAL → HIGH → MEDIUM → LOW.
```

---

### Исправление: убрать infrastructure из application

```
The application layer directly imports infrastructure implementations.
This violates Dependency Inversion Principle.

Current violations:
- auth_command_handlers.py imports from src.infrastructure.security.password
- auth_command_handlers.py imports from src.infrastructure.security.jwt_service
- auth_command_handlers.py imports from src.infrastructure.cache.token_blacklist
- product_command_handlers.py imports from src.infrastructure.storage.image_service
- product_query_handlers.py imports from src.infrastructure.storage.image_service

Fix by:
1. Create abstract interfaces in src/domain/services/:
   - IPasswordService: hash_password(), verify_password()
   - ITokenService: create_access_token(), blacklist_token()
   - IImageService: upload_product_image(), get_object_url()

2. Create implementations in src/infrastructure/:
   - PasswordServiceImpl(IPasswordService)
   - TokenServiceImpl(ITokenService) — takes redis_client in constructor
   - ImageServiceImpl(IImageService)

3. Update all handlers to accept interfaces via constructor — remove all infrastructure imports

4. Wire implementations in src/interfaces/api/v1/dependencies.py

Do not change the external API contract (endpoint request/response shapes must stay the same).
```

**RU:**
```
Application layer напрямую импортирует infrastructure реализации.
Это нарушает Dependency Inversion Principle.

Текущие нарушения:
- auth_command_handlers.py импортирует из src.infrastructure.security.password
- auth_command_handlers.py импортирует из src.infrastructure.security.jwt_service
- auth_command_handlers.py импортирует из src.infrastructure.cache.token_blacklist
- product_command_handlers.py импортирует из src.infrastructure.storage.image_service
- product_query_handlers.py импортирует из src.infrastructure.storage.image_service

Исправить:
1. Создать абстрактные интерфейсы в src/domain/services/:
   - IPasswordService: hash_password(), verify_password()
   - ITokenService: create_access_token(), blacklist_token()
   - IImageService: upload_product_image(), get_object_url()

2. Создать реализации в src/infrastructure/:
   - PasswordServiceImpl(IPasswordService)
   - TokenServiceImpl(ITokenService) — принимает redis_client в конструкторе
   - ImageServiceImpl(IImageService)

3. Обновить все хэндлеры — принимать интерфейсы через конструктор, убрать все infrastructure imports

4. Зарегистрировать реализации в src/interfaces/api/v1/dependencies.py

Не менять внешний API контракт (форматы запросов и ответов должны остаться прежними).
```

---

### Исправление: убрать прямой SQL из endpoints

```
Two endpoints bypass the application layer and access the database directly.

Violations:
1. src/interfaces/api/v1/endpoints/auth.py — get_me endpoint uses:
   session.get(UserModel, user_id) and session.execute(select(UserIdentityModel)...)

2. src/interfaces/api/v1/endpoints/admin_categories.py — list_categories endpoint uses:
   session.execute(select(CategoryModel).order_by(...))

Fix by creating the full application stack for each:

For get_me:
- GetCurrentUserQuery(user_id: uuid.UUID)
- GetCurrentUserHandler → returns MeResponse DTO with user + email
- Add get_me() method to AuthService
- Update endpoint to use AuthService.get_me()

For categories:
- GetCategoriesQuery (no params needed)
- GetCategoriesHandler → returns list[CategoryDTO]
- CategoryService.get_categories()
- CategoryRepository abstract interface in domain/
- SQLAlchemyCategoryRepository implementation
- get_category_service dependency in dependencies.py
- Update endpoint to use CategoryService

Do not change the response schema of either endpoint.
```

**RU:**
```
Два endpoint'а обходят application layer и обращаются к БД напрямую.

Нарушения:
1. src/interfaces/api/v1/endpoints/auth.py — get_me endpoint использует:
   session.get(UserModel, user_id) и session.execute(select(UserIdentityModel)...)

2. src/interfaces/api/v1/endpoints/admin_categories.py — list_categories endpoint использует:
   session.execute(select(CategoryModel).order_by(...))

Исправить созданием полного application-стека для каждого:

Для get_me:
- GetCurrentUserQuery(user_id: uuid.UUID)
- GetCurrentUserHandler → возвращает MeResponse DTO с user + email
- Метод get_me() в AuthService
- Обновить endpoint для использования AuthService.get_me()

Для categories:
- GetCategoriesQuery (параметры не нужны)
- GetCategoriesHandler → возвращает list[CategoryDTO]
- CategoryService.get_categories()
- Абстрактный CategoryRepository интерфейс в domain/
- SQLAlchemyCategoryRepository реализация
- Зависимость get_category_service в dependencies.py
- Обновить endpoint для использования CategoryService

Не менять response schema ни одного из endpoint'ов.
```

---

## Тесты

### Unit-тесты для auth handlers

```
Write unit tests for all auth command handlers using pytest and pytest-asyncio.

Test file: tests/unit/handlers/test_auth_handlers.py

Requirements:
- All tests must be isolated — no real DB, Redis, or external services
- Mock all repositories and services using MagicMock / AsyncMock
- Use pytest fixtures for reusable mocks (mock_user_repo, mock_identity_repo,
  mock_password_service, mock_token_service)

LoginHandler tests:
- Returns JWT token on valid credentials
- Raises AccessDenied when identity not found
- Raises AccessDenied when password is wrong
- Raises AccessDenied when email not verified
- Raises AccessDenied when user is banned

AdminLoginHandler tests:
- Admin user can login
- Moderator user can login
- Regular USER role raises AccessDenied
- Banned admin raises AccessDenied

RegisterHandler tests:
- Creates user and identity, returns User
- New user has PENDING_VERIFICATION status
- New user has USER role
- Raises EntityAlreadyExists when email already registered
- Calls hash_password with the plain password

LogoutHandler tests:
- Calls blacklist_token with correct jti and ttl

Use asyncio_mode = "auto" in pytest config (no need for @pytest.mark.asyncio on each test).
```

**RU:**
```
Напиши unit-тесты для всех auth command handlers с использованием pytest и pytest-asyncio.

Файл тестов: tests/unit/handlers/test_auth_handlers.py

Требования:
- Все тесты изолированы — без реальной БД, Redis или внешних сервисов
- Мокировать все репозитории и сервисы через MagicMock / AsyncMock
- Использовать pytest fixtures для переиспользуемых моков

Тесты LoginHandler:
- Возвращает JWT токен при корректных данных
- Кидает AccessDenied когда identity не найден
- Кидает AccessDenied при неверном пароле
- Кидает AccessDenied когда email не верифицирован
- Кидает AccessDenied когда пользователь забанен

Тесты AdminLoginHandler:
- Admin может войти
- Moderator может войти
- Роль USER кидает AccessDenied
- Забаненный admin кидает AccessDenied

Тесты RegisterHandler:
- Создаёт user и identity, возвращает User
- Новый user имеет статус PENDING_VERIFICATION
- Новый user имеет роль USER
- Кидает EntityAlreadyExists когда email уже занят
- Вызывает hash_password с plain паролем

Тесты LogoutHandler:
- Вызывает blacklist_token с корректными jti и ttl

Использовать asyncio_mode = "auto" в конфиге pytest.
```

---

### Unit-тесты для domain entities

```
Write unit tests for domain entities: User and Product.

Test file: tests/unit/domain/test_user_entity.py and test_product_entity.py

For User entity test:
- is_active returns True only when status == ACTIVE
- is_active returns False for BANNED, INACTIVE, PENDING_VERIFICATION
- is_admin returns True only for ADMIN role
- is_admin returns False for USER and MODERATOR
- full_name combines first_name and last_name with space
- full_name strips whitespace when last_name is empty
- activate() sets status to ACTIVE
- ban() sets status to BANNED
- deactivate() sets status to INACTIVE
- sequence: activate then ban leaves user inactive

For Product entity test:
- Default values: is_active=True, price=0, currency=USD, stock=0
- Fields set correctly on creation
- is_active can be updated
- image_object_key can be set

No mocks needed — pure unit tests of dataclass logic.
```

**RU:**
```
Напиши unit-тесты для domain entities: User и Product.

Для User entity:
- is_active возвращает True только при status == ACTIVE
- is_active возвращает False для BANNED, INACTIVE, PENDING_VERIFICATION
- is_admin возвращает True только для роли ADMIN
- is_admin возвращает False для USER и MODERATOR
- full_name объединяет first_name и last_name через пробел
- full_name обрезает пробелы когда last_name пустой
- activate() устанавливает статус ACTIVE
- ban() устанавливает статус BANNED
- deactivate() устанавливает статус INACTIVE

Для Product entity:
- Дефолтные значения: is_active=True, price=0, currency=USD, stock=0
- Поля устанавливаются корректно при создании
- is_active можно обновить
- image_object_key можно установить

Моки не нужны — чистые unit-тесты логики dataclass'ов.
```

---

## Добавление новых фич

### Шаблон промпта для новой фичи

```
Add [feature name] to the marketplace backend following existing Clean Architecture patterns.

Read these existing files first to understand the patterns used:
- src/application/commands/product_commands.py  (command pattern)
- src/application/handlers/command_handlers/product_command_handlers.py  (handler pattern)
- src/application/dto/product_dto.py  (DTO pattern)
- src/domain/repositories/product_repository.py  (repository interface pattern)
- src/infrastructure/database/repositories/product_repository_impl.py  (repo implementation pattern)
- src/interfaces/api/v1/dependencies.py  (dependency injection pattern)

Implement in this order:
1. Domain: entity fields / repository interface method
2. Application: command/query dataclass → DTO → handler
3. Infrastructure: repository implementation
4. Interface: endpoint + dependency wiring

Rules:
- No infrastructure imports in application layer
- Handler returns DTO, not domain entity
- Endpoint calls service only, no direct DB access
- Follow exact same code style as existing files
```

**RU:**
```
Добавь [название фичи] в бэкенд маркетплейса следуя существующим паттернам Clean Architecture.

Сначала прочитай эти файлы чтобы понять используемые паттерны:
- src/application/commands/product_commands.py
- src/application/handlers/command_handlers/product_command_handlers.py
- src/application/dto/product_dto.py
- src/domain/repositories/product_repository.py
- src/infrastructure/database/repositories/product_repository_impl.py
- src/interfaces/api/v1/dependencies.py

Реализуй в таком порядке:
1. Domain: поля entity / метод интерфейса репозитория
2. Application: dataclass команды/запроса → DTO → хэндлер
3. Infrastructure: реализация репозитория
4. Interface: endpoint + dependency wiring

Правила:
- Никаких импортов infrastructure в application layer
- Хэндлер возвращает DTO, не domain entity
- Endpoint вызывает только service, без прямого доступа к БД
- Следовать точно такому же стилю кода как в существующих файлах
```
