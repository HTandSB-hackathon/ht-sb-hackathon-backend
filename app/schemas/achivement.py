from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AchivementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="実績名")
    description: str = Field(..., description="実績の説明")
    icon_image_url: str = Field(..., description="アイコン画像のURL")

class AchivementCreate(AchivementBase):
    pass

class AchivementUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="実績名")
    description: Optional[str] = Field(None, description="実績の説明")
    icon_image_url: Optional[str] = Field(None, description="アイコン画像のURL")

class AchivementResponse(AchivementBase):
    id: int = Field(..., description="実績ID")
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True


class UserAchivementBase(BaseModel):
    user_id: int = Field(..., description="ユーザーID")
    achivement_id: int = Field(..., description="実績ID")
    is_unlocked: bool = Field(default=False, description="取得状況")

class UserAchivementCreate(UserAchivementBase):
    pass

class UserAchivementUpdate(BaseModel):
    is_unlocked: Optional[bool] = Field(None, description="取得状況")

class UserAchivementResponse(UserAchivementBase):
    id: int = Field(..., description="ユーザー実績ID")
    achivement: Optional[AchivementResponse] = Field(None, description="実績詳細") # 結合表示用
    created_date: datetime = Field(..., description="作成日時")
    updated_date: Optional[datetime] = Field(None, description="更新日時")

    class Config:
        from_attributes = True

class UserAchivementUnlockRequest(BaseModel):
    achivement_id: int = Field(..., description="アンロック試行対象の実績ID")
