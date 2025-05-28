from typing import Optional

from pydantic import BaseModel


class TasukiAuthCheckOutput(BaseModel):
    """TASUKI認証チェックのレスポンススキーマ"""
    status_code: int
    message: Optional[str] = None