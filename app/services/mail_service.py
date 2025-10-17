import os
import logging
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.database import db_cursor  # keep this import for bulk mail

# environment
MAIL_FROM = os.getenv("MAIL_FROM", "Yuksi Destek <support@yuksi.dev>")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# ---------------------------------------------------------------------------------
# Base mail sender via Resend HTTPS API
# ---------------------------------------------------------------------------------
async def send_mail(to: str, subject: str, html_body: str) -> tuple[bool, str]:
    """
    ✅ Tek mail gönderimi (Base fonksiyon)
    Uses Resend API (works on Render – no SMTP)
    """
    try:
        logging.info("[MAIL-A] send_mail STARTED (Resend API)")
        logging.info(f"[MAIL-A1] to={to}, subject={subject}, from={MAIL_FROM}")

        if not RESEND_API_KEY:
            logging.error("[MAIL-ERR] RESEND_API_KEY not set")
            return False, "RESEND_API_KEY missing"

        # MIME generation (optional, for template consistency)
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

        logging.info("[MAIL-B] Sending via Resend API...")
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

# ---------------------------------------------------------------------------------
# Controller wrappers (same signatures as before)
# ---------------------------------------------------------------------------------
async def send_single_mail(email: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Tek kişiye bildirim
    """
    return await send_mail(email, subject, message)


async def send_bulk_mail(user_type: str, subject: str, message: str) -> tuple[bool, str]:
    """
    ✅ Controller -> Toplu bildirim (all, courier, restaurant)
    """
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
        logging.exception("[MAIL-ERR] send_bulk_mail FAILED")
        return False, str(e)
