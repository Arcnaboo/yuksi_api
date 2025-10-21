from typing import List, Dict, Any, Optional, Tuple
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services.mail_service import send_mail
from app.utils.templates.notification_template import NotificationEmailTemplate


# === YARDIMCI: Notification Kaydet ===
async def _save(
    ntype: str,
    subject: str,
    message: str,
    target_email: Optional[str],
    user_type: Optional[str]
) -> int:
    query = """
        INSERT INTO notifications (type, target_email, user_type, subject, message)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
    """
    row = await fetch_one(query, ntype, target_email, user_type, subject, message)
    return int(row["id"]) if row else 0


# === TEK BİLDİRİM GÖNDER ===
async def send_single(email: str, subject: str, message: str) -> Tuple[bool, str, Optional[int]]:
    html = NotificationEmailTemplate.build(subject, message)
    ok, info = await send_mail(email, subject, html)
    notif_id = None
    if ok:
        notif_id = await _save("single", subject, message, target_email=email, user_type=None)
    return ok, info, notif_id


# === TOPLU BİLDİRİM GÖNDER ===
async def send_bulk(user_type: str, subject: str, message: str) -> Tuple[bool, str, Optional[int]]:
    html = NotificationEmailTemplate.build(subject, message)

    if user_type == "courier":
        query = "SELECT email FROM drivers;"
    elif user_type == "restaurant":
        query = "SELECT email FROM restaurants;"
    elif user_type == "all":
        query = "SELECT email FROM drivers UNION SELECT email FROM restaurants;"
    else:
        return False, "Geçersiz user_type", None

    rows = await fetch_all(query)
    if not rows:
        return False, "Gönderilecek kullanıcı bulunamadı", None

    for r in rows:
        await send_mail(r["email"], subject, html)

    notif_id = await _save("bulk", subject, message, target_email=None, user_type=user_type)
    return True, "Toplu bildirim gönderildi", notif_id


# === BİLDİRİMLERİ LİSTELE ===
async def list_notifications_for_user(claims: Dict[str, Any]) -> List[Dict[str, Any]]:
    email = claims.get("email")
    roles = claims.get("role") or claims.get("roles") or []
    role = (roles[0] if isinstance(roles, list) and roles else roles).lower()

    if role == "admin":
        query = "SELECT * FROM notifications ORDER BY created_at DESC;"
        rows = await fetch_all(query)
    elif role == "courier":
        query = """
            SELECT * FROM notifications
            WHERE user_type = 'courier' OR target_email = $1
            ORDER BY created_at DESC;
        """
        rows = await fetch_all(query, email)
    elif role == "restaurant":
        query = """
            SELECT * FROM notifications
            WHERE user_type = 'restaurant' OR target_email = $1
            ORDER BY created_at DESC;
        """
        rows = await fetch_all(query, email)
    else:
        return []

    return [dict(r) for r in rows] if rows else []


# === BİLDİRİM SİL ===
async def delete_notification(
    notification_id: int,
    user_id: str,
    roles: List[str]
) -> Tuple[bool, str]:
    try:
        notif = await fetch_one(
            "SELECT id, user_type FROM notifications WHERE id = $1;",
            notification_id
        )
        if not notif:
            return False, "Bildirim bulunamadı"

        notif_user_type = (notif["user_type"] or "").strip().lower()
        current_role = (roles[0] if roles else "").strip().lower()

        if current_role != "admin" and notif_user_type != current_role:
            return False, "Bu bildirimi silme yetkiniz yok"

        await execute("DELETE FROM notifications WHERE id = $1;", notification_id)
        return True, "Bildirim silindi"

    except Exception as e:
        return False, f"SQL Hatası: {str(e)}"
