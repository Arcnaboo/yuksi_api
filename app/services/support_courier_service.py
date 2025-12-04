from typing import Dict, Any, Tuple, List, Optional
from app.utils.database_async import fetch_one, fetch_all


# === LIST COURIERS ===
async def get_support_couriers(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Çağrı merkezi için tüm kuryeleri listeler (Modül 1)
    """
    try:
        filters = []
        params = []
        i = 1
        
        # Silinmemiş kuryeleri getir
        filters.append("(d.deleted IS NULL OR d.deleted = FALSE)")
        
        # Arama filtresi
        if search:
            filters.append(f"""
                (
                    LOWER(d.first_name) LIKE ${i} OR
                    LOWER(d.last_name) LIKE ${i} OR
                    LOWER(d.email) LIKE ${i} OR
                    LOWER(d.phone) LIKE ${i}
                )
            """)
            params.append(f"%{search.lower()}%")
            i += 1
        
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        params.extend([limit, offset])
        
        query = f"""
        SELECT
            d.id,
            d.first_name,
            d.last_name,
            d.email,
            d.phone,
            d.created_at,
            d.is_active,
            d.deleted,
            d.deleted_at,
            ob.country_id,
            ob.dealer_id,
            COALESCE(ds.online, FALSE) AS is_online,
            c.name AS country_name,
            ob.state_id,
            s.name AS state_name,
            ob.working_type,
            ob.vehicle_type,
            ob.vehicle_capacity,
            ob.vehicle_year,
            ob.step,
            g.latitude,
            g.longitude,
            g.updated_at AS location_updated_at
        FROM drivers d
        LEFT JOIN driver_onboarding ob ON ob.driver_id = d.id
        LEFT JOIN countries c ON c.id = ob.country_id
        LEFT JOIN states s ON s.id = ob.state_id
        LEFT JOIN driver_status ds ON ds.driver_id = d.id
        LEFT JOIN gps_table g ON g.driver_id = d.id
        {where_clause}
        ORDER BY d.created_at DESC
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
                "firstName": row_dict.get("first_name"),
                "lastName": row_dict.get("last_name"),
                "email": row_dict.get("email"),
                "phone": row_dict.get("phone"),
                "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
                "isActive": row_dict.get("is_active", False),
                "deleted": row_dict.get("deleted", False),
                "deletedAt": row_dict["deleted_at"].isoformat() if row_dict.get("deleted_at") else None,
                "countryId": row_dict.get("country_id"),
                "countryName": row_dict.get("country_name"),
                "dealerId": str(row_dict["dealer_id"]) if row_dict.get("dealer_id") else None,
                "isOnline": row_dict.get("is_online", False),
                "stateId": row_dict.get("state_id"),
                "stateName": row_dict.get("state_name"),
                "workingType": row_dict.get("working_type"),
                "vehicleType": row_dict.get("vehicle_type"),
                "vehicleCapacity": row_dict.get("vehicle_capacity"),
                "vehicleYear": row_dict.get("vehicle_year"),
                "step": row_dict.get("step"),
                "location": {
                    "latitude": float(row_dict["latitude"]) if row_dict.get("latitude") else None,
                    "longitude": float(row_dict["longitude"]) if row_dict.get("longitude") else None,
                    "updatedAt": row_dict["location_updated_at"].isoformat() if row_dict.get("location_updated_at") else None
                } if row_dict.get("latitude") or row_dict.get("longitude") else None
            })
        
        return True, formatted_rows
        
    except Exception as e:
        return False, f"Kurye listesi getirilirken hata oluştu: {str(e)}"


