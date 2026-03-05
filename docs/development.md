# Руководство разработчика

## Требования

- Docker + Docker Compose
- Python 3.12+ (для локальной разработки без Docker)
- uv (менеджер пакетов Python)

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo_url> && cd Splat

# 2. Создать .env из шаблона и заполнить
cp .env.example .env

# 3. Запустить всё через Docker Compose
docker compose up
```

После запуска:
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql+asyncpg://postgres:password@db:5432/merilo` |
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | `1234567890:ABC...` |
| `SECRET_KEY` | Секрет для подписи JWT (минимум 32 символа) | `supersecretkey_32chars_minimum!!` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Срок жизни JWT | `1440` (24 часа) |
| `ANTHROPIC_API_KEY` | Ключ Anthropic API | `sk-ant-...` |
| `S3_ENDPOINT_URL` | Endpoint S3-совместимого хранилища | `https://s3.amazonaws.com` |
| `S3_ACCESS_KEY` | Access key S3 | `AKIA...` |
| `S3_SECRET_KEY` | Secret key S3 | `wJal...` |
| `S3_BUCKET_NAME` | Имя бакета | `merilo-receipts` |
| `S3_REGION` | Регион | `us-east-1` |
| `ENVIRONMENT` | Окружение | `development` / `production` |
| `LOG_LEVEL` | Уровень логов | `INFO` / `DEBUG` |

## Локальная разработка (без Docker)

```bash
cd backend

# Установить зависимости
uv sync --dev

# Запустить backend (БД должна быть доступна)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd bot

# Установить зависимости
uv sync

# Запустить бота
uv run python -m app.main
```

## Миграции базы данных

Используется Alembic. Никогда не писать SQL напрямую для изменения схемы.

```bash
cd backend

# Создать новую миграцию (автогенерация из моделей)
uv run alembic revision --autogenerate -m "add column foo to users"

# Применить миграции
uv run alembic upgrade head

# Откатить последнюю миграцию
uv run alembic downgrade -1
```

## Тесты

```bash
cd backend

# Запустить все тесты
uv run pytest

# С подробным выводом
uv run pytest -v

# Конкретный файл
uv run pytest tests/test_orders.py

# Конкретный тест
uv run pytest tests/test_orders.py::test_create_order
```

Тесты находятся в `backend/tests/`. Каждый новый API эндпоинт обязан иметь хотя бы один тест.

## Линтер и форматтер

Используется `ruff`. Обязательно перед коммитом:

```bash
cd backend

# Проверить стиль
uv run ruff check .

# Проверить форматирование
uv run ruff format --check .

# Автоматически исправить
uv run ruff check --fix .
uv run ruff format .
```

## Type checking

```bash
cd backend
uv run mypy .
```

## Структура backend

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py       # POST /auth/telegram
│   │       ├── users.py      # GET/PATCH /users/me
│   │       └── orders.py     # CRUD заказов
│   ├── core/
│   │   ├── config.py         # Настройки из .env
│   │   └── security.py       # JWT токены
│   ├── db/
│   │   └── base.py           # SQLAlchemy engine, сессии
│   ├── models/
│   │   ├── user.py           # User
│   │   └── order.py          # Order, UserOrder
│   ├── schemas/
│   │   ├── auth.py           # Pydantic-схемы авторизации
│   │   ├── user.py           # Pydantic-схемы пользователя
│   │   └── order.py          # Pydantic-схемы заказа
│   ├── services/
│   │   ├── auth.py           # Верификация Telegram initData
│   │   ├── claude.py         # Парсинг чека через Claude API
│   │   └── s3.py             # Загрузка фото в S3
│   └── main.py               # Точка входа FastAPI
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_orders.py
└── pyproject.toml
```

## Git-конвенции

Conventional commits:

```
feat: add item selection endpoint
fix: handle missing user in participants
chore: update dependencies
docs: add API reference
test: cover order summary endpoint
```

Один PR — одна задача. Описания коммитов на английском.
