# backend/app/api/

HTTP слой — роутеры FastAPI.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `router.py` | Агрегирует все v1 роутеры в один `api_router` |
| `deps.py` | Dependency injection: `get_current_user` — парсит JWT и возвращает объект User |
| `v1/` | Версионированные эндпоинты API v1 |
