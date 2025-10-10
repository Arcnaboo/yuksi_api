from contextlib import contextmanager
from typing import Optional

import psycopg2
import psycopg2.extras

# Her zaman fonksiyon üzerinden al: env/APP_ENV mantığını içerir
from .config import get_database_url


def get_connection():
    """Ham psycopg2 bağlantısı döndürür."""
    return psycopg2.connect(get_database_url())


def get_db():
    """
    FastAPI dependency: route içinde Depends(get_db) ile kullan.
    Bağlantıyı yield eder, sonunda kapatır.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def db_cursor(dict_cursor: bool = False):
    """
    with db_cursor() as cur:                -> normal cursor
    with db_cursor(dict_cursor=True) as cur -> RealDictCursor (dict döner)
    """
    conn = get_connection()
    cur = None
    try:
        if dict_cursor:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        conn.close()