# === GET COURIER DETAIL ===
async def get_support_courier_detail(
    courier_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi için tek kurye detayını getirir (Modül 1)
    """
    try:
        query = """
        SELECT
            d.id,
            d.first_name,
            d.last_name,
            d.email,
            d.phone,
            d.created_at,
            d.is_active,
            d.deleted,
            d.deleted_at,
            ob.country_id,
            ob.dealer_id,
            COALESCE(ds.online, FALSE) AS is_online,
            c.name AS country_name,
            ob.state_id,
            s.name AS state_name,
            ob.working_type,
            ob.vehicle_type,
            ob.vehicle_capacity,
            ob.vehicle_year,
            ob.step,
            ob.contract_confirmed,
            g.latitude,
            g.longitude,
            g.updated_at AS location_updated_at
        FROM drivers d
        LEFT JOIN driver_onboarding ob ON ob.driver_id = d.id
        LEFT JOIN countries c ON c.id = ob.country_id
        LEFT JOIN states s ON s.id = ob.state_id
        LEFT JOIN driver_status ds ON ds.driver_id = d.id
        LEFT JOIN gps_table g ON g.driver_id = d.id
        WHERE d.id = $1 AND (d.deleted IS NULL OR d.deleted = FALSE);
        """
        
        row = await fetch_one(query, courier_id)
        
        if not row:
            return False, "Kurye bulunamadı."
        
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        return True, {
            "id": str(row_dict["id"]),
            "firstName": row_dict.get("first_name"),
            "lastName": row_dict.get("last_name"),
            "email": row_dict.get("email"),
            "phone": row_dict.get("phone"),
            "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
            "isActive": row_dict.get("is_active", False),
            "deleted": row_dict.get("deleted", False),
            "deletedAt": row_dict["deleted_at"].isoformat() if row_dict.get("deleted_at") else None,
            "countryId": row_dict.get("country_id"),
            "countryName": row_dict.get("country_name"),
            "dealerId": str(row_dict["dealer_id"]) if row_dict.get("dealer_id") else None,
            "isOnline": row_dict.get("is_online", False),
            "stateId": row_dict.get("state_id"),
            "stateName": row_dict.get("state_name"),
            "workingType": row_dict.get("working_type"),
            "vehicleType": row_dict.get("vehicle_type"),
            "vehicleCapacity": row_dict.get("vehicle_capacity"),
            "vehicleYear": row_dict.get("vehicle_year"),
            "step": row_dict.get("step"),
            "contractConfirmed": row_dict.get("contract_confirmed"),
            "location": {
                "latitude": float(row_dict["latitude"]) if row_dict.get("latitude") else None,
                "longitude": float(row_dict["longitude"]) if row_dict.get("longitude") else None,
                "updatedAt": row_dict["location_updated_at"].isoformat() if row_dict.get("location_updated_at") else None
            } if row_dict.get("latitude") or row_dict.get("longitude") else None
        }
        
    except Exception as e:
        return False, f"Kurye detayı getirilirken hata oluştu: {str(e)}"


# === GET COURIER PACKAGES (ORDERS) ===
async def get_support_courier_packages(
    courier_id: str,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Çağrı merkezi için kuryenin taşıdığı paketleri (siparişleri) getirir (Modül 1)
    """
    try:
        filters = ["o.courier_id = $1"]
        params = [courier_id]
        i = 2
        
        if status:
            filters.append(f"o.status = ${i}")
            params.append(status)
            i += 1
        
        where_clause = f"WHERE {' AND '.join(filters)}"
        params.extend([limit, offset])
        
        query = f"""
        SELECT
            o.id,
            o.code,
            o.customer,
            o.phone,
            o.address,
            o.delivery_address,
            o.type,
            o.status,
            o.amount,
            o.carrier_type,
            o.vehicle_type,
            o.cargo_type,
            o.special_requests,
            o.pickup_lat,
            o.pickup_lng,
            o.dropoff_lat,
            o.dropoff_lng,
            o.created_at,
            o.updated_at,
            r.id AS restaurant_id,
            r.name AS restaurant_name,
            r.phone AS restaurant_phone
        FROM orders o
        LEFT JOIN restaurants r ON r.id = o.restaurant_id
        {where_clause}
        ORDER BY o.created_at DESC
        LIMIT ${i} OFFSET ${i + 1};
        """
        
        rows = await fetch_all(query, *params)
        
        if not rows:
            return True, []
        
        formatted_rows = []
        for row in rows:
            row_dict = dict(row) if not isinstance(row, dict) else row
            formatted_rows.append({
                "id": str(row_dict["id"]),
                "code": row_dict.get("code"),
                "customer": row_dict.get("customer"),
                "phone": row_dict.get("phone"),
                "address": row_dict.get("address"),
                "deliveryAddress": row_dict.get("delivery_address"),
                "type": row_dict.get("type"),
                "status": row_dict.get("status"),
                "amount": float(row_dict["amount"]) if row_dict.get("amount") else None,
                "carrierType": row_dict.get("carrier_type"),
                "vehicleType": row_dict.get("vehicle_type"),
                "cargoType": row_dict.get("cargo_type"),
                "specialRequests": row_dict.get("special_requests"),
                "pickupCoordinates": {
                    "latitude": float(row_dict["pickup_lat"]) if row_dict.get("pickup_lat") else None,
                    "longitude": float(row_dict["pickup_lng"]) if row_dict.get("pickup_lng") else None
                } if row_dict.get("pickup_lat") or row_dict.get("pickup_lng") else None,
                "dropoffCoordinates": {
                    "latitude": float(row_dict["dropoff_lat"]) if row_dict.get("dropoff_lat") else None,
                    "longitude": float(row_dict["dropoff_lng"]) if row_dict.get("dropoff_lng") else None
                } if row_dict.get("dropoff_lat") or row_dict.get("dropoff_lng") else None,
                "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
                "updatedAt": row_dict["updated_at"].isoformat() if row_dict.get("updated_at") else None,
                "restaurant": {
                    "id": str(row_dict["restaurant_id"]) if row_dict.get("restaurant_id") else None,
                    "name": row_dict.get("restaurant_name"),
                    "phone": row_dict.get("restaurant_phone")
                } if row_dict.get("restaurant_id") else None
            })
        
        return True, formatted_rows
        
    except Exception as e:
        return False, f"Kurye paketleri getirilirken hata oluştu: {str(e)}"


# === GET COURIER LOCATION ===
async def get_support_courier_location(
    courier_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi için kuryenin konumunu getirir (Modül 1)
    """
    try:
        query = """
        SELECT
            g.latitude,
            g.longitude,
            g.updated_at,
            COALESCE(ds.online, FALSE) AS is_online
        FROM gps_table g
        LEFT JOIN driver_status ds ON ds.driver_id = g.driver_id
        WHERE g.driver_id = $1;
        """
        
        row = await fetch_one(query, courier_id)
        
        if not row:
            return False, "Kurye konumu bulunamadı."
        
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        return True, {
            "latitude": float(row_dict["latitude"]) if row_dict.get("latitude") else None,
            "longitude": float(row_dict["longitude"]) if row_dict.get("longitude") else None,
            "updatedAt": row_dict["updated_at"].isoformat() if row_dict.get("updated_at") else None,
            "isOnline": row_dict.get("is_online", False)
        }
        
    except Exception as e:
        return False, f"Kurye konumu getirilirken hata oluştu: {str(e)}"


# === GET COURIER STATS ===
async def get_support_courier_stats(
    courier_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi için kurye istatistiklerini getirir (Modül 1)
    - Kaç paket attı (teslim edilen)
    - Toplam mesafe
    - Günlük mesafe
    - Paket bilgileri (subscription)
    """
    try:
        # Kurye var mı kontrol et
        courier_check = await fetch_one(
            "SELECT id FROM drivers WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);",
            courier_id
        )
        if not courier_check:
            return False, "Kurye bulunamadı."
        
        # Teslim edilen paket sayısı
        delivered_count_query = """
        SELECT COUNT(*) as count
        FROM orders
        WHERE courier_id = $1 AND status = 'teslim_edildi';
        """
        delivered_row = await fetch_one(delivered_count_query, courier_id)
        delivered_count = delivered_row["count"] if delivered_row else 0
        
        # Toplam mesafe (km)
        total_distance_query = """
        SELECT COALESCE(SUM(
            CASE 
                WHEN status = 'teslim_edildi' 
                    AND pickup_lat IS NOT NULL 
                    AND pickup_lng IS NOT NULL 
                    AND dropoff_lat IS NOT NULL 
                    AND dropoff_lng IS NOT NULL
                THEN (
                    6371 * acos(
                        LEAST(1.0,
                            cos(radians(pickup_lat)) * 
                            cos(radians(dropoff_lat)) * 
                            cos(radians(dropoff_lng) - radians(pickup_lng)) + 
                            sin(radians(pickup_lat)) * 
                            sin(radians(dropoff_lat))
                        )
                    )
                )
                ELSE 0
            END
        ), 0) AS total_km
        FROM orders
        WHERE courier_id = $1;
        """
        distance_row = await fetch_one(total_distance_query, courier_id)
        total_km = round(float(distance_row["total_km"]), 2) if distance_row and distance_row.get("total_km") else 0.0
        
        # Günlük mesafe (bugün)
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        daily_distance_query = """
        SELECT COALESCE(SUM(
            CASE 
                WHEN status = 'teslim_edildi' 
                    AND updated_at >= $2
                    AND pickup_lat IS NOT NULL 
                    AND pickup_lng IS NOT NULL 
                    AND dropoff_lat IS NOT NULL 
                    AND dropoff_lng IS NOT NULL
                THEN (
                    6371 * acos(
                        LEAST(1.0,
                            cos(radians(pickup_lat)) * 
                            cos(radians(dropoff_lat)) * 
                            cos(radians(dropoff_lng) - radians(pickup_lng)) + 
                            sin(radians(pickup_lat)) * 
                            sin(radians(dropoff_lat))
                        )
                    )
                )
                ELSE 0
            END
        ), 0) AS daily_km
        FROM orders
        WHERE courier_id = $1;
        """
        daily_distance_row = await fetch_one(daily_distance_query, courier_id, today_start)
        daily_km = round(float(daily_distance_row["daily_km"]), 2) if daily_distance_row and daily_distance_row.get("daily_km") else 0.0
        
        # Paket bilgileri (subscription)
        package_query = """
        SELECT 
            s.start_date,
            s.end_date,
            p.duration_days,
            p.package_name,
            p.price,
            CASE 
                WHEN s.end_date > NOW() THEN 
                    GREATEST(0, EXTRACT(EPOCH FROM (s.end_date - NOW())) / 86400)
                ELSE 0
            END AS remaining_days,
            CASE 
                WHEN s.start_date IS NOT NULL THEN 
                    EXTRACT(EPOCH FROM (NOW() - s.start_date)) / 86400
                ELSE 0
            END AS activity_days
        FROM courier_package_subscriptions s
        JOIN courier_packages p ON p.id = s.package_id
        WHERE s.courier_id = $1::uuid
          AND s.is_active = TRUE
          AND s.deleted_at IS NULL
          AND s.start_date <= NOW()
          AND s.end_date > NOW()
        ORDER BY s.end_date DESC
        LIMIT 1;
        """
        package_row = await fetch_one(package_query, courier_id)
        
        package_info = None
        if package_row:
            activity_days = float(package_row["activity_days"]) if package_row.get("activity_days") else 0.0
            activity_days_int = int(activity_days)
            activity_hours = int((activity_days - activity_days_int) * 24)
            
            package_info = {
                "packageName": package_row.get("package_name"),
                "durationDays": package_row.get("duration_days"),
                "price": float(package_row["price"]) if package_row.get("price") else None,
                "startDate": package_row["start_date"].isoformat() if package_row.get("start_date") else None,
                "endDate": package_row["end_date"].isoformat() if package_row.get("end_date") else None,
                "remainingDays": int(package_row["remaining_days"]) if package_row.get("remaining_days") else 0,
                "activityDays": activity_days_int,
                "activityHours": activity_hours
            }
        
        # Mola durumu (son online/offline event)
        break_status_query = """
        SELECT 
            is_online,
            at_utc
        FROM driver_presence_events
        WHERE driver_id = $1
        ORDER BY at_utc DESC
        LIMIT 1;
        """
        break_row = await fetch_one(break_status_query, courier_id)
        
        is_on_break = False
        last_status_change = None
        if break_row:
            is_on_break = not break_row.get("is_online", False)
            last_status_change = break_row["at_utc"].isoformat() if break_row.get("at_utc") else None
        
        return True, {
            "deliveredPackagesCount": delivered_count,
            "totalDistanceKm": total_km,
            "dailyDistanceKm": daily_km,
            "package": package_info,
            "isOnBreak": is_on_break,
            "lastStatusChange": last_status_change
        }
        
    except Exception as e:
        return False, f"Kurye istatistikleri getirilirken hata oluştu: {str(e)}"

