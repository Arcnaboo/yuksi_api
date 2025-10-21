# arda_test.py (updated)
from app.services.paytr_service import PaymentRequest, paytr_service
import base64

req = PaymentRequest(
    user_ip="78.183.89.120",
    merchant_oid="arda1234567",
    email="a@b.com",
    payment_amount=10000,        # 100.00 TL (kuruş pricing)
    currency="TL",
    test_mode=0,                 # keep as you had it (0 or 1 depending on sandbox)
    non_3d=0,                    # use 3D flow
    payment_type="card",         # normal sale
    installment_count=0,
    basket_json=base64.b64encode(b'[["Item", "50.00", 1]]').decode(),

    # --- HARDCODED VIRTUAL CARD (you requested) ---
    cc_owner="Arda Akgur",
    card_number="4183421279930647",
    expiry_month="06",
    expiry_year="32",
    cvv="279"
)

resp = paytr_service.create_payment(req)
print(resp)
