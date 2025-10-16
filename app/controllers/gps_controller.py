from ..models.gps_model import GPSUpdateRequest, GPSData
from ..utils.database_async import fetch_one, fetch_all

async def upsert_location(req: GPSUpdateRequest):
    """
    Create if driver not exists; otherwise update instantly.
    """
    query = """
        INSERT INTO gps_table (driver_id, latitude, longitude, updated_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (driver_id)
        DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            updated_at = NOW()
        RETURNING driver_id, latitude, longitude, updated_at;
    """
    row = await fetch_one(query, req.driver_id, req.latitude, req.longitude)
    return {"success": True, "data": dict(row)}

async def get_all_latest():
    query = "SELECT * FROM gps_table ORDER BY updated_at DESC;"
    rows = await fetch_all(query)
    return {"success": True, "data": [dict(r) for r in rows]}
