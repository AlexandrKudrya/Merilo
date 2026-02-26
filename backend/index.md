# backend/

FastAPI REST API для SplitCheck.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `app/` | Основной Python пакет приложения |
| `tests/` | pytest тесты |
| `pyproject.toml` | Зависимости и конфигурация инструментов (ruff, mypy, pytest) |
| `Dockerfile` | Docker образ для продакшена |
| `alembic.ini` | Конфигурация Alembic (миграции БД) |

## Запуск

```bash
uv sync
uv run uvicorn app.main:app --reload
```

## Тесты

```bash
uv run pytest -v
```

## Линтинг

```bash
uv run ruff check . && uv run ruff format --check .
```
