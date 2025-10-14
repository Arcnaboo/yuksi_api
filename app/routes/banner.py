from fastapi import APIRouter
from ..models.banner_model import BannerReq, UpdateBannerReq
from ..controllers import banner_controller

router = APIRouter(prefix="/api/Banner", tags=["Banners"])

@router.get("/get-banners")
async def get_all_banners():
    return await banner_controller.get_all_banners()

@router.post("/set-banner")
async def add_banner(req: BannerReq):
    return await banner_controller.create_banner(req.title ,req.images, req.link, req.description)

@router.get("/get-banners/{banner_id}")
async def get_banner(banner_id: int):
    return await banner_controller.get_banner_by_id(banner_id)

@router.patch("/update-banner")
async def update_banner(req: UpdateBannerReq):
    return await banner_controller.update_banner(req.id, req.title ,req.images, req.link, req.description)

@router.delete("/delete-banner/{banner_id}")
async def delete_banner(banner_id: int):
    return await banner_controller.delete_banner(banner_id)  