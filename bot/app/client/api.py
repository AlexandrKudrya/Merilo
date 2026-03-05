import logging
from io import BytesIO

import httpx

from app.client.base import AbstractBackendClient
from app.config import settings

logger = logging.getLogger(__name__)


async def _log_request(request: httpx.Request) -> None:
    logger.info("→ %s %s", request.method, request.url)


async def _log_response(response: httpx.Response) -> None:
    await response.aread()
    logger.info("← %s %s %s", response.status_code, response.request.method, response.request.url)
    logger.debug("   body: %s", response.text[:500])


def _make_client(**kwargs: object) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        event_hooks={"request": [_log_request], "response": [_log_response]},
        **kwargs,  # type: ignore[arg-type]
    )


class BackendClient(AbstractBackendClient):
    """Real HTTP client for communicating with the FastAPI backend."""

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"}

    @classmethod
    async def authenticate(cls, init_data: str) -> "BackendClient":
        async with _make_client() as client:
            response = await client.post(
                f"{settings.backend_url}/api/v1/auth/telegram",
                json={"init_data": init_data},
            )
            response.raise_for_status()
            token = response.json()["access_token"]
        return cls(token)

    async def create_order(self) -> dict:
        async with _make_client() as client:
            response = await client.post(
                f"{settings.backend_url}/api/v1/orders",
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def upload_photo(
        self, order_id: int, photo: BytesIO, filename: str = "receipt.jpg"
    ) -> dict:
        async with _make_client() as client:
            response = await client.post(
                f"{settings.backend_url}/api/v1/orders/{order_id}/photo",
                headers=self._headers,
                files={"file": (filename, photo, "image/jpeg")},
            )
            response.raise_for_status()
            return response.json()

    async def add_participants(self, order_id: int, telegram_ids: list[int]) -> dict:
        async with _make_client() as client:
            response = await client.post(
                f"{settings.backend_url}/api/v1/orders/{order_id}/participants",
                headers=self._headers,
                json={"telegram_ids": telegram_ids},
            )
            response.raise_for_status()
            return response.json()

    async def get_order(self, order_id: int) -> dict:
        async with _make_client() as client:
            response = await client.get(
                f"{settings.backend_url}/api/v1/orders/{order_id}",
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def lookup_users(self, usernames: list[str]) -> list[dict]:
        async with _make_client() as client:
            response = await client.post(
                f"{settings.backend_url}/api/v1/users/lookup",
                headers=self._headers,
                json={"usernames": usernames},
            )
            response.raise_for_status()
            return response.json()

    async def get_order_summary(self, order_id: int) -> dict:
        async with _make_client() as client:
            response = await client.get(
                f"{settings.backend_url}/api/v1/orders/{order_id}/summary",
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()
