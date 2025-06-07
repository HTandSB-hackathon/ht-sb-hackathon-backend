from typing import List

from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.city import Municipality
from app.models.relationship import Relationship
from app.schemas.city import MunicipalityFascinatingResponse, MunicipalityResponse


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

async def get_municipality_fascination(
    mongo_db: Session,
    prefecture_id: int,
) -> List[MunicipalityFascinatingResponse]:
    """
    特定の都道府県の市区町村の魅力を取得
    """
    try:
        collection = mongo_db["municipality_fascination"]
        municipalities = await collection.find({"prefecture_id": prefecture_id}).to_list(length=None)

        if not municipalities:
            return []
        
        result = []
        for municipality in municipalities:
            # MongoDBのドキュメントをPydanticモデルに変換
            result.append(MunicipalityFascinatingResponse(
                id=str(municipality["_id"]),  # Convert ObjectId to string
                prefecture_id=int(municipality["prefecture_id"]),
                municipality_id=int(municipality["municipality_id"]),
                content=municipality["content"],
                color=municipality["color"],
                emoji=municipality["emoji"],
                gradient=municipality.get("gradient"),
                details=municipality.get("details", []),  # Can be list or dict
                created_date=municipality["created_date"],
                updated_date=municipality.get("updated_date")
            ))
        
        return result
    except Exception as e:
        print(f"市区町村の魅力の取得に失敗しました: {e}")
        raise Exception(f"市区町村の魅力の取得に失敗しました: {str(e)}")