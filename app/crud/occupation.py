from typing import List

from sqlalchemy.orm import Session

from app.models.occupation import Occupation
from app.schemas.occupation import OccupationResponse


def get_occupations(db: Session) -> List[OccupationResponse]:
    """
    全ての職業情報を取得
    """
    occupations = db.query(Occupation).all()
    return [OccupationResponse.from_orm(occupation) for occupation in occupations]

def get_occupation(db: Session, occupation_id: int) -> OccupationResponse | None:
    """
    特定の職業情報を取得
    """
    occupation = db.query(Occupation).filter(Occupation.id == occupation_id).first()
    if occupation:
        return OccupationResponse.from_orm(occupation)
    return None
