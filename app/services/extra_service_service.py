from app.utils.database_async import fetch_one,fetch_all, execute


TABLE = "extra_services"

async def list_services():
    rows = await fetch_all(f"""
        SELECT id, service_name, carrier_type, price, created_at
        FROM {TABLE}
        ORDER BY created_at DESC;
    """)
    return rows, None


async def get_service(id: str):
    row = await fetch_one(f"""
        SELECT id, service_name, carrier_type, price, created_at
        FROM {TABLE}
        WHERE id = $1;
    """, id)
    return row, None if row else ("Service not found", None)


async def create_service(service_name: str, carrier_type: str, price: float):
    row = await fetch_one(f"""
        INSERT INTO {TABLE} (service_name, carrier_type, price)
        VALUES ($1, $2, $3)
        RETURNING id;
    """, service_name, carrier_type, price)
    return row, None


async def update_service(id: str, fields: dict):
    if not fields:
        return False, "No fields to update"

    set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(fields))
    params = [id] + list(fields.values())

    updated = await fetch_one(f"""
        UPDATE {TABLE}
        SET {set_clause}
        WHERE id = $1
        RETURNING id;
    """, *params)

    if not updated:
        return False, "Service not found"

    return True, None


async def delete_service(id: str):
    deleted = await fetch_one(f"DELETE FROM {TABLE} WHERE id = $1 RETURNING id;", id)
    if not deleted:
        return False, "Service not found"
    return True, None
