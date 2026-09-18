from fastapi import FastAPI

from device_systems.routes.device_routes import router as device_router
from device_systems.routes.loan_routes import router as loan_router
from device_systems.routes.user_routes import router as rutas_usuarios

app = FastAPI(
    title="device_systems API",
    description="API REST para gestionar usuarios, dispositivos y prestamos.",
    version="4.0.0",
    contact={
        "name": "Jhon Ricardo Rios Cuervo",
        "email": "jhonri.0614@gmail.com",
    },
)


app.include_router(rutas_usuarios)
app.include_router(device_router)
app.include_router(loan_router)
