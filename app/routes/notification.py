from fastapi import APIRouter, Depends
from app.models.notification_model import NotificationRequest
from app.controllers import notification_controller as ctrl
from app.controllers import auth_controller
from app.controllers.auth_controller import require_roles
from app.services.notification_service import delete_notification


router = APIRouter(prefix="/api/Notification", tags=["Notification"])

@router.post("/send")
async def send_notification(
    req: NotificationRequest,
    _claims = Depends(auth_controller.require_roles(["Admin"])),
):
    return await ctrl.send(req)

@router.get("/list", dependencies=[Depends(require_roles(["Admin", "Courier", "Restaurant"]))])
async def list_notifications_route(claims=Depends(require_roles(["Admin", "Courier", "Restaurant"]))):
    return await ctrl.list_notifications(claims)


@router.delete("/delete/{id}")
async def delete_notification_route(id: int, claims=Depends(require_roles(["Admin", "Courier", "Restaurant"]))):
    ok, msg = await delete_notification(id, claims.get("userId"), claims.get("role") or claims.get("roles") or [])
    return {"success": ok, "message": msg, "data": {}}
