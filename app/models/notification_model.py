from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

class NotificationRequest(BaseModel):
    type: Literal["single", "bulk"] = Field(..., description="single | bulk")
    subject: str
    message: str  # HTML destekli

    # single için:
    target: Optional[str] = Field(None, description="Tek alıcı email (single)")

    # bulk için:
    user_type: Optional[Literal["courier", "restaurant", "all"]] = Field(
        None, description="Toplu hedef (bulk)"
    )

    @field_validator("target")
    @classmethod
    def _require_target_for_single(cls, v, info):
        data = info.data
        if data.get("type") == "single" and not v:
            raise ValueError("type=single iken target zorunludur (email).")
        return v

    @field_validator("user_type")
    @classmethod
    def _require_user_type_for_bulk(cls, v, info):
        data = info.data
        if data.get("type") == "bulk" and not v:
            raise ValueError("type=bulk iken user_type zorunludur (courier|restaurant|all).")
        return v
