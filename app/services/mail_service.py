import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USER)
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"

async def send_mail(to: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    ✅ Tek mail gönderimi (Base fonksiyon)
    (Same logic, detailed logging only)
    """
    try:
        logging.info("[MAIL-A] send_mail STARTED")
        logging.info(f"[MAIL-A1] to={to}, subject={subject}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = MAIL_FROM
        msg["To"] = to

        part = MIMEText(html_body, "html")
        msg.attach(part)
        logging.info("[MAIL-B] MIME message composed")

        logging.info("[MAIL-C] opening SMTP connection")
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            logging.info("[MAIL-C1] SMTP connection opened")

            if MAIL_TLS:
                logging.info("[MAIL-D] starting TLS handshake")
                server.starttls()
                logging.info("[MAIL-D1] TLS handshake complete")

            logging.info("[MAIL-E] logging in to mail server")
            server.login(MAIL_USER, MAIL_PASS)
            logging.info("[MAIL-E1] login successful")

            logging.info("[MAIL-F] sending email message")
            server.sendmail(MAIL_FROM, to, msg.as_string())
            logging.info("[MAIL-F1] sendmail() completed")

        logging.info("[MAIL-G] SMTP connection closed")
        return True, "Mail başarıyla gönderildi"

    except Exception as e:
        logging.exception("[MAIL-ERR] send_mail FAILED")
        return False, str(e)

async def send_single_mail(email: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Tek kişiye bildirim
    """
    return await send_mail(email, subject, message)


async def send_bulk_mail(user_type: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Toplu bildirim (all, courier, restaurant)
    """
    from app.utils.database import db_cursor

    try:
        if user_type == "all":
            query = "SELECT email FROM drivers UNION SELECT email FROM restaurants"
        elif user_type == "courier":
            query = "SELECT email FROM drivers"
        elif user_type == "restaurant":
            query = "SELECT email FROM restaurants"
        else:
            return False, "Geçersiz user_type"

        with db_cursor(dict_cursor=True) as cur:
            cur.execute(query)
            rows = cur.fetchall()

        if not rows:
            return False, "Gönderilecek kullanıcı bulunamadı"

        for row in rows:
            email = row["email"]
            await send_mail(email, subject, message)

        return True, "Toplu mail gönderildi"

    except Exception as e:
        return False, str(e)
