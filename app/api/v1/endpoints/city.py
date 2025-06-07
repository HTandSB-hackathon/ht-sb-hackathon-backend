from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import city as crud
from app.schemas import city as schemas

router = APIRouter()

# 特定の都道府県の都市情報を取得するエンドポイント
@router.get("/prefectures/{prefecture_id}", response_model=List[schemas.MunicipalityResponse])
def read_cities_by_prefecture(
    *,
    db: Session = Depends(deps.get_db),
    prefecture_id: int, 
    current_user=Depends(deps.get_current_user)
) ->  List[schemas.MunicipalityResponse]:
    """
    特定の都道府県の都市情報を取得
    """
    cities = crud.get_cities_by_prefecture(db, prefecture_id=prefecture_id)
    return cities

# 特定の都道府県の都市情報を取得し、リレーションシップテーブルに含まれている都市のみを返すエンドポイント
@router.get("/prefectures/{prefecture_id}/relationships", response_model=List[schemas.MunicipalityResponse])
def read_cities_by_prefecture_with_relationship(
    *,
    db: Session = Depends(deps.get_db),
    prefecture_id: int,
    current_user=Depends(deps.get_current_user)
) -> List[schemas.MunicipalityResponse]:
    """
    特定の都道府県の都市情報を取得し、リレーションシップテーブルに含まれている都市のみを返す
    """
    user_id = current_user.id if current_user else None
    if user_id is None:
        return []
    
    cities = crud.get_cities_by_prefecture_with_relationship(db, prefecture_id=prefecture_id, user_id=user_id)
    return cities

# 特定の都道府県の市区町村の魅力を取得するエンドポイント
@router.get("/prefectures/{prefecture_id}/fascination", response_model=List[schemas.MunicipalityFascinatingResponse])
async def read_municipality_fascination(
    *,
    mongodb: Session = Depends(deps.get_mongo_db),
    prefecture_id: int
) -> List[schemas.MunicipalityFascinatingResponse]:
    """
    特定の都道府県の市区町村の魅力を取得
    """
    municipalities = await crud.get_municipality_fascination(mongo_db=mongodb, prefecture_id=prefecture_id)
    return municipalities