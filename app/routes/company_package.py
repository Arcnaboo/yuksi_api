from fastapi import APIRouter, Depends, Path
from app.controllers.company_package_controller import *
from app.models.company_package_model import CompanyPackageCreate, CompanyPackageUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/company-packages", tags=["Company Packages"])

# ✅ List
@router.get("", dependencies=[Depends(require_roles(["Admin"]))])
async def list_packages_route():
    return await list_packages()

# ✅ Get by ID
@router.get("/{package_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def get_package_route(package_id: str = Path(...)):
    return await get_package(package_id)

# ✅ Create
@router.post("", dependencies=[Depends(require_roles(["Admin"]))])
async def create_package_route(body: CompanyPackageCreate):
    return await create_package(body.model_dump())

# ✅ Update
@router.put("/{package_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_package_route(package_id: str, body: CompanyPackageUpdate):
    return await update_package(package_id, body.model_dump(exclude_unset=True))

# ✅ Delete
@router.delete("/{package_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_package_route(package_id: str = Path(...)):
    return await delete_package(package_id)
