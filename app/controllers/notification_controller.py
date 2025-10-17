from app.services import notification_service as service
from app.services.notification_service import list_notifications_for_user


async def send(req):
    if req.type == "single":
        ok, info, nid = await service.send_single(req.target, req.subject, req.message)
        if not ok:
            return {"success": False, "message": info, "data": {}}
        return {"success": True, "message": "Notification sent", "data": {"id": nid}}
    else:
        ok, info, nid = await service.send_bulk(req.user_type, req.subject, req.message)
        if not ok:
            return {"success": False, "message": info, "data": {}}
        return {"success": True, "message": "Notification sent", "data": {"id": nid}}

async def list_notifications(claims):
    data = await service.list_notifications_for_user(claims)
    return {
        "success": True,
        "message": "Notifications fetched",
        "data": data
    }


async def delete_notification(notification_id: int, claims):
    user_id = claims.get("sub")
    roles = claims.get("role") or claims.get("roles") or []

    ok, msg = await service.delete_notification(notification_id, user_id, roles)

    if not ok:
        return {"success": False, "message": msg, "data": {}}

    return {"success": True, "message": msg, "data": {}}

