from typing import Dict, Any
from app.services import courier_dashboard_service


async def get_courier_dashboard(courier_id: str) -> Dict[str, Any]:
    """
    Kurye dashboard endpoint handler
    """
    dashboard_data = await courier_dashboard_service.get_courier_dashboard(courier_id)
    
    if dashboard_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye dashboard verileri",
        "data": dashboard_data
    }

