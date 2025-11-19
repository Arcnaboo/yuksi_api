from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.utils.database_async import fetch_one


def _validate_courier_id(courier_id: str) -> bool:
    """UUID kontrolü"""
    try:
        import uuid
        uuid.UUID(courier_id)
        return True
    except:
        return False


def _get_today_start() -> datetime:
    """Bugünün başlangıcı (UTC)"""
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


async def get_courier_earnings(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye kazanç verilerini getirir (toplam ve günlük)
    """
    if not _validate_courier_id(courier_id):
        return None
    
    today_start = _get_today_start()
    
    earnings_query = """
        SELECT 
            COALESCE(SUM(CASE WHEN status = 'teslim_edildi' THEN amount ELSE 0 END), 0) AS total_earnings,
            COALESCE(SUM(CASE WHEN status = 'teslim_edildi' AND updated_at >= $2 THEN amount ELSE 0 END), 0) AS daily_earnings
        FROM orders
        WHERE courier_id = $1
    """
    earnings_row = await fetch_one(earnings_query, courier_id, today_start)
    
    if not earnings_row:
        return None
    
    return {
        "total_earnings": round(float(earnings_row["total_earnings"]), 2),
        "daily_earnings": round(float(earnings_row["daily_earnings"]), 2)
    }


async def get_courier_distance(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye mesafe verilerini getirir (toplam ve günlük km)
    """
    if not _validate_courier_id(courier_id):
        return None
    
    today_start = _get_today_start()
    
    distance_query = """
        SELECT 
            COALESCE(SUM(
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
            ), 0) AS total_km,
            COALESCE(SUM(
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
        WHERE courier_id = $1
    """
    distance_row = await fetch_one(distance_query, courier_id, today_start)
    
    if not distance_row:
        return None
    
    return {
        "total_km": round(float(distance_row["total_km"]), 2),
        "daily_km": round(float(distance_row["daily_km"]), 2)
    }


async def get_courier_package(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye paket bilgilerini getirir (kalan gün ve faaliyet süresi)
    """
    if not _validate_courier_id(courier_id):
        return None
    
    package_query = """
        SELECT 
            s.start_date,
            s.end_date,
            p.duration_days,
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
        LIMIT 1
    """
    package_row = await fetch_one(package_query, courier_id)
    
    if not package_row:
        return {
            "remaining_days": 0,
            "total_activity_duration_days": 0,
            "total_activity_duration_hours": 0
        }
    
    remaining_days = int(package_row["remaining_days"]) if package_row["remaining_days"] else 0
    activity_days = float(package_row["activity_days"]) if package_row["activity_days"] else 0.0
    
    activity_days_int = int(activity_days)
    activity_hours = int((activity_days - activity_days_int) * 24)
    
    return {
        "remaining_days": remaining_days,
        "total_activity_duration_days": activity_days_int,
        "total_activity_duration_hours": activity_hours
    }


async def get_courier_work_hours(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye bugünkü çalışma saatlerini getirir
    """
    if not _validate_courier_id(courier_id):
        return None
    
    today_start = _get_today_start()
    
    today_work_hours_query = """
        WITH bounds AS (
            SELECT $1::uuid AS driver_id,
                   $2::timestamptz AS win_start,
                   NOW() AS win_end
        ),
        base_events AS (
            SELECT dpe.at_utc, dpe.is_online
            FROM driver_presence_events dpe, bounds b
            WHERE dpe.driver_id = b.driver_id
              AND dpe.at_utc >= b.win_start
              AND dpe.at_utc < b.win_end
        ),
        start_state AS (
            SELECT b.win_start AS at_utc,
                   COALESCE((
                     SELECT dpe.is_online
                     FROM driver_presence_events dpe
                     WHERE dpe.driver_id = b.driver_id
                       AND dpe.at_utc < b.win_start
                     ORDER BY dpe.at_utc DESC
                     LIMIT 1
                   ), FALSE) AS is_online
            FROM bounds b
        ),
        end_cap AS (
            SELECT b.win_end AS at_utc, FALSE AS is_online
            FROM bounds b
        ),
        timeline AS (
            SELECT * FROM base_events
            UNION ALL
            SELECT * FROM start_state
            UNION ALL
            SELECT * FROM end_cap
        ),
        ordered AS (
            SELECT
                at_utc,
                is_online,
                LEAD(at_utc) OVER (ORDER BY at_utc) AS next_at
            FROM timeline
        )
        SELECT
            COALESCE(
              SUM(
                CASE WHEN is_online AND next_at IS NOT NULL
                     THEN EXTRACT(EPOCH FROM (next_at - at_utc))
                     ELSE 0 END
              ), 0
            )::bigint AS online_seconds
        FROM ordered;
    """
    work_hours_row = await fetch_one(today_work_hours_query, courier_id, today_start)
    
    if not work_hours_row:
        return {
            "work_hours": 0,
            "work_minutes": 0
        }
    
    online_seconds = int(work_hours_row["online_seconds"]) if work_hours_row["online_seconds"] else 0
    work_hours = online_seconds // 3600
    work_minutes = (online_seconds % 3600) // 60
    
    return {
        "work_hours": work_hours,
        "work_minutes": work_minutes
    }


async def get_courier_activities(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye toplam aktivite sayısını getirir
    """
    if not _validate_courier_id(courier_id):
        return None
    
    activities_query = """
        SELECT 
            COUNT(CASE WHEN status = 'teslim_edildi' THEN 1 END) AS total_activities
        FROM orders
        WHERE courier_id = $1
    """
    activities_row = await fetch_one(activities_query, courier_id)
    
    if not activities_row:
        return None
    
    return {
        "total_activities": int(activities_row["total_activities"]) if activities_row["total_activities"] else 0
    }


async def get_courier_dashboard(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye dashboard verilerini getirir (DEPRECATED - ayrı endpoint'ler kullanılmalı).
    Geriye dönük uyumluluk için tutuluyor.
    """
    earnings = await get_courier_earnings(courier_id)
    distance = await get_courier_distance(courier_id)
    package = await get_courier_package(courier_id)
    work_hours = await get_courier_work_hours(courier_id)
    activities = await get_courier_activities(courier_id)
    
    if not all([earnings, distance, package, work_hours, activities]):
        return None
    
    return {
        **earnings,
        **distance,
        **package,
        **work_hours,
        **activities
    }

