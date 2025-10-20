from app.utils.database import db_cursor
from datetime import datetime
from typing import Tuple
import os
from app.services.mail_service import send_mail
from app.utils.templates.support_reply_template import build_support_reply_email
try:
    from app.utils.templates.support_new_template import build_support_new_ticket_email
except Exception:
    build_support_new_ticket_email = None  # opsiyonel

ALLOWED_STATUSES = {"pending", "answered", "closed"}

# ENV: Admin bilgilendirme adresleri (virgüllü)
ADMIN_NOTIFY_EMAILS = os.getenv("ADMIN_NOTIFY_EMAILS", "")

async def create_ticket(restaurant_id, email, restaurant_name, subject, message):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO support_tickets (restaurant_id, email, restaurant_name, subject, message)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """, (restaurant_id, email, restaurant_name, subject, message))
        new_id = cur.fetchone()[0]

    # Admin'e bilgilendirme (opsiyonel)
    if ADMIN_NOTIFY_EMAILS and build_support_new_ticket_email:
        html = build_support_new_ticket_email(restaurant_name, email, subject, message, new_id)
        for addr in [x.strip() for x in ADMIN_NOTIFY_EMAILS.split(",") if x.strip()]:
            try:
                await send_mail(addr, f"Yeni Destek Talebi #{new_id}", html)
            except Exception:
                pass

    return new_id

async def list_admin_tickets():
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM support_tickets ORDER BY created_at DESC")
        return cur.fetchall()

async def list_my_tickets(restaurant_id):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            "SELECT * FROM support_tickets WHERE restaurant_id = %s ORDER BY created_at DESC",
            (restaurant_id,))
        return cur.fetchall()

async def reply_ticket(ticket_id, reply):
    # Ticket bilgilerini al
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM support_tickets WHERE id=%s", (ticket_id,))
        row = cur.fetchone()
        if not row:
            return False, "Ticket not found"

    # DB'de yanıt ve durum
    with db_cursor() as cur:
        cur.execute("""
            UPDATE support_tickets 
            SET reply = %s, status = 'answered', replied_at = NOW()
            WHERE id = %s
        """, (reply, ticket_id))

    # Restorana mail gönder
    try:
        html = build_support_reply_email(
            restaurant_name=row["restaurant_name"],
            subject=row["subject"],
            original_message=row["message"],
            reply=reply
        )
        ok, msg = await send_mail(row["email"], f"Destek Yanıtı • {row['subject']}", html)
        if not ok:
            return False, f"Yanıt kaydedildi fakat mail gönderilemedi: {msg}"
    except Exception as e:
        return False, f"Yanıt kaydedildi fakat mail hatası: {e}"

    return True, "Reply sent"

async def update_ticket_status(ticket_id: int, new_status: str):
    new_status = (new_status or "").strip().lower()
    if new_status not in ALLOWED_STATUSES:
        return False, f"Invalid status. Allowed: {', '.join(sorted(ALLOWED_STATUSES))}"

    with db_cursor() as cur:
        cur.execute("UPDATE support_tickets SET status=%s WHERE id=%s", (new_status, ticket_id))
        if cur.rowcount == 0:
            return False, "Ticket not found"
    return True, "Status updated"

async def delete_ticket(ticket_id: int, requester_id: str, roles) -> Tuple[bool, str]:
    """
    Admin: her kaydı silebilir
    Restaurant: sadece kendi restaurant_id'sine ait kaydı silebilir
    """
    # rolleri normalize et
    if isinstance(roles, str):
        roles = [roles]
    roles = roles or []

    is_admin = "Admin" in roles
    is_restaurant = "Restaurant" in roles

    if not (is_admin or is_restaurant):
        return False, "Forbidden"

    with db_cursor() as cur:
        if is_admin:
            cur.execute(
                "DELETE FROM support_tickets WHERE id = %s RETURNING id",
                (ticket_id,),
            )
        else:
            # restaurant kendi kaydını silebilir
            cur.execute(
                "DELETE FROM support_tickets WHERE id = %s AND restaurant_id = %s RETURNING id",
                (ticket_id, requester_id),
            )

        row = cur.fetchone()
        if not row:
            # kayıt yok ya da yetkin yok
            return False, "Ticket not found or not allowed"

    return True, "Ticket deleted"