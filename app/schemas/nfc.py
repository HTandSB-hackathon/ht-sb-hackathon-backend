
from pydantic import BaseModel, Field


class NfcRequest(BaseModel):
    """NFCリクエストのスキーマ"""
    nfc_uuid: str = Field(..., description="NFC UUID")