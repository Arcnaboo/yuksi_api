from typing import Any, Dict, Tuple, Optional, List
from app.utils.database import db_cursor

# CREATE
async def create_subsection(title: str, content_type: str, show_in_menu: bool, show_in_footer: bool, content: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO subsections (title, content_type, show_in_menu, show_in_footer, content)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at;
                """,
                (title, content_type, show_in_menu, show_in_footer, content)
            )
            row = cur.fetchone()
            return {
                "id": row["id"] if isinstance(row, dict) else row[0],
                "created_at": row["created_at"] if isinstance(row, dict) else row[1]
            }, None
    except Exception as e:
        return None, str(e)

# GET ALL
async def get_all_subsections(limit: int = 100, offset: int = 0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at, updated_at
                FROM subsections
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
                """,
                (limit, offset)
            )
            rows = cur.fetchall()
            items = []
            for r in rows:
                # Hem dict cursor hem tuple desteği
                if isinstance(r, dict):
                    items.append(r)
                else:
                    items.append({
                        "id": r[0],
                        "title": r[1],
                        "content_type": r[2],
                        "show_in_menu": r[3],
                        "show_in_footer": r[4],
                        "content": r[5],
                        "created_at": r[6],
                        "updated_at": r[7],
                    })
            return items, None
    except Exception as e:
        return None, str(e)


# GET BY ID
async def get_subsection_by_id(sub_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, title, content_type, show_in_menu, show_in_footer, content, created_at, updated_at FROM subsections WHERE id = %s LIMIT 1;",
                (sub_id,)
            )
            row = cur.fetchone()

            if not row:
                return None, None  # Not found

            # ✅ Hem dict hem tuple güvenli dönüşüm
            if isinstance(row, dict):
                return row, None
            else:
                return {
                    "id": row[0],
                    "title": row[1],
                    "content_type": row[2],
                    "show_in_menu": row[3],
                    "show_in_footer": row[4],
                    "content": row[5],
                    "created_at": row[6],
                    "updated_at": row[7],
                }, None

    except Exception as e:
        return None, str(e)

# UPDATE
async def update_subsection(sub_id: int, fields: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    try:
        set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
        values = list(fields.values())
        values.append(sub_id)

        with db_cursor() as cur:
            cur.execute(
                f"""
                UPDATE subsections
                SET {set_clause}, updated_at = NOW()
                WHERE id = %s;
                """,
                tuple(values)
            )
        return True, None
    except Exception as e:
        return False, str(e)

# DELETE
async def delete_subsection(sub_id: int) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM subsections WHERE id = %s;", (sub_id,))
        return None
    except Exception as e:
        return str(e)
