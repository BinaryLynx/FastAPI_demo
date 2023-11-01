from typing import Annotated
from fastapi import APIRouter, Depends, status

from src import schemas
from src.codebase.notificaion import Notification, User


router = APIRouter(tags=["Notifications"])  # prefix="/notification"


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseBase
)
async def create_notification(request: schemas.NotificationBase):
    result = await Notification.create(request)
    return result


@router.get("/list", response_model=schemas.NotificationsResponse)
async def get_user_notifications(
    request: Annotated[schemas.NotificationsRequest, Depends()]
):
    result = await User.get_notifications(request)
    return result


@router.post("/read", response_model=schemas.ResponseBase)
async def notification_mark_read(request: schemas.MarkReadRequest):
    result = await Notification.mark_read(request)
    return result
