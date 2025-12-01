from typing import Dict, Any, Optional, List, Tuple
from uuid import UUID
from app.utils.database import db_cursor
from app.utils.database_async import fetch_all, fetch_one
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


# === GET PROFILE ===
async def get_dealer_profile(dealer_id: UUID) -> Optional[Dict[str, Any]]:
    """Bayi profil bilgilerini getirir"""
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT 
                    email, phone, name, surname, address,
                    account_type, country_id, state_id, city_id,
                    tax_office, tax_number, iban, resume,
                    commission_rate, commission_description,
                    latitude, longitude
                FROM dealers 
                WHERE id = %s;
            """, (str(dealer_id),))
            row = cur.fetchone()
        
        if not row:
            return None

        return {
            "email": row.get("email"),
            "phone": row.get("phone"),
            "name": row.get("name") or "",
            "surname": row.get("surname") or "",
            "fullAddress": row.get("address"),
            "accountType": row.get("account_type"),
            "countryId": int(row["country_id"]) if row.get("country_id") is not None else None,
            "stateId": int(row["state_id"]) if row.get("state_id") is not None else None,
            "cityId": int(row["city_id"]) if row.get("city_id") is not None else None,
            "taxOffice": row.get("tax_office"),
            "taxNumber": row.get("tax_number"),
            "iban": row.get("iban"),
            "resume": row.get("resume"),
            "commissionRate": float(row["commission_rate"]) if row.get("commission_rate") is not None else None,
            "commissionDescription": row.get("commission_description"),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
        }
    except Exception as e:
        print(f"Error getting dealer profile: {e}")
        return None


# === UPDATE PROFILE ===
async def update_dealer_profile(
    dealer_id: UUID,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    full_address: Optional[str] = None,
    account_type: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None,
    tax_office: Optional[str] = None,
    tax_number: Optional[str] = None,
    iban: Optional[str] = None,
    resume: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """Bayi profil bilgilerini günceller"""
    try:
        update_fields = []
        params = {}

        if email is not None:
            # Email unique kontrolü
            with db_cursor(dict_cursor=True) as cur:
                cur.execute(
                    "SELECT id FROM dealers WHERE email = %s AND id != %s LIMIT 1;",
                    (email.lower(), str(dealer_id))
                )
                existing = cur.fetchone()
                if existing:
                    return {"success": False, "message": "Bu email adresi zaten kullanılıyor", "data": {}}
            update_fields.append("email = %(email)s")
            params["email"] = email.lower()
        
        if phone is not None:
            update_fields.append("phone = %(phone)s")
            params["phone"] = phone
        
        if name is not None:
            update_fields.append("name = %(name)s")
            params["name"] = name
        
        if surname is not None:
            update_fields.append("surname = %(surname)s")
            params["surname"] = surname
        
        if full_address is not None:
            update_fields.append("address = %(address)s")
            params["address"] = full_address
        
        if account_type is not None:
            update_fields.append("account_type = %(account_type)s")
            params["account_type"] = account_type
        
        if country_id is not None:
            update_fields.append("country_id = %(country_id)s")
            params["country_id"] = country_id
        
        if state_id is not None:
            update_fields.append("state_id = %(state_id)s")
            params["state_id"] = state_id
        
        if city_id is not None:
            update_fields.append("city_id = %(city_id)s")
            params["city_id"] = city_id
        
        if tax_office is not None:
            update_fields.append("tax_office = %(tax_office)s")
            params["tax_office"] = tax_office
        
        if tax_number is not None:
            update_fields.append("tax_number = %(tax_number)s")
            params["tax_number"] = tax_number
        
        if iban is not None:
            update_fields.append("iban = %(iban)s")
            params["iban"] = iban
        
        if resume is not None:
            update_fields.append("resume = %(resume)s")
            params["resume"] = resume
        
        if latitude is not None:
            update_fields.append("latitude = %(latitude)s")
            params["latitude"] = latitude
        
        if longitude is not None:
            update_fields.append("longitude = %(longitude)s")
            params["longitude"] = longitude

        if not update_fields:
            return {"success": False, "message": "Güncellenecek alan bulunamadı", "data": {}}

        params["dealer_id"] = str(dealer_id)
        
        query = f"""
            UPDATE dealers 
            SET {', '.join(update_fields)}
            WHERE id = %(dealer_id)s;
        """
        
        with db_cursor(dict_cursor=True) as cur:
            cur.execute(query, params)
            if cur.rowcount == 0:
                return {"success": False, "message": "Bayi bulunamadı", "data": {}}
        
        return {"success": True, "message": "Profil başarıyla güncellendi", "data": {}}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# === GET DEALER COURIERS GPS ===
async def get_dealer_couriers_gps(dealer_id: str) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Bayinin kendi kuryelerinin canlı GPS konumlarını getirir.
    Returns: (success, couriers_gps_list_or_none, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, None, "Bayi bulunamadı"
        
        # Bayinin kendi kuryelerinin GPS verilerini getir (driver_onboarding tablosundan)
        rows = await fetch_all("""
            SELECT 
                d.id as courier_id,
                CONCAT(d.first_name, ' ', d.last_name) as courier_name,
                d.phone as courier_phone,
                d.email as courier_email,
                d.is_active,
                d.deleted,
                COALESCE(ds.online, FALSE) AS is_online,
                g.latitude,
                g.longitude,
                g.updated_at as location_updated_at,
                ob.vehicle_type,
                ob.vehicle_capacity,
                ob.state_id
            FROM driver_onboarding ob
            INNER JOIN drivers d ON d.id = ob.driver_id
            LEFT JOIN gps_table g ON g.driver_id = d.id
            LEFT JOIN driver_status ds ON ds.driver_id = d.id
            WHERE ob.dealer_id = $1::uuid
              AND (d.deleted IS NULL OR d.deleted = FALSE)
            ORDER BY g.updated_at DESC NULLS LAST
        """, dealer_id)
        
        # asyncpg.Record objelerini dict'e çevir ve UUID'leri string'e çevir
        result = []
        if rows:
            for row in rows:
                row_dict = dict(row)
                # UUID'leri string'e çevir
                if row_dict.get("courier_id"):
                    row_dict["courier_id"] = str(row_dict["courier_id"])
                # Timestamp'leri ISO formatına çevir
                if row_dict.get("location_updated_at"):
                    row_dict["location_updated_at"] = row_dict["location_updated_at"].isoformat() if hasattr(row_dict["location_updated_at"], "isoformat") else str(row_dict["location_updated_at"])
                result.append(row_dict)
        
        return True, result, None
        
    except Exception as e:
        return False, None, str(e)