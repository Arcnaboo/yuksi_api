from typing import Dict, Any, Optional, List, Tuple
from app.utils.database_async import fetch_one, fetch_all, execute


# === CREATE PACKAGE ===
async def create_package(carrier: str, days: int, price: float) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        query = """
            INSERT INTO packages (carrier, days, price)
            VALUES ($1, $2, $3)
            RETURNING id, carrier, days, price, created_at;
        """
        row = await fetch_one(query, carrier, days, price)
        return dict(row), None if row else (None, "Insert failed")
    except Exception as e:
        return None, str(e)


# === GET ALL PACKAGES ===
async def get_all_packages() -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        query = "SELECT * FROM packages ORDER BY created_at DESC;"
        rows = await fetch_all(query)
        return [dict(r) for r in rows], None if rows else (None, "No packages found")
    except Exception as e:
        return None, str(e)


# === UPDATE PACKAGE ===
async def update_package(pkg_id: str, fields: Dict[str, Any]) -> Optional[str]:
    try:
        if not fields:
            return "No fields to update"

        set_parts = []
        values = []
        i = 1
        for k, v in fields.items():
            set_parts.append(f"{k} = ${i}")
            values.append(v)
            i += 1

        query = f"UPDATE packages SET {', '.join(set_parts)} WHERE id = ${i};"
        values.append(pkg_id)
        await execute(query, *values)
        return None
    except Exception as e:
        return str(e)


# === DELETE PACKAGE ===
async def delete_package(pkg_id: str) -> Optional[str]:
    try:
        query = "DELETE FROM packages WHERE id = $1;"
        await execute(query, pkg_id)
        return None
    except Exception as e:
        return str(e)
