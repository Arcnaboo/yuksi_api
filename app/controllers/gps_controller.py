from ..models.gps_model import GPSUpdateRequest
from ..services import gps_service as svc
from ..services.courier_route_websocket_service import calculate_and_push_route
import asyncio
import logging

logger = logging.getLogger(__name__)

async def upsert_location(req: GPSUpdateRequest):
    """
    Create if driver not exists; otherwise update instantly.
    GPS güncellemesi geldiğinde otomatik olarak rota hesaplanır ve WebSocket ile push edilir.
    """
    result, err = await svc.upsert_location(req.driver_id, req.latitude, req.longitude)

    if err:
        return { "succes": False, "message": err, "data": {} }
    
    # GPS güncellemesi başarılı oldu, arka planda rota hesapla (non-blocking)
    # Background task olarak çalıştır ki GPS response gecikmesin
    try:
        asyncio.create_task(calculate_and_push_route(req.driver_id))
    except Exception as e:
        logger.error(f"Error triggering route calculation for courier {req.driver_id}: {e}")
    
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

