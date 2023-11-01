from motor import motor_asyncio
from src.config import settings

client = motor_asyncio.AsyncIOMotorClient(settings.DB_URI)
db = client.NotificationDB
user_collection = db.user
