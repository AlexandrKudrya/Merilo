import asyncio
import logging
import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app import storage
from app.client.base import AbstractBackendClient

logger = logging.getLogger(__name__)
router = Router()

# Keep strong references to background tasks to prevent GC cancellation
_background_tasks: set[asyncio.Task] = set()

_POLL_INTERVAL = 3  # seconds between status checks
_POLL_MAX_TRIES = 20  # ~60 seconds total


class OrderStates(StatesGroup):
    waiting_photo = State()
    order_active = State()


def _format_items(order_info: list[dict]) -> str:
    if not order_info:
        return "(позиции не найдены)"
    lines = []
    for item in order_info:
        price_rub = item["price"] / 100
        lines.append(f"• {item['name']} — {price_rub:.0f} ₽ x{item['quantity']:.0f}")
    return "\n".join(lines)


async def _poll_order(
    bot: Bot,
    telegram_id: int,
    order_id: int,
    token: str,
    client_class: type[AbstractBackendClient],
) -> None:
    client = client_class(token)
    for _ in range(_POLL_MAX_TRIES):
        await asyncio.sleep(_POLL_INTERVAL)
        try:
            order = await client.get_order(order_id)
        except Exception:
            logger.exception("Polling error for order %s", order_id)
            continue

        status = order.get("status")

        if status == "PENDING":
            items_text = _format_items(order.get("order_info", []))
            await bot.send_message(
                chat_id=telegram_id,
                text=f"Чек распознан!\n\n{items_text}\n\nДобавь участников: /add @username",
            )
            return

        if status == "FAILED":
            await bot.send_message(
                chat_id=telegram_id,
                text="Не удалось распознать чек. Попробуй ещё раз: /new",
            )
            storage.clear_active_order(telegram_id)
            return

    await bot.send_message(
        chat_id=telegram_id,
        text="Превышено время ожидания распознавания чека. Попробуй ещё раз: /new",
    )
    storage.clear_active_order(telegram_id)


@router.message(Command("new"))
async def handle_new(
    message: Message,
    state: FSMContext,
    client_class: type[AbstractBackendClient],
) -> None:
    user = message.from_user
    if user is None:
        return

    token = storage.get_token(user.id)
    if token is None:
        await message.answer("Сначала напиши /start")
        return

    try:
        order = await client_class(token).create_order()
    except Exception:
        logger.exception("Failed to create order for user %s", user.id)
        await message.answer("Не удалось создать заказ. Попробуй позже.")
        return

    order_id = order["id"]
    storage.set_active_order(user.id, order_id)
    await state.set_state(OrderStates.waiting_photo)
    await state.update_data(order_id=order_id)
    await message.answer(f"Создан заказ #{order_id}. Отправь фото чека.")


@router.message(OrderStates.waiting_photo, F.photo)
async def handle_photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
    client_class: type[AbstractBackendClient],
) -> None:
    user = message.from_user
    if user is None:
        return

    token = storage.get_token(user.id)
    data = await state.get_data()
    order_id = data.get("order_id")

    if token is None or order_id is None:
        await message.answer("Что-то пошло не так. Начни заново: /new")
        await state.clear()
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file.file_path)  # type: ignore[arg-type]

    try:
        await client_class(token).upload_photo(order_id, photo_bytes)
    except Exception:
        logger.exception("Failed to upload photo for order %s", order_id)
        await message.answer("Не удалось загрузить фото. Попробуй ещё раз.")
        return

    await state.set_state(OrderStates.order_active)
    await message.answer("Чек обрабатывается, подожди немного...")

    task = asyncio.create_task(_poll_order(bot, user.id, order_id, token, client_class))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


@router.message(OrderStates.waiting_photo)
async def handle_photo_wrong_input(message: Message) -> None:
    await message.answer("Отправь фото чека.")


@router.message(Command("add"))
async def handle_add(
    message: Message,
    client_class: type[AbstractBackendClient],
) -> None:
    user = message.from_user
    if user is None:
        return

    token = storage.get_token(user.id)
    order_id = storage.get_active_order(user.id)

    if token is None:
        await message.answer("Сначала напиши /start")
        return
    if order_id is None:
        await message.answer("Нет активного заказа. Создай новый: /new")
        return

    usernames = re.findall(r"@?(\w+)", (message.text or "").split(maxsplit=1)[-1])
    if not usernames:
        await message.answer("Укажи username: /add @petya @masha")
        return

    try:
        found = await client_class(token).lookup_users(usernames)
    except Exception:
        logger.exception("Failed to lookup users for order %s", order_id)
        await message.answer("Не удалось найти пользователей. Попробуй позже.")
        return

    if not found:
        names = ", ".join(f"@{u}" for u in usernames)
        await message.answer(
            f"Никто из {names} ещё не зарегистрирован. Попроси их написать /start боту."
        )
        return

    found_names = {u["username"] for u in found}
    not_found = [u for u in usernames if u not in found_names]
    telegram_ids = [u["telegram_id"] for u in found]

    try:
        await client_class(token).add_participants(order_id, telegram_ids)
    except Exception:
        logger.exception("Failed to add participants to order %s", order_id)
        await message.answer("Не удалось добавить участников. Попробуй позже.")
        return

    lines = [f"Добавлены: {', '.join(f'@{u}' for u in found_names)}"]
    if not_found:
        lines.append(f"Не найдены: {', '.join(f'@{u}' for u in not_found)}")
    await message.answer("\n".join(lines))
