from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.utils.database_async import fetch_one


async def get_courier_dashboard(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kurye dashboard verilerini getirir.
    """
    try:
        # UUID kontrolü
        import uuid
        uuid.UUID(courier_id)
    except:
        return None

    # Bugünün başlangıcı (Türkiye saati - UTC+3)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 1. Toplam kazanç ve günlük kazanç
    earnings_query = """
        SELECT 
            COALESCE(SUM(CASE WHEN status = 'teslim_edildi' THEN amount ELSE 0 END), 0) AS total_earnings,
            COALESCE(SUM(CASE WHEN status = 'teslim_edildi' AND updated_at >= $2 THEN amount ELSE 0 END), 0) AS daily_earnings,
            COUNT(CASE WHEN status = 'teslim_edildi' THEN 1 END) AS total_activities
        FROM orders
        WHERE courier_id = $1
    """
    earnings_row = await fetch_one(earnings_query, courier_id, today_start)
    
    total_earnings = float(earnings_row["total_earnings"]) if earnings_row else 0.0
    daily_earnings = float(earnings_row["daily_earnings"]) if earnings_row else 0.0
    total_activities = int(earnings_row["total_activities"]) if earnings_row else 0

    # 2. Mesafe hesaplamaları (Haversine formülü ile)
    # Pickup-dropoff arası mesafe (km)
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
    
    total_km = round(float(distance_row["total_km"]) if distance_row else 0.0, 2)
    daily_km = round(float(distance_row["daily_km"]) if distance_row else 0.0, 2)

    # 3. Paket bilgileri (kalan gün ve faaliyet süresi)
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
    
    remaining_days = int(package_row["remaining_days"]) if package_row and package_row["remaining_days"] else 0
    activity_days = float(package_row["activity_days"]) if package_row and package_row["activity_days"] else 0.0
    
    # Faaliyet süresi: gün + saat formatı
    activity_days_int = int(activity_days)
    activity_hours = int((activity_days - activity_days_int) * 24)

    # 4. Bugünkü çalışma saati (driver_presence_events'tan)
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
    
    online_seconds = int(work_hours_row["online_seconds"]) if work_hours_row else 0
    work_hours = online_seconds // 3600
    work_minutes = (online_seconds % 3600) // 60

    return {
        "total_earnings": round(total_earnings, 2),
        "daily_earnings": round(daily_earnings, 2),
        "total_activity_duration_days": activity_days_int,
        "total_activity_duration_hours": activity_hours,
        "remaining_days": remaining_days,
        "daily_km": daily_km,
        "total_km": total_km,
        "total_activities": total_activities,
        "work_hours": work_hours,
        "work_minutes": work_minutes
    }

