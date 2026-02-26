from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    payment_methods: dict

    model_config = {"from_attributes": True}


class UpdatePaymentMethodsRequest(BaseModel):
    payment_methods: dict
