import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import character as crud
from app.crud import relationship as relationship_crud
from app.crud.event import save_event
from app.crud.redis import RedisCacheService
from app.models.relationship import LevelThreshold as LevelThresholdModel
from app.models.relationship import Relationship as RelationshipModel
from app.schemas.character import CharacterLockedResponse, CharacterResponse, StoryLockedResponse, StoryUnlockedResponse
from app.schemas.relationship import RelationshipResponse, RelationshipUpdate

router = APIRouter()

def get_redis_service() -> RedisCacheService:
    """Redisキャッシュサービスを取得"""
    try:
        return RedisCacheService()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Redis cache service. Please check configuration."
        )

# ユーザーに紐づいたキャラクター情報を取得するエンドポイント
@router.get("", response_model=List[CharacterResponse])
def read_all_characters(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
) -> List[CharacterResponse]:
    """
    unlocked済みのキャラクター情報を取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    characters = crud.get_characters_by_user_id(db, user_id=current_user_id)
    return characters

# ロック済みのキャラクター情報を取得するエンドポイント
@router.get("/locked", response_model=List[CharacterLockedResponse])
def read_locked_characters(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
) -> List[CharacterLockedResponse]:
    """
    ロック中のキャラクター情報を取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    characters = crud.get_characters_without_user(db, user_id=current_user_id)
    return characters

@router.get("/all", response_model=List[RelationshipResponse])
def read_all_relationships(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
) -> List[RelationshipResponse]:
    """
    指定したキャラクターの全てのリレーションシップ情報を取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    relationships = relationship_crud.get_relationships_by_user_id(
        db, user_id=current_user_id
    )
    return relationships

@router.post("/{character_id}/insert", response_model=RelationshipResponse)
def create_relationship(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> RelationshipResponse:
    """
    指定したキャラクターのリレーションシップ情報を新規作成するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return None

    # 既にリレーションシップが存在する場合は何もしない
    existing_relationship = relationship_crud.get_relationships_by_user_id_and_character_id(
        db, user_id=current_user_id, character_id=character_id
    )
    if existing_relationship:
        return existing_relationship
    
    ## ここで実際はunlockedできるかどうかのチェックを行う
    check = relationship_crud.unlock_character(
        db, user_id=current_user_id, character_id=character_id
    )

    if not check:
        return RelationshipResponse(id=None)

    new_relationship = relationship_crud.insert_relationship(
        db, user_id=current_user_id, character_id=character_id
    )
    return new_relationship

