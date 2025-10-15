from fastapi import APIRouter
from app.models.subsection_model import SubSectionCreate, SubSectionUpdate
from app.controllers import subsection_controller as controller

router = APIRouter(prefix="/api/SubSection", tags=["SubSection"])

# CREATE
@router.post("/create", operation_id="create_subsection")
async def create_subsection(req: SubSectionCreate):
    return await controller.create_subsection(
        req.title,
        req.content_type,
        req.show_in_menu,
        req.show_in_footer,
        req.content
    )

# GET ALL
@router.get("/all", operation_id="get_all_subsections")
async def get_all(limit: int = 100, offset: int = 0):
    return await controller.get_all_subsections(limit, offset)

# GET BY ID
@router.get("/{sub_id}", operation_id="get_subsection_by_id")
async def get_by_id(sub_id: int):
    return await controller.get_subsection_by_id(sub_id)

# UPDATE
@router.patch("/update", operation_id="update_subsection")
async def update(req: SubSectionUpdate):
    fields = {k: v for k, v in req.dict().items() if v is not None and k != "id"}
    return await controller.update_subsection(req.id, fields)

# DELETE
@router.delete("/delete/{sub_id}", operation_id="delete_subsection")
async def delete(sub_id: int):
    return await controller.delete_subsection(sub_id)
