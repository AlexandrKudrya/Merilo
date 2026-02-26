import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_telegram_invalid_init_data(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/telegram", json={"init_data": "invalid"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
