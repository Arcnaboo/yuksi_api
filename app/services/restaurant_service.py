from typing import Optional, Tuple, List, Dict, Any
from datetime import time
from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.security import hash_pwd


# === REGISTER ===
async def restaurant_register(
    email: str,
    password: str,
    phone: str,
    country_id: int,
    name: str,
    contact_person: str,
    tax_number: str,
    address_line1: str,
    address_line2: str,
    state_id: int,
    city_id: int,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Yeni restoran kaydı oluşturur"""
    try:
        existing = await fetch_one("SELECT id FROM restaurants WHERE email=$1;", email)
        if existing:
            return None, "Email already registered"

        # Opsiyonel geo kontrolü (hata vermez)
        for table, val in [("countries", country_id), ("states", state_id), ("cities", city_id)]:
            try:
                exists = await fetch_one(f"SELECT 1 FROM {table} WHERE id=$1;", val)
                if not exists:
                    print(f"[WARN] {table} id {val} not found")
            except Exception as e:
                print(f"[WARN] {table} lookup failed: {e}")

        pwd_hash = hash_pwd(password)

        row = await fetch_one(
            """
            INSERT INTO restaurants (
                email, password_hash, phone, country_id, name, 
                contact_person, tax_number, address_line1, address_line2,
                state_id, city_id
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            RETURNING id, email, name, contact_person, tax_number, phone, address_line1, address_line2;
            """,
            email, pwd_hash, phone, country_id, name,
            contact_person, tax_number, address_line1, address_line2,
            state_id, city_id
        )

        if not row:
            return None, "Insert failed"

        restaurant_data = {
            "id": str(row["id"]),
            "email": row["email"],
            "name": row["name"],
            "contactPerson": row["contact_person"],
            "taxNumber": row["tax_number"],
            "phone": row["phone"],
            "fullAddress": f"{row['address_line1'] or ''} {row['address_line2'] or ''}".strip()
        }

        return restaurant_data, None
    except Exception as e:
        return None, str(e)


# === LIST RESTAURANTS ===
async def list_restaurants(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = """
        SELECT id, email, name, contact_person, tax_number, phone, address_line1, address_line2
        FROM restaurants
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2;
    """
    rows = await fetch_all(query, limit, offset)
    if not rows:
        return []

    return [
        {
            "id": str(r["id"]),
            "email": r["email"],
            "name": r["name"],
            "contactPerson": r["contact_person"],
            "taxNumber": r["tax_number"],
            "phone": r["phone"],
            "fullAddress": f"{r['address_line1'] or ''} {r['address_line2'] or ''}".strip(),
        }
        for r in rows
    ]


# === GET PROFILE ===
async def get_restaurant_profile(restaurant_id: str) -> Optional[Dict[str, Any]]:
    try:
        row = await fetch_one(
            """
            SELECT email, phone, contact_person, address_line1, address_line2, 
                   opening_hour, closing_hour
            FROM restaurants 
            WHERE id=$1;
            """,
            restaurant_id
        )
        if not row:
            return None

        return {
            "email": row.get("email"),
            "phone": row.get("phone"),
            "contactPerson": row.get("contact_person") or "",
            "addressLine1": row.get("address_line1") or "",
            "addressLine2": row.get("address_line2") or "",
            "openingHour": row["opening_hour"].strftime("%H:%M") if row.get("opening_hour") else None,
            "closingHour": row["closing_hour"].strftime("%H:%M") if row.get("closing_hour") else None,
        }
    except Exception as e:
        print(f"Error getting restaurant profile: {e}")
        return None


# === UPDATE PROFILE ===
async def update_restaurant_profile(
    restaurant_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    contact_person: Optional[str] = None,
    address_line1: Optional[str] = None,
    address_line2: Optional[str] = None,
    opening_hour: Optional[str] = None,
    closing_hour: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    try:
        update_fields = []
        params = []
        i = 1

        if email is not None:
            update_fields.append(f"email = ${i}")
            params.append(email)
            i += 1
        if phone is not None:
            update_fields.append(f"phone = ${i}")
            params.append(phone)
            i += 1
        if contact_person is not None:
            update_fields.append(f"contact_person = ${i}")
            params.append(contact_person)
            i += 1
        if address_line1 is not None:
            update_fields.append(f"address_line1 = ${i}")
            params.append(address_line1)
            i += 1
        if address_line2 is not None:
            update_fields.append(f"address_line2 = ${i}")
            params.append(address_line2)
            i += 1
        if opening_hour is not None:
            h, m = opening_hour.split(":")
            update_fields.append(f"opening_hour = ${i}")
            params.append(time(int(h), int(m)))
            i += 1
        if closing_hour is not None:
            h, m = closing_hour.split(":")
            update_fields.append(f"closing_hour = ${i}")
            params.append(time(int(h), int(m)))
            i += 1

        if not update_fields:
            return False, "No fields to update"

        params.append(restaurant_id)
        query = f"UPDATE restaurants SET {', '.join(update_fields)} WHERE id = ${i};"
        result = await execute(query, *params)

        if result.endswith(" 0"):
            return False, "Restaurant not found"

        return True, None

    except Exception as e:
        print(f"Error updating restaurant profile: {e}")
        return False, f"Güncelleme hatası: {str(e)}"
