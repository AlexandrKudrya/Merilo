# SplitCheck

Приложение для разделения счёта через Telegram.

## Как это работает

1. Создатель заказа фотографирует чек и добавляет участников
2. Claude API разбирает чек на позиции
3. Каждый участник отмечает что он ел
4. Все платят создателю нужную сумму

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Kotlin, Spring Boot 3, JPA |
| Telegram Bot | aiogram |
| База данных | PostgreSQL 16 |
| AI | Claude API (Anthropic) |
| Хранилище | S3-compatible |

## Структура репозитория

```
Merilo/
├── backend/           # Spring Boot (Kotlin) REST API
├── bot/               # Telegram бот
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
