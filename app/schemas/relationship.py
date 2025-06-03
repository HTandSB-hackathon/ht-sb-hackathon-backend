from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class TrustLevelBase(BaseModel):
    """信頼レベルの基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=50, description="信頼レベル名")

class TrustLevelCreate(TrustLevelBase):
    """信頼レベル作成用スキーマ"""
    pass

class TrustLevelUpdate(BaseModel):
    """信頼レベル更新用スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="信頼レベル名")

class TrustLevelResponse(TrustLevelBase):
    """信頼レベルレスポンス用スキーマ"""
    id: int = Field(..., description="信頼レベルID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class TrustLevelListResponse(BaseModel):
    """信頼レベル一覧レスポンス用スキーマ"""
    trust_levels: list[TrustLevelResponse] = Field(..., description="信頼レベル一覧")
    total: int = Field(..., description="総件数")

class RelationshipBase(BaseModel):
    """信頼関係の基本スキーマ"""
    user_id: int = Field(..., description="ユーザーID")
    character_id: int = Field(..., description="キャラクターID")
    trust_level_id: int = Field(..., description="信頼レベルID")
    total_points: int = Field(default=0, ge=0, description="総ポイント数")
    conversation_count: int = Field(default=0, ge=0, description="会話回数")
    first_met_at: Optional[datetime] = Field(None, description="初回出会い日時")
    is_favorite: bool = Field(default=False, description="お気に入りフラグ")

    @validator('total_points')
    def validate_total_points(cls, v):
        if v < 0:
            raise ValueError('総ポイント数は0以上である必要があります')
        return v

    @validator('conversation_count')
    def validate_conversation_count(cls, v):
        if v < 0:
            raise ValueError('会話回数は0以上である必要があります')
        return v

class RelationshipCreate(RelationshipBase):
    """信頼関係作成用スキーマ"""
    pass

class RelationshipUpdate(BaseModel):
    """信頼関係更新用スキーマ"""
    trust_level_id: Optional[int] = Field(None, description="信頼レベルID")
    total_points: Optional[int] = Field(None, ge=0, description="総ポイント数")
    conversation_count: Optional[int] = Field(None, ge=0, description="会話回数")
    first_met_at: Optional[datetime] = Field(None, description="初回出会い日時")
    is_favorite: Optional[bool] = Field(None, description="お気に入りフラグ")

    @validator('total_points')
    def validate_total_points(cls, v):
        if v is not None and v < 0:
            raise ValueError('総ポイント数は0以上である必要があります')
        return v

    @validator('conversation_count')
    def validate_conversation_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('会話回数は0以上である必要があります')
        return v

class RelationshipResponse(RelationshipBase):
    """信頼関係レスポンス用スキーマ"""
    id: int = Field(..., description="信頼関係ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class RelationshipListResponse(BaseModel):
    """信頼関係一覧レスポンス用スキーマ"""
    relationships: list[RelationshipResponse] = Field(..., description="信頼関係一覧")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    limit: int = Field(..., description="1ページあたりの件数")


class RelationshipSearchParams(BaseModel):
    """信頼関係検索パラメータ"""
    user_id: Optional[int] = Field(None, description="ユーザーID")
    character_id: Optional[int] = Field(None, description="キャラクターID")
    trust_level_id: Optional[int] = Field(None, description="信頼レベルID")
    min_points: Optional[int] = Field(None, ge=0, description="最小ポイント数")
    max_points: Optional[int] = Field(None, ge=0, description="最大ポイント数")
    min_conversations: Optional[int] = Field(None, ge=0, description="最小会話回数")
    max_conversations: Optional[int] = Field(None, ge=0, description="最大会話回数")

    @validator('max_points')
    def validate_points_range(cls, v, values):
        if v is not None and 'min_points' in values and values['min_points'] is not None:
            if v < values['min_points']:
                raise ValueError('最大ポイント数は最小ポイント数以上である必要があります')
        return v

    @validator('max_conversations')
    def validate_conversations_range(cls, v, values):
        if v is not None and 'min_conversations' in values and values['min_conversations'] is not None:
            if v < values['min_conversations']:
                raise ValueError('最大会話回数は最小会話回数以上である必要があります')
        return v

class RelationshipStatistics(BaseModel):
    """信頼関係統計情報"""
    total_relationships: int = Field(..., description="総信頼関係数")
    average_points: float = Field(..., description="平均ポイント数")
    average_conversations: float = Field(..., description="平均会話回数")
    relationships_by_trust_level: dict[str, int] = Field(..., description="信頼レベル別関係数")

class RelationshipPointsUpdate(BaseModel):
    """ポイント更新用スキーマ"""
    points_to_add: int = Field(..., description="追加するポイント数")
    increment_conversation: bool = Field(default=True, description="会話回数をインクリメントするか")

    @validator('points_to_add')
    def validate_points_to_add(cls, v):
        if v < 0:
            raise ValueError('追加ポイント数は0以上である必要があります')
        return v


class LevelThresholdBase(BaseModel):
    """レベル閾値の基本スキーマ"""
    character_id: int = Field(..., description="キャラクターID")
    trust_level_id: int = Field(..., description="信頼レベルID")
    required_points: Optional[int] = Field(default=0, ge=0, description="必要ポイント数")
    required_conversations: Optional[int] = Field(default=0, ge=0, description="必要会話回数")
    required_days_from_first: Optional[int] = Field(default=0, ge=0, description="初回出会いからの必要日数")

class LevelThresholdResponse(LevelThresholdBase):
    """レベル閾値レスポンス用スキーマ"""
    id: int = Field(..., description="レベル閾値ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True
