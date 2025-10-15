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
