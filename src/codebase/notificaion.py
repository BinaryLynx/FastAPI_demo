import asyncio
from typing import Annotated
from bson.objectid import ObjectId  # from bson import ObjectId
from fastapi import (
    Depends,
    status,
    HTTPException,
)
from datetime import datetime
import aiosmtplib
from email.message import EmailMessage

from src import schemas
from src.database import user_collection
from src.config import settings


class Notification:
    async def create(request: schemas.NotificationBase):
        if request.key.value == schemas.NotificationKey.registration.value:
            await Notification.send(request)
        elif (
            request.key.value == schemas.NotificationKey.new_message.value
            or request.key.value == schemas.NotificationKey.new_post.value
        ):
            await Notification.write_db_log(request)
        else:
            # Не собрано в таск группу, чтобы если ошибка возникла на этапе отправки - запись в бд не создавалась.
            await Notification.send(request)
            await Notification.write_db_log(request)
        return {"success": True}

    async def send(request: schemas.NotificationBase):
        message = EmailMessage()
        message["From"] = settings.SMTP_LOGIN
        message["To"] = request.target_mail
        message["Subject"] = request.key.value
        message.set_content(request.key.value)
        try:
            async with aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, use_tls=True
            ) as mail_server:
                await mail_server.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
                await mail_server.send_message(message)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Ошибка отправки сообщения! Проверьте корректность почты получателя и другие данные",
            )
        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Ошибка отправки сообщения! Проверьте корректность почты отправителя и другие данные",
            )
        except aiosmtplib.SMTPAuthenticationError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Указан неверный логин/пароль отправителя!",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера. Ошибка подключения к сервису отправки писем",
            )
        async with asyncio.TaskGroup() as tg:
            tg.create_task(User.check_create_new(request.target_mail))
            tg.create_task(User.check_create_new(settings.SMTP_LOGIN))

    async def write_db_log(request: schemas.NotificationBase):
        user = await User.find({"email": settings.SMTP_LOGIN})
        await User.check_notification_limit(user)
        await user_collection.update_one(
            {"email": settings.SMTP_LOGIN},
            {
                "$addToSet": {
                    "notifications": {
                        "_id": ObjectId(),
                        "timestamp": datetime.utcnow(),
                        "is_new": True,
                        "user_mail": settings.SMTP_LOGIN,
                        "key": request.key.value,
                        "target_mail": request.target_mail,
                        "data": request.data,
                    }
                }
            },
        )

    async def mark_read(request: schemas.MarkReadRequest):
        update_result = await user_collection.update_one(
            {
                "_id": ObjectId(request.user_id),
                "notifications._id": ObjectId(request.notification_id),
            },
            {"$set": {"notifications.$.is_new": False}},
        )
        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нотификация по данным запроса не найдена!",
            )
        return {"success": True}


class User:
    notification_limit = 5

    async def check_create_new(email: str):
        user = await user_collection.find_one({"email": email})
        if user is None:
            res = await user_collection.insert_one({"email": email})
            return res.inserted_id
        else:
            return user["_id"]

    async def get_notifications(request: schemas.NotificationsRequest):
        user = await User.find({"user_mail": request.user_mail})
        return {
            "success": True,
            "data": {
                "elements": len(user["notifications"]),
                "new": len(
                    [el for el in user["notifications"] if el["is_new"] == True]
                ),
                "request": request,
                "list": user["notifications"],
            },
        }

    async def find(query: dict):
        user = await user_collection.find_one(query)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Не найден пользователь с указаными данными!",
            )
        return user

    async def check_notification_limit(user):
        if (user["notifications"] is not None) and (
            len(user["notifications"]) >= User.notification_limit
        ):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Не возможно добавить больше записей нотификаций для данного пользователя!",
            )
