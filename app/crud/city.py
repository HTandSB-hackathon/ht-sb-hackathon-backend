from typing import List

from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.city import Municipality
from app.models.relationship import Relationship
from app.schemas.city import MunicipalityResponse


# 都道府県のIDに基づいて都市情報を取得
def get_cities_by_prefecture(db: Session, prefecture_id: int) -> List[MunicipalityResponse]:
    """
    特定の都道府県の都市情報を取得
    """
    municipalities = db.query(Municipality).filter(Municipality.prefecture_id == prefecture_id).all()
    if not municipalities:
        return []
    return  [MunicipalityResponse.from_orm(municipality) for municipality in municipalities]

# 都道府県のIDに基づいて都市情報を取得しリレーションシップテーブルに含まれている都市のみを返す
def get_cities_by_prefecture_with_relationship(db: Session, prefecture_id: int, user_id: int) -> List[MunicipalityResponse]:
    """
    特定の都道府県の都市情報を取得し、リレーションシップテーブルに含まれている都市のみを返す
    """
    municipalities =  db.query(Municipality).filter(
        Municipality.prefecture_id == prefecture_id,
    ).join(
        Character, Character.municipality_id == Municipality.id
    ). join(
        Relationship, Relationship.character_id == Character.id
    ).filter(
        Relationship.user_id == user_id
    ).all()
    
    if not municipalities:
        return []
    
    return [MunicipalityResponse.from_orm(municipality) for municipality in municipalities]