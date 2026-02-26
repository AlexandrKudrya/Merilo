from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Привет! Я SplitCheck бот.\n\n"
        "Я помогу разделить счёт с друзьями. "
        "Открой приложение через кнопку ниже или используй команды."
    )
