from pydantic import BaseModel


class Split(BaseModel):
    user_id: int
    quantity: float


class OrderItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: float
    splits: list[Split] = []


class ParticipantInfo(BaseModel):
    user_id: int
    status: str


class OrderResponse(BaseModel):
    id: int
    status: str
    creator_id: int
    order_info: list[OrderItem]
    participants: list[ParticipantInfo]
    created_at: str

    model_config = {"from_attributes": True}


class AddParticipantsRequest(BaseModel):
    telegram_ids: list[int]


class ItemSelection(BaseModel):
    item_id: int
    quantity: float


class SelectItemsRequest(BaseModel):
    selections: list[ItemSelection]


class SelectItemsResponse(BaseModel):
    your_total: float
    order_status: str


class ParticipantSummary(BaseModel):
    user_id: int
    username: str | None
    amount_due: float
    status: str


class OrderSummaryResponse(BaseModel):
    order_id: int
    participants: list[ParticipantSummary]
    payment_methods: dict
