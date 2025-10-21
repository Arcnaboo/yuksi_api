from app.utils.database import db_cursor
from typing import Dict, Any, Optional, List, Tuple

async def create_package(carrier: str, days: int, price: float) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO packages (carrier, days, price)
                VALUES (%s, %s, %s)
                RETURNING id, carrier, days, price, created_at
            """, (carrier, days, price))
            return cur.fetchone(), None
    except Exception as e:
        return None, str(e)

async def get_all_packages() -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("SELECT * FROM packages ORDER BY created_at DESC")
            return cur.fetchall(), None
    except Exception as e:
        return None, str(e)

async def update_package(pkg_id: str, fields: Dict[str, Any]) -> Optional[str]:
    try:
        set_clause = ", ".join([f"{k}=%s" for k in fields.keys()])
        values = list(fields.values()) + [pkg_id]
        with db_cursor() as cur:
            cur.execute(f"UPDATE packages SET {set_clause} WHERE id=%s", values)
        return None
    except Exception as e:
        return str(e)

async def delete_package(pkg_id: str) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM packages WHERE id=%s", (pkg_id,))
        return None
    except Exception as e:
        return str(e)
