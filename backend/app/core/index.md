# backend/app/core/

Конфигурация приложения и утилиты безопасности.

## Что здесь

| Файл | Описание |
|---|---|
| `config.py` | `Settings` — все переменные окружения через pydantic-settings. Единственный источник конфига. |
| `security.py` | `create_access_token` / `decode_access_token` — работа с JWT (python-jose) |

## Использование Settings

```python
from app.core.config import settings

settings.database_url
settings.anthropic_api_key
```

Настройки загружаются из `.env` файла или переменных окружения.
