import hashlib
import hmac
import json
import urllib.parse

from app.utils.initdata import generate_init_data

BOT_TOKEN = "1234567890:test_token_for_tests"


def _verify(init_data: str, bot_token: str) -> bool:
    parsed = dict(urllib.parse.parse_qsl(init_data))
    hash_value = parsed.pop("hash")
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    expected = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hash_value == expected


def test_hash_is_valid():
    result = generate_init_data(BOT_TOKEN, 123456, "testuser", "Test")
    assert _verify(result, BOT_TOKEN)


def test_contains_user_data():
    result = generate_init_data(BOT_TOKEN, 123456, "testuser", "Test")
    parsed = dict(urllib.parse.parse_qsl(result))
    user = json.loads(parsed["user"])
    assert user["id"] == 123456
    assert user["username"] == "testuser"
    assert user["first_name"] == "Test"


def test_without_username():
    result = generate_init_data(BOT_TOKEN, 999, None, "NoUsername")
    assert _verify(result, BOT_TOKEN)
    parsed = dict(urllib.parse.parse_qsl(result))
    user = json.loads(parsed["user"])
    assert "username" not in user


def test_wrong_token_fails_verification():
    result = generate_init_data(BOT_TOKEN, 123, "u", "U")
    assert not _verify(result, "wrong_token")
