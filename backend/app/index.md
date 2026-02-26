# backend/app/

Корневой пакет FastAPI приложения.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `main.py` | Точка входа — создаёт FastAPI app, подключает роутеры |
| `api/` | HTTP роутеры (эндпоинты) |
| `models/` | SQLAlchemy ORM модели (таблицы БД) |
| `schemas/` | Pydantic схемы (request/response тела) |
| `services/` | Бизнес-логика: Telegram auth, Claude API, S3 |
| `db/` | SQLAlchemy engine, сессии, базовый класс |
| `core/` | Конфигурация (Settings) и утилиты безопасности (JWT) |
