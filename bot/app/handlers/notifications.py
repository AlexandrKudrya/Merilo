from aiogram import Bot, Router

router = Router()


async def notify_receipt_parsed(bot: Bot, telegram_id: int, order_id: int) -> None:
    """Notify participant that receipt has been parsed and they can select items."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"Чек готов! Выбери что ты ел в заказе #{order_id}.",
    )


async def notify_payment_required(
    bot: Bot, telegram_id: int, order_id: int, amount: float
) -> None:
    """Notify participant of the amount they need to pay."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"Заказ #{order_id}: нужно оплатить {amount:.2f} ₽.",
    )


async def notify_all_paid(bot: Bot, telegram_id: int, order_id: int) -> None:
    """Notify the order creator that all participants have paid."""
    await bot.send_message(
        chat_id=telegram_id,
        text=f"Все участники оплатили заказ #{order_id}!",
    )
