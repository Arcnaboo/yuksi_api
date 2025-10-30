from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query, Body
from app.controllers import dealer_controller as ctrl
from app.models.dealer_model import DealerCreate, DealerUpdate, DealerStatusUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/dealers", tags=["Dealers"])


# ✅ CREATE (Admin)
@router.post(
    "",
    summary="Yeni Bayi Ekle",
    description="Yeni bayi kaydı oluşturur (UUID id döner).",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def create_dealer(body: DealerCreate = Body(...)):
    # body.model_dump() -> pydantic v2
    return await ctrl.create_dealer(body.model_dump())


# ✅ GET LIST (Admin)
@router.get(
    "",
    summary="Bayi Listesi",
    description="Tüm bayileri ülke/şehir/ilçe isimleriyle listeler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_dealers(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await ctrl.list_dealers(limit, offset)


# ✅ GET BY ID (Admin)
@router.get(
    "/{dealer_id}",
    summary="Bayi Detayı",
    description="Belirli bir bayiyi (ülke/şehir/ilçe isimleriyle) döner.",
    dependencies=[Depends(require_roles(["Admin,Dealer"]))],
)
async def get_dealer(dealer_id: UUID = Path(..., description="Dealer UUID")):
    return await ctrl.get_dealer_by_id(dealer_id)


# ✅ UPDATE (Admin)
@router.put(
    "/{dealer_id}",
    summary="Bayi Güncelleme",
    description="Bayi bilgilerini günceller.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_dealer(
    dealer_id: UUID = Path(..., description="Dealer UUID"),
    body: DealerUpdate = Body(...),
):
    return await ctrl.update_dealer(dealer_id, body.model_dump(exclude_unset=True))


# ✅ UPDATE STATUS (Admin)
@router.patch(
    "/{dealer_id}/status",
    summary="Bayi Durum Güncelleme",
    description="Bayiyi pendingApproval / active / inactive durumuna çeker.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_dealer_status(
    dealer_id: UUID = Path(..., description="Dealer UUID"),
    body: DealerStatusUpdate = Body(...),
):
    return await ctrl.update_dealer_status(dealer_id, body.status)


# ✅ DELETE (Admin)
@router.delete(
    "/{dealer_id}",
    summary="Bayi Silme",
    description="Bayi kaydını siler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_dealer(dealer_id: UUID = Path(..., description="Dealer UUID")):
    return await ctrl.delete_dealer(dealer_id)
