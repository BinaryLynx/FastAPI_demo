from pydantic import BaseModel
from typing import Annotated, Any, List
from fastapi import Body, Path, Query
from enum import Enum
from datetime import datetime


class ResponseBase(BaseModel):
    success: bool


class NotificationKey(str, Enum):
    registration = "registration"
    new_message = "new_message"
    new_post = "new_post"
    new_login = "new_login"


class NotificationBase(BaseModel):
    user_mail: Annotated[str, Body(max_length=24)]
    target_mail: Annotated[str, Body(max_length=24)]
    key: NotificationKey
    data: dict | None = None


class Notification(ResponseBase, NotificationBase):
    id: str
    timestamp: datetime
    is_new: bool


class NotificationsRequest(BaseModel):
    user_mail: Annotated[str, Path(max_length=24)]
    skip: int
    limit: int


class NotificationResponseData(BaseModel):
    elements: int
    new: int
    request: NotificationsRequest
    list: List[Notification]


class NotificationsResponse(ResponseBase):
    data: NotificationResponseData


class MarkReadRequest(BaseModel):
    user_id: Annotated[str, Body(max_length=24)]
    notification_id: Annotated[str, Body(max_length=1000)]
