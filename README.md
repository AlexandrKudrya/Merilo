# Merilo

Приложение для разделения счёта через Telegram.

## Как это работает

1. Создатель заказа фотографирует чек и добавляет участников
2. Claude API разбирает чек на позиции
3. Каждый участник отмечает что он ел
4. Все платят создателю нужную сумму

## Стек

| Слой | Технология |
|------|-----------|
| Backend | FastAPI (Python) |
| Telegram Bot | aiogram |
| База данных | PostgreSQL |
| AI | Claude API (Anthropic) |
| Хранилище | S3-compatible |

## Структура репозитория

```
Splat/
├── backend/           # FastAPI REST API
├── bot/               # Telegram бот (aiogram)
├── docker-compose.yml
└── .env.example
```

## Быстрый старт

```bash
cp .env.example .env
# Заполнить переменные в .env
docker compose up
```

## Документация

- [API Spec](SplitCheck_API.pdf)
- [Architecture](SplitCheck_Architecture.pdf)
