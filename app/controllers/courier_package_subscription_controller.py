from typing import Dict, Any
from app.services import courier_package_subscription_service
from uuid import UUID

async def create_subscription(data: dict) -> Dict[str, Any]:
    return await courier_package_subscription_service.create_subscription(data)

async def list_subscriptions(limit: int, offset: int) -> Dict[str, Any]:
    return await courier_package_subscription_service.list_subscriptions(limit, offset)

async def get_subscription_by_id(subscription_id: UUID) -> Dict[str, Any]:   
    return await courier_package_subscription_service.get_subscription_by_id(subscription_id)

async def get_subscription_by_courier_id(courier_id: UUID) -> Dict[str, Any]:   
    return await courier_package_subscription_service.get_subscription_by_courier_id(courier_id)

async def update_subscription(subscription_id: UUID, fields: Dict[str, Any]) -> Dict[str, Any]:
    return await courier_package_subscription_service.update_subscription(subscription_id, fields)

async def delete_subscription(subscription_id: UUID) -> Dict[str, Any]:
    return await courier_package_subscription_service.delete_subscription(subscription_id)

