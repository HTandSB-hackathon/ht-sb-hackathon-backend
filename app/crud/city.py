from typing import List

from sqlalchemy.orm import Session

from app.models.city import Municipality
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