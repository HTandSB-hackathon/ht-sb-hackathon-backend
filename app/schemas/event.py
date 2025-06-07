from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    """イベントの基本スキーマ"""
    user_id: str = Field(..., description="ユーザーID")
    character_id: str = Field(..., description="キャラクターID")
    event_type: str = Field(..., description="イベントタイプ")
    title: str = Field(..., description="イベントのタイトル")
    details: Optional[str] = Field(None, description="イベントの詳細")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="イベントの発生日時")


class EventResponse(Event):
    """イベントのレスポンススキーマ"""
    id: str = Field(..., description="イベントのID")

    class Config:
        orm_mode = True