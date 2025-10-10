# app/utils/config.py
import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import Tuple


def get_app_env() -> str:
    """dev | prod"""
    return os.getenv("APP_ENV", "dev").lower()

def _with_sslmode_require(db_url: str) -> str:
    """Render/Neon gibi yerlerde sslmode=require ekle (varsa dokunma)."""
    if not db_url:
        return db_url
    parsed = urlparse(db_url)
    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in qs:
        qs["sslmode"] = "require"
    new_query = urlencode(qs)
    return urlunparse(parsed._replace(query=new_query))

def get_database_url() -> str:
    """
    dev => LOCAL_DATABASE_URL (yoksa localhost fallback)
    prod => DATABASE_URL (+ sslmode=require ekler)
    """
    env = get_app_env()
    if env == "dev":
        db_url = os.getenv("LOCAL_DATABASE_URL", "postgresql://yuksi:yuksi@localhost:5432/yuksi")
        return db_url
    else:
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            raise RuntimeError("DATABASE_URL (prod) tanımlanmalı.")
        return _with_sslmode_require(db_url)

def get_jwt_settings() -> Tuple[str, str]:
    secret = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-min-32-chars")
    alg = os.getenv("JWT_ALGORITHM", "HS256")
    return secret, alg

def is_dev() -> bool:
    return get_app_env() == "dev"

def get_uvicorn_bind() -> Tuple[str, int]:
    """Opsiyonel: Uvicorn için host/port (Render süreçlerinde PORT env gelir)."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    return host, port



APP_ENV = get_app_env()
DATABASE_URL = get_database_url()
JWT_SECRET_KEY, JWT_ALGORITHM = get_jwt_settings()