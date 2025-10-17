# app/services/paytr_service.py
import base64, hmac, hashlib, requests
from app.models.paytr_models import PaytrConfig, PaymentRequest, PaymentResponse, CallbackData
import logging, os

class PaytrService:
    TOKEN_URL = "https://www.paytr.com/odeme/api/get-token"

    def __init__(self, config: PaytrConfig):
        self.config = config
        logging.info("[PaytrService] Initialized with merchant_id=%s", config.merchant_id)

    def _create_hash(self, req: PaymentRequest) -> str:
        logging.info("[_create_hash] Start creating hash for merchant_oid=%s", req.merchant_oid)
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
        logging.info("[_create_hash] Hash string prepared: %s", hash_str)
        hashed = hmac.new(
            self.config.merchant_key.encode(),
            hash_str.encode(),
            hashlib.sha256
        ).digest()
        encoded = base64.b64encode(hashed).decode()
        logging.info("[_create_hash] Hash created successfully")
        return encoded

    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        logging.info("[create_payment] Starting payment creation for merchant_oid=%s", req.merchant_oid)
        token_hash = self._create_hash(req)
        logging.info("[create_payment] Token hash created")

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
            "no_installment": 0,  # ✅ Zorunlu alan eklendi
        }

        logging.info("[create_payment] Payload prepared: %s", payload)
        logging.info("[create_payment] Using no_installment=%s", payload["no_installment"])

        try:
            r = requests.post(self.TOKEN_URL, data=payload, timeout=10)
            logging.info("[create_payment] Request sent to PayTR, status_code=%s", r.status_code)
            data = r.json()
            logging.info("[create_payment] Response received: %s", data)
            return PaymentResponse(
                status=data.get("status", "error"),
                token=data.get("token"),
                reason=data.get("reason")
            )
        except Exception as e:
            logging.info("[create_payment] Exception occurred: %s", str(e))
            return PaymentResponse(status="error", reason=str(e))

    def verify_callback(self, callback: CallbackData) -> bool:
        logging.info("[verify_callback] Verifying callback for merchant_oid=%s", callback.merchant_oid)
        check_str = f"{callback.merchant_oid}{self.config.merchant_salt}{callback.status}{callback.total_amount}"
        logging.info("[verify_callback] Check string prepared: %s", check_str)

        hashed = hmac.new(
            self.config.merchant_key.encode(),
            check_str.encode(),
            hashlib.sha256
        ).digest()
        expected_hash = base64.b64encode(hashed).decode()

        logging.info("[verify_callback] Expected hash: %s", expected_hash)
        result = expected_hash == callback.hash
        if not result:
            logging.warning("[verify_callback] Hash mismatch! expected=%s got=%s", expected_hash, callback.hash)
        else:
            logging.info("[verify_callback] Hash match verified successfully")
        return result


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


paytr_service = PaytrService(get_config())
