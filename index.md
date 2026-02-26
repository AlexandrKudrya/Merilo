# Корневая директория проекта SplitCheck

## Что здесь

| Файл / папка | Описание |
|---|---|
| `backend/` | FastAPI REST API — бизнес-логика, база данных, Claude API интеграция |
| `bot/` | aiogram Telegram бот — уведомления, команды |
| `.github/workflows/` | GitHub Actions CI/CD пайплайны |
| `docker-compose.yml` | Локальный запуск всех сервисов (db + backend + bot) |
| `.env.example` | Шаблон переменных окружения — скопировать в `.env` и заполнить |
| `README.md` | Обзор проекта и быстрый старт |
| `CLAUDE.md` | Правила работы с кодом для Claude Code |
| `docs/` | Документация проекта на русском (архитектура, API, модели, разработка) |
| `SplitCheck_API.pdf` | Исходная спека REST API |
| `SplitCheck_Architecture.pdf` | Исходный архитектурный документ |
