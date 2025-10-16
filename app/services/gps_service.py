from typing import Any, Dict, Tuple, Optional, List
from ..utils.database_async import fetch_one, fetch_all

async def get_all_latest() -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Collect latest dataset from database.
    """
    query = "SELECT * FROM gps_table ORDER BY updated_at DESC;"
    rows = await fetch_all(query)
    if not rows:
        return None, "Latest locations not found"
    return rows ,None

async def upsert_location(driver_id: str, latitude: float, longitude: float) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Update location from database instantly.
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
    row = await fetch_one(query, driver_id, latitude, longitude)
    if not row:
        return None, "Location update failed"
    return row, None

async def get_latest(driver_id: str):
    """
    Get latest data from database for selected driver.
    """
    query = """
        SELECT * FROM gps_table WHERE driver_id = $1
    """
    row = await fetch_one(query, driver_id)
    if not row:
        return None, "Latest location not found"
    return row, None