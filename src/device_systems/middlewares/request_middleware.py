import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger("device_systems")
limiter = Limiter(key_func=get_remote_address)


async def request_middleware(request: Request, call_next):
    # Reutilizar el identificador recibido o generar uno para la petición.
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time

    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "%s %s - %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response
