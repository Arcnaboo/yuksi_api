from fastapi import APIRouter, Depends, Query, Path, Body
from uuid import UUID
from typing import Optional
from app.controllers.auth_controller import require_roles
from app.controllers import company_controller as ctrl
from app.models.company_model import (
    CompanyCreate, CompanyUpdate,
    ManagerCreate, ManagerUpdate
)

router = APIRouter(prefix="/api/admin/companies", tags=["Companies"])

# CREATE
@router.post("", dependencies=[Depends(require_roles(["Admin"]))])
async def create_company(req: CompanyCreate = Body(...)):
    return await ctrl.create_company(req.model_dump())

# LIST
@router.get("", dependencies=[Depends(require_roles(["Admin"]))])
async def list_companies(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    cityId: Optional[int] = Query(None, ge=1),
    status: Optional[str] = Query(None)  # active | inactive
):
    return await ctrl.list_companies(limit, offset, cityId, status)

# GET BY ID
@router.get("/{company_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def get_company(company_id: UUID = Path(...)):
    return await ctrl.get_company(str(company_id))

# UPDATE (PATCH)
@router.patch("/{company_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_company(company_id: UUID, req: CompanyUpdate = Body(...)):  # ✅ doğru model
    return await ctrl.update_company(str(company_id), req.model_dump(exclude_none=True))

# DELETE
@router.delete("/{company_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_company(company_id: UUID):
    return await ctrl.delete_company(str(company_id))

# ----- MANAGERS -----

@router.post("/{company_id}/managers", dependencies=[Depends(require_roles(["Admin"]))])
async def add_manager(company_id: UUID, req: ManagerCreate = Body(...)):
    return await ctrl.add_manager(str(company_id), req.model_dump())

@router.get("/{company_id}/managers", dependencies=[Depends(require_roles(["Admin"]))])
async def list_managers(company_id: UUID):
    return await ctrl.list_managers(str(company_id))

@router.patch("/{company_id}/managers/{manager_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_manager(company_id: UUID, manager_id: UUID, req: ManagerUpdate = Body(...)):
    return await ctrl.update_manager(str(company_id), str(manager_id), req.model_dump(exclude_none=True))

@router.delete("/{company_id}/managers/{manager_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_manager(company_id: UUID, manager_id: UUID):
    return await ctrl.delete_manager(str(company_id), str(manager_id))
