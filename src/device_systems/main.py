from fastapi import FastAPI

from device_systems.routes.user_routes import router as user_router

app = FastAPI(title="device_systems", version="1.0")


app.include_router(user_router)
