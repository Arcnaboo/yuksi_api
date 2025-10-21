from app.utils.database import db_cursor
from typing import Any, Dict, List, Optional, Tuple

async def create_city_price(data: Dict[str, Any]) -> Tuple[Optional[int], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute("""
                INSERT INTO city_prices (
                    route_name, country_id, state_id,
                    courier_price, minivan_price, panelvan_price,
                    kamyonet_price, kamyon_price
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id;
            """, (
                data["route_name"], data["country_id"], data["state_id"],
                data["courier_price"], data["minivan_price"],
                data["panelvan_price"], data["kamyonet_price"], data["kamyon_price"]
            ))
            new_id = cur.fetchone()[0]
            return new_id, None
    except Exception as e:
        return None, str(e)


async def list_city_prices():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT cp.id, cp.route_name,
                       c.name AS country_name,
                       s.name AS state_name,
                       cp.courier_price, cp.minivan_price, cp.panelvan_price,
                       cp.kamyonet_price, cp.kamyon_price, cp.created_at
                FROM city_prices cp
                LEFT JOIN countries c ON cp.country_id = c.id
                LEFT JOIN states s ON cp.state_id = s.id
                ORDER BY cp.id DESC;
            """)
            rows = cur.fetchall()
            print("DEBUG CITY DATA:", rows)
            return rows, None
    except Exception as e:
        return None, str(e)


async def update_city_price(id: int, fields: Dict[str, Any]) -> Optional[str]:
    try:
        if not fields:
            return "No fields provided."

        set_parts, values = [], []
        for k, v in fields.items():
            set_parts.append(f"{k} = %s")
            values.append(v)
        values.append(id)

        sql = f"UPDATE city_prices SET {', '.join(set_parts)} WHERE id = %s"
        with db_cursor() as cur:
            cur.execute(sql, tuple(values))
        return None
    except Exception as e:
        return str(e)


async def delete_city_price(id: int) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM city_prices WHERE id = %s;", (id,))
        return None
    except Exception as e:
        return str(e)
