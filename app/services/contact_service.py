from typing import Any, Dict, Tuple, Optional, List
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services.mail_service import send_mail
from app.utils.templates.contact_user_template import ContactMessageEmailTemplate
from app.utils.templates.contact_admin_template import ContactAdminEmailTemplate
import os
from datetime import datetime
import logging

ADMIN_EMAIL = os.getenv("MAIL_USER", "testmaildeneme77@gmail.com")


# === CREATE CONTACT MESSAGE ===
async def create_contact_message(
    name: str,
    email: str,
    phone: str,
    subject: str,
    message: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        logging.info("[A] create_contact_message STARTED")
        logging.info(f"[A1] incoming data name={name}, email={email}, phone={phone}")

        # --- DB INSERT ---
        query = """
            INSERT INTO contact_messages (name, email, phone, subject, message)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, created_at;
        """
        row = await fetch_one(query, name, email, phone, subject, message)
        if not row:
            return None, "Insert failed"

        result = {"id": row["id"], "created_at": row["created_at"]}
        sent_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        logging.info(f"[C] sent_at={sent_at}")

        # --- USER EMAIL ---
        user_html = ContactMessageEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        await send_mail(email, "Mesajınız Başarıyla Alındı 🎉", user_html)
        logging.info("[D2] user email sent successfully")

        # --- ADMIN EMAIL ---
        admin_html = ContactAdminEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        await send_mail(ADMIN_EMAIL, f"Yeni Contact Mesajı - {subject}", admin_html)
        logging.info("[E2] admin email sent successfully")

        logging.info("[F] create_contact_message COMPLETED SUCCESSFULLY")
        return result, None

    except Exception as e:
        logging.exception("[ERR] create_contact_message FAILED")
        return None, str(e)


# === GET ALL CONTACT MESSAGES ===
async def get_all_contact_messages(
    limit: int = 50,
    offset: int = 0
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        logging.info("[A] get_all_contact_messages STARTED")
        query = """
            SELECT id, name, email, phone, subject, message, created_at
            FROM contact_messages
            ORDER BY id DESC
            LIMIT $1 OFFSET $2;
        """
        rows = await fetch_all(query, limit, offset)
        if not rows:
            return None, "No messages found"

        items = [
            {
                "id": r["id"],
                "name": r["name"],
                "email": r["email"],
                "phone": r["phone"],
                "subject": r["subject"],
                "message": r["message"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
        logging.info(f"[C] {len(items)} contact messages fetched")
        return items, None

    except Exception as e:
        logging.exception("[ERR] get_all_contact_messages FAILED")
        return None, str(e)


# === DELETE CONTACT MESSAGE ===
async def delete_contact_message(contact_id: int) -> Optional[str]:
    try:
        logging.info("[A] delete_contact_message STARTED")
        query = "DELETE FROM contact_messages WHERE id = $1 RETURNING id;"
        row = await fetch_one(query, contact_id)
        if not row:
            return "Contact message not found"
        logging.info("[C] delete_contact_message COMPLETED SUCCESSFULLY")
        return None

    except Exception as e:
        logging.exception("[ERR] delete_contact_message FAILED")
        return str(e)
