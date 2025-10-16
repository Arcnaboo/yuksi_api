
# app/utils/templates/notification_template.py

class NotificationEmailTemplate:
    @staticmethod
    def build(subject: str, message: str) -> str:
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
        </head>
        <body style="margin:0; padding:0; background:#f7f7f7; font-family:Arial,sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding:24px;">
                        <table width="600" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.08); overflow:hidden;">
                            
                            <!-- ✅ LOGO -->
                            <tr>
                                <td style="text-align:center; padding:20px;">
                                    <img src="https://yuksi.tr/wp-content/uploads/2025/05/yuksituruncu.jpg" width="120" alt="Yuksi" style="border-radius:8px; margin-bottom:10px;">
                                </td>
                            </tr>

                            <!-- ✅ BAŞLIK -->
                            <tr>
                                <td style="padding:10px 24px 0 24px; text-align:center;">
                                    <h2 style="color:#FF6F3C; margin:0;">{subject}</h2>
                                </td>
                            </tr>

                            <!-- ✅ MESAJ GÖVDE -->
                            <tr>
                                <td style="padding:16px 24px 28px 24px;">
                                    <div style="padding:16px 18px; background:#FFF5EB; border-left:6px solid #FF6F3C; border-radius:8px;">
                                        {message}
                                    </div>
                                    <p style="font-size:12px; color:#888; margin-top:24px;">Bu e-posta sistem tarafından otomatik gönderildi.</p>
                                </td>
                            </tr>

                            <!-- ✅ FOOTER -->
                            <tr>
                                <td style="background:#FF6F3C; color:#fff; text-align:center; padding:12px; font-size:12px;">
                                    © 2025 YuksiApp — Bildirim Sistemi
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

