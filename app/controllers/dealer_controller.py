from typing import Dict, Any
from app.services import dealer_service


async def create_dealer(data: dict) -> Dict[str, Any]:
    return await dealer_service.create_dealer(data)

async def list_dealers(limit: int, offset: int) -> Dict[str, Any]:
    return await dealer_service.list_dealers(limit, offset)

async def get_dealer_by_id(dealer_id: int) -> Dict[str, Any]:
    return await dealer_service.get_dealer_by_id(dealer_id)

async def update_dealer(dealer_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return await dealer_service.update_dealer(dealer_id, fields)

async def update_dealer_status(dealer_id: int, status: str) -> Dict[str, Any]:
    return await dealer_service.update_dealer_status(dealer_id, status)

async def delete_dealer(dealer_id: int) -> Dict[str, Any]:
    return await dealer_service.delete_dealer(dealer_id)
