from typing import Dict, Any
from app.utils.database import db_cursor


# ✅ CREATE
async def create_dealer(data: dict):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO dealers (
                    name, surname, address, account_type,
                    country_id, city_id, state_id,
                    tax_office, phone, tax_number, iban, resume, status
                )
                VALUES (
                    %(name)s, %(surname)s, %(address)s, %(account_type)s,
                    %(country_id)s, %(city_id)s, %(state_id)s,
                    %(tax_office)s, %(phone)s, %(tax_number)s, %(iban)s, %(resume)s, %(status)s
                )
                RETURNING id;
            """, data)
            row = cur.fetchone()
        return {"success": True, "message": "Dealer created successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ GET LIST (isimlerle)
async def list_dealers(limit: int = 100, offset: int = 0):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    d.id           AS dealerId,
                    d.name         AS name,
                    d.surname      AS surname,
                    d.address      AS address,
                    d.account_type AS accountType,
                    d.country_id   AS countryId,
                    c.name         AS countryName,
                    d.city_id      AS cityId,
                    ci.name        AS cityName,
                    d.state_id     AS stateId,
                    s.name         AS stateName,
                    d.tax_office   AS taxOffice,
                    d.phone        AS phone,
                    d.tax_number   AS taxNumber,
                    d.iban         AS iban,
                    d.resume       AS resume,
                    d.status       AS status,
                    d.created_at
                FROM dealers d
                LEFT JOIN countries c ON c.id = d.country_id
                LEFT JOIN cities ci    ON ci.id = d.city_id
                LEFT JOIN states s     ON s.id = d.state_id
                ORDER BY d.created_at DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            rows = cur.fetchall() or []
        return {"success": True, "message": "Dealers fetched", "data": rows}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


# ✅ GET BY ID
async def get_dealer_by_id(dealer_id: int):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    d.id           AS dealerId,
                    d.name         AS name,
                    d.surname      AS surname,
                    d.address      AS address,
                    d.account_type AS accountType,
                    d.country_id   AS countryId,
                    c.name         AS countryName,
                    d.city_id      AS cityId,
                    ci.name        AS cityName,
                    d.state_id     AS stateId,
                    s.name         AS stateName,
                    d.tax_office   AS taxOffice,
                    d.phone        AS phone,
                    d.tax_number   AS taxNumber,
                    d.iban         AS iban,
                    d.resume       AS resume,
                    d.status       AS status,
                    d.created_at
                FROM dealers d
                LEFT JOIN countries c ON c.id = d.country_id
                LEFT JOIN cities ci    ON ci.id = d.city_id
                LEFT JOIN states s     ON s.id = d.state_id
                WHERE d.id = %s;
            """, (dealer_id,))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer fetched", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ UPDATE
async def update_dealer(dealer_id: int, fields: Dict[str, Any]):
    try:
        if not fields:
            return {"success": False, "message": "No fields to update", "data": {}}

        set_clause = ", ".join([f"{k} = %({k})s" for k in fields.keys()])
        params = {**fields, "id": dealer_id}

        with db_cursor(dict_cursor=True) as cur:
            cur.execute(f"""
                UPDATE dealers
                SET {set_clause}
                WHERE id = %(id)s
                RETURNING id;
            """, params)
            row = cur.fetchone()

        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer updated", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ UPDATE STATUS
async def update_dealer_status(dealer_id: int, status: str):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                UPDATE dealers
                SET status = %s
                WHERE id = %s
                RETURNING id;
            """, (status, dealer_id))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer status updated", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ DELETE
async def delete_dealer(dealer_id: int):
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                DELETE FROM dealers
                WHERE id = %s
                RETURNING id;
            """, (dealer_id,))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer deleted", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
