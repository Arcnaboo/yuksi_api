
from app.services.paytr_service import PaymentRequest, paytr_service
import base64

req = PaymentRequest(
    user_ip="78.183.89.120",
    merchant_oid="test123456",
    email="a@b.com",
    payment_amount=10000,        # 100.00 TL
    currency="TL",
    test_mode=0,
    non_3d=1,
    payment_type="card",             # normal sale
    installment_count=0,
    basket_json=base64.b64encode(b'[["Item", "50.00", 1]]').decode()
)
resp = paytr_service.create_payment(req)
print(resp)