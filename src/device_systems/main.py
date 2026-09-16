from fastapi import FastAPI

from device_systems.database.connection import Base, engine
from device_systems.models.user_model import User
from device_systems.routes.user_routes import router as rutas_usuarios

# Crear las tablas que todavia no existan en SQLite.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="device_systems API",
    description="API REST con SQLAlchemy para la gestion de usuarios.",
    version="3.0.0",
    contact={
        "name": "Jhon Ricardo Rios Cuervo",
        "email": "jhonri.0614@gmail.com",
    },
)


app.include_router(rutas_usuarios)