@router.get("/{character_id}", response_model=RelationshipResponse)
def read_relationship(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> RelationshipResponse:
    """
    指定したキャラクターの詳細情報を取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return RelationshipResponse()
    relationship = relationship_crud.get_relationships_by_user_id_and_character_id(
        db, user_id=current_user_id, character_id=character_id
    )
    if not relationship:
        return RelationshipResponse()
    return relationship

@router.put("/{character_id}/put", response_model=RelationshipResponse)
def update_relationship(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user),
    inputs: RelationshipUpdate
) -> RelationshipResponse:
    """
    指定したキャラクターのリレーションシップ情報を更新するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return RelationshipResponse()

    updated_relationship = relationship_crud.update_relationship(
        db, user_id=current_user_id, character_id=character_id, update_data=inputs
    )
    if not updated_relationship:
        return RelationshipResponse()
    return updated_relationship
    

# キャラクターのストーリーを取得するエンドポイント
@router.get("/{character_id}/stories/unlocked", response_model=List[StoryUnlockedResponse])
def read_character_stories(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> List[StoryUnlockedResponse]:
    """
    指定したキャラクターのアンロック済みストーリーを取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    stories = crud.get_unlocked_stories(db, character_id=character_id, user_id=current_user_id)
    return stories

@router.get("/{character_id}/stories/locked", response_model=List[StoryLockedResponse])
def read_character_locked_stories(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> List[StoryLockedResponse]:
    """
    指定したキャラクターのアンロック済みストーリーを取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    stories = crud.get_locked_stories(db, character_id=character_id, user_id=current_user_id)
    return stories

@router.put("/{character_id}/check_trust_level", response_model=RelationshipResponse)
async def check_trust_level(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user),
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db)
) -> RelationshipResponse:
    """
    キャラクターの信頼レベルをチェックし閾値を超えている場合は更新するエンドポイント
    現在の実績値で到達可能な最も高い信頼レベルに更新し、更新後のリレーションシップ情報を返す
    """
    current_user_id = current_user.id

    db_relationship: Optional[RelationshipModel] = db.query(RelationshipModel).filter(
        RelationshipModel.user_id == current_user_id,
        RelationshipModel.character_id == character_id
    ).first()

    if not db_relationship:
        return RelationshipResponse()

    current_trust_level_id = db_relationship.trust_level_id
    total_points = db_relationship.total_points
    # conversation_count = await get_chat_count(mongodb, user_id=current_user.id, character_id=character_id)
    # first_met_at = db_relationship.first_met_at

    # キャラクターの全てのレベル閾値を信頼度IDの降順で取得
    all_thresholds = db.query(LevelThresholdModel).filter(
        LevelThresholdModel.character_id == character_id
    ).order_by(LevelThresholdModel.trust_level_id.asc()).all()

    target_trust_level_id = current_trust_level_id # 更新がない場合のデフォルト
    target_next_level_points = db_relationship.next_level_points # 更新がない場合のデフォルト

    conditions_met = False
    for threshold in all_thresholds:
        # この閾値レベルが現在のレベル以下なら、それ以上高いレベルにはなれないのでチェック終了

        if conditions_met:
            # 条件を満たす最も高いレベルが見つかった場合ループを抜ける
            print(f"条件を満たすレベルが見つかりました: {threshold.trust_level_id}, 必要ポイント: {threshold.required_points}")
            target_trust_level_id = threshold.trust_level_id
            target_next_level_points = threshold.required_points
            break

        print(total_points, threshold.required_points, total_points < threshold.required_points)
        if threshold.required_points is not None and total_points >= threshold.required_points:
            conditions_met = True
            
        # if threshold.required_conversations is not None and conversation_count < threshold.required_conversations:
        #     conditions_met = False
        
        # if threshold.required_days_from_first is not None:
        #     if first_met_at is not None:
        #         first_met_at_aware = first_met_at.replace(tzinfo=timezone.utc) if first_met_at.tzinfo is None else first_met_at
        #         days_passed = (datetime.now(timezone.utc) - first_met_at_aware).days
        #         if days_passed < threshold.required_days_from_first:
        #             conditions_met = False
        #     else:
        #         conditions_met = False
        
    print(f"Current Trust Level ID: {current_trust_level_id}, Target Trust Level ID: {target_trust_level_id}, Total Points: {total_points}, Next Level Points: {target_next_level_points}")
    if target_trust_level_id > current_trust_level_id:
        updated_relationship_response = await relationship_crud.update_relationship_trust_level(
            # level_thresholdsにはtrust_levelからレベルアップするための条件が含まれているため更新する値は+1を指定
            db, user_id=current_user_id, character_id=character_id, new_trust_level_id=target_trust_level_id, next_level_points=target_next_level_points
        )

        try: 

            character = crud.get_character_by_id(db, character_id=character_id)
            await save_event(
                mongodb,
                user_id=current_user_id,
                character_id=character_id,
                title="信頼度レベルアップ！",
                event_type="level_up",
                detail=f"{character.name}との関係が深まりました。")
        except Exception as e:
            print(f"イベントの保存に失敗しました: {e}")


        if not updated_relationship_response or not hasattr(updated_relationship_response, 'id'):
            return RelationshipResponse.from_orm(db_relationship) # 更新失敗時は元データを返す
        return updated_relationship_response
    else:
        # 更新がない場合は現在のリレーションシップ情報を返す
        return RelationshipResponse.from_orm(db_relationship)

@router.put("/{character_id}/stories/unlock", response_model=StoryUnlockedResponse)
async def unlock_character_story(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> StoryUnlockedResponse:
    """
    指定したキャラクターのストーリーをアンロックするエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return StoryUnlockedResponse()

    # ストーリーをアンロックするためのロジックを実装
    story = await crud.unlock_character_story(db, character_id=character_id, user_id=current_user_id)
    
    if not story:
        return StoryUnlockedResponse()

    return story

@router.put("/{character_id}/levelup/limit")
async def level_up_limit(
    *,
    cache_service: RedisCacheService = Depends(get_redis_service),
    current_user=Depends(deps.get_current_user)
):
    """
    キャラクターのレベルアップ制限を確認するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return {"message": "User not authenticated"}

    # キャッシュからレベルアップ制限を取得
    cache_key = f"levelup_limit:{current_user_id}"
    limit_data = await cache_service.get_cached_data(cache_key)  # 2時間の有効期限

    # limit_dataはbytes型で返されるため、JSONデコードを行う
    if limit_data:
        try:
            limit_data = int(limit_data.decode('utf-8'))
        except json.JSONDecodeError:
            return {"message": "Invalid cache data format"}