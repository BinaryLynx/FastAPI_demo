from fastapi import FastAPI
from src.routers import notification

app = FastAPI()
app.include_router(notification.router)


@app.get("/")
def go_reroute_yourslef():
    return "visit '/docs' to view available routes"
