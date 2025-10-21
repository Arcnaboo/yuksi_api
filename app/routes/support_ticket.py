from fastapi import APIRouter, Depends
from app.controllers import support_ticket_controller as ctrl
from app.models.support_ticket_model import SupportTicketCreate, SupportTicketReply
from app.controllers.auth_controller import require_roles
from app.controllers import auth_controller

router = APIRouter(prefix="/api/Ticket", tags=["Support Ticket"])

# Restoran: talep oluştur
@router.post("/create")
async def create_ticket(req: SupportTicketCreate, claims = Depends(require_roles(["Restaurant"]))):
    return await ctrl.create_ticket_controller(claims, req.subject, req.message)

# Admin: tüm talepler
@router.get("/admin/list")
async def list_admin(claims = Depends(require_roles(["Admin"]))):
    return await ctrl.list_admin_controller()

# Restoran: kendi talepleri
@router.get("/my")
async def list_my_tickets(claims = Depends(require_roles(["Restaurant"]))):
    return await ctrl.list_my_tickets_controller(claims)

# Admin: yanıt ver
@router.post("/reply/{ticket_id}")
async def reply(ticket_id: int, req: SupportTicketReply, claims = Depends(require_roles(["Admin"]))):
    return await ctrl.reply_ticket_controller(ticket_id, req.reply)

# Admin: durum güncelle (pending|answered|closed)
@router.patch("/status/{ticket_id}")
async def update_status(ticket_id: int, status: str, claims = Depends(require_roles(["Admin"]))):
    return await ctrl.update_ticket_status_controller(ticket_id, status)

@router.delete("/delete/{ticket_id}")
async def delete_ticket_route(
    ticket_id: int,
    claims = Depends(auth_controller.require_roles(["Admin", "Restaurant"]))
):
    return await ctrl.delete_ticket_controller(ticket_id, claims)