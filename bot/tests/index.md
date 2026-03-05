# bot/tests/

Тесты для Telegram бота.

## Что здесь

| Файл | Описание |
|---|---|
| `test_storage.py` | Тесты in-memory хранилища (JWT токены, username маппинг, активные заказы) |
| `test_initdata.py` | Тесты генерации и верификации Telegram initData (HMAC-SHA256) |
| `test_mock_client.py` | Тесты MockBackendClient — все методы и lifecycle заказа |

## Запуск

```bash
cd bot
uv run pytest
```
