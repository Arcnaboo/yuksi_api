from typing import Optional, Tuple, List, Dict, Any
from ..utils.database import db_cursor
from ..utils.security import hash_pwd


def restaurant_register(
    email: str,
    password: str,
    phone: str,
    country_id: int,
    name: str,
    contact_person: str,
    tax_number: str,
    address_line1: str,
    address_line2: str,
    state_id: int,  # .NET'teki cityId
    city_id: int,   # .NET'teki districtId
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Restaurant kayıt işlemi.
    Returns: (restaurant_data, error_message)
    """
    with db_cursor() as cur:
        # Email kontrolü
        cur.execute("SELECT id FROM restaurants WHERE email=%s", (email,))
        if cur.fetchone():
            return None, "Email already registered"

        # Geo kontrolü (opsiyonel - yoksa uyarı ver ama devam et)
        try:
            cur.execute("SELECT 1 FROM countries WHERE id=%s", (country_id,))
            if not cur.fetchone():
                print(f"[WARNING] Country {country_id} not found in database")
            
            cur.execute("SELECT 1 FROM states WHERE id=%s", (state_id,))
            if not cur.fetchone():
                print(f"[WARNING] State {state_id} not found in database")
                
            cur.execute("SELECT 1 FROM cities WHERE id=%s", (city_id,))
            if not cur.fetchone():
                print(f"[WARNING] City {city_id} not found in database")
        except Exception as e:
            print(f"[WARNING] Geo validation failed: {e}")

        # Password hash
        pwd_hash = hash_pwd(password)

        # Insert restaurant
        cur.execute(
            """
            INSERT INTO restaurants (
                email, password_hash, phone, country_id, name, 
                contact_person, tax_number, address_line1, address_line2,
                state_id, city_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, name, contact_person, tax_number, phone, 
                      address_line1, address_line2
            """,
            (
                email, pwd_hash, phone, country_id, name,
                contact_person, tax_number, address_line1, address_line2,
                state_id, city_id
            )
        )
        row = cur.fetchone()

        # Tuple'ı dict'e çevir
        restaurant_data = {
            "id": str(row[0]),
            "email": row[1],
            "name": row[2],
            "contactPerson": row[3],
            "taxNumber": row[4],
            "phone": row[5],
            "fullAddress": f"{row[6] or ''} {row[7] or ''}".strip()
        }

        return restaurant_data, None


def list_restaurants(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Tüm restoranları listeler.
    Returns: List of restaurant dicts
    """
    sql = """
    SELECT 
        id,
        email,
        name,
        contact_person,
        tax_number,
        phone,
        address_line1,
        address_line2
    FROM restaurants
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s
    """
    
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (limit, offset))
        rows = cur.fetchall()
        
        # fullAddress ekle
        result = []
        for row in rows:
            result.append({
                "id": str(row["id"]),
                "email": row["email"],
                "name": row["name"],
                "contactPerson": row["contact_person"],
                "taxNumber": row["tax_number"],
                "phone": row["phone"],
                "fullAddress": f"{row['address_line1'] or ''} {row['address_line2'] or ''}".strip()
            })
        
        return result


async def get_restaurant_profile(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Restaurant profil bilgilerini getir"""
    try:
        from ..utils.database_async import fetch_one
        
        row = await fetch_one("""
            SELECT email, phone, contact_person, address_line1, address_line2, 
                   opening_hour, closing_hour
            FROM restaurants 
            WHERE id = $1
        """, restaurant_id)
        
        if not row:
            return None
            
        return {
            "email": row.get("email"),
            "phone": row.get("phone"),
            "contactPerson": row.get("contact_person") or "",
            "addressLine1": row.get("address_line1") or "",
            "addressLine2": row.get("address_line2") or "",
            "openingHour": row.get("opening_hour").strftime("%H:%M") if row.get("opening_hour") else None,
            "closingHour": row.get("closing_hour").strftime("%H:%M") if row.get("closing_hour") else None
        }
    except Exception as e:
        print(f"Error getting restaurant profile: {e}")
        return None

async def update_restaurant_profile(
    restaurant_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    contact_person: Optional[str] = None,
    address_line1: Optional[str] = None,
    address_line2: Optional[str] = None,
    opening_hour: Optional[str] = None,
    closing_hour: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Restaurant profil bilgilerini güncelle"""
    try:
        from ..utils.database_async import execute
        from datetime import time
        
        # Güncellenecek alanları belirle
        update_fields = []
        params = []
        param_count = 1
        
        if email is not None:
            update_fields.append(f"email = ${param_count}")
            params.append(email)
            param_count += 1
        if phone is not None:
            update_fields.append(f"phone = ${param_count}")
            params.append(phone)
            param_count += 1
        if contact_person is not None:
            update_fields.append(f"contact_person = ${param_count}")
            params.append(contact_person)
            param_count += 1
        if address_line1 is not None:
            update_fields.append(f"address_line1 = ${param_count}")
            params.append(address_line1)
            param_count += 1
        if address_line2 is not None:
            update_fields.append(f"address_line2 = ${param_count}")
            params.append(address_line2)
            param_count += 1
        if opening_hour is not None:
            update_fields.append(f"opening_hour = ${param_count}")
            # String'i time objesine çevir
            hour, minute = opening_hour.split(':')
            params.append(time(int(hour), int(minute)))
            param_count += 1
        if closing_hour is not None:
            update_fields.append(f"closing_hour = ${param_count}")
            # String'i time objesine çevir
            hour, minute = closing_hour.split(':')
            params.append(time(int(hour), int(minute)))
            param_count += 1
            
        if not update_fields:
            return False, "Güncellenecek alan bulunamadı"
            
        # SQL sorgusu oluştur
        sql = f"UPDATE restaurants SET {', '.join(update_fields)} WHERE id = ${param_count}"
        params.append(restaurant_id)
        
        result = await execute(sql, *params)
        if result == "UPDATE 0":
            return False, "Restaurant bulunamadı"
                
        return True, None
        
    except Exception as e:
        print(f"Error updating restaurant profile: {e}")
        return False, f"Güncelleme hatası: {str(e)}"