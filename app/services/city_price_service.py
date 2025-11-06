from app.utils.database import db_cursor

TABLE = "city_prices"


async def list_city_prices():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"SELECT * FROM {TABLE} ORDER BY created_at DESC;")
            return cur.fetchall(), None
    except Exception as e:
        return None, str(e)


async def get_city_price(id: str):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"SELECT * FROM {TABLE} WHERE id = %s;", (id,))
            return cur.fetchone(), None
    except Exception as e:
        return None, str(e)


async def create_city_price(route_name, country_id, state_id, city_id,
                            courier_price, minivan_price,
                            panelvan_price, kamyonet_price, kamyon_price):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"""
                INSERT INTO {TABLE}
                (id, route_name, country_id, state_id, city_id, 
                 courier_price, minivan_price, panelvan_price, kamyonet_price, kamyon_price)
                VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (route_name, country_id, state_id, city_id,
                  courier_price, minivan_price,
                  panelvan_price, kamyonet_price, kamyon_price))

            return cur.fetchone(), None
    except Exception as e:
        return None, str(e)


async def update_city_price(id: str, route_name, country_id, state_id, city_id,
                            courier_price, minivan_price,
                            panelvan_price, kamyonet_price, kamyon_price):
    try:
        with db_cursor() as cur:
            cur.execute(f"""
                UPDATE {TABLE}
                SET route_name=%s, country_id=%s, state_id=%s, city_id=%s,
                    courier_price=%s, minivan_price=%s, panelvan_price=%s,
                    kamyonet_price=%s, kamyon_price=%s
                WHERE id=%s;
            """, (route_name, country_id, state_id, city_id,
                  courier_price, minivan_price,
                  panelvan_price, kamyonet_price, kamyon_price, id))
            return True, None
    except Exception as e:
        return False, str(e)


async def delete_city_price(id: str):
    try:
        with db_cursor() as cur:
            cur.execute(f"DELETE FROM {TABLE} WHERE id=%s RETURNING id;", (id,))
            if not cur.fetchone():
                return False, "Record not found"
            return True, None
    except Exception as e:
        return False, str(e)
