from app.utils.database import db_cursor
from app.services.file_service import get_public_url
from uuid import UUID

async def create_carrier_type(data):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            INSERT INTO carrier_types (name, start_km, start_price, km_price, image_file_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (data.name, data.start_km, data.start_price, data.km_price, str(data.image_file_id) if data.image_file_id else None))
        row = cur.fetchone()
        return row["id"]

async def list_carrier_types():
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT ct.id, ct.name, ct.start_km, ct.start_price, ct.km_price, ct.created_at, f.image_url, f.key
            FROM carrier_types ct
            LEFT JOIN files f ON f.id = ct.image_file_id;
        """)
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "name": r["name"],
                "start_km": r["start_km"],
                "start_price": r["start_price"],
                "km_price": r["km_price"],
                "image_url": get_public_url(r["key"]) if r["key"] else None,
                "created_at": r["created_at"]
            })
        return result

async def delete_carrier_type(id: UUID):
    with db_cursor() as cur:
        cur.execute("DELETE FROM carrier_types WHERE id = %s;", (str(id),))

async def update_carrier_type(id: str, data):
    with db_cursor() as cur:
        # Dinamik UPDATE (yalnızca gönderilen alanlar güncellensin)
        fields = []
        values = []

        if data.name is not None:
            fields.append("name = %s")
            values.append(data.name)
        if data.start_km is not None:
            fields.append("start_km = %s")
            values.append(data.start_km)
        if data.start_price is not None:
            fields.append("start_price = %s")
            values.append(data.start_price)
        if data.km_price is not None:
            fields.append("km_price = %s")
            values.append(data.km_price)
        if data.image_file_id is not None:
            fields.append("image_file_id = %s")
            values.append(str(data.image_file_id))

        if not fields:
            return "No fields to update"

        values.append(str(id))
        query = f"UPDATE carrier_types SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        return None
