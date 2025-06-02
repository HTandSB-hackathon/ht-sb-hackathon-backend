from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class CharacterBase(BaseModel):
    """キャラクターの基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=50, description="キャラクター名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年齢")
    occupation_id: Optional[int] = Field(None, description="職業ID")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="プロフィール画像URL")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="カバー画像URL")
    gender: int = Field(..., ge=0, le=2, description="性別 (0: 男性, 1: 女性, 2: その他)")
    personality: List[str] = Field(default_factory=list, description="性格特性のリスト")
    hobbies: List[str] = Field(default_factory=list, description="趣味のリスト")
    specialties: List[str] = Field(default_factory=list, description="特技のリスト")
    is_active: bool = Field(True, description="アクティブフラグ")
    introduction: Optional[str] = Field(None, description="自己紹介文")
    unlock_condition: Optional[str] = Field("このキャラクターは現在取得できません", description="キャラクターのアンロック条件")
    prefecture_id: Optional[int] = Field(None, description="都道府県ID")
    municipality_id: Optional[int] = Field(None, description="市区町村ID")
    tasuki_project_id: Optional[int] = Field(None, description="TASUKIプロジェクトID")

    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('プロフィール画像URLは有効なHTTP/HTTPSのURLである必要があります')
        return v

class CharacterCreate(CharacterBase):
    """キャラクター作成用スキーマ"""
    pass

class CharacterUpdate(BaseModel):
    """キャラクター更新用スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="キャラクター名")
    age: Optional[int] = Field(None, ge=0, le=150, description="年齢")
    occupation_id: Optional[int] = Field(None, description="職業ID")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="プロフィール画像URL")
    is_active: Optional[bool] = Field(None, description="アクティブフラグ")
    introduction: Optional[str] = Field(None, description="自己紹介文")
    prefecture_id: Optional[int] = Field(None, description="都道府県ID")
    municipality_id: Optional[int] = Field(None, description="市区町村ID")
    tasuki_project_id: Optional[int] = Field(None, description="TASUKIプロジェクトID")

    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('プロフィール画像URLは有効なHTTP/HTTPSのURLである必要があります')
        return v

class CharacterResponse(CharacterBase):
    """キャラクター レスポンス用スキーマ"""
    id: int = Field(..., description="キャラクターID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")
    is_locked: bool = False

    class Config:
        from_attributes = True

class CharacterLockedResponse(CharacterBase):
    """キャラクター レスポンス用スキーマ"""
    id: int = Field(..., description="キャラクターID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")
    is_locked: bool = True

    class Config:
        from_attributes = True

class CharacterListResponse(BaseModel):
    """キャラクター一覧レスポンス用スキーマ"""
    characters: list[CharacterResponse] = Field(..., description="キャラクター一覧")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    limit: int = Field(..., description="1ページあたりの件数")

class CharacterSearchParams(BaseModel):
    """キャラクター検索パラメータ"""
    name: Optional[str] = Field(None, description="名前での部分一致検索")
    age_min: Optional[int] = Field(None, ge=0, description="年齢の最小値")
    age_max: Optional[int] = Field(None, le=150, description="年齢の最大値")
    occupation_id: Optional[int] = Field(None, description="職業ID")
    prefecture_id: Optional[int] = Field(None, description="都道府県ID")
    municipality_id: Optional[int] = Field(None, description="市区町村ID")
    is_active: Optional[bool] = Field(None, description="アクティブフラグ")
    tasuki_project_id: Optional[int] = Field(None, description="TASUKIプロジェクトID")

    @validator('age_max')
    def validate_age_range(cls, v, values):
        if v is not None and 'age_min' in values and values['age_min'] is not None:
            if v < values['age_min']:
                raise ValueError('年齢の最大値は最小値以上である必要があります')
        return v
    

class StoryBase(BaseModel):
    """ストーリーの基本スキーマ"""
    character_id: int = Field(..., description="キャラクターID")
    required_trust_level: int = Field(0, ge=0, description="必要な信頼レベル")
    title: str = Field(..., min_length=1, max_length=100, description="ストーリータイトル")
    content: str = Field(..., min_length=1, description="ストーリー内容")

class StoryCreate(StoryBase):
    """ストーリー作成用スキーマ"""
    pass

class StoryUpdate(BaseModel):
    """ストーリー更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="ストーリータイトル")
    content: Optional[str] = Field(None, min_length=1, description="ストーリー内容")
    required_trust_level: Optional[int] = Field(None, ge=0, description="必要な信頼レベル")

class StoryResponse(StoryBase):
    """ストーリー レスポンス用スキーマ"""
    id: int = Field(..., description="ストーリーID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True