from app.utils.database import db_cursor

async def create_or_update_price(data):
    try:
        with db_cursor() as cur:
            # Eğer restoranın kaydı varsa güncelle, yoksa oluştur
            cur.execute("""
                INSERT INTO restaurant_package_prices (restaurant_id, unit_price, min_package, max_package, note)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (restaurant_id)
                DO UPDATE SET
                    unit_price = EXCLUDED.unit_price,
                    min_package = EXCLUDED.min_package,
                    max_package = EXCLUDED.max_package,
                    note = EXCLUDED.note,
                    updated_at = now()
                RETURNING id;
            """, (
                data["restaurant_id"], data["unit_price"],
                data.get("min_package"), data.get("max_package"),
                data.get("note")
            ))
            result = cur.fetchone()
        return True, {"id": result[0]}
    except Exception as e:
        return False, str(e)


async def list_prices():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT p.id, r.name AS restaurant_name, r.email, p.unit_price,
                       p.min_package, p.max_package, p.note, p.updated_at
                FROM restaurant_package_prices p
                JOIN restaurants r ON r.id = p.restaurant_id
                ORDER BY p.updated_at DESC;
            """)
            data = cur.fetchall()
        return True, data
    except Exception as e:
        return False, str(e)
