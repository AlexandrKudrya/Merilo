# bot/app/

Корневой пакет Telegram бота.

## Что здесь

| Файл / папка | Описание |
|---|---|
| `main.py` | Точка входа — создаёт Bot, Dispatcher, запускает polling |
| `config.py` | `Settings` — `TELEGRAM_BOT_TOKEN`, `BACKEND_URL` |
| `storage.py` | In-memory хранилище JWT токенов, username→telegram_id, активных заказов |
| `handlers/` | aiogram роутеры (обработчики команд и сообщений) |
| `client/` | HTTP клиент для общения с backend API |
| `utils/` | Вспомогательные утилиты (генерация Telegram initData) |
