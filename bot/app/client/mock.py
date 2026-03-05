import json
import logging
import time
import urllib.parse
from io import BytesIO

from app.client.base import AbstractBackendClient

logger = logging.getLogger(__name__)


def _log(method: str, path: str, req: object = None, resp: object = None) -> None:
    logger.info("[MOCK] → %s %s", method, path)
    if req is not None:
        logger.debug("[MOCK]   req:  %s", json.dumps(req, ensure_ascii=False))
    logger.debug("[MOCK]   resp: %s", json.dumps(resp, ensure_ascii=False))


# Sample items from the API docs (prices in kopecks)
_MOCK_ITEMS = [
    {"id": 1, "name": "Маргарита 30см", "price": 89000, "quantity": 2, "splits": []},
    {"id": 2, "name": "Кола 0.5л", "price": 15000, "quantity": 1, "splits": []},
    {"id": 3, "name": "Тирамису", "price": 42000, "quantity": 1, "splits": []},
]

_MOCK_SUMMARY = {
    "participants": [
        {"user_id": 2, "username": "petr", "amount_due": 650.00, "status": "pending"},
        {"user_id": 3, "username": "masha", "amount_due": 430.00, "status": "paid"},
    ],
    "payment_methods": {"tinkoff": "@ivan_tinkoff"},
}


class MockBackendClient(AbstractBackendClient):
    """Fake backend client for local development. No real HTTP calls."""

    # Shared state across all instances (simulates a real server)
    _next_order_id: int = 1
    _orders: dict[int, dict] = {}
    _photo_upload_times: dict[int, float] = {}  # order_id -> upload timestamp

    _PARSE_DELAY = 9.0  # seconds to simulate Claude parsing

    @classmethod
    async def authenticate(cls, init_data: str) -> "MockBackendClient":
        # Auto-register the user so they can be found via lookup_users
        try:
            parsed = dict(urllib.parse.parse_qsl(init_data))
            user = json.loads(parsed.get("user", "{}"))
            if "username" in user and "id" in user:
                cls._registered_users[user["username"].lower()] = user["id"]
                logger.debug("[MOCK] Registered user @%s (id=%s)", user["username"], user["id"])
        except Exception:
            pass

        resp = {"access_token": "mock-token", "token_type": "bearer"}
        _log("POST", "/api/v1/auth/telegram", req={"init_data": init_data[:40] + "..."}, resp=resp)
        return cls("mock-token")

    async def create_order(self) -> dict:
        order_id = MockBackendClient._next_order_id
        MockBackendClient._next_order_id += 1
        order = {
            "id": order_id,
            "status": "DRAFT",
            "creator_id": 1,
            "order_info": [],
            "participants": [],
            "created_at": "2024-01-15T12:00:00Z",
        }
        MockBackendClient._orders[order_id] = order
        _log("POST", "/api/v1/orders", resp=order)
        return order

    async def upload_photo(
        self, order_id: int, photo: BytesIO, filename: str = "receipt.jpg"
    ) -> dict:
        MockBackendClient._photo_upload_times[order_id] = time.monotonic()
        resp = {"message": "parsing started", "order_id": order_id}
        _log("POST", f"/api/v1/orders/{order_id}/photo", req={"filename": filename}, resp=resp)
        return resp

    async def get_order(self, order_id: int) -> dict:
        upload_time = MockBackendClient._photo_upload_times.get(order_id)
        parsing_done = (
            upload_time is not None
            and (time.monotonic() - upload_time) >= MockBackendClient._PARSE_DELAY
        )

        if parsing_done:
            resp = {
                "id": order_id,
                "status": "PENDING",
                "creator_id": 1,
                "order_info": _MOCK_ITEMS,
                "participants": [],
                "created_at": "2024-01-15T12:00:00Z",
            }
        elif upload_time is not None:
            # Photo uploaded but Claude is still "parsing"
            elapsed = time.monotonic() - upload_time
            resp = {
                "id": order_id,
                "status": "DRAFT",
                "creator_id": 1,
                "order_info": [],
                "participants": [],
                "created_at": "2024-01-15T12:00:00Z",
                "_mock_parsing_progress": f"{elapsed:.1f}s / {MockBackendClient._PARSE_DELAY}s",
            }
        else:
            resp = MockBackendClient._orders.get(
                order_id,
                {
                    "id": order_id,
                    "status": "DRAFT",
                    "creator_id": 1,
                    "order_info": [],
                    "participants": [],
                    "created_at": "2024-01-15T12:00:00Z",
                },
            )
        _log("GET", f"/api/v1/orders/{order_id}", resp=resp)
        return resp

    # Pre-seeded users matching mock summary data
    _registered_users: dict[str, int] = {"petr": 987654321, "masha": 111222333}

    async def lookup_users(self, usernames: list[str]) -> list[dict]:
        result = [
            {"telegram_id": MockBackendClient._registered_users[u], "username": u}
            for u in usernames
            if u.lower() in MockBackendClient._registered_users
        ]
        _log("POST", "/api/v1/users/lookup", req={"usernames": usernames}, resp=result)
        return result

    async def add_participants(self, order_id: int, telegram_ids: list[int]) -> dict:
        resp = {"added": len(telegram_ids)}
        _log(
            "POST",
            f"/api/v1/orders/{order_id}/participants",
            req={"telegram_ids": telegram_ids},
            resp=resp,
        )
        return resp

    async def get_order_summary(self, order_id: int) -> dict:
        resp = {"order_id": order_id, **_MOCK_SUMMARY}
        _log("GET", f"/api/v1/orders/{order_id}/summary", resp=resp)
        return resp
