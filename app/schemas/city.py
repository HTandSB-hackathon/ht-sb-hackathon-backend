from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class PrefectureBase(BaseModel):
    """都道府県の基本スキーマ"""
    name: str = Field(..., min_length=1, max_length=50, description="都道府県名")

class PrefectureCreate(PrefectureBase):
    """都道府県作成用スキーマ"""
    pass

class PrefectureUpdate(BaseModel):
    """都道府県更新用スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="都道府県名")

class PrefectureResponse(PrefectureBase):
    """都道府県レスポンス用スキーマ"""
    id: int = Field(..., description="都道府県ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class PrefectureListResponse(BaseModel):
    """都道府県一覧レスポンス用スキーマ"""
    prefectures: list[PrefectureResponse] = Field(..., description="都道府県一覧")
    total: int = Field(..., description="総件数")

class PrefectureWithCities(PrefectureResponse):
    """市区町村情報付き都道府県レスポンス"""
    municipalities: list["MunicipalityResponse"] = Field(default_factory=list, description="市区町村一覧")

class PrefectureSearchParams(BaseModel):
    """都道府県検索パラメータ"""
    name: Optional[str] = Field(None, description="名前での部分一致検索")


class MunicipalityBase(BaseModel):
    """市区町村の基本スキーマ"""
    prefecture_id: int = Field(..., description="都道府県ID")
    name: str = Field(..., min_length=1, max_length=50, description="市区町村名")
    kana: Optional[str] = Field(None, max_length=50, description="フリガナ")

class MunicipalityCreate(MunicipalityBase):
    """市区町村作成用スキーマ"""
    pass

class MunicipalityUpdate(BaseModel):
    """市区町村更新用スキーマ"""
    prefecture_id: Optional[int] = Field(None, description="都道府県ID")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="市区町村名")
    kana: Optional[str] = Field(None, max_length=50, description="フリガナ")

class MunicipalityResponse(MunicipalityBase):
    """市区町村レスポンス用スキーマ"""
    id: int = Field(..., description="市区町村ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class MunicipalityListResponse(BaseModel):
    """市区町村一覧レスポンス用スキーマ"""
    municipalities: list[MunicipalityResponse] = Field(..., description="市区町村一覧")
    total: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    limit: int = Field(..., description="1ページあたりの件数")

class MunicipalityWithDetails(MunicipalityResponse):
    """詳細情報付き市区町村レスポンス"""
    prefecture: Optional["PrefectureResponse"] = Field(None, description="都道府県情報")

class MunicipalitySearchParams(BaseModel):
    """市区町村検索パラメータ"""
    name: Optional[str] = Field(None, description="名前での部分一致検索")
    kana: Optional[str] = Field(None, description="フリガナでの部分一致検索")
    prefecture_id: Optional[int] = Field(None, description="都道府県ID")

class MunicipalityBulkCreate(BaseModel):
    """市区町村一括作成用スキーマ"""
    municipalities: list[MunicipalityCreate] = Field(..., description="作成する市区町村一覧")

    @validator('municipalities')
    def validate_municipalities_limit(cls, v):
        if len(v) > 100:
            raise ValueError('一度に作成できる市区町村は100件までです')
        return v

class MunicipalityStatistics(BaseModel):
    """市区町村統計情報"""
    total_municipalities: int = Field(..., description="総市区町村数")
    municipalities_by_prefecture: dict[str, int] = Field(..., description="都道府県別市区町村数")

# 前方参照の解決
def resolve_forward_refs():
    """前方参照を解決する関数"""
    
    MunicipalityWithDetails.model_rebuild()

# モジュール読み込み時に前方参照を解決
try:
    resolve_forward_refs()
except ImportError:
    # 他のスキーマモジュールがまだ作成されていない場合は無視
    pass