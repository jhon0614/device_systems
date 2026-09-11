from fastapi import FastAPI

from device_systems.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestion de usuarios de device_systems.",
    version="2.0.0",
    contact={
        "name": "Jhon Ricardo Rios Cuervo",
        "email": "jhonri.0614@gmail.com",
    },
)


app.include_router(user_router)
