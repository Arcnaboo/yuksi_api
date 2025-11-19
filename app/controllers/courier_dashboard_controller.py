from typing import Dict, Any
from app.services import courier_dashboard_service


async def get_courier_earnings(courier_id: str) -> Dict[str, Any]:
    """Kurye kazanç verilerini getirir"""
    earnings_data = await courier_dashboard_service.get_courier_earnings(courier_id)
    
    if earnings_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye kazanç verileri",
        "data": earnings_data
    }


async def get_courier_distance(courier_id: str) -> Dict[str, Any]:
    """Kurye mesafe verilerini getirir"""
    distance_data = await courier_dashboard_service.get_courier_distance(courier_id)
    
    if distance_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye mesafe verileri",
        "data": distance_data
    }


async def get_courier_package(courier_id: str) -> Dict[str, Any]:
    """Kurye paket bilgilerini getirir"""
    package_data = await courier_dashboard_service.get_courier_package(courier_id)
    
    if package_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye paket bilgileri",
        "data": package_data
    }


async def get_courier_work_hours(courier_id: str) -> Dict[str, Any]:
    """Kurye çalışma saatlerini getirir"""
    work_hours_data = await courier_dashboard_service.get_courier_work_hours(courier_id)
    
    if work_hours_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye çalışma saatleri",
        "data": work_hours_data
    }


async def get_courier_activities(courier_id: str) -> Dict[str, Any]:
    """Kurye aktivite sayısını getirir"""
    activities_data = await courier_dashboard_service.get_courier_activities(courier_id)
    
    if activities_data is None:
        return {
            "success": False,
            "message": "Kurye bulunamadı veya geçersiz ID",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Kurye aktivite sayısı",
        "data": activities_data
    }


async def get_courier_dashboard(courier_id: str) -> Dict[str, Any]:
    """
    Kurye dashboard endpoint handler (DEPRECATED - ayrı endpoint'ler kullanılmalı)
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

