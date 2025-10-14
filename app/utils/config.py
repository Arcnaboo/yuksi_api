import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import Tuple
from pathlib import Path
from dotenv import load_dotenv

_APP_DIR = Path(__file__).resolve().parents[2]  
_DOTENV_PATH = _APP_DIR / ".env"
print(f"[BOOT] dotenv path: {_DOTENV_PATH} exists={_DOTENV_PATH.exists()}")
if _DOTENV_PATH.exists():
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)  


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
    dev => LOCAL_DATABASE_URL (yoksa DATABASE_URL fallback)
    prod => DATABASE_URL (+ sslmode=require ekler)
    """
    env = get_app_env()
    if env == "dev":
        db_url = os.getenv("LOCAL_DATABASE_URL") or os.getenv("DATABASE_URL", "postgresql://yuksi:yuksi@localhost:5432/yuksi")
        # Neon için SSL ekle
        if "neon.tech" in db_url:
            return _with_sslmode_require(db_url)
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

def get_filestack_api_key() -> str:
    """Filestack API key alır, yoksa hata fırlatır."""
    print("[BOOT] Filestack API Key alınıyor...")
    print(f"[BOOT] FILESTACK_API_KEY={'set' if os.getenv('FILESTACK_API_KEY') else 'NOT set'}")
    key = os.getenv("FILESTACK_API_KEY", "")
    if not key:
        print("[BOOT][WARNING] FILESTACK_API_KEY not set, using dummy key")
        return "dummy-key-for-testing"
    return key



APP_ENV = get_app_env()
DATABASE_URL = get_database_url()
JWT_SECRET_KEY, JWT_ALGORITHM = get_jwt_settings()