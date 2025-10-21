# app/models/paytr_models.py
from pydantic import BaseModel, Field
import uuid

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
    # 🔹 Basic required fields
    id: uuid.UUID
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

    # 🔹 Card info fields (for Direct API mode)
    cc_owner: str | None = Field(default=None, description="Card holder name")
    card_number: str | None = Field(default=None, description="Card number (no spaces)")
    expiry_month: str | None = Field(default=None, description="MM format, e.g. '12'")
    expiry_year: str | None = Field(default=None, description="YY format, e.g. '26'")
    cvv: str | None = Field(default=None, description="3-digit CVV")

    # 🔹 Optional customer info fields
    user_name: str | None = None
    user_address: str | None = None
    user_phone: str | None = None



class PaymentResponse(BaseModel):
    status: str
    token: str | None = None
    reason: str | None = None


class CallbackData(BaseModel):
    merchant_oid: str
    status: str
    total_amount: int
    hash: str
