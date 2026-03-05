from abc import ABC, abstractmethod
from io import BytesIO


class AbstractBackendClient(ABC):
    def __init__(self, token: str) -> None:
        self._token = token

    @classmethod
    @abstractmethod
    async def authenticate(cls, init_data: str) -> "AbstractBackendClient":
        """Exchange Telegram initData for an authenticated client instance."""

    @abstractmethod
    async def create_order(self) -> dict:
        """POST /orders — create a new order in DRAFT status."""

    @abstractmethod
    async def upload_photo(
        self, order_id: int, photo: BytesIO, filename: str = "receipt.jpg"
    ) -> dict:
        """POST /orders/{id}/photo — upload receipt photo, triggers Claude parsing."""

    @abstractmethod
    async def add_participants(self, order_id: int, telegram_ids: list[int]) -> dict:
        """POST /orders/{id}/participants — add participants by telegram_id."""

    @abstractmethod
    async def get_order(self, order_id: int) -> dict:
        """GET /orders/{id} — get order with status and parsed items."""

    @abstractmethod
    async def lookup_users(self, usernames: list[str]) -> list[dict]:
        """POST /users/lookup — find registered users by username list.

        Returns only users found in the system. Each item: {"telegram_id": int, "username": str}.
        """

    @abstractmethod
    async def get_order_summary(self, order_id: int) -> dict:
        """GET /orders/{id}/summary — get final breakdown of who owes what."""
