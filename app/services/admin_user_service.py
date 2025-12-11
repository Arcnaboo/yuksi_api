from typing import Dict, Any, List, Optional, Tuple
from app.utils.database_async import fetch_all, fetch_one, execute


async def get_all_users(
    user_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Admin tarafından tüm kullanıcıları getirir (Courier, Restaurant, Admin, Dealer)
    
    Args:
        user_type: 'courier', 'restaurant', 'admin', 'dealer', 'support', 'corporate' 'all' (varsayılan: 'all')
        search: Email, name, phone üzerinde arama
        limit: Her tip için maksimum kayıt sayısı
        offset: Her tip için offset
    
    Returns:
        Tuple[bool, Dict[str, Any] | str]: (success, data veya error message)
    """
    try:
        result = {
            "couriers": [],
            "restaurants": [],
            "admins": [],
            "dealers": [],
            "supports":[],
            "corporates":[]
        }
        totals = {
            "couriers": 0,
            "restaurants": 0,
            "admins": 0,
            "dealers": 0,
            "supports":0,
            "corporates":0,
            "total": 0
        }

        # Search için WHERE clause hazırla
        search_clause = ""
        search_params = []
        if search:
            search_term = f"%{search.lower()}%"
            # Her tip için farklı search alanları
            # Courier: email, first_name, last_name, phone
            # Restaurant: email, name, phone
            # Admin: email, first_name, last_name
            # Dealer: email, name, surname, phone

        # Couriers
        if not user_type or user_type == "all" or user_type == "courier":
            courier_query = """
                SELECT
                    d.id AS userId,
                    d.first_name AS firstName,
                    d.last_name AS lastName,
                    d.email,
                    d.phone,
                    d.is_active AS isActive,
                    d.deleted,
                    d.deleted_at AS deletedAt,
                    d.created_at AS createdAt,
                    ob.country_id AS countryId,
                    c.name AS countryName,
                    ob.state_id AS stateId,
                    s.name AS stateName,
                    ob.working_type AS workingType,
                    ob.vehicle_type AS vehicleType,
                    ob.vehicle_capacity AS vehicleCapacity,
                    ob.vehicle_year AS vehicleYear
                FROM drivers d
                LEFT JOIN driver_onboarding ob ON ob.driver_id = d.id
                LEFT JOIN countries c ON c.id = ob.country_id
                LEFT JOIN states s ON s.id = ob.state_id
            """
            params = []
            
            if search:
                courier_query += """
                    WHERE (
                        LOWER(d.email) LIKE $1 OR
                        LOWER(d.first_name) LIKE $1 OR
                        LOWER(d.last_name) LIKE $1 OR
                        LOWER(d.phone) LIKE $1
                    )
                """
                params.append(f"%{search.lower()}%")
                courier_query += f" ORDER BY d.created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
            else:
                courier_query += " ORDER BY d.created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            courier_rows = await fetch_all(courier_query, *params)
            
            result["couriers"] = [
                {
                    "userId": str(r["userid"]),
                    "firstName": r.get("firstname"),
                    "lastName": r.get("lastname"),
                    "email": r.get("email"),
                    "phone": r.get("phone"),
                    "isActive": r.get("isactive"),
                    "deleted": r.get("deleted"),
                    "deletedAt": r.get("deletedat").isoformat() if r.get("deletedat") else None,
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None,
                    "countryId": r.get("countryid"),
                    "countryName": r.get("countryname"),
                    "stateId": r.get("stateid"),
                    "stateName": r.get("statename"),
                    "workingType": r.get("workingtype"),
                    "vehicleType": r.get("vehicletype"),
                    "vehicleCapacity": r.get("vehiclecapacity"),
                    "vehicleYear": r.get("vehicleyear")
                }
                for r in (courier_rows or [])
            ]
            
            # Count query for couriers
            count_query = "SELECT COUNT(*) AS count FROM drivers d"
            if search:
                count_query += """
                    WHERE (
                        LOWER(d.email) LIKE $1 OR
                        LOWER(d.first_name) LIKE $1 OR
                        LOWER(d.last_name) LIKE $1 OR
                        LOWER(d.phone) LIKE $1
                    )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM drivers")
            
            totals["couriers"] = count_row.get("count", 0) if count_row else 0

        # Restaurants
        if not user_type or user_type == "all" or user_type == "restaurant":
            restaurant_query = """
                SELECT
                    id AS userId,
                    email,
                    name,
                    contact_person AS contactPerson,
                    tax_number AS taxNumber,
                    phone,
                    address_line1 AS addressLine1,
                    address_line2 AS addressLine2,
                    latitude,
                    longitude,
                    opening_hour AS openingHour,
                    closing_hour AS closingHour,
                    created_at AS createdAt
                FROM restaurants
                WHERE (deleted IS NULL OR deleted = FALSE)
            """
            params = []
            
            if search:
                restaurant_query += """
                    AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(name) LIKE $1 OR
                        LOWER(phone) LIKE $1 OR
                        LOWER(contact_person) LIKE $1
                    )
                """
                params.append(f"%{search.lower()}%")
                restaurant_query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
            else:
                restaurant_query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            restaurant_rows = await fetch_all(restaurant_query, *params)
            
            result["restaurants"] = [
                {
                    "userId": str(r["userid"]),
                    "email": r.get("email"),
                    "name": r.get("name"),
                    "contactPerson": r.get("contactperson"),
                    "taxNumber": r.get("taxnumber"),
                    "phone": r.get("phone"),
                    "addressLine1": r.get("addressline1"),
                    "addressLine2": r.get("addressline2"),
                    "fullAddress": f"{r.get('addressline1') or ''} {r.get('addressline2') or ''}".strip(),
                    "latitude": float(r["latitude"]) if r.get("latitude") is not None else None,
                    "longitude": float(r["longitude"]) if r.get("longitude") is not None else None,
                    "openingHour": r.get("openinghour").strftime("%H:%M") if r.get("openinghour") else None,
                    "closingHour": r.get("closinghour").strftime("%H:%M") if r.get("closinghour") else None,
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None
                }
                for r in (restaurant_rows or [])
            ]
            
            # Count query for restaurants
            if search:
                count_query = """
                    SELECT COUNT(*) AS count FROM restaurants
                    WHERE (deleted IS NULL OR deleted = FALSE)
                      AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(name) LIKE $1 OR
                        LOWER(phone) LIKE $1 OR
                        LOWER(contact_person) LIKE $1
                      )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM restaurants WHERE (deleted IS NULL OR deleted = FALSE)")
            
            totals["restaurants"] = count_row.get("count", 0) if count_row else 0

        # Admins
        if not user_type or user_type == "all" or user_type == "admin":
            admin_query = """
                SELECT
                    id AS userId,
                    first_name AS firstName,
                    last_name AS lastName,
                    email,
                    created_at AS createdAt
                FROM system_admins
            """
            params = []
            
            if search:
                admin_query += """
                    WHERE (
                        LOWER(email) LIKE $1 OR
                        LOWER(first_name) LIKE $1 OR
                        LOWER(last_name) LIKE $1
                    )
                """
                params.append(f"%{search.lower()}%")
                admin_query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
            else:
                admin_query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            admin_rows = await fetch_all(admin_query, *params)
            
            result["admins"] = [
                {
                    "userId": str(r["userid"]),
                    "firstName": r.get("firstname"),
                    "lastName": r.get("lastname"),
                    "email": r.get("email"),
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None
                }
                for r in (admin_rows or [])
            ]
            
            # Count query for admins
            if search:
                count_query = """
                    SELECT COUNT(*) AS count FROM system_admins
                    WHERE (
                        LOWER(email) LIKE $1 OR
                        LOWER(first_name) LIKE $1 OR
                        LOWER(last_name) LIKE $1
                    )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM system_admins")
            
            totals["admins"] = count_row.get("count", 0) if count_row else 0

        # Dealers
        if not user_type or user_type == "all" or user_type == "dealer":
            dealer_query = """
                SELECT
                    d.id AS userId,
                    d.name,
                    d.surname,
                    d.email,
                    d.phone,
                    d.address,
                    d.account_type AS accountType,
                    d.country_id AS countryId,
                    c.name AS countryName,
                    d.city_id AS cityId,
                    ci.name AS cityName,
                    d.state_id AS stateId,
                    s.name AS stateName,
                    d.tax_office AS taxOffice,
                    d.tax_number AS taxNumber,
                    d.iban,
                    d.resume,
                    d.status,
                    d.created_at AS createdAt
                FROM dealers d
                LEFT JOIN countries c ON c.id = d.country_id
                LEFT JOIN cities ci ON ci.id = d.city_id
                LEFT JOIN states s ON s.id = d.state_id
            """
            params = []
            
            if search:
                dealer_query += """
                    WHERE (
                        LOWER(d.email) LIKE $1 OR
                        LOWER(d.name) LIKE $1 OR
                        LOWER(d.surname) LIKE $1 OR
                        LOWER(d.phone) LIKE $1
                    )
                """
                params.append(f"%{search.lower()}%")
                dealer_query += f" ORDER BY d.created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
            else:
                dealer_query += " ORDER BY d.created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            dealer_rows = await fetch_all(dealer_query, *params)
            
            result["dealers"] = [
                {
                    "userId": str(r["userid"]),
                    "name": r.get("name"),
                    "surname": r.get("surname"),
                    "email": r.get("email"),
                    "phone": r.get("phone"),
                    "address": r.get("address"),
                    "accountType": r.get("accounttype"),
                    "countryId": r.get("countryid"),
                    "countryName": r.get("countryname"),
                    "cityId": r.get("cityid"),
                    "cityName": r.get("cityname"),
                    "stateId": r.get("stateid"),
                    "stateName": r.get("statename"),
                    "taxOffice": r.get("taxoffice"),
                    "taxNumber": r.get("taxnumber"),
                    "iban": r.get("iban"),
                    "resume": r.get("resume"),
                    "status": r.get("status"),
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None
                }
                for r in (dealer_rows or [])
            ]
            
            # Count query for dealers
            if search:
                count_query = """
                    SELECT COUNT(*) AS count FROM dealers d
                    WHERE (
                        LOWER(d.email) LIKE $1 OR
                        LOWER(d.name) LIKE $1 OR
                        LOWER(d.surname) LIKE $1 OR
                        LOWER(d.phone) LIKE $1
                    )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM dealers")
            
            totals["dealers"] = count_row.get("count", 0) if count_row else 0

        #Support Users
        if not user_type or user_type == "all" or user_type == "support":
            support_query = """
                SELECT
                    id AS userId,
                    first_name AS firstName,
                    last_name AS lastName,
                    email,
                    phone,
                    is_active AS isActive,
                    access,
                    created_at AS createdAt
                FROM support_users
                WHERE (deleted IS NULL OR deleted = FALSE)
            """
            params = []
            
            # Apply search filter
            if search:
                support_query += """
                    AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(first_name) LIKE $1 OR
                        LOWER(last_name) LIKE $1 OR
                        LOWER(phone) LIKE $1
                    )
                """
                params.append(f"%{search.lower()}%")
                support_query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])

            else:
                support_query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            support_rows = await fetch_all(support_query, *params)
            
            result["supports"] = [
                {
                    "userId": str(r["userid"]),
                    "firstName": r.get("firstname"),
                    "lastName": r.get("lastname"),
                    "fullName": f"{r.get('firstname', '')} {r.get('lastname', '')}".strip(),
                    "email": r.get("email"),
                    "phone": r.get("phone"),
                    "isActive": r.get("isactive"),
                    "access": r.get("access"),
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None
                }
                for r in (support_rows or [])
            ]
            
            # --- Count query for support users ---
            if search:
                count_query = """
                    SELECT COUNT(*) AS count FROM support_users
                    WHERE (deleted IS NULL OR deleted = FALSE)
                      AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(first_name) LIKE $1 OR
                        LOWER(last_name) LIKE $1 OR
                        LOWER(phone) LIKE $1
                      )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM support_users WHERE (deleted IS NULL OR deleted = FALSE)")
            
            totals["supports"] = count_row.get("count", 0) if count_row else 0

        # Corporate (Kurumsal Kullanıcılar)
        if not user_type or user_type == "all" or user_type == "corporate":
            corporate_query = """
                SELECT
                    id AS userId,
                    email,
                    phone,
                    first_name AS firstName,
                    last_name AS lastName,
                    is_active AS isActive,
                    commission_rate AS commissionRate,
                    country_id AS countryId,
                    state_id AS stateId,
                    city_id AS cityId,
                    address_line1 AS addressLine1,
                    address_line2 AS addressLine2,
                    latitude,
                    longitude,
                    tax_office AS taxOffice,
                    tax_number AS taxNumber,
                    iban,
                    resume,
                    created_at AS createdAt
                FROM corporate_users
                WHERE (deleted IS NULL OR deleted = FALSE)
            """
            params = []
            
            if search:
                corporate_query += """
                    AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(first_name) LIKE $1 OR
                        LOWER(last_name) LIKE $1 OR
                        LOWER(phone) LIKE $1 OR
                    )
                """
                params.append(f"%{search.lower()}%")
                corporate_query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
            else:
                corporate_query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
            
            corporate_rows = await fetch_all(corporate_query, *params)
            
            result["corporates"] = [
                {
                    "userId": str(r["userid"]),
                    "email": r.get("email"),
                    "name": r.get("name"),
                    "contactPerson": r.get("contactperson"),
                    "taxNumber": r.get("taxnumber"),
                    "phone": r.get("phone"),
                    "addressLine1": r.get("addressline1"),
                    "addressLine2": r.get("addressline2"),
                    "fullAddress": f"{r.get('addressline1') or ''} {r.get('addressline2') or ''}".strip(),
                    "latitude": float(r["latitude"]) if r.get("latitude") is not None else None,
                    "longitude": float(r["longitude"]) if r.get("longitude") is not None else None,
                    "openingHour": r.get("openinghour").strftime("%H:%M") if r.get("openinghour") else None,
                    "closingHour": r.get("closinghour").strftime("%H:%M") if r.get("closinghour") else None,
                    "createdAt": r.get("createdat").isoformat() if r.get("createdat") else None
                }
                for r in (corporate_rows or [])
            ]
            
            # Count query for corporate users
            if search:
                count_query = """
                    SELECT COUNT(*) AS count FROM corporate_users
                    WHERE (deleted IS NULL OR deleted = FALSE)
                      AND (
                        LOWER(email) LIKE $1 OR
                        LOWER(name) LIKE $1 OR
                        LOWER(phone) LIKE $1 OR
                        LOWER(contact_person) LIKE $1
                      )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM corporate_users WHERE (deleted IS NULL OR deleted = FALSE)")
            
            totals["corporates"] = count_row.get("count", 0) if count_row else 0

        # Total count
        # Bu kod kısım yerine başka kod yazıldı
        #totals["total"] = totals["couriers"] + totals["restaurants"] + totals["admins"] + totals["dealers"] + totals["supportUsers"] 
        
        totals["total"] = 0
        t_count = 0
        for key in totals:
            t_count += totals[key]
        totals["total"] = t_count

        return True, {
            "users": result,
            "totals": totals
        }

    except Exception as e:
        return False, str(e)


async def get_user_commission_rate(user_id: str) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Admin tarafından kullanıcının komisyon oranını getirme (ID'ye göre otomatik tespit: Corporate veya Dealer)
    """
    try:
        # Önce kurumsal kullanıcı tablosunda kontrol et
        corporate_user = await fetch_one("""
            SELECT 
                id, email, phone, first_name, last_name, is_active,
                commission_rate, commission_description,
                country_id, state_id, city_id,
                address_line1, address_line2, created_at
            FROM corporate_users
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
        """, user_id)
        
        if corporate_user:
            return True, {
                "userType": "corporate",
                "id": str(corporate_user["id"]),
                "email": corporate_user["email"],
                "phone": corporate_user["phone"],
                "firstName": corporate_user["first_name"],
                "lastName": corporate_user["last_name"],
                "isActive": corporate_user["is_active"],
                "commissionRate": float(corporate_user["commission_rate"]) if corporate_user.get("commission_rate") is not None else None,
                "commissionDescription": corporate_user.get("commission_description"),
                "countryId": int(corporate_user["country_id"]) if corporate_user.get("country_id") is not None else None,
                "stateId": int(corporate_user["state_id"]) if corporate_user.get("state_id") is not None else None,
                "cityId": int(corporate_user["city_id"]) if corporate_user.get("city_id") is not None else None,
                "addressLine1": corporate_user.get("address_line1"),
                "addressLine2": corporate_user.get("address_line2"),
                "createdAt": corporate_user["created_at"].isoformat() if corporate_user["created_at"] else None
            }
        
        # Kurumsal kullanıcı değilse, bayi tablosunda kontrol et
        dealer = await fetch_one("""
            SELECT 
                id, name, surname, email, address, account_type,
                country_id, city_id, state_id,
                tax_office, phone, tax_number, iban, resume, status,
                commission_rate, commission_description,
                created_at
            FROM dealers
            WHERE id = $1;
        """, user_id)
        
        if dealer:
            return True, {
                "userType": "dealer",
                "id": str(dealer["id"]),
                "name": dealer["name"],
                "surname": dealer["surname"],
                "email": dealer["email"],
                "address": dealer.get("address"),
                "accountType": dealer.get("account_type"),
                "countryId": int(dealer["country_id"]) if dealer.get("country_id") is not None else None,
                "cityId": int(dealer["city_id"]) if dealer.get("city_id") is not None else None,
                "stateId": int(dealer["state_id"]) if dealer.get("state_id") is not None else None,
                "taxOffice": dealer.get("tax_office"),
                "phone": dealer.get("phone"),
                "taxNumber": dealer.get("tax_number"),
                "iban": dealer.get("iban"),
                "resume": dealer.get("resume"),
                "status": dealer.get("status"),
                "commissionRate": float(dealer["commission_rate"]) if dealer.get("commission_rate") is not None else None,
                "commissionDescription": dealer.get("commission_description"),
                "createdAt": dealer["created_at"].isoformat() if dealer["created_at"] else None
            }
        
        # Diğer kullanıcı tipleri için kontrol
        restaurant = await fetch_one("SELECT id FROM restaurants WHERE id = $1;", user_id)
        if restaurant:
            return False, "Restoran kullanıcıları için komisyon oranı belirlenemez"

        driver = await fetch_one("SELECT id FROM drivers WHERE id = $1;", user_id)
        if driver:
            return False, "Kurye kullanıcıları için komisyon oranı belirlenemez"

        admin = await fetch_one("SELECT id FROM system_admins WHERE id = $1;", user_id)
        if admin:
            return False, "Admin kullanıcıları için komisyon oranı belirlenemez"

        default_user = await fetch_one("SELECT id FROM users WHERE id = $1;", user_id)
        if default_user:
            return False, "Bireysel kullanıcılar için komisyon oranı belirlenemez"

        # Hiçbirinde bulunamadı
        return False, "Kullanıcı bulunamadı"
        
    except Exception as e:
        return False, str(e)


