from typing import Dict, Any
from app.services import company_service as svc

# Companies
async def create_company(data: Dict[str, Any]):
    ok, res = await svc.create_company(data)
    return {"success": ok, "message": None if ok else res, "data": res if ok else {}}

async def list_companies(limit: int, offset: int, city_id: int | None, status: str | None):
    ok, res = await svc.list_companies(limit, offset, city_id, status)
    return {"success": ok, "message": None if ok else res, "data": res if ok else []}

async def get_company(company_id: str):
    ok, res = await svc.get_company(company_id)
    return {"success": ok, "message": None if ok else res, "data": res if ok else {}}

async def update_company(company_id: str, fields: Dict[str, Any]):
    ok, err = await svc.update_company(company_id, fields)
    return {"success": ok, "message": None if ok else err, "data": {}}

async def delete_company(company_id: str):
    ok, err = await svc.delete_company(company_id)
    return {"success": ok, "message": None if ok else err, "data": {}}

# Managers
async def add_manager(company_id: str, body: Dict[str, Any]):
    ok, res = await svc.add_manager(company_id, body)
    return {"success": ok, "message": None if ok else res, "data": res if ok else {}}

async def list_managers(company_id: str):
    ok, res = await svc.list_managers(company_id)
    return {"success": ok, "message": None if ok else res, "data": res if ok else []}

async def update_manager(company_id: str, manager_id: str, body: Dict[str, Any]):
    ok, err = await svc.update_manager(company_id, manager_id, body)
    return {"success": ok, "message": None if ok else err, "data": {}}

async def delete_manager(company_id: str, manager_id: str):
    ok, err = await svc.delete_manager(company_id, manager_id)
    return {"success": ok, "message": None if ok else err, "data": {}}
