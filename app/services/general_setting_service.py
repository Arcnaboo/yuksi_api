from typing import Any, Dict, Optional, Tuple
from app.utils.database import db_cursor

def create_general_setting(data: Dict[str, Any]) -> Optional[str]:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM general_settings")
        count = cur.fetchone()[0]

        if count > 0:
            return "Only one general setting record is allowed"

        cur.execute("""
            INSERT INTO general_settings (app_name, app_title, keywords, email, whatsapp, address, map_embed_code, logo_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["app_name"], data["app_title"], data["keywords"], data["email"],
            data["whatsapp"], data["address"], data["map_embed_code"], data.get("logo_path")
        ))
    return None

def get_general_setting() -> Optional[Dict[str, Any]]:
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM general_settings LIMIT 1")
        row = cur.fetchone()
        return row

def update_general_setting(gs_id: str, fields: Dict[str, Any]) -> Optional[str]:
    if not fields:
        return "No fields to update"

    set_query = ", ".join([f"{k} = %s" for k in fields.keys()])
    values = list(fields.values())
    values.append(gs_id)

    with db_cursor() as cur:
        cur.execute(f"UPDATE general_settings SET {set_query} WHERE id = %s", values)
    return None
