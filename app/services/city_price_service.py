from app.utils.database import db_cursor
from typing import Any, Dict, List, Optional, Tuple


# Listeleme
async def list_city_prices():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT cp.id, cp.route_name,
                       c.name AS country_name,
                       s.name AS state_name,
                       ci.name AS city_name,
                       cp.courier_price, cp.minivan_price, cp.panelvan_price,
                       cp.kamyonet_price, cp.kamyon_price, cp.created_at
                FROM city_prices cp
                LEFT JOIN countries c ON cp.country_id = c.id
                LEFT JOIN states s ON cp.state_id = s.id
                LEFT JOIN cities ci ON cp.city_id = ci.id
                ORDER BY cp.id DESC;
            """)
            rows = cur.fetchall()
            return rows, None
    except Exception as e:
        return None, str(e)


# Tek kayıt getir
async def get_city_price(id: int):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT cp.id, cp.route_name,
                       c.name AS country_name,
                       s.name AS state_name,
                       ci.name AS city_name,
                       cp.courier_price, cp.minivan_price, cp.panelvan_price,
                       cp.kamyonet_price, cp.kamyon_price, cp.created_at
                FROM city_prices cp
                LEFT JOIN countries c ON cp.country_id = c.id
                LEFT JOIN states s ON cp.state_id = s.id
                LEFT JOIN cities ci ON cp.city_id = ci.id
                WHERE cp.id = %s;
            """, (id,))
            row = cur.fetchone()
            return row, None
    except Exception as e:
        return None, str(e)


# Yeni kayıt ekle
async def create_city_price(route_name: str, country_id: int, state_id: int, city_id: int,
                            courier_price: float, minivan_price: float,
                            panelvan_price: float, kamyonet_price: float, kamyon_price: float):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO city_prices (route_name, country_id, state_id, city_id,
                                         courier_price, minivan_price, panelvan_price, kamyonet_price, kamyon_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (route_name, country_id, state_id, city_id,
                  courier_price, minivan_price, panelvan_price, kamyonet_price, kamyon_price))
            row = cur.fetchone()
            return row, None
    except Exception as e:
        return None, str(e)


# Güncelleme
async def update_city_price(id: int, route_name: str, country_id: int, state_id: int, city_id: int,
                            courier_price: float, minivan_price: float,
                            panelvan_price: float, kamyonet_price: float, kamyon_price: float):
    try:
        with db_cursor() as cur:
            cur.execute("""
                UPDATE city_prices
                SET route_name = %s,
                    country_id = %s,
                    state_id = %s,
                    city_id = %s,
                    courier_price = %s,
                    minivan_price = %s,
                    panelvan_price = %s,
                    kamyonet_price = %s,
                    kamyon_price = %s
                WHERE id = %s;
            """, (route_name, country_id, state_id, city_id,
                  courier_price, minivan_price, panelvan_price, kamyonet_price, kamyon_price, id))
            return True, None
    except Exception as e:
        return False, str(e)

async def delete_city_price(id: int):
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM city_prices WHERE id = %s RETURNING id;", (id,))
            deleted = cur.fetchone()
            if not deleted:
                return False, "Record not found"
            return True, None
    except Exception as e:
        return False, str(e)