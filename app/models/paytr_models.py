# app/models/paytr_models.py
from pydantic import BaseModel

class PaytrConfig(BaseModel):
    merchant_id: str
    merchant_key: str
    merchant_salt: str
    ok_url: str
    fail_url: str
    callback_url: str
    test_mode: int = 1
    non_3d: int = 0


class PaymentRequest(BaseModel):
    merchant_oid: str
    email: str
    payment_amount: int  # örn: 100.00 TL = 10000
    currency: str = "TL"
    user_ip: str = "127.0.0.1"
    installment_count: int = 0
    no_installment: int = 1
    basket_json: str = '[["Ürün", "1.00", 1]]'
    lang: str = "tr"
    test_mode: int = 1
    non_3d: int = 0


class PaymentResponse(BaseModel):
    status: str
    token: str | None = None
    reason: str | None = None


class CallbackData(BaseModel):
    merchant_oid: str
    status: str
    total_amount: int
    hash: str
