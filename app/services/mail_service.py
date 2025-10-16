import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USER)
MAIL_TLS = os.getenv("MAIL_TLS", "true").lower() == "true"

async def send_mail(to: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    ✅ Tek mail gönderimi (Base fonksiyon)
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = MAIL_FROM
        msg["To"] = to

        part = MIMEText(html_body, "html")
        msg.attach(part)

        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            if MAIL_TLS:
                server.starttls()
            server.login(MAIL_USER, MAIL_PASS)
            server.sendmail(MAIL_FROM, to, msg.as_string())

        return True, "Mail başarıyla gönderildi"
    except Exception as e:
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
