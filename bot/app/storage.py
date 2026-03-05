# In-memory storage for the bot process lifetime.
# Restarting the bot clears all state — acceptable for MVP.

# telegram_id -> JWT token
_jwt_tokens: dict[int, str] = {}

# username (without @) -> telegram_id
_usernames: dict[str, int] = {}

# telegram_id -> current active order_id
_active_orders: dict[int, int] = {}


def save_token(telegram_id: int, token: str) -> None:
    _jwt_tokens[telegram_id] = token


def get_token(telegram_id: int) -> str | None:
    return _jwt_tokens.get(telegram_id)


def save_username(username: str, telegram_id: int) -> None:
    _usernames[username.lstrip("@").lower()] = telegram_id


def resolve_username(username: str) -> int | None:
    return _usernames.get(username.lstrip("@").lower())


def set_active_order(telegram_id: int, order_id: int) -> None:
    _active_orders[telegram_id] = order_id


def get_active_order(telegram_id: int) -> int | None:
    return _active_orders.get(telegram_id)


def clear_active_order(telegram_id: int) -> None:
    _active_orders.pop(telegram_id, None)
