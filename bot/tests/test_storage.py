import pytest

from app import storage


@pytest.fixture(autouse=True)
def clear_storage():
    storage._jwt_tokens.clear()
    storage._usernames.clear()
    storage._active_orders.clear()
    yield


def test_save_and_get_token():
    storage.save_token(123, "jwt-abc")
    assert storage.get_token(123) == "jwt-abc"


def test_get_token_missing():
    assert storage.get_token(999) is None


def test_save_and_resolve_username():
    storage.save_username("petya", 456)
    assert storage.resolve_username("petya") == 456
    assert storage.resolve_username("@petya") == 456


def test_resolve_username_case_insensitive():
    storage.save_username("Petya", 456)
    assert storage.resolve_username("petya") == 456
    assert storage.resolve_username("PETYA") == 456


def test_resolve_username_missing():
    assert storage.resolve_username("nobody") is None


def test_active_order_lifecycle():
    storage.set_active_order(1, 42)
    assert storage.get_active_order(1) == 42

    storage.clear_active_order(1)
    assert storage.get_active_order(1) is None


def test_clear_active_order_noop():
    # should not raise if no order exists
    storage.clear_active_order(999)
