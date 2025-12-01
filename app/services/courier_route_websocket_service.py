"""
Kurye rota WebSocket servisi - GPS güncellemesi geldiğinde otomatik rota hesaplar ve push eder
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.utils.database_async import fetch_one
from app.services.map_service import create_courier_route_serpapi
from app.utils.websocket_manager import websocket_manager
import logging

logger = logging.getLogger(__name__)


async def get_active_order_for_courier(courier_id: str) -> Optional[Dict[str, Any]]:
    """
    Kuryenin aktif order'ını getirir (KURYEYE_VERILDI veya YOLDA status'unda)
    """
    try:
        row = await fetch_one("""
            SELECT 
                id,
                status,
                pickup_lat,
                pickup_lng,
                dropoff_lat,
                dropoff_lng
            FROM orders
            WHERE courier_id = $1::uuid
              AND status IN ('kuryeye_verildi', 'yolda')
            ORDER BY created_at DESC
            LIMIT 1
        """, courier_id)
        
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Error getting active order for courier {courier_id}: {e}")
        return None


async def calculate_and_push_route(courier_id: str):
    """
    Kurye için rota hesapla ve WebSocket ile push et
    """
    try:
        # WebSocket bağlantısı var mı kontrol et
        if not websocket_manager.has_connection(courier_id):
            return  # Bağlantı yoksa işlem yapma
        
        # Aktif order var mı kontrol et
        active_order = await get_active_order_for_courier(courier_id)
        if not active_order:
            return  # Aktif order yoksa işlem yapma
        
        order_id = str(active_order["id"])
        
        # Rota hesapla
        try:
            route_data = await create_courier_route_serpapi(courier_id, order_id)
            
            # WebSocket ile push et
            message = {
                "type": "route_update",
                "order_id": order_id,
                "data": route_data
            }
            
            await websocket_manager.send_to_courier(courier_id, message)
            logger.info(f"Route pushed to courier {courier_id} for order {order_id}")
            
        except HTTPException as e:
            logger.error(f"HTTP error calculating route for courier {courier_id}, order {order_id}: {e.detail}")
            # Hata durumunda da frontend'e bilgi ver
            error_message = {
                "type": "route_error",
                "order_id": order_id,
                "error": e.detail,
                "status_code": e.status_code
            }
            await websocket_manager.send_to_courier(courier_id, error_message)
        except Exception as e:
            logger.error(f"Error calculating route for courier {courier_id}, order {order_id}: {e}")
            # Hata durumunda da frontend'e bilgi ver
            error_message = {
                "type": "route_error",
                "order_id": order_id,
                "error": str(e)
            }
            await websocket_manager.send_to_courier(courier_id, error_message)
            
    except Exception as e:
        logger.error(f"Error in calculate_and_push_route for courier {courier_id}: {e}")

