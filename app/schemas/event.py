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

class FukushimaWeek(BaseModel):
    """市町村ウィーク"""
    date: str = Field(..., description="日付")
    title: str = Field(..., description="タイトル")
    municipality: str = Field(..., description="市町村名")
    url: str = Field(..., description="関連URL")

class FukushimaWeekResponse(FukushimaWeek):
    """市町村ウィークのレスポンススキーマ"""
    id: str = Field(..., description="ウィークのID")

    class Config:
        orm_mode = True