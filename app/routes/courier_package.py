from fastapi import APIRouter, Depends, Path, Query
from app.controllers import courier_package_controller as ctrl
from app.models.courier_package_model import CourierPackageCreate, CourierPackageUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/packages", tags=["Courier Packages"])

# ✅ CREATE
@router.post(
    "",
    summary="Create Courier Package",
    description="Creates a new courier package.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def create_package(body: CourierPackageCreate):
    return await ctrl.create_package(body.dict())


# ✅ LIST
@router.get(
    "",
    summary="List Courier Packages",
    description="Lists all courier packages.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_packages(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await ctrl.list_packages(limit, offset)


# ✅ GET BY ID
@router.get(
    "/{package_id}",
    summary="Get Courier Package by ID",
    description="Returns a single courier package by its ID.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_package(package_id: int = Path(..., ge=1)):
    return await ctrl.get_package_by_id(package_id)


# ✅ UPDATE
@router.put(
    "/{package_id}",
    summary="Update Courier Package",
    description="Updates a courier package.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_package(
    package_id: int = Path(..., ge=1),
    body: CourierPackageUpdate = ...,
):
    return await ctrl.update_package(package_id, body.dict(exclude_unset=True))


# ✅ DELETE
@router.delete(
    "/{package_id}",
    summary="Delete Courier Package",
    description="Deletes a courier package.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_package(package_id: int = Path(..., ge=1)):
    return await ctrl.delete_package(package_id)
