from typing import Any, Dict
from app.services import subsection_service as svc

# CREATE
async def create_subsection(title: str, content_type: str, show_in_menu: bool, show_in_footer: bool, content: str) -> Dict[str, Any]:
    result, err = await svc.create_subsection(title, content_type, show_in_menu, show_in_footer, content)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "SubSection created", "data": result }

# GET ALL
async def get_all_subsections(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    result, err = await svc.get_all_subsections(limit, offset)
    if err:
        return { "success": False, "message": err, "data": [] }
    return { "success": True, "message": "SubSections retrieved", "data": result }

# GET BY ID
async def get_subsection_by_id(sub_id: int) -> Dict[str, Any]:
    result, err = await svc.get_subsection_by_id(sub_id)
    if err or not result:
        return { "success": False, "message": err or "Not found", "data": {} }
    return { "success": True, "message": "SubSection retrieved", "data": result }

# UPDATE
async def update_subsection(sub_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    err = await svc.update_subsection(sub_id, fields)
    if err:
        return { "success": False, "message": err or "Update failed", "data": {} }
    return { "success": True, "message": "SubSection updated", "data": {} }

# DELETE
async def delete_subsection(sub_id: int) -> Dict[str, Any]:
    err = await svc.delete_subsection(sub_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "SubSection deleted", "data": {} }
