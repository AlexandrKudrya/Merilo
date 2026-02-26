# backend/app/models/

SQLAlchemy ORM модели — маппинг на таблицы PostgreSQL.

## Что здесь

| Файл | Модели | Таблица |
|---|---|---|
| `user.py` | `User` | `users` — пользователи (telegram_id, username, payment_methods) |
| `order.py` | `Order`, `UserOrder`, `OrderStatus`, `ParticipantStatus` | `orders`, `user_orders` — заказы и участники |

## Ключевые поля

**User:**
- `telegram_id` — уникальный ID из Telegram
- `payment_methods` — JSONB: `{"sbp": "+7...", "tinkoff": "t.me/..."}`

**Order:**
- `order_info` — JSONB массив позиций чека с разбивкой по участникам
- `status` — `DRAFT | PENDING | ACTIVE | FINISHED | FAILED`

**UserOrder:**
- Join table участников заказа
- `status` — `pending | confirmed | paid`
