import os
from dotenv import load_dotenv
from fastapi import Request
from app.models.paytr_models import PaytrConfig, PaymentRequest, CallbackData
from app.services.paytr_service import paytr_service
import logging
from app.utils.database import db_cursor
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from fastapi import Response
load_dotenv()

def get_config() -> PaytrConfig:
    return PaytrConfig(
        merchant_id=os.getenv("PAYTR_MERCHANT_ID"),
        merchant_key=os.getenv("PAYTR_MERCHANT_KEY"),
        merchant_salt=os.getenv("PAYTR_MERCHANT_SALT"),
        ok_url=os.getenv("PAYTR_OK_URL"),
        fail_url=os.getenv("PAYTR_FAIL_URL"),
        callback_url=os.getenv("PAYTR_CALLBACK_URL"),
        test_mode=1
    )

def init_payment(req: PaymentRequest):
    service = paytr_service
    return service.create_payment(req)

async def handle_callback(request: Request):
    # 1. Loglamayı detaylandıralım
    logging.info(f"PAYTR CALLBACK RECEIVED - Client IP: {request.client.host}")
    
    try:
        form = await request.form()
        
        # Form verilerini güvenli alalım (Hata çıkarsa loglayıp yakalayabilelim)
        callback = CallbackData(
            merchant_oid=form.get("merchant_oid"),
            status=form.get("status"),
            total_amount=int(form.get("total_amount", "0")),
            hash=form.get("hash"),
        )
        
        logging.info(f"Callback Parsed: {callback.merchant_oid} - Status: {callback.status}")

        service = paytr_service
        # Hash doğrulaması
        verified = service.verify_callback(callback)

        if not verified:
            logging.error("PAYTR HASH VERIFICATION FAILED! - Hack attempt or configuration error.")
            # Hash tutmuyorsa OK dönmemeliyiz ki PayTR hata olduğunu bilsin, 
            # ya da loglayıp OK dönebilirsin (saldırı ise log kirlenmesin diye).
            return Response(content="OK", media_type="text/plain") 

        # Sadece SUCCESS durumunda işlem yap
        if callback.status == "success":
            sub_id = callback.merchant_oid.removeprefix("SUB")

            with db_cursor(dict_cursor=True) as cur:
                # 1) Request kaydını çek
                cur.execute("""
                    SELECT * FROM courier_subscription_requests
                    WHERE id = %(id)s
                """, {"id": sub_id})
                row = cur.fetchone()

                # --- KRİTİK DÜZELTME BURADA ---
                if not row:
                    logging.error(f"FATAL: Ödeme başarılı ama Request ID DB'de bulunamadı: {sub_id}")
                    # Kayıt yoksa yapacak bir şey yok, PayTR'a OK dönüp döngüyü kıralım.
                    return Response(content="OK", media_type="text/plain")

                # Kayıt varsa işleme devam et
                try:
                    # 2) Yeni subscription INSERT
                    cur.execute("""
                        INSERT INTO courier_package_subscriptions
                        (id,courier_id, package_id, start_date, end_date, is_active)
                        VALUES
                        (%(sub_id)s,%(courier_id)s, %(package_id)s, %(start)s, %(end)s, TRUE)
                        RETURNING id;
                    """, {
                        "sub_id": sub_id,
                        "courier_id": row["courier_id"],
                        "package_id": row["package_id"],
                        "start": row["start_date"],
                        "end": row["end_date"],
                    })

                    # 3) Ödeme durumunu güncelle
                    cur.execute("""
                        UPDATE courier_subscription_requests
                        SET payment_status = 'completed', is_active = TRUE
                        WHERE id = %(id)s
                    """, {"id": sub_id})
                    
                    logging.info(f"Payment processed successfully for ID: {sub_id}")

                except Exception as db_err:
                    logging.error(f"DB Transaction Error for {sub_id}: {str(db_err)}")
                    # Veritabanı hatası varsa 500 fırlatabiliriz ki PayTR sonra tekrar denesin.
                    # VEYA manuel düzeltme yapacaksan 'OK' dönüp loga bakarsın.
                    # Şimdilik sonsuz döngüden çıkmak için OK dönüyoruz:
                    return Response(content="OK", media_type="text/plain")

        else:
            # Ödeme başarısız (status != success)
            logging.info(f"Payment failed via PayTR for {callback.merchant_oid}")
            # Başarısız işlem için de PayTR bizden "OK" bekler (bildirimi aldım demek için).
            
    except Exception as e:
        # En genel hata yakalayıcı (Form parsing hatası vs.)
        logging.error(f"UNHANDLED EXCEPTION IN CALLBACK: {str(e)}")
        # Eğer kod burada patlarsa PayTR'a OK gitmez, 500 gider.
        # Sonsuz döngüyü kırmak istiyorsan buraya da return OK koyabilirsin.
        return Response(content="OK", media_type="text/plain")

    # En son her şey yolundaysa
    return Response(content="OK", media_type="text/plain")