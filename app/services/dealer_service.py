from typing import Dict, Any, Optional
from uuid import UUID
from app.utils.database import db_cursor
from app.utils.security import hash_pwd  # parolayı hashlemek için


# -- Yardımcı: Whitelist alanlar (UPDATE için)
ALLOWED_UPDATE_COLUMNS = {
    "name", "surname", "email", "address", "account_type",
    "country_id", "city_id", "state_id",
    "tax_office", "phone", "tax_number", "iban", "resume", "status"
}


# ✅ CREATE (UUID döner)
async def create_dealer(data: dict) -> Dict[str, Any]:
    try:
        # email benzersizlik kontrolü
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("SELECT 1 FROM dealers WHERE email = %s LIMIT 1;", (data["email"].lower(),))
            exists = cur.fetchone()

            if exists:
                return {"success": False, "message": "Email already registered", "data": {}}

            pwd_hash = hash_pwd(data.pop("password"))

            cur.execute("""
                INSERT INTO dealers (
                    name, surname, email, password_hash, address, account_type,
                    country_id, city_id, state_id,
                    tax_office, phone, tax_number, iban, resume, status
                )
                VALUES (
                    %(name)s, %(surname)s, %(email)s, %(password_hash)s, %(address)s, %(account_type)s,
                    %(country_id)s, %(city_id)s, %(state_id)s,
                    %(tax_office)s, %(phone)s, %(tax_number)s, %(iban)s, %(resume)s, %(status)s
                )
                RETURNING id;
            """, {
                **data,
                "email": data["email"].lower(),
                "password_hash": pwd_hash
            })
            row = cur.fetchone()

        return {"success": True, "message": "Dealer created successfully", "data": {"id": str(row["id"])}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ GET LIST (isimlerle, UUID id ile)
async def list_dealers(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    d.id           AS dealerId,
                    d.name         AS name,
                    d.surname      AS surname,
                    d.email        AS email,
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

        # UUID nesnelerini string'e çevir
        for r in rows:
            if r.get("dealerId"):
                r["dealerId"] = str(r["dealerId"])

        return {"success": True, "message": "Dealers fetched", "data": rows}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


# ✅ GET BY ID (UUID)
async def get_dealer_by_id(dealer_id: UUID) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    d.id           AS dealerid,
                    d.name         AS name,
                    d.surname      AS surname,
                    d.email        AS email,
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
                    d.created_at   AS createdAt
                FROM dealers d
                LEFT JOIN countries c ON c.id = d.country_id
                LEFT JOIN cities ci    ON ci.id = d.city_id
                LEFT JOIN states s     ON s.id = d.state_id
                WHERE d.id = %s;
            """, (str(dealer_id),))
            row = cur.fetchone()

        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}

        # ➕ UUID string
        row["dealerId"] = str(row.pop("dealerid"))

        return {"success": True, "message": "Dealer fetched", "data": row}

    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ UPDATE (UUID) — email benzersizliği korunur
async def update_dealer(dealer_id: UUID, fields: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not fields:
            return {"success": False, "message": "No fields to update", "data": {}}

        # Sadece izin verilen kolonları güncelle
        filtered = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_COLUMNS}
        if not filtered:
            return {"success": False, "message": "No valid fields to update", "data": {}}

        # email güncelleniyorsa çakışma kontrolü
        if "email" in filtered and filtered["email"]:
            with db_cursor(dict_cursor=True) as cur:
                cur.execute("""
                    SELECT 1 FROM dealers WHERE email = %s AND id <> %s LIMIT 1;
                """, (filtered["email"].lower(), str(dealer_id)))
                ex = cur.fetchone()
                if ex:
                    return {"success": False, "message": "Email already in use", "data": {}}
            filtered["email"] = filtered["email"].lower()

        set_clause = ", ".join([f"{k} = %({k})s" for k in filtered.keys()])
        params = {**filtered, "id": str(dealer_id)}

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

        return {"success": True, "message": "Dealer updated", "data": {"id": str(row["id"])}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ UPDATE STATUS (UUID)
async def update_dealer_status(dealer_id: UUID, status: str) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                UPDATE dealers
                SET status = %s
                WHERE id = %s
                RETURNING id;
            """, (status, str(dealer_id)))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer status updated", "data": {"id": str(row["id"])}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# ✅ DELETE (UUID)
async def delete_dealer(dealer_id: UUID) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                DELETE FROM dealers
                WHERE id = %s
                RETURNING id;
            """, (str(dealer_id),))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Dealer not found", "data": {}}
        return {"success": True, "message": "Dealer deleted", "data": {"id": str(row["id"])}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
