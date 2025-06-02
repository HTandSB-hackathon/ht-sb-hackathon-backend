
from sqlalchemy.orm import Session

from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipResponse


def get_relationships_by_user_id_and_character_id(db: Session, user_id: int, character_id: int) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係を取得
    """
    relationships = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()
    
    if not relationships:
        return RelationshipResponse()
    return RelationshipResponse.from_orm(relationships)