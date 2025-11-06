from fastapi import APIRouter, Depends, Path
from app.controllers.campaign_controller import *
from app.models.campaign_model import CampaignCreate, CampaignUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/campaigns", tags=["Campaigns"])


@router.get("", dependencies=[Depends(require_roles(["Admin"]))])
async def list_route():
    return await list_campaigns()


@router.get("/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def get_route(id: str = Path(...)):
    return await get_campaign(id)


@router.post("", dependencies=[Depends(require_roles(["Admin"]))])
async def create_route(body: CampaignCreate):
    return await create_campaign(body.model_dump())


@router.put("/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_route(id: str, body: CampaignUpdate):
    return await update_campaign(id, body.model_dump(exclude_unset=True))


@router.delete("/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_route(id: str):
    return await delete_campaign(id)
