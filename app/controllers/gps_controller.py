from ..models.gps_model import GPSUpdateRequest, GPSData
from ..services import gps_service as svc

async def upsert_location(req: GPSUpdateRequest):
    """
    Create if driver not exists; otherwise update instantly.
    """
    result, err = await svc.upsert_location(req.driver_id, req.latitude, req.longitude)

    if err:
        return { "succes": False, "message": err, "data": {} }
    return { "succes": True, "message": "Updated location", "data": result}

async def get_all_latest():
    """
    Get all drivers latest locations.
    """
    result, err = await svc.get_all_latest()

    if err:
        return { "succes": False, "message": err, "data": {} }
    return { "succes": True, "message": "Latest locations retrieved", "data": result}

async def get_latest(driver_id: str):
    """
    Get a driver's latest location.
    """
    result, err = await svc.get_latest(driver_id)
    
    if err:
        return { "succes": False, "message": err, "data": {} }
    return { "succes": True, "message": "Latest location retrieved", "data": result}

