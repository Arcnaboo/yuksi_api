from typing import Dict, Any, Tuple, List, Optional
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services import restaurant_package_price_service


# === LIST RESTAURANTS ===
async def get_support_restaurants(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Çağrı merkezi için tüm restoranları listeler (Modül 3)
    Hangi bayinin eklediği bilgisi dahil
    """
    try:
        filters = []
        params = []
        i = 1
        
        # Silinmemiş restoranları getir
        filters.append("(r.deleted IS NULL OR r.deleted = FALSE)")
        
        # Arama filtresi
        if search:
            filters.append(f"""
                (
                    LOWER(r.name) LIKE ${i} OR
                    LOWER(r.email) LIKE ${i} OR
                    LOWER(r.phone) LIKE ${i} OR
                    LOWER(r.contact_person) LIKE ${i} OR
                    LOWER(r.tax_number) LIKE ${i}
                )
            """)
            params.append(f"%{search.lower()}%")
            i += 1
        
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        params.extend([limit, offset])
        
        query = f"""
        SELECT
            r.id,
            r.email,
            r.phone,
            r.name,
            r.contact_person,
            r.tax_number,
            r.address_line1,
            r.address_line2,
            r.latitude,
            r.longitude,
            r.opening_hour,
            r.closing_hour,
            r.created_at,
            r.deleted,
            r.deleted_at,
            c.name AS city_name,
            s.name AS state_name,
            co.name AS country_name,
            c.id AS city_id,
            s.id AS state_id,
            co.id AS country_id,
            d.id AS dealer_id,
            d.name AS dealer_name,
            d.email AS dealer_email,
            d.phone AS dealer_phone,
            dr.created_at AS linked_at
        FROM restaurants r
        LEFT JOIN cities c ON c.id = r.city_id
        LEFT JOIN states s ON s.id = r.state_id
        LEFT JOIN countries co ON co.id = r.country_id
        LEFT JOIN dealer_restaurants dr ON dr.restaurant_id = r.id
        LEFT JOIN dealers d ON d.id = dr.dealer_id
        {where_clause}
        ORDER BY r.created_at DESC
        LIMIT ${i} OFFSET ${i + 1};
        """
        
        rows = await fetch_all(query, *params)
        
        if not rows:
            return True, []
        
        # Formatla
        formatted_rows = []
        for row in rows:
            row_dict = dict(row) if not isinstance(row, dict) else row
            formatted_rows.append({
                "id": str(row_dict["id"]),
                "email": row_dict.get("email"),
                "phone": row_dict.get("phone"),
                "name": row_dict.get("name"),
                "contactPerson": row_dict.get("contact_person"),
                "taxNumber": row_dict.get("tax_number"),
                "addressLine1": row_dict.get("address_line1"),
                "addressLine2": row_dict.get("address_line2"),
                "fullAddress": f"{row_dict.get('address_line1') or ''} {row_dict.get('address_line2') or ''}".strip(),
                "latitude": float(row_dict["latitude"]) if row_dict.get("latitude") else None,
                "longitude": float(row_dict["longitude"]) if row_dict.get("longitude") else None,
                "openingHour": row_dict["opening_hour"].strftime("%H:%M") if row_dict.get("opening_hour") else None,
                "closingHour": row_dict["closing_hour"].strftime("%H:%M") if row_dict.get("closing_hour") else None,
                "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
                "deleted": row_dict.get("deleted", False),
                "deletedAt": row_dict["deleted_at"].isoformat() if row_dict.get("deleted_at") else None,
                "location": {
                    "cityId": row_dict.get("city_id"),
                    "cityName": row_dict.get("city_name"),
                    "stateId": row_dict.get("state_id"),
                    "stateName": row_dict.get("state_name"),
                    "countryId": row_dict.get("country_id"),
                    "countryName": row_dict.get("country_name"),
                } if row_dict.get("city_id") else None,
                "dealer": {
                    "id": str(row_dict["dealer_id"]) if row_dict.get("dealer_id") else None,
                    "name": row_dict.get("dealer_name"),
                    "email": row_dict.get("dealer_email"),
                    "phone": row_dict.get("dealer_phone"),
                    "linkedAt": row_dict["linked_at"].isoformat() if row_dict.get("linked_at") else None
                } if row_dict.get("dealer_id") else None
            })
        
        return True, formatted_rows
        
    except Exception as e:
        return False, f"Restoran listesi getirilirken hata oluştu: {str(e)}"


# === GET RESTAURANT DETAIL ===
async def get_support_restaurant_detail(
    restaurant_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi için tek restoran detayını getirir (Modül 3)
    Tüm bilgiler, günlük paket durumu, konum, vs.
    """
    try:
        query = """
        SELECT
            r.id,
            r.email,
            r.phone,
            r.name,
            r.contact_person,
            r.tax_number,
            r.address_line1,
            r.address_line2,
            r.latitude,
            r.longitude,
            r.opening_hour,
            r.closing_hour,
            r.created_at,
            r.deleted,
            r.deleted_at,
            c.name AS city_name,
            s.name AS state_name,
            co.name AS country_name,
            c.id AS city_id,
            s.id AS state_id,
            co.id AS country_id,
            d.id AS dealer_id,
            d.name AS dealer_name,
            d.email AS dealer_email,
            d.phone AS dealer_phone,
            dr.created_at AS linked_at
        FROM restaurants r
        LEFT JOIN cities c ON c.id = r.city_id
        LEFT JOIN states s ON s.id = r.state_id
        LEFT JOIN countries co ON co.id = r.country_id
        LEFT JOIN dealer_restaurants dr ON dr.restaurant_id = r.id
        LEFT JOIN dealers d ON d.id = dr.dealer_id
        WHERE r.id = $1 AND (r.deleted IS NULL OR r.deleted = FALSE);
        """
        
        row = await fetch_one(query, restaurant_id)
        
        if not row:
            return False, "Restoran bulunamadı."
        
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        # Paket durumunu getir
        package_success, package_data, package_error = await restaurant_package_price_service.get_restaurant_package_status(restaurant_id)
        package_info = package_data if package_success else None
        
        # Restoranın kuryelerini say
        courier_count_query = """
        SELECT COUNT(*) as count
        FROM restaurant_couriers
        WHERE restaurant_id = $1;
        """
        courier_count_row = await fetch_one(courier_count_query, restaurant_id)
        courier_count = courier_count_row["count"] if courier_count_row else 0
        
        return True, {
            "id": str(row_dict["id"]),
            "email": row_dict.get("email"),
            "phone": row_dict.get("phone"),
            "name": row_dict.get("name"),
            "contactPerson": row_dict.get("contact_person"),
            "taxNumber": row_dict.get("tax_number"),
            "addressLine1": row_dict.get("address_line1"),
            "addressLine2": row_dict.get("address_line2"),
            "fullAddress": f"{row_dict.get('address_line1') or ''} {row_dict.get('address_line2') or ''}".strip(),
            "latitude": float(row_dict["latitude"]) if row_dict.get("latitude") else None,
            "longitude": float(row_dict["longitude"]) if row_dict.get("longitude") else None,
            "openingHour": row_dict["opening_hour"].strftime("%H:%M") if row_dict.get("opening_hour") else None,
            "closingHour": row_dict["closing_hour"].strftime("%H:%M") if row_dict.get("closing_hour") else None,
            "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
            "deleted": row_dict.get("deleted", False),
            "deletedAt": row_dict["deleted_at"].isoformat() if row_dict.get("deleted_at") else None,
            "location": {
                "cityId": row_dict.get("city_id"),
                "cityName": row_dict.get("city_name"),
                "stateId": row_dict.get("state_id"),
                "stateName": row_dict.get("state_name"),
                "countryId": row_dict.get("country_id"),
                "countryName": row_dict.get("country_name"),
            } if row_dict.get("city_id") else None,
            "dealer": {
                "id": str(row_dict["dealer_id"]) if row_dict.get("dealer_id") else None,
                "name": row_dict.get("dealer_name"),
                "email": row_dict.get("dealer_email"),
                "phone": row_dict.get("dealer_phone"),
                "linkedAt": row_dict["linked_at"].isoformat() if row_dict.get("linked_at") else None
            } if row_dict.get("dealer_id") else None,
            "package": package_info,
            "courierCount": courier_count
        }
        
    except Exception as e:
        return False, f"Restoran detayı getirilirken hata oluştu: {str(e)}"


# === UPDATE RESTAURANT ===
async def update_support_restaurant(
    restaurant_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    contact_person: Optional[str] = None,
    tax_number: Optional[str] = None,
    address_line1: Optional[str] = None,
    address_line2: Optional[str] = None,
    opening_hour: Optional[str] = None,
    closing_hour: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Çağrı merkezi için restoran güncelleme (sistemsel müdahale için) (Modül 3)
    """
    try:
        # Restoran var mı kontrol et
        restaurant_check = await fetch_one(
            "SELECT id FROM restaurants WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);",
            restaurant_id
        )
        if not restaurant_check:
            return False, "Restoran bulunamadı."
        
        # Email unique kontrolü
        if email:
            existing = await fetch_one(
                "SELECT id FROM restaurants WHERE email = $1 AND id != $2 AND (deleted IS NULL OR deleted = FALSE);",
                email, restaurant_id
            )
            if existing:
                return False, "Bu email adresi başka bir restoran tarafından kullanılıyor."
        
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
        if name is not None:
            update_fields.append(f"name = ${i}")
            params.append(name)
            i += 1
        if contact_person is not None:
            update_fields.append(f"contact_person = ${i}")
            params.append(contact_person)
            i += 1
        if tax_number is not None:
            update_fields.append(f"tax_number = ${i}")
            params.append(tax_number)
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
            from datetime import time
            h, m = opening_hour.split(":")
            update_fields.append(f"opening_hour = ${i}")
            params.append(time(int(h), int(m)))
            i += 1
        if closing_hour is not None:
            from datetime import time
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
            return False, "Güncellenecek alan bulunamadı."
        
        params.append(restaurant_id)
        query = f"UPDATE restaurants SET {', '.join(update_fields)} WHERE id = ${i};"
        result = await execute(query, *params)
        
        if result.endswith(" 0"):
            return False, "Restoran güncellenemedi."
        
        return True, None
        
    except Exception as e:
        return False, f"Restoran güncellenirken hata oluştu: {str(e)}"


# === GET RESTAURANT PACKAGE STATUS ===
async def get_support_restaurant_package(
    restaurant_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi için restoran paket durumunu getirir (Modül 3)
    Günlük paket bilgisi
    """
    try:
        # Restoran var mı kontrol et
        restaurant_check = await fetch_one(
            "SELECT id FROM restaurants WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);",
            restaurant_id
        )
        if not restaurant_check:
            return False, "Restoran bulunamadı."
        
        # Paket durumunu getir
        package_success, package_data, package_error = await restaurant_package_price_service.get_restaurant_package_status(restaurant_id)
        
        if not package_success:
            return False, package_error or "Paket durumu getirilemedi."
        
        return True, package_data
        
    except Exception as e:
        return False, f"Restoran paket durumu getirilirken hata oluştu: {str(e)}"

