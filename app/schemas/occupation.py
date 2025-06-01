from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OccupationBase(BaseModel):
    """職業の基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=50, description="職業名")

class OccupationCreate(OccupationBase):
    """職業作成用スキーマ"""
    pass

class OccupationUpdate(BaseModel):
    """職業更新用スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="職業名")

class OccupationResponse(OccupationBase):
    """職業レスポンス用スキーマ"""
    id: int = Field(..., description="職業ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class OccupationListResponse(BaseModel):
    """職業一覧レスポンス用スキーマ"""
    occupations: list[OccupationResponse] = Field(..., description="職業一覧")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    limit: int = Field(..., description="1ページあたりの件数")

class OccupationSearchParams(BaseModel):
    """職業検索パラメータ"""
    name: Optional[str] = Field(None, description="職業名での部分一致検索")

class OccupationBulkCreate(BaseModel):
    """職業一括作成用スキーマ"""
    occupations: list[OccupationCreate] = Field(..., description="作成する職業一覧")

    @Field.validator('occupations')
    def validate_occupations_limit(cls, v):
        if len(v) > 50:
            raise ValueError('一度に作成できる職業は50件までです')
        return v

class OccupationStatistics(BaseModel):
    """職業統計情報"""
    total_occupations: int = Field(..., description="総職業数")
    character_count_by_occupation: dict[str, int] = Field(..., description="職業別キャラクター数")