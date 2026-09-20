from fastapi import Request
from fastapi.responses import JSONResponse
from limits import parse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from . import config

parse(config.RATE_LIMIT)  # falla al arrancar si RATE_LIMIT es inválido, no en la primera request

# El límite se lee en cada request (callable) para poder sobreescribirlo en tests.
# La key es request.client.host: detrás de un proxy hay que arrancar uvicorn con --proxy-headers.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[lambda: config.RATE_LIMIT],
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # Debe ser sync: SlowAPIMiddleware ignora los handlers async y usa el default.
    default = _rate_limit_exceeded_handler(request, exc)
    headers = {k: v for k, v in default.headers.items() if k.startswith(("retry-after", "x-ratelimit"))}
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes, intente nuevamente más tarde"},
        headers=headers,
    )
