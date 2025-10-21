from typing import Any, Dict, Tuple, Optional, List
from app.utils.database import db_cursor
from app.services.mail_service import send_mail
from app.utils.templates.contact_user_template import ContactMessageEmailTemplate
from app.utils.templates.contact_admin_template import ContactAdminEmailTemplate
import os
from datetime import datetime
import logging
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
        logging.info("[A] create_contact_message STARTED")
        logging.info(f"[A1] incoming data name={name}, email={email}, phone={phone}")

        # --- DB INSERT ---
        logging.info("[B] opening db_cursor()")
        with db_cursor() as cur:
            logging.info("[B1] cursor opened, executing INSERT")
            cur.execute(
                """
                INSERT INTO contact_messages (name, email, phone, subject, message)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at;
                """,
                (name, email, phone, subject, message)
            )
            logging.info("[B2] INSERT executed, fetching result")
            row = cur.fetchone()
            logging.info(f"[B3] fetchone() result: {row}")

            result = {
                "id": row["id"] if isinstance(row, dict) else row[0],
                "created_at": row["created_at"] if isinstance(row, dict) else row[1],
            }
        logging.info("[B4] DB COMMIT COMPLETE")

        # --- DATE FORMAT ---
        sent_at = datetime.now().strftime("%d.%m.%Y %H:%M")
        logging.info(f"[C] sent_at={sent_at}")

        # --- USER EMAIL ---
        logging.info("[D] building user email template")
        user_html = ContactMessageEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        logging.info("[D1] user template built, sending email")
        await send_mail(email, "Mesajınız Başarıyla Alındı 🎉", user_html)
        logging.info("[D2] user email sent successfully")

        # --- ADMIN EMAIL ---
        logging.info("[E] building admin email template")
        admin_html = ContactAdminEmailTemplate.build(
            full_name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            sent_at=sent_at
        )
        logging.info("[E1] admin template built, sending email")
        await send_mail(ADMIN_EMAIL, f"Yeni Contact Mesajı - {subject}", admin_html)
        logging.info("[E2] admin email sent successfully")

        logging.info("[F] create_contact_message COMPLETED SUCCESSFULLY")
        return result, None

    except Exception as e:
        logging.exception("[ERR] create_contact_message FAILED")
        return None, str(e)

async def get_all_contact_messages(
    limit: int = 50,
    offset: int = 0
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    try:
        logging.info("[A] get_all_contact_messages STARTED")
        logging.info(f"[A1] params → limit={limit}, offset={offset}")

        logging.info("[B] opening db_cursor()")
        with db_cursor() as cur:
            logging.info("[B1] cursor opened, executing SELECT query")
            cur.execute(
                """
                SELECT id, name, email, phone, subject, message, created_at
                FROM contact_messages
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
                """,
                (limit, offset)
            )
            logging.info("[B2] SELECT executed, fetching rows")
            rows = cur.fetchall()
            logging.info(f"[B3] fetched {len(rows)} rows")

            items: List[Dict[str, Any]] = []
            for idx, r in enumerate(rows):
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
                if idx < 3:
                    logging.info(f"[B4-{idx}] first rows preview: {items[-1]}")
            logging.info("[C] all rows processed successfully")

        logging.info("[D] get_all_contact_messages COMPLETED SUCCESSFULLY")
        return items, None

    except Exception as e:
        logging.exception("[ERR] get_all_contact_messages FAILED")
        return None, str(e)

async def delete_contact_message(contact_id: int) -> Optional[str]:
    try:
        logging.info("[A] delete_contact_message STARTED")
        logging.info(f"[A1] deleting contact_id={contact_id}")

        logging.info("[B] opening db_cursor()")
        with db_cursor() as cur:
            logging.info("[B1] cursor opened, executing DELETE")
            cur.execute("DELETE FROM contact_messages WHERE id = %s;", (contact_id,))
            logging.info("[B2] DELETE executed successfully")

        logging.info("[C] delete_contact_message COMPLETED SUCCESSFULLY")
        return None

    except Exception as e:
        logging.exception("[ERR] delete_contact_message FAILED")
        return str(e)
