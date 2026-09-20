import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from . import config

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)):
    # config.API_KEYS se lee en cada request (no se importa por valor) para poder sobreescribirlo en tests.
    # Si API_KEYS está vacío, ninguna key es válida: la API falla cerrada en vez de quedar abierta.
    if not key or not any(secrets.compare_digest(key, valid) for valid in config.API_KEYS):
        raise HTTPException(status_code=401, detail="API key inválida o ausente")
