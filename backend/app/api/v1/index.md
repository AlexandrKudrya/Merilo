# backend/app/api/v1/

Эндпоинты REST API v1. Каждый файл — отдельный роутер.

## Что здесь

| Файл | Эндпоинты | Описание |
|---|---|---|
| `auth.py` | `POST /auth/telegram` | Аутентификация через Telegram initData, выдаёт JWT |
| `users.py` | `GET /users/me`, `PATCH /users/me/payment-methods` | Профиль пользователя и реквизиты оплаты |
| `orders.py` | `POST/GET /orders`, `/orders/{id}/photo`, `/orders/{id}/participants`, и др. | Весь жизненный цикл заказа |

## Жизненный цикл заказа

```
DRAFT → PENDING → ACTIVE → FINISHED
               ↘ FAILED
```

- `DRAFT` — создан, ждёт фото чека
- `PENDING` — Claude распарсил чек, ждём выбора позиций от участников
- `ACTIVE` — все выбрали, ждём оплаты
- `FINISHED` — все оплатили
- `FAILED` — Claude не смог распарсить чек
