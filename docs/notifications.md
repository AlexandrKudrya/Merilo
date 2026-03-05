# Уведомления: Backend → Bot

## Как это работает

Backend не может напрямую слать сообщения в Telegram — он не знает про бота. Вместо этого backend делает HTTP POST на внутренний эндпоинт бота, а бот уже шлёт сообщение пользователю.

```
Backend ──POST /internal/notify──▶ Bot ──send_message──▶ Telegram
```

Бот поднимает два сервера параллельно:
- **Polling** (порт не нужен) — слушает обновления от Telegram
- **aiohttp** на порту `8001` — принимает уведомления от backend

Оба запускаются через `asyncio.gather` в `main.py`.

## Безопасность

Эндпоинт доступен только внутри Docker-сети (`bot:8001`). Запросы защищены shared secret:

```
X-Bot-Secret: <BOT_INTERNAL_SECRET>
```

Если заголовок отсутствует или не совпадает — `403`.

## Эндпоинт

### POST /internal/notify

**Заголовки:**
```
X-Bot-Secret: <BOT_INTERNAL_SECRET>
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "event": "<event_type>",
  "order_id": 42,
  "telegram_id": 123456789
}
```

Дополнительные поля зависят от события — см. таблицу ниже.

**Ответ:**
- `200 OK` — уведомление отправлено
- `400 Bad Request` — неизвестный event или невалидный payload
- `403 Forbidden` — неверный или отсутствующий секрет

## События

Backend вызывает эндпоинт **по одному разу на каждого получателя**.

### `receipt_parsed`

Бот показывает позиции из чека — они передаются прямо в payload, без дополнительного GET.

```json
{
  "event": "receipt_parsed",
  "order_id": 42,
  "telegram_id": 123456789,
  "order_info": [
    {"id": 1, "name": "Маргарита 30см", "price": 89000, "quantity": 2},
    {"id": 2, "name": "Кола 0.5л", "price": 15000, "quantity": 1}
  ]
}
```

### `receipt_failed`

```json
{ "event": "receipt_failed", "order_id": 42, "telegram_id": 123456789 }
```

### `payment_required`

Сумма передаётся в рублях.

```json
{ "event": "payment_required", "order_id": 42, "telegram_id": 123456789, "amount": 650.0 }
```

### `order_finished`

```json
{ "event": "order_finished", "order_id": 42, "telegram_id": 123456789 }
```

---

| `event` | Кто получает | Доп. поля |
|---|---|---|
| `receipt_parsed` | Все участники | `order_info` |
| `receipt_failed` | Создатель | — |
| `payment_required` | Все участники | `amount` |
| `order_finished` | Создатель | — |

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_INTERNAL_SECRET` | Shared secret для авторизации запросов от backend |
| `BOT_INTERNAL_PORT` | Порт внутреннего сервера (по умолчанию `8001`) |

## Схема в docker-compose

```
services:
  backend:
    environment:
      BOT_INTERNAL_URL: http://bot:8001
      BOT_INTERNAL_SECRET: <secret>

  bot:
    ports:
      - "8001"   # только внутри Docker-сети, не наружу
    environment:
      BOT_INTERNAL_SECRET: <secret>
      BOT_INTERNAL_PORT: 8001
```
