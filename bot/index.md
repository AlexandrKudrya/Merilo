# bot/

aiogram Telegram бот для SplitCheck.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `app/` | Основной Python пакет бота |
| `pyproject.toml` | Зависимости (aiogram, httpx, pydantic-settings) |
| `Dockerfile` | Docker образ бота |

## Запуск

```bash
uv sync
uv run python -m app.main
```

## Роль бота

Бот отвечает только за:
1. Команду `/start`
2. Уведомления пользователям при смене статуса заказа

Вся бизнес-логика — в `backend/`.
