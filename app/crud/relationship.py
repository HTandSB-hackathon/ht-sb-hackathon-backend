
from sqlalchemy.orm import Session

from app.models.relationship import LevelThreshold, Relationship
from app.schemas.relationship import LevelThresholdResponse, RelationshipResponse, RelationshipUpdate


def get_relationships_by_user_id(db: Session, user_id: int) -> list[RelationshipResponse]:
    """
    指定したユーザーIDに紐づく信頼関係を取得
    """
    relationships = db.query(Relationship).filter(
        Relationship.user_id == user_id
    ).all()

    if not relationships:
        return []
    
    return [RelationshipResponse.from_orm(rel) for rel in relationships]

def get_relationships_by_user_id_and_character_id(db: Session, user_id: int, character_id: int) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係を取得
    """
    relationships = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()
    
    if not relationships:
        return None
    return RelationshipResponse.from_orm(relationships)

def get_level_thresholds_by_character_id_and_trust_level_id(db: Session, character_id: int, trust_level_id: int) -> LevelThresholdResponse:
    """
    指定したキャラクターIDと信頼度IDに紐づくレベル閾値を取得
    """

    level_threshold = db.query(LevelThreshold).filter(
        LevelThreshold.character_id == character_id,
        LevelThreshold.trust_level_id == 1
    ).first()

    if not level_threshold:
        return LevelThresholdResponse()
    return LevelThresholdResponse.from_orm(level_threshold)

def insert_relationship(
    db: Session,
    user_id: int,
    character_id: int,
) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係を新規作成
    信頼レベルはデフォルトで1、total_pointsは0、会話数は0、初対面日時は現在日時、is_favoriteはFalseとする
    """
    
    # 対象のキャラクターのlevel_thresholdsを取得
    level_threshold = db.query(LevelThreshold).filter(
        LevelThreshold.character_id == character_id,
        LevelThreshold.trust_level_id == 1  # デフォルトの信頼レベル
    ).first()

    next_level_points = level_threshold.required_points if level_threshold else 100  # デフォルト値は100

    db_relationship = Relationship(
        user_id=user_id,
        character_id=character_id,
        trust_level_id=1,  # デフォルトの信頼レベル
        total_points=0,    # 初期ポイントは0
        conversation_count=0,  # 初期会話数は0
        next_level_points=next_level_points,  # 次のレベルに必要なポイント
        first_met_at=None,  # 初対面日時はNone（後で設定可能）
        is_favorite=False   # 初期状態ではお気に入りではない
    )

    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return RelationshipResponse.from_orm(db_relationship)

def update_relationship_trust_level(db: Session, user_id: int, character_id: int, new_trust_level_id: int, next_level_points: int) -> RelationshipResponse:
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
    db_relationship.next_level_points = next_level_points
    db.commit()
    db.refresh(db_relationship)
    return RelationshipResponse.from_orm(db_relationship)

def update_relationship_total_point(db: Session, user_id: int, character_id: int, points_to_add: int) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係のtotal_pointsにポイントを加算する
    加算するポイントを引数とする（points_to_add）
    points_to_addは正の値であることを想定
    """
    db_relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()

    if not db_relationship:
        return RelationshipResponse()

    if db_relationship.total_points is None:
        db_relationship.total_points = 0

    db_relationship.total_points += points_to_add
    db.commit()
    db.refresh(db_relationship)
    return RelationshipResponse.from_orm(db_relationship)

def update_relationship(
    db: Session,
    user_id: int,
    character_id: int,
    update_data: RelationshipUpdate
) -> RelationshipResponse:
    """
    指定したユーザーIDとキャラクターIDに紐づく信頼関係を更新
    引数に対象のカラムがあれば更新する。Noneの場合は更新しない。
    """
    db_relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()

    if not db_relationship:
        return RelationshipResponse()
    # 更新可能なフィールドを更新
    # if update_data.trust_level_id is not None:
    #     db_relationship.trust_level_id = update_data.trust_level_id
    # if update_data.total_points is not None:
    #     db_relationship.total_points = update_data.total_points
    # if update_data.conversation_count is not None:
    #     db_relationship.conversation_count = update_data.conversation_count
    # if update_data.first_met_at is not None:
    #     db_relationship.first_met_at = update_data.first_met_at
    if update_data.is_favorite is not None:
        db_relationship.is_favorite = update_data.is_favorite
    # 更新日時を自動で更新
    db_relationship.updated_date = db_relationship.updated_date

    db.commit()
    db.refresh(db_relationship)
    return RelationshipResponse.from_orm(db_relationship)