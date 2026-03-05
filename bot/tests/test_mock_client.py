import pytest

from app.client.mock import MockBackendClient


@pytest.fixture(autouse=True)
def reset_mock_state():
    MockBackendClient._next_order_id = 1
    MockBackendClient._orders.clear()
    MockBackendClient._photo_upload_times.clear()
    yield


async def test_authenticate_returns_mock_client():
    client = await MockBackendClient.authenticate("any_init_data")
    assert isinstance(client, MockBackendClient)
    assert client._token == "mock-token"


async def test_create_order_returns_draft():
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    assert order["status"] == "DRAFT"
    assert order["id"] == 1
    assert order["order_info"] == []


async def test_create_order_increments_id():
    client = MockBackendClient("mock-token")
    first = await client.create_order()
    second = await client.create_order()
    assert second["id"] == first["id"] + 1


async def test_get_order_before_photo_is_draft():
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    result = await client.get_order(order["id"])
    assert result["status"] == "DRAFT"


async def test_get_order_right_after_photo_is_still_draft():
    """Parsing takes _PARSE_DELAY seconds — status stays DRAFT immediately after upload."""
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    await client.upload_photo(order["id"], b"fake-photo-bytes")  # type: ignore[arg-type]
    result = await client.get_order(order["id"])
    assert result["status"] == "DRAFT"


async def test_get_order_after_parse_delay_is_pending():
    """Simulate parse delay by backdating the upload timestamp."""
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    await client.upload_photo(order["id"], b"fake-photo-bytes")  # type: ignore[arg-type]
    # Backdate upload time so delay has already passed
    MockBackendClient._photo_upload_times[order["id"]] -= MockBackendClient._PARSE_DELAY
    result = await client.get_order(order["id"])
    assert result["status"] == "PENDING"
    assert len(result["order_info"]) > 0


async def test_add_participants():
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    result = await client.add_participants(order["id"], [111, 222])
    assert result == {"added": 2}


async def test_get_order_summary():
    client = MockBackendClient("mock-token")
    order = await client.create_order()
    summary = await client.get_order_summary(order["id"])
    assert summary["order_id"] == order["id"]
    assert len(summary["participants"]) > 0
