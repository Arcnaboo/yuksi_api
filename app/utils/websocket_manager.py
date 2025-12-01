"""
WebSocket bağlantılarını yönetmek için manager
"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket bağlantılarını yönetir"""
    
    def __init__(self):
        # courier_id -> Set[WebSocket] mapping
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, courier_id: str):
        """WebSocket bağlantısını ekle"""
        await websocket.accept()
        
        if courier_id not in self.active_connections:
            self.active_connections[courier_id] = set()
        
        self.active_connections[courier_id].add(websocket)
        logger.info(f"WebSocket connected for courier {courier_id}. Total connections: {len(self.active_connections[courier_id])}")
    
    def disconnect(self, websocket: WebSocket, courier_id: str):
        """WebSocket bağlantısını kaldır"""
        if courier_id in self.active_connections:
            self.active_connections[courier_id].discard(websocket)
            
            # Eğer bu courier için bağlantı kalmadıysa, dict'ten kaldır
            if not self.active_connections[courier_id]:
                del self.active_connections[courier_id]
            
            logger.info(f"WebSocket disconnected for courier {courier_id}")
    
    async def send_to_courier(self, courier_id: str, message: dict):
        """Belirli bir kuryeye mesaj gönder"""
        if courier_id not in self.active_connections:
            return False
        
        disconnected = set()
        message_str = json.dumps(message)
        
        for websocket in self.active_connections[courier_id]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message to courier {courier_id}: {e}")
                disconnected.add(websocket)
        
        # Bağlantısı kopan websocket'leri temizle
        for ws in disconnected:
            self.disconnect(ws, courier_id)
        
        return len(disconnected) == 0
    
    def has_connection(self, courier_id: str) -> bool:
        """Kuryenin aktif WebSocket bağlantısı var mı?"""
        return courier_id in self.active_connections and len(self.active_connections[courier_id]) > 0


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

