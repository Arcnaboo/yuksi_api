from fastapi import APIRouter
from ..models.banner_model import BannerReq
from ..controllers import banner_controller

router = APIRouter(prefix="/api/Banners", tags=["Banners"])

@router.get("")
async def get_all_banners():
    return await banner_controller.get_all_banners()

@router.post("")
async def add_banner(req: BannerReq):
    return await banner_controller.create_banner(req.title ,req.images, req.link, req.description)

@router.get("/{banner_id}")
async def get_banner(banner_id: int):
    return await banner_controller.get_banner_by_id(banner_id)

@router.put("/{banner_id}")
async def update_banner(banner_id: int, req: BannerReq):
    return await banner_controller.update_banner(banner_id, req.title ,req.images, req.link, req.description)

@router.delete("/{banner_id}")
async def delete_banner(banner_id: int):
    return await banner_controller.delete_banner(banner_id)  