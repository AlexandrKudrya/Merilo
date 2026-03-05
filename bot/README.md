# Merilo Bot

Telegram-бот для разделения счёта. Работает в паре с backend API.

## Быстрый старт

### 1. Установить uv

```powershell
powershell -ExecutionPolicy BypassPolicy -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Или через pip:

```bash
pip install uv
```

### 2. Создать `.env`

```bash
cp ../.env.example .env
```

Минимум для запуска бота:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
BACKEND_URL=http://localhost:8000
MOCK_BACKEND=false
```

Чтобы запустить без реального backend (моки):

```env
MOCK_BACKEND=true
```

Токен получить у [@BotFather](https://t.me/BotFather) — команда `/newbot`.

### 3. Установить зависимости и запустить

```bash
uv sync
uv run python -m app.main
```

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Регистрация, приветствие |
| `/new` | Создать новый заказ и загрузить фото чека |
| `/add @username` | Добавить участника к активному заказу |

## Флоу заказа

```
/new
 └─> создаётся заказ на backend
 └─> бот просит прислать фото чека

[пользователь отправляет фото]
 └─> фото загружается на backend
 └─> Claude API распознаёт позиции (~10-30 сек)
 └─> бот показывает список позиций

/add @username
 └─> добавляет участника к заказу
     (участник должен был написать /start боту хотя бы раз)
```

## Запуск через Docker

```bash
# из корня проекта
docker compose up bot
```

## Разработка

```bash
# линтер
uv run ruff check .

# форматтер
uv run ruff format .

# type check
uv run mypy app
```
