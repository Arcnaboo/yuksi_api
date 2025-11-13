from typing import Dict, Any, List, Optional, Tuple
from app.utils.database_async import fetch_all, fetch_one


async def get_all_users(
    user_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Admin tarafından tüm kullanıcıları getirir (Courier, Restaurant, Admin, Dealer)
    
    Args:
        user_type: 'courier', 'restaurant', 'admin', 'dealer', 'all' (varsayılan: 'all')
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
            "dealers": []
        }
        totals = {
            "couriers": 0,
            "restaurants": 0,
            "admins": 0,
            "dealers": 0,
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
            """
            params = []
            
            if search:
                restaurant_query += """
                    WHERE (
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
                    WHERE (
                        LOWER(email) LIKE $1 OR
                        LOWER(name) LIKE $1 OR
                        LOWER(phone) LIKE $1 OR
                        LOWER(contact_person) LIKE $1
                    )
                """
                count_params = [f"%{search.lower()}%"]
                count_row = await fetch_one(count_query, *count_params)
            else:
                count_row = await fetch_one("SELECT COUNT(*) AS count FROM restaurants")
            
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

        # Total count
        totals["total"] = totals["couriers"] + totals["restaurants"] + totals["admins"] + totals["dealers"]

        return True, {
            "users": result,
            "totals": totals
        }

    except Exception as e:
        return False, str(e)

