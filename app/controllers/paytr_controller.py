import os
from dotenv import load_dotenv
from fastapi import Request
from app.models.paytr_models import PaytrConfig, PaymentRequest, CallbackData
from app.services.paytr_service import PaytrService

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
    service = PaytrService(get_config())
    return service.create_payment(req)

async def handle_callback(request: Request):
    form = await request.form()
    callback = CallbackData(
        merchant_oid=form.get("merchant_oid"),
        status=form.get("status"),
        total_amount=int(form.get("total_amount", "0")),
        hash=form.get("hash")
    )

    service = PaytrService(get_config())
    verified = service.verify_callback(callback)

    if verified and callback.status == "success":
        # buraya sipariş güncelleme, fatura oluşturma vb.
        return "OK"
    else:
        return "FAIL"
