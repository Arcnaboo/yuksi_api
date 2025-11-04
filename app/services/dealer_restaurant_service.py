from typing import List, Dict, Any, Tuple, Optional
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services import restaurant_service


async def dealer_create_and_link_restaurant(
    dealer_id: str,
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
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Bayi için yeni restoran oluşturur ve bayisine bağlar.
    Returns: (success, data, error_message)
    """
    try:
        # Önce restoranı oluştur
        restaurant_data, err = await restaurant_service.restaurant_register(
            email=email,
            password=password,
            phone=phone,
            country_id=country_id,
            name=name,
            contact_person=contact_person,
            tax_number=tax_number,
            address_line1=address_line1,
            address_line2=address_line2,
            state_id=state_id,
            city_id=city_id,
            latitude=latitude,
            longitude=longitude,
        )
        
        if err:
            return False, None, err
        
        restaurant_id = restaurant_data.get("id")
        if not restaurant_id:
            return False, None, "Restoran oluşturulamadı"
        
        # Şimdi bayisine bağla
        link_success, link_err = await dealer_link_existing_restaurant(dealer_id, restaurant_id)
        if not link_success:
            return False, None, f"Restoran oluşturuldu ancak bayisine bağlanamadı: {link_err}"
        
        return True, restaurant_data, None
        
    except Exception as e:
        return False, None, str(e)


async def dealer_link_existing_restaurant(
    dealer_id: str,
    restaurant_id: str,
) -> Tuple[bool, Optional[str]]:
    """
    Mevcut bir restoranı bayisine bağlar.
    Returns: (success, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Restoran kontrolü
        restaurant = await fetch_one("SELECT id, name FROM restaurants WHERE id = $1", restaurant_id)
        if not restaurant:
            return False, "Restoran bulunamadı"
        
        # Zaten bağlı mı kontrol et
        existing = await fetch_one(
            "SELECT id FROM dealer_restaurants WHERE dealer_id = $1 AND restaurant_id = $2",
            dealer_id, restaurant_id
        )
        if existing:
            return False, "Bu restoran zaten bu bayisine bağlı"
        
        # Bağla
        await execute(
            "INSERT INTO dealer_restaurants (dealer_id, restaurant_id) VALUES ($1, $2)",
            dealer_id, restaurant_id
        )
        
        return True, None
        
    except Exception as e:
        # Unique constraint hatası
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return False, "Bu restoran zaten bu bayisine bağlı"
        return False, str(e)


async def dealer_get_restaurants(
    dealer_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Bayinin bağlı olduğu restoranları listeler.
    Returns: (success, data_or_error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Restoranları getir
        rows = await fetch_all("""
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
                dr.created_at as linked_at,
                c.name as city_name,
                s.name as state_name,
                co.name as country_name
            FROM dealer_restaurants dr
            INNER JOIN restaurants r ON r.id = dr.restaurant_id
            LEFT JOIN cities c ON c.id = r.city_id
            LEFT JOIN states s ON s.id = r.state_id
            LEFT JOIN countries co ON co.id = r.country_id
            WHERE dr.dealer_id = $1
            ORDER BY dr.created_at DESC
            LIMIT $2 OFFSET $3
        """, dealer_id, limit, offset)
        
        result = []
        if rows:
            for row in rows:
                row_dict = dict(row)
                # UUID'leri string'e çevir
                if row_dict.get("id"):
                    row_dict["id"] = str(row_dict["id"])
                result.append(row_dict)
        
        return True, result
        
    except Exception as e:
        return False, str(e)


async def dealer_get_restaurant_profile(
    dealer_id: str,
    restaurant_id: str
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Bayinin kendisine ait bir restoranın detaylı profilini getirir.
    Returns: (success, profile_data_or_none, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, None, "Bayi bulunamadı"
        
        # Restoranın bayinin kendisine ait olup olmadığını kontrol et
        link = await fetch_one(
            "SELECT id FROM dealer_restaurants WHERE dealer_id = $1 AND restaurant_id = $2",
            dealer_id, restaurant_id
        )
        if not link:
            return False, None, "Bu restoran bu bayisine bağlı değil"
        
        # Restoran profilini getir
        row = await fetch_one("""
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
                dr.created_at as linked_at,
                c.name as city_name,
                s.name as state_name,
                co.name as country_name,
                c.id as city_id,
                s.id as state_id,
                co.id as country_id
            FROM restaurants r
            INNER JOIN dealer_restaurants dr ON dr.restaurant_id = r.id
            LEFT JOIN cities c ON c.id = r.city_id
            LEFT JOIN states s ON s.id = r.state_id
            LEFT JOIN countries co ON co.id = r.country_id
            WHERE r.id = $1 AND dr.dealer_id = $2
        """, restaurant_id, dealer_id)
        
        if not row:
            return False, None, "Restoran bulunamadı"
        
        # Profil formatında döndür
        profile = {
            "id": str(row["id"]),
            "email": row.get("email"),
            "phone": row.get("phone"),
            "name": row.get("name"),
            "contactPerson": row.get("contact_person") or "",
            "taxNumber": row.get("tax_number") or "",
            "addressLine1": row.get("address_line1") or "",
            "addressLine2": row.get("address_line2") or "",
            "fullAddress": f"{row.get('address_line1') or ''} {row.get('address_line2') or ''}".strip(),
            "latitude": float(row["latitude"]) if row.get("latitude") is not None else None,
            "longitude": float(row["longitude"]) if row.get("longitude") is not None else None,
            "openingHour": row["opening_hour"].strftime("%H:%M") if row.get("opening_hour") else None,
            "closingHour": row["closing_hour"].strftime("%H:%M") if row.get("closing_hour") else None,
            "createdAt": row["created_at"].isoformat() if row.get("created_at") else None,
            "linkedAt": row["linked_at"].isoformat() if row.get("linked_at") else None,
            "location": {
                "cityId": row["city_id"],
                "cityName": row.get("city_name"),
                "stateId": row["state_id"],
                "stateName": row.get("state_name"),
                "countryId": row["country_id"],
                "countryName": row.get("country_name"),
            } if row.get("city_id") else None
        }
        
        return True, profile, None
        
    except Exception as e:
        return False, None, str(e)


async def dealer_remove_restaurant(
    dealer_id: str,
    restaurant_id: str,
) -> Tuple[bool, Optional[str]]:
    """
    Bayiden restoran bağlantısını kaldırır (restoran silinmez, sadece bağlantı kesilir).
    Returns: (success, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Bağlantı var mı kontrol et
        link = await fetch_one(
            "SELECT id FROM dealer_restaurants WHERE dealer_id = $1 AND restaurant_id = $2",
            dealer_id, restaurant_id
        )
        if not link:
            return False, "Bu restoran bu bayisine bağlı değil"
        
        # Bağlantıyı kaldır
        await execute(
            "DELETE FROM dealer_restaurants WHERE dealer_id = $1 AND restaurant_id = $2",
            dealer_id, restaurant_id
        )
        
        return True, None
        
    except Exception as e:
        return False, str(e)

