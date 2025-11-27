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
    latitude: float,
    longitude: float,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Yeni restoran kaydı oluşturur"""
    try:
        existing = await fetch_one("SELECT id FROM restaurants WHERE email=$1 AND (deleted IS NULL OR deleted = FALSE);", email)
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
                state_id, city_id, latitude, longitude
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
            RETURNING id, email, name, contact_person, tax_number, phone, address_line1, address_line2, latitude, longitude;
            """,
            email, pwd_hash, phone, country_id, name,
            contact_person, tax_number, address_line1, address_line2,
            state_id, city_id, latitude, longitude
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
            "fullAddress": f"{row['address_line1'] or ''} {row['address_line2'] or ''}".strip(),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None
        }

        return restaurant_data, None
    except Exception as e:
        return None, str(e)


# === LIST RESTAURANTS ===
async def list_restaurants(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    query = """
        SELECT id, email, name, contact_person, tax_number, phone,
               address_line1, address_line2,
               latitude, longitude,
               opening_hour, closing_hour
        FROM restaurants
        WHERE (deleted IS NULL OR deleted = FALSE)
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
            "latitude": float(r["latitude"]) if r.get("latitude") is not None else None,
            "longitude": float(r["longitude"]) if r.get("longitude") is not None else None,
            "openingHour": r["opening_hour"].strftime("%H:%M") if r.get("opening_hour") else None,
            "closingHour": r["closing_hour"].strftime("%H:%M") if r.get("closing_hour") else None,
        }
        for r in rows
    ]


# === GET PROFILE ===
async def get_restaurant_profile(restaurant_id: str) -> Optional[Dict[str, Any]]:
    try:
        row = await fetch_one(
            """
            SELECT email, phone, contact_person, address_line1, address_line2, 
                   opening_hour, closing_hour, latitude, longitude
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
            "latitude": float(row.get("latitude")) if row.get("latitude") is not None else None,
            "longitude": float(row.get("longitude")) if row.get("longitude") is not None else None,
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
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
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
        if latitude is not None:
            update_fields.append(f"latitude = ${i}")
            params.append(latitude)
            i += 1
        if longitude is not None:
            update_fields.append(f"longitude = ${i}")
            params.append(longitude)
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
    
    
async def assign_courier_to_restaurant(
    restaurant_id: str,
    courier_id: str,
    notes: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Restorana kurye ata"""
    try:
        from ..utils.database_async import fetch_one, execute
        
        # Restoran kontrolü
        restaurant = await fetch_one("SELECT id, name FROM restaurants WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE)", restaurant_id)
        if not restaurant:
            return False, "Restaurant not found"
        
        # Kurye kontrolü
        courier = await fetch_one("SELECT id, first_name, last_name, is_active FROM drivers WHERE id = $1", courier_id)
        if not courier:
            return False, "Courier not found"
        
        if not courier["is_active"]:
            return False, "Courier is not active"
        
        # Kurye başka bir restoranta atanmış mı kontrol et
        other_restaurant_assignment = await fetch_one("""
            SELECT restaurant_id FROM restaurant_couriers 
            WHERE courier_id = $1
        """, courier_id)
        
        if other_restaurant_assignment:
            other_restaurant_id = str(other_restaurant_assignment.get("restaurant_id"))
            # Eğer aynı restoranta atanmışsa, "zaten atanmış" mesajı ver
            if other_restaurant_id == restaurant_id:
                return False, "Bu kurye zaten bu restoranta atanmış"
            # Başka bir restoranta atanmışsa hata ver
            return False, "Bu kurye başka bir restoranta atanmış"
        
        # Atama yap
        await execute("""
            INSERT INTO restaurant_couriers (restaurant_id, courier_id, notes)
            VALUES ($1, $2, $3)
        """, restaurant_id, courier_id, notes)
        
        return True, None
        
    except Exception as e:
        return False, str(e)

async def get_restaurant_couriers(
    restaurant_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Restoranın kuryelerini getir"""
    try:
        from ..utils.database_async import fetch_all
        
        rows = await fetch_all("""
            SELECT 
                rc.id,
                rc.restaurant_id,
                rc.courier_id,
                rc.assigned_at,
                rc.notes,
                rc.created_at,
                d.first_name,
                d.last_name,
                d.email,
                d.phone,
                d.is_active,
                CONCAT(d.first_name, ' ', d.last_name) as courier_name
            FROM restaurant_couriers rc
            LEFT JOIN drivers d ON d.id = rc.courier_id
            WHERE rc.restaurant_id = $1
            ORDER BY rc.assigned_at DESC
            LIMIT $2 OFFSET $3
        """, restaurant_id, limit, offset)
        
        # asyncpg.Record objelerini dict'e çevir
        result = []
        if rows:
            for row in rows:
                result.append(dict(row))
        
        return result
        
    except Exception as e:
        return []

async def remove_courier_from_restaurant(
    assignment_id: str,
    restaurant_id: str
) -> Tuple[bool, Optional[str]]:
    """Restorandan kurye atamasını kaldır"""
    try:
        from ..utils.database_async import execute
        
        result = await execute("""
            DELETE FROM restaurant_couriers 
            WHERE id = $1 AND restaurant_id = $2
        """, assignment_id, restaurant_id)
        
        if result == "DELETE 0":
            return False, "Assignment not found"
        
        return True, None
        
    except Exception as e:
        return False, str(e)

async def get_restaurant_courier_stats(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Restoran kurye istatistikleri"""
    try:
        from ..utils.database_async import fetch_one
        
        # Restoran bilgileri
        restaurant = await fetch_one("SELECT name FROM restaurants WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE)", restaurant_id)
        if not restaurant:
            return None
        
        # İstatistikler
        stats = await fetch_one("""
            SELECT COUNT(*) as total_couriers
            FROM restaurant_couriers 
            WHERE restaurant_id = $1
        """, restaurant_id)
        
        # asyncpg.Record objelerini dict'e çevir
        restaurant_dict = dict(restaurant) if restaurant else {}
        stats_dict = dict(stats) if stats else {}
        
        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant_dict.get("name", ""),
            "total_couriers": stats_dict.get("total_couriers", 0) or 0
        }
        
    except Exception as e:
        return None
    
async def admin_update_restaurant(restaurant_id: str, fields: Dict[str, Any]) -> Tuple[bool, str | None]:
    """Admin tarafından restoran güncelleme"""
    try:
        if not fields:
            return False, "No fields to update"

        # Şifre yok, sadece tabloya ait alanlar
        update_fields = []
        params = []
        i = 1

        for key, value in fields.items():
            if key in ["opening_hour", "closing_hour"] and isinstance(value, str):
                h, m = value.split(":")
                value = time(int(h), int(m))
            update_fields.append(f"{key} = ${i}")
            params.append(value)
            i += 1

        params.append(restaurant_id)
        query = f"UPDATE restaurants SET {', '.join(update_fields)} WHERE id = ${i};"

        result = await execute(query, *params)
        if result.endswith(" 0"):
            return False, "Restaurant not found"

        return True, None

    except Exception as e:
        return False, str(e)


# === ADMIN DELETE RESTAURANT ===
async def admin_delete_restaurant(restaurant_id: str) -> Tuple[bool, Optional[str]]:
    """Admin tarafından restoran silme (soft delete)"""
    try:
        # Önce restoranın var olup olmadığını ve silinmemiş olduğunu kontrol et
        restaurant = await fetch_one("""
            SELECT id, deleted 
            FROM restaurants 
            WHERE id = $1;
        """, restaurant_id)
        
        if not restaurant:
            return False, "Restaurant not found"
        
        if restaurant.get("deleted"):
            return False, "Restaurant already deleted"
        
        # Soft delete yap
        result = await execute("""
            UPDATE restaurants 
            SET deleted = TRUE, deleted_at = NOW() 
            WHERE id = $1;
        """, restaurant_id)
        
        if result.endswith(" 0"):
            return False, "Restaurant not found"
        
        return True, None
    except Exception as e:
        return False, str(e)


# === GET RESTAURANT COURIERS GPS ===
async def get_restaurant_couriers_gps(restaurant_id: str) -> List[Dict[str, Any]]:
    """Restoranın kuryelerinin canlı GPS konumlarını getir"""
    try:
        rows = await fetch_all("""
            SELECT 
                d.id as courier_id,
                CONCAT(d.first_name, ' ', d.last_name) as courier_name,
                d.phone as courier_phone,
                d.email as courier_email,
                g.latitude,
                g.longitude,
                g.updated_at as location_updated_at,
                rc.assigned_at,
                rc.notes
            FROM restaurant_couriers rc
            INNER JOIN drivers d ON d.id = rc.courier_id
            LEFT JOIN gps_table g ON g.driver_id = d.id
            WHERE rc.restaurant_id = $1
            ORDER BY g.updated_at DESC
        """, restaurant_id)
        
        # asyncpg.Record objelerini dict'e çevir
        result = []
        if rows:
            for row in rows:
                result.append(dict(row))
        
        return result
        
    except Exception as e:
        print(f"Error getting restaurant couriers GPS: {e}")
        return []


# === GET NEARBY COURIERS (max 10km, sorted by distance, active and online only) ===
async def get_nearby_couriers(restaurant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Restorana 10 km içindeki aktif ve online kuryeleri mesafeye göre sırala (en yakından en uzağa)"""
    try:
        rows = await fetch_all("""
            WITH restaurant_location AS (
                SELECT latitude, longitude
                FROM restaurants
                WHERE id = $1
                  AND (deleted IS NULL OR deleted = FALSE)
                  AND latitude IS NOT NULL
                  AND longitude IS NOT NULL
            ),
            courier_distances AS (
                SELECT 
                    d.id as courier_id,
                    CONCAT(d.first_name, ' ', d.last_name) as courier_name,
                    d.phone,
                    d.email,
                    g.latitude,
                    g.longitude,
                    g.updated_at as location_updated_at,
                    (
                        6371000 * acos(
                            LEAST(1.0, 
                                cos(radians(rl.latitude)) * 
                                cos(radians(g.latitude)) * 
                                cos(radians(g.longitude) - radians(rl.longitude)) + 
                                sin(radians(rl.latitude)) * 
                                sin(radians(g.latitude))
                            )
                        )
                    ) AS distance_meters
                FROM drivers d
                INNER JOIN gps_table g ON g.driver_id = d.id
                INNER JOIN driver_status ds ON ds.driver_id = d.id
                CROSS JOIN restaurant_location rl
                WHERE d.is_active = true
                  AND d.deleted = false
                  AND COALESCE(ds.online, false) = true
                  AND g.latitude IS NOT NULL
                  AND g.longitude IS NOT NULL
            )
            SELECT *
            FROM courier_distances
            WHERE distance_meters <= 10000
            ORDER BY distance_meters ASC
            LIMIT $2;
        """, restaurant_id, limit)
        
        # asyncpg.Record objelerini dict'e çevir ve distance_km ekle
        result = []
        if rows:
            for row in rows:
                row_dict = dict(row)
                # Mesafeyi kilometreye çevir
                distance_meters = float(row_dict.get("distance_meters", 0))
                row_dict["distance_km"] = round(distance_meters / 1000, 2)
                row_dict["distance_meters"] = round(distance_meters, 2)
                result.append(row_dict)
        
        return result
        
    except Exception as e:
        print(f"Error getting nearby couriers: {e}")
        return []