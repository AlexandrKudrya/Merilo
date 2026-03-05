# REST API

Base URL: `http://localhost:8000/api/v1`

Все защищённые эндпоинты требуют заголовок:
```
Authorization: Bearer <jwt_token>
```

---

## Авторизация

### POST /auth/telegram

Авторизация через Telegram initData. Создаёт пользователя если он новый.

**Тело запроса:**
```json
{
  "init_data": "query_id=...&user=%7B%22id%22%3A123...&hash=abc..."
}
```

**Ответ 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ошибки:**
| Код | Причина |
|---|---|
| `401` | Невалидная подпись initData |
| `400` | В initData нет данных пользователя |

---

## Пользователи

### GET /users/me

Получить текущего авторизованного пользователя.

**Ответ 200:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "ivan",
  "payment_methods": {
    "tinkoff": "@ivan_tinkoff",
    "sbp": "+7 999 000-00-00"
  }
}
```

---

### PATCH /users/me/payment-methods

Обновить способы оплаты (мерджится с существующими).

**Тело запроса:**
```json
{
  "payment_methods": {
    "tinkoff": "@ivan_tinkoff"
  }
}
```

**Ответ 200:** объект пользователя (см. GET /users/me)

---

### POST /users/lookup

Найти пользователей по списку Telegram username. Возвращает только тех, кто зарегистрирован в системе (хотя бы раз авторизовался).

**Тело запроса:**
```json
{
  "usernames": ["petya", "masha", "unknown"]
}
```

> Username передаётся без `@`.

**Ответ 200:**
```json
[
  {"telegram_id": 987654321, "username": "petya"},
  {"telegram_id": 111222333, "username": "masha"}
]
```

> `unknown` отсутствует в ответе — пользователь не найден.

**Ошибки:**
| Код | Причина |
|---|---|
| `422` | Пустой список usernames |

---

## Заказы

### POST /orders

Создать новый заказ в статусе `DRAFT`.

**Ответ 201:**
```json
{
  "id": 42,
  "status": "DRAFT",
  "creator_id": 1,
  "order_info": [],
  "participants": [],
  "created_at": "2024-01-15T12:00:00Z"
}
```

---

### GET /orders

Получить список заказов текущего пользователя.

**Query-параметры:**
| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `order_status` | `string` | — | Фильтр по статусу (`DRAFT`, `PENDING`, `ACTIVE`, `FINISHED`, `FAILED`) |
| `limit` | `int` | `20` | Кол-во записей |
| `offset` | `int` | `0` | Смещение |

**Ответ 200:** массив объектов заказа

---

### GET /orders/{order_id}

Получить заказ по ID.

**Ответ 200:** объект заказа

**Ошибки:**
| Код | Причина |
|---|---|
| `404` | Заказ не найден |

---

### POST /orders/{order_id}/photo

Загрузить фото чека. Запускает фоновую задачу парсинга через Claude API.

**Тело запроса:** `multipart/form-data`
| Поле | Тип | Описание |
|---|---|---|
| `file` | `UploadFile` | Фото чека (image/jpeg, image/png) |

**Ответ 202:**
```json
{
  "message": "parsing started",
  "order_id": 42
}
```

**Ошибки:**
| Код | Причина |
|---|---|
| `403` | Текущий пользователь не создатель заказа |
| `404` | Заказ не найден |

> **Примечание:** после успешного парсинга статус заказа меняется на `PENDING`, при ошибке — на `FAILED`. Это происходит асинхронно.

---

### POST /orders/{order_id}/participants

Добавить участников к заказу по их Telegram ID. Пользователи должны быть зарегистрированы в системе (т.е. хотя бы раз авторизовались).

**Тело запроса:**
```json
{
  "telegram_ids": [987654321, 111222333]
}
```

**Ответ 200:**
```json
{
  "added": 2
}
```

**Ошибки:**
| Код | Причина |
|---|---|
| `403` | Текущий пользователь не создатель заказа |
| `404` | Заказ не найден |

---

### PATCH /orders/{order_id}/items

Участник выбирает позиции которые он ел. После того как все участники сделают выбор, статус заказа переходит в `ACTIVE`.

> **Статус:** не реализовано (501)

**Тело запроса:**
```json
{
  "selections": [
    {"item_id": 1, "quantity": 1.0},
    {"item_id": 3, "quantity": 0.5}
  ]
}
```

**Ответ 200:**
```json
{
  "your_total": 750.00,
  "order_status": "ACTIVE"
}
```

---

### GET /orders/{order_id}/summary

Получить итоговый расчёт — кто сколько должен заплатить и куда.

> **Статус:** не реализовано (501)

**Ответ 200:**
```json
{
  "order_id": 42,
  "participants": [
    {
      "user_id": 2,
      "username": "petr",
      "amount_due": 650.00,
      "status": "pending"
    },
    {
      "user_id": 3,
      "username": "masha",
      "amount_due": 430.00,
      "status": "paid"
    }
  ],
  "payment_methods": {
    "tinkoff": "@ivan_tinkoff"
  }
}
```

---

### PATCH /orders/{order_id}/paid

Отметить что текущий участник оплатил. Когда все участники оплатили — заказ переходит в `FINISHED`, создателю приходит уведомление.

> **Статус:** не реализовано (501)

**Ответ 200:**
```json
{
  "status": "paid"
}
```
