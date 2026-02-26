from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.base import get_session
from app.models.user import User
from app.schemas.auth import TelegramAuthRequest, TokenResponse
from app.services.auth import verify_telegram_init_data

router = APIRouter()


@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(
    body: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    try:
        parsed = verify_telegram_init_data(body.init_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    import json

    user_data = json.loads(parsed.get("user", "{}"))
    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user in initData")

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))
