import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.client.api import BackendClient
from app.client.base import AbstractBackendClient
from app.client.mock import MockBackendClient
from app.config import settings
from app.handlers import notifications, order, start

logging.basicConfig(level=settings.log_level.upper())


def _select_client() -> type[AbstractBackendClient]:
    if settings.mock_backend:
        logging.getLogger(__name__).info("Running with MOCK backend")
        return MockBackendClient
    return BackendClient


async def main() -> None:
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["client_class"] = _select_client()

    dp.include_router(start.router)
    dp.include_router(order.router)
    dp.include_router(notifications.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