async def set_user_commission_rate(user_id: str, commission_rate: float, description: Optional[str] = None) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Admin tarafından kullanıcıya komisyon oranı belirleme (ID'ye göre otomatik tespit: Corporate veya Dealer)
    POST ve PUT için kullanılır
    """
    try:
        # Önce kurumsal kullanıcı tablosunda kontrol et
        corporate_user = await fetch_one("""
            SELECT id, email, first_name, last_name
            FROM corporate_users
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
        """, user_id)
        
        if corporate_user:
            # Kurumsal kullanıcı bulundu
            result = await execute("""
                UPDATE corporate_users
                SET commission_rate = $1, commission_description = $2, updated_at = NOW()
                WHERE id = $3;
            """, commission_rate, description, user_id)
            
            if result.endswith(" 0"):
                return False, "Kurumsal kullanıcı bulunamadı"
            
            # Güncellenmiş kullanıcı bilgilerini getir
            updated_user = await fetch_one("""
                SELECT 
                    id, email, phone, first_name, last_name, is_active,
                    commission_rate, commission_description,
                    country_id, state_id, city_id,
                    address_line1, address_line2, created_at
                FROM corporate_users
                WHERE id = $1;
            """, user_id)
            
            return True, {
                "userType": "corporate",
                "id": str(updated_user["id"]),
                "email": updated_user["email"],
                "phone": updated_user["phone"],
                "firstName": updated_user["first_name"],
                "lastName": updated_user["last_name"],
                "isActive": updated_user["is_active"],
                "commissionRate": float(updated_user["commission_rate"]) if updated_user.get("commission_rate") is not None else None,
                "commissionDescription": updated_user.get("commission_description"),
                "countryId": int(updated_user["country_id"]) if updated_user.get("country_id") is not None else None,
                "stateId": int(updated_user["state_id"]) if updated_user.get("state_id") is not None else None,
                "cityId": int(updated_user["city_id"]) if updated_user.get("city_id") is not None else None,
                "addressLine1": updated_user.get("address_line1"),
                "addressLine2": updated_user.get("address_line2"),
                "createdAt": updated_user["created_at"].isoformat() if updated_user["created_at"] else None
            }
        
        # Kurumsal kullanıcı değilse, bayi tablosunda kontrol et
        dealer = await fetch_one("""
            SELECT id, name, surname, email
            FROM dealers
            WHERE id = $1;
        """, user_id)
        
        if dealer:
            # Bayi bulundu
            result = await execute("""
                UPDATE dealers
                SET commission_rate = $1, commission_description = $2
                WHERE id = $3;
            """, commission_rate, description, user_id)
            
            if result.endswith(" 0"):
                return False, "Bayi bulunamadı"
            
            # Güncellenmiş bayi bilgilerini getir
            updated_dealer = await fetch_one("""
                SELECT 
                    id, name, surname, email, address, account_type,
                    country_id, city_id, state_id,
                    tax_office, phone, tax_number, iban, resume, status,
                    commission_rate, commission_description,
                    created_at
                FROM dealers
                WHERE id = $1;
            """, user_id)
            
            return True, {
                "userType": "dealer",
                "id": str(updated_dealer["id"]),
                "name": updated_dealer["name"],
                "surname": updated_dealer["surname"],
                "email": updated_dealer["email"],
                "address": updated_dealer.get("address"),
                "accountType": updated_dealer.get("account_type"),
                "countryId": int(updated_dealer["country_id"]) if updated_dealer.get("country_id") is not None else None,
                "cityId": int(updated_dealer["city_id"]) if updated_dealer.get("city_id") is not None else None,
                "stateId": int(updated_dealer["state_id"]) if updated_dealer.get("state_id") is not None else None,
                "taxOffice": updated_dealer.get("tax_office"),
                "phone": updated_dealer.get("phone"),
                "taxNumber": updated_dealer.get("tax_number"),
                "iban": updated_dealer.get("iban"),
                "resume": updated_dealer.get("resume"),
                "status": updated_dealer.get("status"),
                "commissionRate": float(updated_dealer["commission_rate"]) if updated_dealer.get("commission_rate") is not None else None,
                "commissionDescription": updated_dealer.get("commission_description"),
                "createdAt": updated_dealer["created_at"].isoformat() if updated_dealer["created_at"] else None
            }
        
        # Diğer kullanıcı tipleri için kontrol (veya hata döndür)
        restaurant = await fetch_one("SELECT id FROM restaurants WHERE id = $1;", user_id)
        if restaurant:
            return False, "Restoran kullanıcıları için komisyon oranı belirlenemez"

        driver = await fetch_one("SELECT id FROM drivers WHERE id = $1;", user_id)
        if driver:
            return False, "Kurye kullanıcıları için komisyon oranı belirlenemez"

        admin = await fetch_one("SELECT id FROM system_admins WHERE id = $1;", user_id)
        if admin:
            return False, "Admin kullanıcıları için komisyon oranı belirlenemez"

        default_user = await fetch_one("SELECT id FROM users WHERE id = $1;", user_id)
        if default_user:
            return False, "Bireysel kullanıcılar için komisyon oranı belirlenemez"

        # Hiçbirinde bulunamadı
        return False, "Kullanıcı bulunamadı"
        
    except Exception as e:
        return False, str(e)


async def get_all_users_commissions(
    limit: int = 50,
    offset: int = 0,
    user_type: Optional[str] = None
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Admin tarafından tüm kullanıcıların (Corporate ve Dealer) komisyon oranlarını getirir
    
    Args:
        limit: Maksimum kayıt sayısı
        offset: Offset değeri
        user_type: 'corporate', 'dealer', veya None (hepsi)
    
    Returns:
        Tuple[bool, Dict[str, Any] | str]: (success, data veya error message)
    """
    try:
        result = {
            "corporate": [],
            "dealer": []
        }
        totals = {
            "corporate": 0,
            "dealer": 0,
            "total": 0
        }

        # Corporate Users
        if not user_type or user_type == "corporate":
            corporate_query = """
                SELECT 
                    id, email, phone, first_name, last_name, is_active,
                    commission_rate, commission_description,
                    country_id, state_id, city_id,
                    address_line1, address_line2, created_at
                FROM corporate_users
                WHERE (deleted IS NULL OR deleted = FALSE)
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2;
            """
            corporate_rows = await fetch_all(corporate_query, limit, offset)
            
            result["corporate"] = [
                {
                    "id": str(r["id"]),
                    "email": r["email"],
                    "phone": r["phone"],
                    "firstName": r["first_name"],
                    "lastName": r["last_name"],
                    "isActive": r["is_active"],
                    "commissionRate": float(r["commission_rate"]) if r.get("commission_rate") is not None else None,
                    "commissionDescription": r.get("commission_description"),
                    "countryId": int(r["country_id"]) if r.get("country_id") is not None else None,
                    "stateId": int(r["state_id"]) if r.get("state_id") is not None else None,
                    "cityId": int(r["city_id"]) if r.get("city_id") is not None else None,
                    "addressLine1": r.get("address_line1"),
                    "addressLine2": r.get("address_line2"),
                    "createdAt": r["created_at"].isoformat() if r["created_at"] else None
                }
                for r in (corporate_rows or [])
            ]
            
            # Count query for corporate
            count_row = await fetch_one("""
                SELECT COUNT(*) AS count 
                FROM corporate_users
                WHERE (deleted IS NULL OR deleted = FALSE);
            """)
            totals["corporate"] = count_row.get("count", 0) if count_row else 0

        # Dealers
        if not user_type or user_type == "dealer":
            dealer_query = """
                SELECT 
                    id, name, surname, email, address, account_type,
                    country_id, city_id, state_id,
                    tax_office, phone, tax_number, iban, resume, status,
                    commission_rate, commission_description,
                    created_at
                FROM dealers
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2;
            """
            dealer_rows = await fetch_all(dealer_query, limit, offset)
            
            result["dealer"] = [
                {
                    "id": str(r["id"]),
                    "name": r["name"],
                    "surname": r["surname"],
                    "email": r["email"],
                    "address": r.get("address"),
                    "accountType": r.get("account_type"),
                    "countryId": int(r["country_id"]) if r.get("country_id") is not None else None,
                    "cityId": int(r["city_id"]) if r.get("city_id") is not None else None,
                    "stateId": int(r["state_id"]) if r.get("state_id") is not None else None,
                    "taxOffice": r.get("tax_office"),
                    "phone": r.get("phone"),
                    "taxNumber": r.get("tax_number"),
                    "iban": r.get("iban"),
                    "resume": r.get("resume"),
                    "status": r.get("status"),
                    "commissionRate": float(r["commission_rate"]) if r.get("commission_rate") is not None else None,
                    "commissionDescription": r.get("commission_description"),
                    "createdAt": r["created_at"].isoformat() if r["created_at"] else None
                }
                for r in (dealer_rows or [])
            ]
            
            # Count query for dealers
            count_row = await fetch_one("SELECT COUNT(*) AS count FROM dealers")
            totals["dealer"] = count_row.get("count", 0) if count_row else 0

        # Total count
        totals["total"] = totals["corporate"] + totals["dealer"]

        return True, {
            "users": result,
            "totals": totals
        }

    except Exception as e:
        return False, str(e)

