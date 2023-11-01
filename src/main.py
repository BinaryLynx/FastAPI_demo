from fastapi import FastAPI

from src.routers import notification

app = FastAPI()
app.include_router(notification.router)
