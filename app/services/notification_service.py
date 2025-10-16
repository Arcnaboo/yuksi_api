from app.utils.database import db_cursor
from typing import List, Dict, Any
from app.services.mail_service import send_mail
from app.utils.templates.notification_template import NotificationEmailTemplate

async def _save(ntype: str, subject: str, message: str, target_email: str | None, user_type: str | None) -> int:
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            """
            INSERT INTO notifications (type, target_email, user_type, subject, message)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (ntype, target_email, user_type, subject, message),
        )
        row = cur.fetchone()
        return int(row["id"])

async def send_single(email: str, subject: str, message: str) -> tuple[bool, str, int | None]:
    html = NotificationEmailTemplate.build(subject, message)
    ok, info = await send_mail(email, subject, html)
    notif_id = None
    if ok:
        notif_id = await _save("single", subject, message, target_email=email, user_type=None)
    return ok, info, notif_id

async def send_bulk(user_type: str, subject: str, message: str) -> tuple[bool, str, int | None]:
    html = NotificationEmailTemplate.build(subject, message)

    if user_type == "courier":
        query = "SELECT email FROM drivers"
    elif user_type == "restaurant":
        query = "SELECT email FROM restaurants"
    elif user_type == "all":
        query = "SELECT email FROM drivers UNION SELECT email FROM restaurants"
    else:
        return False, "Geçersiz user_type", None

    with db_cursor(dict_cursor=True) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    if not rows:
        return False, "Gönderilecek kullanıcı bulunamadı", None

    # basit ardışık gönderim (gerekirse burada batch/async kuyruğa çevrilebilir)
    for r in rows:
        await send_mail(r["email"], subject, html)

    notif_id = await _save("bulk", subject, message, target_email=None, user_type=user_type)
    return True, "Toplu bildirim gönderildi", notif_id

async def list_notifications_for_user(claims):
    email = claims.get("email")
    roles = claims.get("role") or claims.get("roles") or []

    with db_cursor(dict_cursor=True) as cur:
        # ✅ Admin → Tümünü görür
        if "Admin" in roles:
            cur.execute("SELECT * FROM notifications ORDER BY created_at DESC")
        # ✅ Courier → courier türü veya kendine özel
        elif "Courier" in roles:
            cur.execute("""
                SELECT * FROM notifications 
                WHERE user_type = 'courier' OR target_email = %s
                ORDER BY created_at DESC
            """, (email,))
        # ✅ Restaurant → restaurant türü veya kendine özel
        elif "Restaurant" in roles:
            cur.execute("""
                SELECT * FROM notifications 
                WHERE user_type = 'restaurant' OR target_email = %s
                ORDER BY created_at DESC
            """, (email,))
        else:
            return []

        return cur.fetchall()
