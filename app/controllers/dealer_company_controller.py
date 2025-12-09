from typing import Dict, Any
from ..services import dealer_company_service as svc


async def dealer_create_and_link_company(dealer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Bayi için yeni şirket oluştur ve bağla controller"""
    success, company_data, error = await svc.dealer_create_and_link_company(
        dealer_id=dealer_id,
        company_tracking_no=data["companyTrackingNo"],
        assigned_kilometers=data["assignedKilometers"],
        special_commission_rate=data["specialCommissionRate"],
        is_visible=data.get("isVisible", True),
        can_receive_payments=data.get("canReceivePayments", True),
        city_id=data["cityId"],
        state_id=data["stateId"],
        location=data["location"],
        company_name=data["companyName"],
        company_phone=data["companyPhone"],
        description=data["description"],
    )
    
    if not success:
        return {
            "success": False,
            "message": error or "Şirket oluşturulamadı",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Şirket başarıyla oluşturuldu ve bayisine bağlandı",
        "data": company_data
    }


async def dealer_link_existing_company(dealer_id: str, company_id: str) -> Dict[str, Any]:
    """Mevcut şirketi bayisine bağla controller"""
    success, error = await svc.dealer_link_existing_company(dealer_id, company_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Şirket bağlanamadı",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Şirket başarıyla bayisine bağlandı",
        "data": {"company_id": company_id}
    }


async def dealer_get_companies(dealer_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Bayinin şirketlerini listele controller"""
    success, result = await svc.dealer_get_companies(dealer_id, limit, offset)
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Şirketler getirilemedi",
            "data": []
        }
    
    return {
        "success": True,
        "message": "Şirketler başarıyla getirildi",
        "data": result if isinstance(result, list) else []
    }


async def dealer_get_company_detail(dealer_id: str, company_id: str) -> Dict[str, Any]:
    """Bayinin belirli bir şirketinin detayını getir controller"""
    success, company_data, error = await svc.dealer_get_company_detail(dealer_id, company_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Şirket detayı getirilemedi",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Şirket detayı başarıyla getirildi",
        "data": company_data
    }


async def dealer_update_company(dealer_id: str, company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Bayinin belirli bir şirketini güncelle controller"""
    success, error = await svc.dealer_update_company(dealer_id, company_id, data)
    
    if not success:
        return {
            "success": False,
            "message": error or "Şirket güncellenemedi",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Şirket başarıyla güncellendi",
        "data": {}
    }

