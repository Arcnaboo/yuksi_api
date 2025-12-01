"""
WebSocket endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.utils.websocket_manager import websocket_manager
from app.services.courier_route_websocket_service import calculate_and_push_route
from app.utils.security import decode_jwt
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/courier/{courier_id}/route")
async def websocket_courier_route(
    websocket: WebSocket,
    courier_id: str,
    token: str = Query(..., description="JWT token for authentication")
):
    """
    Kurye için rota güncellemelerini almak için WebSocket endpoint
    
    Kullanım:
    1. WebSocket bağlantısı aç: ws://your-api/ws/courier/{courier_id}/route?token=JWT_TOKEN
    2. Backend otomatik olarak GPS güncellemesi geldiğinde rota hesaplar ve push eder
    3. Frontend sadece mesajları dinler ve gösterir
    
    Mesaj formatı:
    {
        "type": "route_update",
        "order_id": "uuid",
        "data": {
            "order_id": "uuid",
            "route_polyline": "...",
            "distance": 1234.5,
            "duration": 123.4,
            "driver": {"lat": 39.9, "lgn": 32.8},
            "pickup": {"lat": 39.9, "lgn": 32.8},
            "dropoff": {"lat": 39.9, "lgn": 32.8},
            "steps": [...]
        }
    }
    """
    try:
        # JWT token kontrolü
        try:
            payload = decode_jwt(token)
            if not payload:
                await websocket.close(code=1008, reason="Invalid token")
                return
            
            # Token'dan courier_id'yi al ve doğrula
            token_courier_id = payload.get("sub") or payload.get("userId")
            if not token_courier_id or str(token_courier_id) != courier_id:
                await websocket.close(code=1008, reason="Token does not match courier_id")
                return
                
        except Exception as e:
            logger.error(f"JWT decode error: {e}")
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # WebSocket bağlantısını ekle
        await websocket_manager.connect(websocket, courier_id)
        
        # İlk bağlantıda mevcut rota varsa hesapla ve gönder
        await calculate_and_push_route(courier_id)
        
        # Bağlantıyı dinle (frontend'den mesaj gelirse işle)
        try:
            while True:
                # Frontend'den mesaj bekle (opsiyonel - ping/pong için kullanılabilir)
                data = await websocket.receive_text()
                
                # Ping mesajı gelirse pong gönder
                if data == "ping":
                    await websocket.send_text("pong")
                    
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, courier_id)
            logger.info(f"WebSocket disconnected for courier {courier_id}")
            
    except Exception as e:
        logger.error(f"WebSocket error for courier {courier_id}: {e}")
        websocket_manager.disconnect(websocket, courier_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

