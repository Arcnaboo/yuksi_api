"""
Periyodik rota kontrolü - Yedek mekanizma (GPS güncellemesi gelmediyse bile kontrol eder)
"""
import asyncio
import logging
from typing import List, Dict, Any
from app.utils.database_async import fetch_all
from app.services.courier_route_websocket_service import calculate_and_push_route
from app.utils.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


async def check_all_active_couriers():
    """
    Aktif order'ı olan ve WebSocket bağlantısı açık olan tüm kuryeleri kontrol et
    """
    try:
        # Aktif order'ı olan kuryeleri getir
        rows = await fetch_all("""
            SELECT DISTINCT courier_id
            FROM orders
            WHERE courier_id IS NOT NULL
              AND status IN ('kuryeye_verildi', 'yolda')
        """)
        
        if not rows:
            return
        
        courier_ids = [str(row["courier_id"]) for row in rows]
        
        # Her kurye için rota kontrolü yap (sadece WebSocket bağlantısı varsa)
        tasks = []
        for courier_id in courier_ids:
            if websocket_manager.has_connection(courier_id):
                tasks.append(calculate_and_push_route(courier_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"Periodic route check completed for {len(tasks)} couriers")
            
    except Exception as e:
        logger.error(f"Error in periodic route check: {e}")


async def start_periodic_check(interval_seconds: int = 60):
    """
    Periyodik kontrol task'ını başlat (her 60 saniyede bir)
    """
    logger.info(f"Starting periodic route check (interval: {interval_seconds}s)")
    
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            await check_all_active_couriers()
        except Exception as e:
            logger.error(f"Error in periodic check loop: {e}")
            await asyncio.sleep(interval_seconds)  # Hata durumunda da bekle

