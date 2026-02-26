# backend/app/services/

Бизнес-логика и интеграции с внешними сервисами.

## Что здесь

| Файл | Описание |
|---|---|
| `auth.py` | Верификация Telegram initData через HMAC-SHA256 |
| `claude.py` | Интеграция с Claude API (Anthropic) — парсинг фото чека в JSON |
| `s3.py` | Загрузка фотографий чеков в S3-совместимое хранилище |

## Важно

- `claude.py` вызывается в **фоновой задаче** (BackgroundTasks) — не блокирует HTTP запрос
- При ошибке от Claude API заказ переходит в статус `FAILED`
- `s3.py` использует `aiobotocore` (async S3 клиент)
