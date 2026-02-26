import httpx

from app.config import settings


class BackendClient:
    """HTTP client for communicating with the FastAPI backend."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._base_url = settings.backend_url

    async def get_order(self, order_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/api/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            response.raise_for_status()
            return response.json()

    async def get_order_summary(self, order_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._base_url}/api/v1/orders/{order_id}/summary",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            response.raise_for_status()
            return response.json()
