from pydantic import BaseModel
from typing import Annotated, List
from pydantic import Field
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
    key: NotificationKey
    data: dict | None = None
    target_mail: Annotated[str, Field(max_length=50, pattern="^(.+)@(\S+)$")]


class Notification(NotificationBase):
    user_mail: Annotated[str, Field(max_length=50)]
    id: Annotated[str, Field(max_length=50)]
    timestamp: datetime
    is_new: bool


class NotificationsRequest(BaseModel):
    user_mail: Annotated[str, Field(max_length=50, pattern="^(.+)@(\S+)$")]
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
    user_id: Annotated[str, Field(max_length=24)]
    notification_id: Annotated[str, Field(max_length=50)]
