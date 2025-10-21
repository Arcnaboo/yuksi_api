# app/services/paytr_service.py
import base64
import hashlib
import hmac
import logging
import os
import re
from typing import Optional

import requests

from app.models.paytr_models import PaytrConfig, PaymentRequest, PaymentResponse, CallbackData

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOKEN_URL = "https://www.paytr.com/odeme"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ensure_str(val: Optional[str], default: str) -> str:
    """Return stripped value or default when None/empty."""
    return (val and str(val).strip()) or default


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------
class PaytrService:
    def __init__(self, config: PaytrConfig):
        self.config = config
        logger.info("[PaytrService] init merchant_id=%s", config.merchant_id)

    # -----------------------------------------------------------------------
    # Create hash (Direct API – 2025 spec)
    # -----------------------------------------------------------------------
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
        hashed = hmac.new(
            self.config.merchant_key.encode("utf-8"),
            hash_str.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return base64.b64encode(hashed).decode("utf-8")

    # -----------------------------------------------------------------------
    # Create payment
    # -----------------------------------------------------------------------
    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        logger.info("[create_payment] oid=%s amount=%s", req.merchant_oid, req.payment_amount)

        token_hash = self._create_hash(req)

        # Build payload – ensure NOTHING is empty
        payload = {
            "merchant_id": self.config.merchant_id,
            "user_ip": req.user_ip,
            "merchant_oid": req.merchant_oid,
            "email": req.email.strip(),
            "payment_amount": int(req.payment_amount),
            "currency": req.currency.upper(),
            "payment_type": getattr(req, "payment_type", "card"),
            "installment_count": int(getattr(req, "installment_count", 0)),
            "test_mode": int(req.test_mode),
            "non_3d": int(req.non_3d),
            "merchant_ok_url": self.config.ok_url,
            "merchant_fail_url": self.config.fail_url,
            "user_basket": req.basket_json,
            "paytr_token": token_hash,
            "no_installment": int(getattr(req, "no_installment", 0)),
            "max_installment": int(getattr(req, "max_installment", 12)),
            # Mandatory user fields – NEVER empty
            "user_name": _ensure_str(getattr(req, "user_name", None), "Test Kullanıcı"),
            "user_address": _ensure_str(getattr(req, "user_address", None), "Ankara, Türkiye"),
            "user_phone": _ensure_str(getattr(req, "user_phone", None), "+905551112233"),
            "expiry_month":int(req.expiry_month),
            "expiry_year": int(req.expiry_year),
            "cc_owner": req.cc_owner,
            "card_number": req.card_number,
            "cvv":req.cvv
        }

        # -------------------------------------------------------------------
        # If you want NON-3D (non_3d=1) you MUST supply card_* parameters.
        # Remove this block if you only use 3-DS.
        # -------------------------------------------------------------------
        
        # -------------------------------------------------------------------

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html",
        }

        try:
            rsp = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
            logger.info("[create_payment] HTTP %s", rsp.status_code)
        except Exception as exc:
            logger.exception("[create_payment] network error: %s", exc)
            return PaymentResponse(status="error", reason=str(exc))

        # PayTR returns HTML for both success and failure
        html = rsp.text

        if rsp.status_code == 200 and "İşlem başarısız" not in html:
            return PaymentResponse(status="success", token=None, reason=None)

        # Try to extract fail_message
        reason = None
        m = re.search(r'name="fail_message"\s+value="([^"]*)"', html)
        if m:
            reason = m.group(1)
        else:
            body_start = html.find("<body>")
            if body_start != -1:
                reason = html[body_start : body_start + 400]

        return PaymentResponse(status="error", reason=reason or "Integration failed")

    # -----------------------------------------------------------------------
    # Callback signature verification
    # -----------------------------------------------------------------------
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
            hashlib.sha256,
        ).digest()
        expected = base64.b64encode(hashed).decode()
        ok = hmac.compare_digest(expected, callback.hash)
        if not ok:
            logger.warning(
                "[verify_callback] hash mismatch expected=%s got=%s", expected, callback.hash
            )
        return ok


# ---------------------------------------------------------------------------
# Config factory
# ---------------------------------------------------------------------------
def get_config() -> PaytrConfig:
    return PaytrConfig(
        merchant_id=os.getenv("PAYTR_MERCHANT_ID"),
        merchant_key=os.getenv("PAYTR_MERCHANT_KEY"),
        merchant_salt=os.getenv("PAYTR_MERCHANT_SALT"),
        ok_url=os.getenv("PAYTR_OK_URL"),
        fail_url=os.getenv("PAYTR_FAIL_URL"),
        callback_url=os.getenv("PAYTR_CALLBACK_URL"),
        test_mode=int(os.getenv("PAYTR_TEST_MODE", "1")),
    )


# Singleton instance
paytr_service = PaytrService(get_config())