from fastapi import APIRouter
from ..models.contact_model import ContactReq
from ..controllers import contact_controller

router = APIRouter(prefix="/api/Contact", tags=["Contact"])

@router.post("/send")
async def send_contact(req: ContactReq):
    return await contact_controller.send_contact(
        req.name, req.email, req.phone, req.subject, req.message
    )

@router.get("/list")
async def list_contacts(limit: int = 50, offset: int = 0):
    return await contact_controller.get_contact_list(limit, offset)

@router.delete("/delete/{contact_id}")
async def delete_contact(contact_id:int):
    return await contact_controller.delete_contact(contact_id)
