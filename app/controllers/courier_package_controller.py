from typing import Dict, Any
from app.services import courier_package_service


async def create_package(data: dict) -> Dict[str, Any]:
    return await courier_package_service.create_package(data)

async def list_packages(limit: int, offset: int) -> Dict[str, Any]:
    return await courier_package_service.list_packages(limit, offset)

async def get_package_by_id(package_id: int) -> Dict[str, Any]:
    return await courier_package_service.get_package_by_id(package_id)

async def update_package(package_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return await courier_package_service.update_package(package_id, fields)

async def delete_package(package_id: int) -> Dict[str, Any]:
    return await courier_package_service.delete_package(package_id)
