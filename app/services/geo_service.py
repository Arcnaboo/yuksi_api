from typing import Optional, List, Dict, Any
from app.utils.db import fetch_all, fetch_one


# --- ÜLKELER ---
async def list_countries(q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    if q:
        query = """
            SELECT DISTINCT ON (clean_code)
                   id, name, iso2, iso3, phonecode
            FROM (
                SELECT id, name, iso2, iso3, phonecode,
                       NULLIF(regexp_replace(phonecode, '\\D', '', 'g'), '')::int AS clean_code
                FROM public.countries
                WHERE lower(name) LIKE lower($1)
            ) AS sub
            WHERE clean_code IS NOT NULL
            ORDER BY clean_code ASC, name
            LIMIT $2 OFFSET $3;
        """
        rows = await fetch_all(query, f"%{q}%", limit, offset)
    else:
        query = """
            SELECT DISTINCT ON (clean_code)
                   id, name, iso2, iso3, phonecode
            FROM (
                SELECT id, name, iso2, iso3, phonecode,
                       NULLIF(regexp_replace(phonecode, '\\D', '', 'g'), '')::int AS clean_code
                FROM public.countries
            ) AS sub
            WHERE clean_code IS NOT NULL
            ORDER BY clean_code ASC, name
            LIMIT $1 OFFSET $2;
        """
        rows = await fetch_all(query, limit, offset)
    return [dict(r) for r in rows] if rows else []


# --- EYALETLER ---
async def list_states_by_country(country_id: int, q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    if q:
        query = """
            SELECT id, name, country_id, country_code, iso2
            FROM public.states
            WHERE country_id=$1 AND lower(name) LIKE lower($2)
            ORDER BY name
            LIMIT $3 OFFSET $4;
        """
        rows = await fetch_all(query, country_id, f"%{q}%", limit, offset)
    else:
        query = """
            SELECT id, name, country_id, country_code, iso2
            FROM public.states
            WHERE country_id=$1
            ORDER BY name
            LIMIT $2 OFFSET $3;
        """
        rows = await fetch_all(query, country_id, limit, offset)
    return [dict(r) for r in rows] if rows else []


# --- ŞEHİRLER ---
async def list_cities_by_state(state_id: int, q: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
    if q:
        query = """
            SELECT id, name, state_id, state_code, country_id, country_code, timezone
            FROM public.cities
            WHERE state_id=$1 AND lower(name) LIKE lower($2)
            ORDER BY name
            LIMIT $3 OFFSET $4;
        """
        rows = await fetch_all(query, state_id, f"%{q}%", limit, offset)
    else:
        query = """
            SELECT id, name, state_id, state_code, country_id, country_code, timezone
            FROM public.cities
            WHERE state_id=$1
            ORDER BY name
            LIMIT $2 OFFSET $3;
        """
        rows = await fetch_all(query, state_id, limit, offset)
    return [dict(r) for r in rows] if rows else []


# --- TEKİL KAYITLAR ---
async def get_country_by_id(country_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT id, name, iso2 FROM public.countries WHERE id=$1;"
    row = await fetch_one(query, country_id)
    return dict(row) if row else None


async def get_state_by_id(state_id: int) -> Optional[Dict[str, Any]]:
    query = "SELECT id, name, country_id FROM public.states WHERE id=$1;"
    row = await fetch_one(query, state_id)
    return dict(row) if row else None
