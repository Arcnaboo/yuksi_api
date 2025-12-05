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
    print("CALLBACK")
    logging.info(f"PAYTR CALLBACK {request}")
    form = await request.form()

    callback = CallbackData(
        merchant_oid=form.get("merchant_oid"),
        status=form.get("status"),
        total_amount=int(form.get("total_amount", "0")),
        hash=form.get("hash"),
    )

    logging.info(f"callback data {callback}")

    service = paytr_service
    verified = service.verify_callback(callback)

    if verified and callback.status == "success":
        print("başarı")
        # SUB-uuid → uuid
        sub_id = callback.merchant_oid.removeprefix("SUB")

        with db_cursor(dict_cursor=True) as cur:
            # 1) Request kaydını çek
            cur.execute("""
                SELECT * FROM courier_subscription_requests
                WHERE id = %(id)s
            """, {"id": sub_id})
            row = cur.fetchone()

            # 2) Yeni subscription INSERT
            cur.execute("""
                INSERT INTO courier_package_subscriptions
                (courier_id, package_id, start_date, end_date, is_active)
                VALUES
                (%(courier_id)s, %(package_id)s, %(start)s, %(end)s, TRUE)
                RETURNING id;
            """, {
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

    else:    
        print("hata")
        logging.info("callback failed")

    return Response(content="OK", media_type="text/plain")