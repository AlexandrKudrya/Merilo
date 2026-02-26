# backend/app/schemas/

Pydantic схемы для валидации request/response тел.

## Что здесь

| Файл | Схемы | Используется в |
|---|---|---|
| `auth.py` | `TelegramAuthRequest`, `TokenResponse` | `POST /auth/telegram` |
| `user.py` | `UserResponse`, `UpdatePaymentMethodsRequest` | `GET/PATCH /users/me` |
| `order.py` | `OrderResponse`, `OrderItem`, `Split`, `SelectItemsRequest`, `OrderSummaryResponse`, и др. | Все `/orders` эндпоинты |

## Правило

Схемы — только для валидации данных на границе HTTP. Бизнес-логика живёт в `services/`, не в схемах.
