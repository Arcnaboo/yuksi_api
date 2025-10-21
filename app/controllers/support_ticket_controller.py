from app.services import support_ticket_service as service
from typing import Any, Dict


async def create_ticket_controller(claims, subject, message):
    restaurant_id = claims.get("sub")
    email = claims.get("email")
    # İstersen restoran adını DB'den çekebilirsin; şimdilik email local-part kullanıyoruz
    restaurant_name = email.split("@")[0] if email else "Restaurant"

    new_id = await service.create_ticket(restaurant_id, email, restaurant_name, subject, message)
    return {"success": True, "message": "Ticket created", "data": {"id": new_id}}

async def list_admin_controller():
    data = await service.list_admin_tickets()
    return {"success": True, "message": "Tickets fetched", "data": data}

async def list_my_tickets_controller(claims):
    restaurant_id = claims.get("sub")
    data = await service.list_my_tickets(restaurant_id)
    return {"success": True, "message": "My tickets fetched", "data": data}

async def reply_ticket_controller(ticket_id, reply):
    ok, msg = await service.reply_ticket(ticket_id, reply)
    return {
        "success": bool(ok),
        "message": msg,
        "data": {}
    }

async def update_ticket_status_controller(ticket_id: int, new_status: str):
    ok, msg = await service.update_ticket_status(ticket_id, new_status)
    return {
        "success": bool(ok),
        "message": msg,
        "data": {}
    }

async def delete_ticket_controller(ticket_id: int, claims: Dict[str, Any]) -> Dict[str, Any]:
    requester_id = claims.get("sub") or claims.get("userId")
    roles = claims.get("role") or claims.get("roles") or []

    ok, msg = await service.delete_ticket(ticket_id, requester_id, roles)
    return {
        "success": ok,
        "message": msg,
        "data": {}
    }