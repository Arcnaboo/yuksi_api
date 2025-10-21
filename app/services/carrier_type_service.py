from uuid import UUID
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services.file_service import get_public_url

# === CREATE ===
async def create_carrier_type(data):
    query = """
        INSERT INTO carrier_types (name, start_km, start_price, km_price, image_file_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
    """
    row = await fetch_one(
        query,
        data.name,
        data.start_km,
        data.start_price,
        data.km_price,
        str(data.image_file_id) if data.image_file_id else None,
    )
    return row["id"]


# === LIST ===
async def list_carrier_types():
    query = """
        SELECT ct.id, ct.name, ct.start_km, ct.start_price, ct.km_price, ct.created_at, f.key
        FROM carrier_types ct
        LEFT JOIN files f ON f.id = ct.image_file_id;
    """
    rows = await fetch_all(query)
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


# === DELETE ===
async def delete_carrier_type(id: UUID):
    query = "DELETE FROM carrier_types WHERE id = $1;"
    await execute(query, str(id))


# === UPDATE ===
async def update_carrier_type(id: str, data):
    fields = []
    values = []

    if data.name is not None:
        fields.append("name = ${}".format(len(values) + 1))
        values.append(data.name)
    if data.start_km is not None:
        fields.append("start_km = ${}".format(len(values) + 1))
        values.append(data.start_km)
    if data.start_price is not None:
        fields.append("start_price = ${}".format(len(values) + 1))
        values.append(data.start_price)
    if data.km_price is not None:
        fields.append("km_price = ${}".format(len(values) + 1))
        values.append(data.km_price)
    if data.image_file_id is not None:
        fields.append("image_file_id = ${}".format(len(values) + 1))
        values.append(str(data.image_file_id))

    if not fields:
        return "No fields to update"

    # id parametresi eklenir
    values.append(str(id))
    param_index = len(values)
    query = f"UPDATE carrier_types SET {', '.join(fields)} WHERE id = ${param_index}"
    await execute(query, *values)
    return None
