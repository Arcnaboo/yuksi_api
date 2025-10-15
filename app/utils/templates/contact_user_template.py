# app/utils/templates/contact_message_template.py

class ContactMessageEmailTemplate:
    @staticmethod
    def build(full_name: str, email: str, phone: str, subject: str, message: str, sent_at: str) -> str:
        return f"""
        <html>
        <head>
            <meta charset='UTF-8'>
            <title>YuksiApp - Mesajınız Alındı</title>
        </head>
        <body style='margin:0; padding:0; background:linear-gradient(120deg, #FFE5B4, #FFDAB3); font-family:Arial,sans-serif;'>
            <table width='100%' cellpadding='0' cellspacing='0'>
                <tr>
                    <td align='center'>
                        <table width='600' cellpadding='0' cellspacing='0' style='background:#fff; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.1); overflow:hidden;'>
                            <tr>
                                <td align='center' style='padding:40px 20px 20px 20px;'>
                                    <img src='https://yuksi.tr/wp-content/uploads/2025/05/yuksituruncu.jpg' width='100' style='margin-bottom:20px;'/>
                                    <h2 style='color:#FF6F3C; margin:0;'>Mesajınız Alındı 🎉</h2>
                                    <p style='color:#555; font-size:16px; margin:10px 0;'>Merhaba <b>{full_name}</b>,</p>
                                    <p style='color:#555; font-size:16px; margin:5px 0;'>Mesajınız bize başarıyla ulaştı. En kısa sürede size geri dönüş yapacağız.</p>
                                    
                                    <hr style='margin:25px 0; border:none; border-top:1px solid #eee;'/>
                                    
                                    <table width='100%' cellpadding='5' cellspacing='0' style='font-size:15px; color:#333;'>
                                        <tr><td><b>Konu:</b></td><td>{subject}</td></tr>
                                        <tr><td><b>Telefon:</b></td><td>{phone}</td></tr>
                                        <tr><td><b>E-posta:</b></td><td>{email}</td></tr>
                                        <tr><td><b>Gönderim Zamanı:</b></td><td>{sent_at}</td></tr>
                                    </table>

                                    <div style='margin:30px 0; padding:20px 25px; background:#FFF5EB; border-left:6px solid #FF6F3C; border-radius:10px; box-shadow:0 3px 8px rgba(255,111,60,0.15); text-align:left;'>
                                        <p style='color:#333; font-size:15px; line-height:1.6; margin:0;'>
                                            <b style='color:#FF6F3C;'>Mesajınız:</b><br>
                                            <span style='display:block; margin-top:10px; white-space:pre-line;'>{message}</span>
                                        </p>
                                    </div>

                                    <p style='font-size:14px; color:#777;'>YuksiApp ekibinden sevgiler 💛</p>
                                </td>
                            </tr>
                            <tr>
                                <td style='background:#FF6F3C; color:#fff; text-align:center; padding:15px; font-size:12px;'>
                                    © 2025 YuksiApp. Tüm hakları saklıdır.
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
