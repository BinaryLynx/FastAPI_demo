from motor import motor_asyncio
from src.config import DB_URI

client = motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client.NotificationDB
user_collection = db.user
