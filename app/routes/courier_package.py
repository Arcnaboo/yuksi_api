from fastapi import APIRouter, Depends, Path, Query
from app.controllers import courier_package_controller as ctrl
from app.models.courier_package_model import CourierPackageCreate, CourierPackageUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/packages", tags=["Courier Packages"])

# ✅ CREATE (Sadece Admin)
@router.post(
    "",
    summary="Yeni Kurye Paketi Oluştur",
    description="Admin yeni bir kurye paketi ekleyebilir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def create_package(body: CourierPackageCreate):
    return await ctrl.create_package(body.dict())


# ✅ LIST (Admin + Courier)
@router.get(
    "",
    summary="List Courier Packages",
    description="Lists all courier packages.",
    dependencies=[Depends(require_roles(["Admin","Courier"]))],
)
async def get_packages(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await ctrl.list_packages(limit, offset)


# ✅ GET BY ID (Admin + Courier)
@router.get(
    "/{package_id}",
    summary="Paket Detayı",
    description="Admin veya Courier belirli bir paketin detayını görebilir.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def get_package(package_id: str = Path(..., description="UUID formatında paket kimliği")):
    return await ctrl.get_package_by_id(package_id)


# ✅ UPDATE (Sadece Admin)
@router.put(
    "/{package_id}",
    summary="Paketi Güncelle",
    description="Admin paket bilgilerini günceller.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_package(
    package_id: str = Path(..., description="UUID formatında paket kimliği"),
    body: CourierPackageUpdate = ...,
):
    return await ctrl.update_package(package_id, body.dict(exclude_unset=True))


# ✅ DELETE (Sadece Admin)
@router.delete(
    "/{package_id}",
    summary="Paketi Sil",
    description="Admin mevcut bir paketi siler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_package(package_id: str = Path(..., description="UUID formatında paket kimliği")):
    return await ctrl.delete_package(package_id)
