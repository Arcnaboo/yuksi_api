# app/services/paytr_service.py
import base64
import hmac
import hashlib
import requests
import logging
import os, re
from app.models.paytr_models import PaytrConfig, PaymentRequest, PaymentResponse, CallbackData


class PaytrService:
    # Direct API endpoint
    TOKEN_URL = "https://www.paytr.com/odeme"

    def __init__(self, config: PaytrConfig):
        self.config = config
        logging.info("[PaytrService] Initialized with merchant_id=%s", config.merchant_id)

    # -------------------------------------------------------------------------
    # HASH CREATION (Direct API – confirmed 2025 structure)
    # -------------------------------------------------------------------------
    def _create_hash(self, req: PaymentRequest) -> str:
        hash_str = (
            f"{self.config.merchant_id}"
            f"{req.user_ip}"
            f"{req.merchant_oid}"
            f"{req.email}"
            f"{req.payment_amount}"
            f"{getattr(req, 'payment_type', 'card')}"
            f"{getattr(req, 'installment_count', 0)}"
            f"{req.currency}"
            f"{req.test_mode}"
            f"{req.non_3d}"
            f"{self.config.merchant_salt}"
        )

        hashed_bytes = hmac.new(
            self.config.merchant_key.encode("utf-8"),
            hash_str.encode("utf-8"),
            hashlib.sha256
        ).digest()

        return base64.b64encode(hashed_bytes).decode("utf-8")

    # -------------------------------------------------------------------------
    # CREATE PAYMENT REQUEST
    # -------------------------------------------------------------------------
    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        logging.info("[create_payment] Starting payment creation for merchant_oid=%s", req.merchant_oid)
        token_hash = self._create_hash(req)

        payload = {
            "merchant_id": self.config.merchant_id,
            "user_ip": req.user_ip,
            "merchant_oid": req.merchant_oid,
            "email": req.email,
            "payment_amount": req.payment_amount,  # integer (kuruş)
            "currency": req.currency,
            "payment_type": getattr(req, "payment_type", "card"),
            "installment_count": getattr(req, "installment_count", 0),
            "test_mode": req.test_mode,
            "non_3d": req.non_3d,
            "merchant_ok_url": self.config.ok_url,
            "merchant_fail_url": self.config.fail_url,
            "user_basket": req.basket_json,
            "paytr_token": token_hash,
            "no_installment": getattr(req, "no_installment", 0),
            "max_installment": getattr(req, "max_installment", 12),
            "user_name": getattr(req, "user_name", "Test Kullanıcı"),
            "user_address": getattr(req, "user_address", "Ankara, Türkiye"),
            "user_phone": getattr(req, "user_phone", "+905551112233"),
            # For Direct API, card details are required:
            "cc_owner": getattr(req, "cc_owner", "Test Kullanıcı"),
            "card_number": getattr(req, "card_number", "4355084355084358"),
            "expiry_month": getattr(req, "expiry_month", "12"),
            "expiry_year": getattr(req, "expiry_year", "26"),
            "cvv": getattr(req, "cvv", "000"),
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html"
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload, headers=headers, timeout=10)
            logging.info("[create_payment] HTTP %s from PayTR", response.status_code)

            # PayTR Direct API returns HTML for success/failure — not JSON
            if response.status_code == 200 and "İşlem başarısız" not in response.text:
                return PaymentResponse(status="success", token=None, reason=None)
            
            

            # Extract fail reason if possible
            reason = None
            match = re.search(r'name="fail_message"\s+value="([^"]+)"', response.text)
            if match:
                reason = match.group(1)
            else:
                # fallback: capture the entire <body> if no match
                body_start = response.text.find("<body>")
                if body_start != -1:
                    reason = response.text[body_start:][:400]  # trim long HTML

            if response.status_code == 200 and "İşlem başarısız" not in response.text:
                return PaymentResponse(status="success", token=None, reason=None)
            return PaymentResponse(status="error", reason=reason or "Integration failed")

        except Exception as e:
            logging.exception("[create_payment] Exception occurred: %s", str(e))
            return PaymentResponse(status="error", reason=str(e))

    # -------------------------------------------------------------------------
    # VERIFY CALLBACK SIGNATURE
    # -------------------------------------------------------------------------
    def verify_callback(self, callback: CallbackData) -> bool:
        check_str = (
            f"{callback.merchant_oid}"
            f"{self.config.merchant_salt}"
            f"{callback.status}"
            f"{callback.total_amount}"
        )

        hashed = hmac.new(
            self.config.merchant_key.encode(),
            check_str.encode(),
            hashlib.sha256
        ).digest()
        expected_hash = base64.b64encode(hashed).decode()

        result = expected_hash == callback.hash
        if not result:
            logging.warning("[verify_callback] Hash mismatch! expected=%s got=%s", expected_hash, callback.hash)
        return result


# -------------------------------------------------------------------------
# CONFIG LOADER
# -------------------------------------------------------------------------
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
