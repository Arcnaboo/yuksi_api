from typing import Any, Dict, Tuple, Optional, List
from app.utils.database import db_cursor
from app.services.mail_service import send_mail
from app.utils.templates.contact_user_template import ContactMessageEmailTemplate
from app.utils.templates.contact_admin_template import ContactAdminEmailTemplate
import os
from datetime import datetime

# Admin Email .env'den çekiyoruz
ADMIN_EMAIL = os.getenv("MAIL_USER", "testmaildeneme77@gmail.com")


async def create_contact_message(
    name: str,
    email: str,
    phone: str,
    subject: str,
    message: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        # DB INSERT
        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO contact_messages (name, email, phone, subject, message)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at;
                """,
                (name, email, phone, subject, message)
            )
            row = cur.fetchone()
            result = {
                "id": row["id"] if isinstance(row, dict) else row[0],
                "created_at": row["created_at"] if isinstance(row, dict) else row[1],
            }

        # Tarih Format
        sent_at = datetime.now().strftime("%d.%m.%Y %H:%M")

        # ✅ Kullanıcı Maili (Templated)
        user_html = ContactMessageEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        await send_mail(email, "Mesajınız Başarıyla Alındı 🎉", user_html)

        # ✅ Admin Maili (Templated)
        admin_html = ContactAdminEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        await send_mail(ADMIN_EMAIL, f"Yeni Contact Mesajı - {subject}", admin_html)

        return result, None

    except Exception as e:
        return None, str(e)


async def get_all_contact_messages(
    limit: int = 50,
    offset: int = 0
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, name, email, phone, subject, message, created_at
                FROM contact_messages
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
                """,
                (limit, offset)
            )
            rows = cur.fetchall()
            items: List[Dict[str, Any]] = []
            for r in rows:
                row = r if isinstance(r, dict) else None
                items.append({
                    "id": (row and row.get("id")) or r[0],
                    "name": (row and row.get("name")) or r[1],
                    "email": (row and row.get("email")) or r[2],
                    "phone": (row and row.get("phone")) or r[3],
                    "subject": (row and row.get("subject")) or r[4],
                    "message": (row and row.get("message")) or r[5],
                    "created_at": (row and row.get("created_at")) or r[6],
                })
            return items, None
    except Exception as e:
        return None, str(e)


async def delete_contact_message(contact_id: int) -> Optional[str]:
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM contact_messages WHERE id = %s;", (contact_id,))
        return None
    except Exception as e:
        return str(e)
