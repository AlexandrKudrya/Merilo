import hashlib
import hmac
import json
import time
import urllib.parse


def generate_init_data(
    bot_token: str, telegram_id: int, username: str | None, first_name: str
) -> str:
    """Generate a valid Telegram initData string signed with bot_token."""
    user: dict = {"id": telegram_id, "first_name": first_name}
    if username:
        user["username"] = username

    data = {
        "auth_date": str(int(time.time())),
        "user": json.dumps(user, separators=(",", ":")),
    }

    # Step 1: secret_key = HMAC-SHA256(key="WebAppData", msg=bot_token)
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    # Step 2: data_check_string = sorted key=value pairs joined by \n (no hash)
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    # Step 3: hash = HMAC-SHA256(key=secret_key, msg=data_check_string)
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    data["hash"] = hash_value
    return urllib.parse.urlencode(data)
