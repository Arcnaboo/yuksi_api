# app/utils/templates/support_reply_template.py
LOGO_URL = "https://yuksi.tr/wp-content/uploads/2025/05/yuksituruncu.jpg"

def build_support_reply_email(restaurant_name: str, subject: str, original_message: str, reply: str) -> str:
    return f"""
    <html>
    <head><meta charset="UTF-8"><title>Destek Talebinize Yanıt</title></head>
    <body style="margin:0;padding:0;background:#f7f7f9;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.08);">
            <tr>
              <td align="center" style="padding:24px 24px 8px 24px;">
                <img src="{LOGO_URL}" alt="Yuksi" width="88" style="display:block;margin-bottom:8px;" />
                <h2 style="margin:8px 0 0 0;color:#FF6F3C;">Destek Yanıtı</h2>
              </td>
            </tr>
            <tr>
              <td style="padding:0 24px 24px 24px;">
                <p style="color:#333;">Merhaba <b>{restaurant_name}</b>,</p>
                <p style="color:#333;">"<b>{subject}</b>" konulu talebinize aşağıdaki yanıtı ilettik:</p>

                <div style="margin:16px 0;padding:14px 16px;background:#FFF5EB;border-left:6px solid #FF6F3C;border-radius:8px;">
                  <div style="font-size:13px;color:#777;margin-bottom:6px;">Orijinal Mesaj</div>
                  <div style="white-space:pre-line;color:#333;">{original_message}</div>
                </div>

                <div style="margin:16px 0;padding:14px 16px;background:#E9F7FF;border-left:6px solid #2F80ED;border-radius:8px;">
                  <div style="font-size:13px;color:#555;margin-bottom:6px;">Yönetici Yanıtı</div>
                  <div style="white-space:pre-line;color:#0F3A60;">{reply}</div>
                </div>

                <p style="color:#666;font-size:12px;margin-top:24px;">Bu e-posta otomatik gönderilmiştir.</p>
              </td>
            </tr>
            <tr>
              <td style="background:#FF6F3C;color:#fff;text-align:center;padding:12px;font-size:12px;">
                © 2025 Yuksi • Destek Sistemi
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """
