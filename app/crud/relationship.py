
from sqlalchemy.orm import Session

from app.models.relationship import LevelThreshold, Relationship
from app.schemas.relationship import LevelThresholdResponse, RelationshipResponse


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


def get_level_thresholds_by_character_id_and_trust_level_id(db: Session, character_id: int, trust_level_id: int) -> LevelThresholdResponse:
    """
    指定したキャラクターIDと信頼度IDに紐づくレベル閾値を取得
    """

    level_threshold = db.query(LevelThreshold).filter(
        LevelThreshold.character_id == character_id,
        LevelThreshold.trust_level_id == trust_level_id
    ).first()

    if not level_threshold:
        return LevelThresholdResponse()
    return LevelThresholdResponse.from_orm(level_threshold)


def update_relationship_trust_level(db: Session, user_id: int, character_id: int, new_trust_level_id: int) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係の信頼レベルを更新
    """

    db_relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()

    if not db_relationship:
        return RelationshipResponse()
    
    # 信頼レベルを更新
    db_relationship.trust_level_id = new_trust_level_id
    db.commit()
    db.refresh(db_relationship)
    return RelationshipResponse.from_orm(db_relationship)