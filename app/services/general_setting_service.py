from typing import Any, Dict, Optional
from app.utils.database_async import fetch_one, execute


# === CREATE GENERAL SETTING ===
async def create_general_setting(data: Dict[str, Any]) -> Optional[str]:
    # Var olan kayıt var mı kontrol et
    row = await fetch_one("SELECT COUNT(*) AS count FROM general_settings;")
    if row and row["count"] > 0:
        return "Only one general setting record is allowed"

    query = """
        INSERT INTO general_settings
        (app_name, app_title, keywords, email, whatsapp, address, map_embed_code, logo_path)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
    """
    await execute(
        query,
        data["app_name"],
        data["app_title"],
        data["keywords"],
        data["email"],
        data["whatsapp"],
        data["address"],
        data["map_embed_code"],
        data.get("logo_path"),
    )
    return None


# === GET GENERAL SETTING ===
async def get_general_setting() -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM general_settings LIMIT 1;"
    row = await fetch_one(query)
    return dict(row) if row else None


# === UPDATE GENERAL SETTING ===
async def update_general_setting(gs_id: str, fields: Dict[str, Any]) -> Optional[str]:
    if not fields:
        return "No fields to update"

    # Dinamik SET kısmı oluştur
    set_parts = []
    values = []
    i = 1
    for k, v in fields.items():
        set_parts.append(f"{k} = ${i}")
        values.append(v)
        i += 1

    query = f"UPDATE general_settings SET {', '.join(set_parts)} WHERE id = ${i};"
    values.append(gs_id)

    await execute(query, *values)
    return None
