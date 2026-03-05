import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app import storage
from app.client.base import AbstractBackendClient
from app.config import settings
from app.utils.initdata import generate_init_data

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, client_class: type[AbstractBackendClient]) -> None:
    user = message.from_user
    if user is None:
        return

    if user.username:
        storage.save_username(user.username, user.id)

    if storage.get_token(user.id) is None:
        try:
            init_data = generate_init_data(
                bot_token=settings.telegram_bot_token,
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
            )
            client = await client_class.authenticate(init_data)
            storage.save_token(user.id, client._token)
        except Exception:
            logger.exception("Failed to authenticate user %s with backend", user.id)
            await message.answer("Не удалось подключиться к серверу. Попробуй позже.")
            return

    await message.answer(
        "Привет! Я Merilo — помогаю делить счёт.\n\n"
        "/new — создать новый заказ\n"
        "/add @username — добавить участника к заказу"
    )
