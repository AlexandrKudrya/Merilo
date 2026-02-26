from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_session
from app.models.order import Order, OrderStatus, ParticipantStatus, UserOrder
from app.models.user import User
from app.schemas.order import (
    AddParticipantsRequest,
    OrderResponse,
    OrderSummaryResponse,
    SelectItemsRequest,
    SelectItemsResponse,
)
from app.services import claude as claude_service
from app.services import s3 as s3_service

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Order:
    order = Order(creator_id=current_user.id)
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    order_status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Order]:
    # TODO: also include orders where user is a participant
    q = select(Order).where(Order.creator_id == current_user.id)
    if order_status:
        q = q.where(Order.status == order_status)
    q = q.limit(limit).offset(offset)
    result = await session.execute(q)
    return list(result.scalars())


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Order:
    order = await _get_order_or_404(order_id, session)
    return order


@router.post("/{order_id}/photo", status_code=status.HTTP_202_ACCEPTED)
async def upload_photo(
    order_id: int,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    order = await _get_order_or_404(order_id, session)
    if order.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    file_bytes = await file.read()
    photo_url = await s3_service.upload_photo(file_bytes, file.content_type or "image/jpeg")
    order.photo_url = photo_url
    session.add(order)
    await session.commit()

    background_tasks.add_task(_parse_receipt_background, order_id, photo_url)
    return {"message": "parsing started", "order_id": order_id}


@router.post("/{order_id}/participants")
async def add_participants(
    order_id: int,
    body: AddParticipantsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    order = await _get_order_or_404(order_id, session)
    if order.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    for tg_id in body.telegram_ids:
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            session.add(UserOrder(user_id=user.id, order_id=order_id))

    await session.commit()
    return {"added": len(body.telegram_ids)}


@router.patch("/{order_id}/items", response_model=SelectItemsResponse)
async def select_items(
    order_id: int,
    body: SelectItemsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SelectItemsResponse:
    # TODO: implement item selection logic and auto-transition to ACTIVE
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
async def get_summary(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OrderSummaryResponse:
    # TODO: implement summary calculation
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.patch("/{order_id}/paid")
async def mark_paid(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    # TODO: mark participant as paid, auto-transition to FINISHED when all paid
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


async def _get_order_or_404(order_id: int, session: AsyncSession) -> Order:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


async def _parse_receipt_background(order_id: int, photo_url: str) -> None:
    """Background task: call Claude API to parse receipt and update order."""
    from app.db.base import async_session_factory

    async with async_session_factory() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            return

        try:
            parsed = await claude_service.parse_receipt(photo_url)
            items = [
                {
                    "id": i + 1,
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": item["quantity"],
                    "splits": [],
                }
                for i, item in enumerate(parsed.get("items", []))
            ]
            order.order_info = items
            order.status = OrderStatus.PENDING
        except Exception:
            order.status = OrderStatus.FAILED

        session.add(order)
        await session.commit()
