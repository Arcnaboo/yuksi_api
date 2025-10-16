from typing import Optional, List, Dict, Any
from app.utils.database import db_cursor

# --- küçük yardımcılar (tuple -> dict) ---
def _rows_to_dicts(rows, description) -> List[Dict[str, Any]]:
    if not rows:
        return []
    cols = [col[0] for col in description]
    return [dict(zip(cols, row)) for row in rows]

def _row_to_dict(row, description) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    cols = [col[0] for col in description]
    return dict(zip(cols, row))

# --- servis fonksiyonları ---

def list_countries(q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    with db_cursor() as cur:
        if q:
            cur.execute(
                """
                SELECT id, name, iso2, iso3, phonecode
                FROM public.countries
                WHERE lower(name) LIKE lower(%s)
                ORDER BY NULLIF(regexp_replace(phonecode, '\\D', '', 'g'), '')::int ASC, name
                LIMIT %s OFFSET %s
                """,
                (f"%{q}%", limit, offset),
            )
        else:
            cur.execute(
                """
                SELECT id, name, iso2, iso3, phonecode
                FROM public.countries
                ORDER BY NULLIF(regexp_replace(phonecode, '\\D', '', 'g'), '')::int ASC, name
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
        rows = cur.fetchall()
        return _rows_to_dicts(rows, cur.description)

def list_states_by_country(country_id: int, q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    with db_cursor() as cur:
        if q:
            cur.execute(
                """
                SELECT id, name, country_id, country_code, iso2
                FROM public.states
                WHERE country_id=%s AND lower(name) LIKE lower(%s)
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (country_id, f"%{q}%", limit, offset),
            )
        else:
            cur.execute(
                """
                SELECT id, name, country_id, country_code, iso2
                FROM public.states
                WHERE country_id=%s
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (country_id, limit, offset),
            )
        rows = cur.fetchall()
        return _rows_to_dicts(rows, cur.description)

def list_cities_by_state(state_id: int, q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    with db_cursor() as cur:
        if q:
            cur.execute(
                """
                SELECT id, name, state_id, state_code, country_id, country_code, timezone
                FROM public.cities
                WHERE state_id=%s AND lower(name) LIKE lower(%s)
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (state_id, f"%{q}%", limit, offset),
            )
        else:
            cur.execute(
                """
                SELECT id, name, state_id, state_code, country_id, country_code, timezone
                FROM public.cities
                WHERE state_id=%s
                ORDER BY name
                LIMIT %s OFFSET %s
                """,
                (state_id, limit, offset),
            )
        rows = cur.fetchall()
        return _rows_to_dicts(rows, cur.description)

def get_country_by_id(country_id: int) -> Optional[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, name, iso2 FROM public.countries WHERE id=%s",
            (country_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row, cur.description)

def get_state_by_id(state_id: int) -> Optional[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, name, country_id FROM public.states WHERE id=%s",
            (state_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row, cur.description)
