from app.utils.database import db_cursor

# ✅ Tüm Paketleri Listele
async def list_company_packages():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT id, carrier_km, requested_km, price,is_active, created_at
                FROM company_packages
                ORDER BY created_at DESC;
            """)
            rows = cur.fetchall()
        return rows, None
    except Exception as e:
        return None, str(e)


# ✅ Paket Detayı
async def get_company_package(id: str):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT id, carrier_km, requested_km, price, is_active, created_at
                FROM company_packages
                WHERE id = %s;
            """, (id,))
            row = cur.fetchone()
        return row, None
    except Exception as e:
        return None, str(e)


# ✅ Paket Oluştur
async def create_company_package(carrier_km: int, requested_km: int, price: float):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO company_packages
                (carrier_km, requested_km, price)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (carrier_km, requested_km, price))
            row = cur.fetchone()
        return row, None
    except Exception as e:
        return None, str(e)


# ✅ Paket Güncelle

async def update_company_package(id: str, carrier_km: int, requested_km: int, price: float):
    try:
        with db_cursor() as cur:
            cur.execute("""
                UPDATE company_packages
                SET carrier_km = %s,
                    requested_km = %s,
                    price = %s
                WHERE id = %s
                RETURNING id;
            """, (carrier_km, requested_km, price, id))
            updated = cur.fetchone()

        if not updated:
            return False, "Record not found"

        return True, None

    except Exception as e:
        return False, str(e)



# ✅ Paket Sil
async def delete_company_package(id: str):
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM company_packages WHERE id = %s RETURNING id;", (id,))
            deleted = cur.fetchone()

        if not deleted:
            return False, "Record not found"

        return True, None

    except Exception as e:
        return False, str(e)
