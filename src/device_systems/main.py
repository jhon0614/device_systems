import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from device_systems.auth.auth_routes import router as auth_router
from device_systems.middlewares.request_middleware import limiter, request_middleware
from device_systems.routes.device_routes import router as device_router
from device_systems.routes.loan_routes import router as loan_router
from device_systems.routes.user_routes import router as rutas_usuarios

app = FastAPI(
    title="device_systems API",
    description="API REST segura para gestión de usuarios, dispositivos y préstamos.",
    version="3.0.0",
    contact={
        "name": "Jhon Ricardo Rios Cuervo",
        "email": "jhonri.0614@gmail.com",
    },
)

logging.basicConfig(level=logging.INFO)

# Permitir únicamente los clientes locales definidos para desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar el control global de límites y sus respuestas HTTP 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.middleware("http")(request_middleware)

app.include_router(auth_router)
app.include_router(rutas_usuarios)
app.include_router(device_router)
app.include_router(loan_router)
