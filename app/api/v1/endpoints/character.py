from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import character as crud
from app.crud import relationship as relationship_crud
from app.schemas.character import CharacterLockedResponse, CharacterResponse, StoryResponse
from app.schemas.relationship import RelationshipResponse

router = APIRouter()

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

# キャラクターのストーリーを取得するエンドポイント
@router.get("/{character_id}/stories", response_model=List[StoryResponse])
def read_character_stories(
    *,
    db: Session = Depends(deps.get_db),
    character_id: int,
    current_user=Depends(deps.get_current_user)
) -> List[StoryResponse]:
    """
    指定したキャラクターのストーリーを取得するエンドポイント
    """
    current_user_id = current_user.id if current_user else None
    if current_user_id is None:
        return []
    stories = crud.get_character_stories(db, character_id=character_id, user_id=current_user_id)
    return stories