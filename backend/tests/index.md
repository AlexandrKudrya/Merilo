# backend/tests/

pytest тесты для backend.

## Что здесь

| Файл | Описание |
|---|---|
| `conftest.py` | Фикстуры: тестовая БД, async HTTP клиент (`AsyncClient`), сессия |
| `test_auth.py` | Тесты аутентификации: `POST /auth/telegram` |
| `test_users.py` | Тесты профиля пользователя: `GET/PATCH /users/me` |
| `test_orders.py` | Тесты заказов: создание, фото, участники, выбор позиций, summary, оплата |

## Правила

- Каждый новый эндпоинт → минимум один тест
- Тесты используют отдельную БД (`splitcheck_test`)
- Все тесты async (`pytest-asyncio`)

## Запуск

```bash
cd backend && uv run pytest -v
```
