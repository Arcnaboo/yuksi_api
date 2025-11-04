from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.database import db_cursor

TABLE = "extra_services"


# ✅ Listele
async def list_services():
    rows = await fetch_all(f"SELECT * FROM {TABLE} ORDER BY created_at DESC;")
    return rows, None


# ✅ Tek kayıt
async def get_service(id: str):
    row = await fetch_one(
        f"SELECT * FROM {TABLE} WHERE id=$1;",
        id
    )
    return row, None


# ✅ Oluştur
async def create_service(carrier_type: str, service_name: str, price: float):
    row = await fetch_one(
        f"""
        INSERT INTO {TABLE} (carrier_type, service_name, price)
        VALUES ($1, $2, $3)
        RETURNING id;
        """,
        carrier_type, service_name, price
    )
    return row, None


# ✅ Güncelle
async def update_service(id: str, carrier_type: str = None, service_name: str = None, price: float = None):
    try:
        with db_cursor() as cur:
            cur.execute("SELECT carrier_type, service_name, price FROM extra_services WHERE id=%s;", (id,))
            existing = cur.fetchone()
            if not existing:
                return False, "Record not found"

            carrier_type = carrier_type if carrier_type is not None else existing[0]
            service_name = service_name if service_name is not None else existing[1]
            price = price if price is not None else existing[2]

            cur.execute("""
                UPDATE extra_services
                SET carrier_type = %s,
                    service_name = %s,
                    price = %s
                WHERE id = %s
                RETURNING id;
            """, (carrier_type, service_name, price, id))

            updated = cur.fetchone()

        return (True, None) if updated else (False, "Record not found")
    except Exception as e:
        return False, str(e)



# ✅ Sil
async def delete_service(id: str):
    row = await fetch_one(
        f"DELETE FROM {TABLE} WHERE id=$1 RETURNING id;",
        id
    )

    if not row:
        return False, "Record not found"

    return True, None
