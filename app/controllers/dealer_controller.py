from typing import Dict, Any
from uuid import UUID
from app.services import dealer_service


async def create_dealer(data: dict) -> Dict[str, Any]:
    return await dealer_service.create_dealer(data)

async def list_dealers(limit: int, offset: int) -> Dict[str, Any]:
    return await dealer_service.list_dealers(limit, offset)

async def get_dealer_by_id(dealer_id: UUID) -> Dict[str, Any]:
    return await dealer_service.get_dealer_by_id(dealer_id)

async def update_dealer(dealer_id: UUID, fields: Dict[str, Any]) -> Dict[str, Any]:
    return await dealer_service.update_dealer(dealer_id, fields)

async def update_dealer_status(dealer_id: UUID, status: str) -> Dict[str, Any]:
    return await dealer_service.update_dealer_status(dealer_id, status)

async def delete_dealer(dealer_id: UUID) -> Dict[str, Any]:
    return await dealer_service.delete_dealer(dealer_id)


async def get_dealer_profile(dealer_id: UUID) -> Dict[str, Any]:
    """Bayi profil görüntüleme controller"""
    profile = await dealer_service.get_dealer_profile(dealer_id)
    if not profile:
        return {"error": "Bayi bulunamadı"}, 404
    return profile


async def update_dealer_profile(dealer_id: UUID, req) -> Dict[str, Any]:
    """Bayi profil güncelleme controller"""
    return await dealer_service.update_dealer_profile(
        dealer_id,
        email=getattr(req, "email", None),
        phone=getattr(req, "phone", None),
        name=getattr(req, "name", None),
        surname=getattr(req, "surname", None),
        full_address=getattr(req, "fullAddress", None) or getattr(req, "full_address", None),
        account_type=getattr(req, "accountType", None) or getattr(req, "account_type", None),
        country_id=getattr(req, "countryId", None) or getattr(req, "country_id", None),
        state_id=getattr(req, "stateId", None) or getattr(req, "state_id", None),
        city_id=getattr(req, "cityId", None) or getattr(req, "city_id", None),
        tax_office=getattr(req, "taxOffice", None) or getattr(req, "tax_office", None),
        tax_number=getattr(req, "taxNumber", None) or getattr(req, "tax_number", None),
        iban=getattr(req, "iban", None),
        resume=getattr(req, "resume", None),
        latitude=getattr(req, "latitude", None),
        longitude=getattr(req, "longitude", None),
    )


async def get_dealer_couriers_gps(dealer_id: str) -> Dict[str, Any]:
    """Bayinin kendi kuryelerinin GPS konumlarını getir controller"""
    success, couriers_gps, error = await dealer_service.get_dealer_couriers_gps(dealer_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Kurye GPS konumları getirilemedi",
            "data": {"couriers": []}
        }
    
    return {
        "success": True,
        "message": "Bayi kuryelerinin GPS konumları başarıyla getirildi",
        "data": {"couriers": couriers_gps if couriers_gps else []}
    }