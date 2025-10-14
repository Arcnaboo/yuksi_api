from ..services import banner_service as svc

async def get_all_banners():
    result, err = await svc.get_all_banners()
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banners retrieved", "data": result }

async def get_banner_by_id(banner_id: int):
    result, err = await svc.get_banner_by_id(banner_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner retrieved", "data": result }

async def create_banner(title: str, images: list, link: str = None, description: str = None):
    result, err = await svc.create_banner(title, images, link, description)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner created", "data": result }

async def update_banner(banner_id: int, title: str, images: list, link: str = None, description: str = None):
    result, err = await svc.update_banner(banner_id, title, images, link, description)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner updated", "data": result }

async def delete_banner(banner_id: int):
    err = await svc.delete_banner(banner_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Banner deleted", "data": {} }