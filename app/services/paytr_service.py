# app/services/paytr_service.py
import base64, hmac, hashlib, requests
from app.models.paytr_models import PaytrConfig, PaymentRequest, PaymentResponse, CallbackData

class PaytrService:
    TOKEN_URL = "https://www.paytr.com/odeme/api/get-token"

    def __init__(self, config: PaytrConfig):
        self.config = config

    def _create_hash(self, req: PaymentRequest) -> str:
        hash_str = (
            f"{self.config.merchant_id}"
            f"{req.user_ip}"
            f"{req.merchant_oid}"
            f"{req.email}"
            f"{req.payment_amount}"
            f"{req.currency}"
            f"{req.test_mode}"
            f"{req.non_3d}"
            f"{self.config.merchant_salt}"
        )
        hashed = hmac.new(
            self.config.merchant_key.encode(),
            hash_str.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(hashed).decode()

    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        token_hash = self._create_hash(req)
        payload = {
            "merchant_id": self.config.merchant_id,
            "user_ip": req.user_ip,
            "merchant_oid": req.merchant_oid,
            "email": req.email,
            "payment_amount": req.payment_amount,
            "currency": req.currency,
            "test_mode": req.test_mode,
            "non_3d": req.non_3d,
            "merchant_ok_url": self.config.ok_url,
            "merchant_fail_url": self.config.fail_url,
            "user_basket": req.basket_json,
            "paytr_token": token_hash,
        }
        try:
            r = requests.post(self.TOKEN_URL, data=payload, timeout=10)
            data = r.json()
            return PaymentResponse(status=data.get("status", "error"), token=data.get("token"), reason=data.get("reason"))
        except Exception as e:
            return PaymentResponse(status="error", reason=str(e))

    def verify_callback(self, callback: CallbackData) -> bool:
        check_str = f"{callback.merchant_oid}{self.config.merchant_salt}{callback.status}{callback.total_amount}"
        hashed = hmac.new(
            self.config.merchant_key.encode(),
            check_str.encode(),
            hashlib.sha256
        ).digest()
        expected_hash = base64.b64encode(hashed).decode()
        return expected_hash == callback.hash
