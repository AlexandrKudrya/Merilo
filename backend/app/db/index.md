# backend/app/db/

SQLAlchemy настройка и Alembic миграции.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `base.py` | Создаёт async engine, session factory, базовый класс `Base` для моделей, dependency `get_session` |
| `migrations/` | Alembic миграции схемы БД |

## Добавить новую миграцию

```bash
cd backend
uv run alembic revision --autogenerate -m "описание изменения"
uv run alembic upgrade head
```

## Правило

Никаких изменений схемы БД вручную. Только через `alembic revision --autogenerate`.
