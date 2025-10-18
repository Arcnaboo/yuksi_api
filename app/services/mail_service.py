import os
import logging
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.db import fetch_all  # asyncpg tabanlı

# Environment
MAIL_FROM = os.getenv("MAIL_FROM", "Yuksi Destek <support@yuksi.dev>")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


# === BASE MAIL SENDER ===
async def send_mail(to: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    ✅ Tek mail gönderimi (Resend API kullanır)
    """
    try:
        logging.info("[MAIL-A] send_mail STARTED (Resend API)")
        logging.info(f"[MAIL-A1] to={to}, subject={subject}, from={MAIL_FROM}")

        if not RESEND_API_KEY:
            logging.error("[MAIL-ERR] RESEND_API_KEY not set")
            return False, "RESEND_API_KEY missing"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = MAIL_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        payload = {
            "from": MAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html_body,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )

        if r.status_code == 200:
            logging.info("[MAIL-C] Resend accepted message ✅")
            return True, "Mail başarıyla gönderildi"
        else:
            logging.error(f"[MAIL-ERR] Resend error {r.status_code}: {r.text}")
            return False, f"Resend error {r.status_code}: {r.text}"

    except Exception as e:
        logging.exception("[MAIL-ERR] send_mail FAILED")
        return False, str(e)


# === TEK KİŞİLİK GÖNDERİ ===
async def send_single_mail(email: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Tek kişiye bildirim
    """
    return await send_mail(email, subject, message)


# === TOPLU GÖNDERİ ===
async def send_bulk_mail(user_type: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Toplu bildirim (all, courier, restaurant)
    """
    try:
        if user_type == "all":
            query = "SELECT email FROM drivers UNION SELECT email FROM restaurants;"
        elif user_type == "courier":
            query = "SELECT email FROM drivers;"
        elif user_type == "restaurant":
            query = "SELECT email FROM restaurants;"
        else:
            return False, "Geçersiz user_type"

        rows = await fetch_all(query)
        if not rows:
            return False, "Gönderilecek kullanıcı bulunamadı"

        # Toplu gönderim (asenkron sırayla)
        for r in rows:
            email = r["email"]
            ok, msg = await send_mail(email, subject, message)
            if not ok:
                logging.warning(f"[MAIL-WARN] Mail gönderilemedi: {email} ({msg})")

        return True, "Toplu mail gönderildi"

    except Exception as e:
        logging.exception("[MAIL-ERR] send_bulk_mail FAILED")
        return False, str(e)
