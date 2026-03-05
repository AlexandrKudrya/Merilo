# bot/app/client/

HTTP клиент для общения бота с backend API.

## Что здесь

| Файл | Описание |
|---|---|
| `base.py` | `AbstractBackendClient` — ABC с интерфейсом всех методов |
| `api.py` | `BackendClient` — реальный HTTP клиент (httpx → FastAPI) |
| `mock.py` | `MockBackendClient` — мок с хардкоженными ответами для локальной разработки |

## Использование

```python
client = BackendClient(token=user_jwt_token)
order = await client.get_order(order_id=42)
summary = await client.get_order_summary(order_id=42)
```

Токен JWT получается через `POST /auth/telegram` при первом обращении пользователя.
