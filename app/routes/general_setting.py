from fastapi import APIRouter, Depends
from app.controllers import general_setting_controller as ctrl
from app.models.general_setting_model import GeneralSettingCreate, GeneralSettingUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/GeneralSetting", tags=["GeneralSetting"])

# ✅ SADECE ADMIN ERİŞEBİLİR
@router.post("/create", dependencies=[Depends(require_roles(["Admin"]))])
async def create(req: GeneralSettingCreate):
    return await ctrl.create(req.dict())

# ✅ SADECE ADMIN OKUYABİLİR
@router.get("/get", dependencies=[Depends(require_roles(["Admin"]))])
async def get():
    return await ctrl.get()

# ✅ SADECE ADMIN GÜNCELLEYEBİLİR
@router.patch("/update", dependencies=[Depends(require_roles(["Admin"]))])
async def update(req: GeneralSettingUpdate):
    fields = {k: v for k, v in req.dict().items() if v is not None and k != "id"}
    return await ctrl.update(req.id, fields)
