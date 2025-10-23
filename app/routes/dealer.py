from fastapi import APIRouter, Depends, Path, Query
from app.controllers import dealer_controller as ctrl
from app.models.dealer_model import DealerCreate, DealerUpdate, DealerStatusUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/dealers", tags=["Dealers"])

# ✅ CREATE
@router.post(
    "",
    summary="Yeni Bayi Ekle",
    description="Yeni bayi kaydı oluşturur.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def create_dealer(body: DealerCreate):
    return await ctrl.create_dealer(body.dict())


# ✅ GET LIST
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


# ✅ GET BY ID
@router.get(
    "/{dealer_id}",
    summary="Bayi Detayı",
    description="Belirli bir bayiyi (ülke/şehir/ilçe isimleriyle) döner.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_dealer(dealer_id: int = Path(..., ge=1)):
    return await ctrl.get_dealer_by_id(dealer_id)


# ✅ UPDATE
@router.put(
    "/{dealer_id}",
    summary="Bayi Güncelleme",
    description="Bayi bilgilerini günceller.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_dealer(
    dealer_id: int = Path(..., ge=1),
    body: DealerUpdate = ...,
):
    return await ctrl.update_dealer(dealer_id, body.dict(exclude_unset=True))


# ✅ UPDATE STATUS
@router.patch(
    "/{dealer_id}/status",
    summary="Bayi Durum Güncelleme",
    description="Bayiyi pendingApproval / active / inactive durumuna çeker.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_dealer_status(
    dealer_id: int = Path(..., ge=1),
    body: DealerStatusUpdate = ...,
):
    return await ctrl.update_dealer_status(dealer_id, body.status)


# ✅ DELETE
@router.delete(
    "/{dealer_id}",
    summary="Bayi Silme",
    description="Bayi kaydını siler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_dealer(dealer_id: int = Path(..., ge=1)):
    return await ctrl.delete_dealer(dealer_id)
