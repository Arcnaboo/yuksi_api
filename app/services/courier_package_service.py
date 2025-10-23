from typing import Dict, Any
from app.utils.database import db_cursor


# ✅ CREATE
async def create_package(data: dict) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO courier_packages (package_name, description, price, duration_days)
                VALUES (%(package_name)s, %(description)s, %(price)s, %(duration_days)s)
                RETURNING id;
            """, data)
            row = cur.fetchone()
        return {"success": True, "message": "Package created successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ LIST
async def list_packages(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    id AS packageId,
                    package_name AS packageName,
                    description AS description,
                    price AS price,
                    duration_days AS durationDays
                FROM courier_packages
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            rows = cur.fetchall() or []
        return {"success": True, "message": "Packages fetched successfully", "data": rows}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


# ✅ GET BY ID
async def get_package_by_id(package_id: int) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    id AS packageId,
                    package_name AS packageName,
                    description AS description,
                    price AS price,
                    duration_days AS durationDays
                FROM courier_packages
                WHERE id = %s;
            """, (package_id,))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Package not found", "data": {}}
        return {"success": True, "message": "Package fetched", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ UPDATE
async def update_package(package_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not fields:
            return {"success": False, "message": "No fields to update", "data": {}}

        set_clause = ", ".join([f"{k} = %({k})s" for k in fields.keys()])
        params = {**fields, "id": package_id}

        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"""
                UPDATE courier_packages
                SET {set_clause}
                WHERE id = %(id)s
                RETURNING id;
            """, params)
            row = cur.fetchone()

        if not row:
            return {"success": False, "message": "Package not found", "data": {}}
        return {"success": True, "message": "Package updated successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ DELETE
async def delete_package(package_id: int) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                DELETE FROM courier_packages
                WHERE id = %s
                RETURNING id;
            """, (package_id,))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Package not found", "data": {}}
        return {"success": True, "message": "Package deleted successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
