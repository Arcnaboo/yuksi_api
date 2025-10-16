from ..services import banner_service as svc

async def get_all_banners():
    result, err = await svc.get_all_banners()
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banners retrieved", "data": result }

async def get_banner_by_id(banner_id: str):
    result, err = await svc.get_banner_by_id(banner_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner retrieved", "data": result }

async def create_banner(title: str, image_url: str, priority: int = 0, active: bool = True):
    result, err = await svc.create_banner(title, image_url, priority, active)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner created", "data": result }

async def update_banner(banner_id: str, title: str, image_url: str, priority: int = 0, active: bool = True):
    result, err = await svc.update_banner(banner_id, title, image_url, priority, active)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner updated", "data": result }

async def delete_banner(banner_id: str):
    err = await svc.delete_banner(banner_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner deleted", "data": {} }