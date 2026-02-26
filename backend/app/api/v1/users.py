from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_session
from app.models.user import User
from app.schemas.user import UpdatePaymentMethodsRequest, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me/payment-methods", response_model=UserResponse)
async def update_payment_methods(
    body: UpdatePaymentMethodsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    current_user.payment_methods = {**current_user.payment_methods, **body.payment_methods}
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user
