from typing import List

from sqlalchemy.orm import Session

from app.models.character import Character, Story
from app.models.nfc import CharacterNfcUuid
from app.models.relationship import Relationship
from app.schemas.character import CharacterLockedResponse, CharacterResponse, StoryLockedResponse, StoryUnlockedResponse


# 全キャラクター情報を取得
def get_all_characters(db: Session) -> List[CharacterResponse]:
    """
    全キャラクター情報を取得
    """
    characters = db.query(Character).all()
    if not characters:
        return []
    return [CharacterResponse.from_orm(character) for character in characters]

def get_character_by_id(db: Session, character_id: int) -> CharacterResponse:
    """
    指定したIDのキャラクター情報を取得
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        return None
    return CharacterResponse.from_orm(character)

# relationshipsのuser_idを指定してキャラクター情報を取得
def get_characters_by_user_id(db: Session, user_id: int) -> List[CharacterResponse]:
    """
    指定したuser_idに紐づくキャラクター情報を取得
    """
    characters = db.query(Character).join(Relationship).filter(
        Relationship.user_id == user_id
    ).all()
    if not characters:
        return []
    return [CharacterResponse.from_orm(character) for character in characters]

# relationshipsの特定のuser_idを含んでいないキャラクター情報を取得
def get_characters_without_user(db: Session, user_id: int) -> List[CharacterLockedResponse]:
    """
    特定のユーザーに紐づいていないキャラクター情報を取得
    """
    characters = db.query(Character).all()
    relationships = db.query(Relationship).filter(
        Relationship.user_id == user_id
    ).all()
    characters = [character for character in characters if character.id not in [rel.character_id for rel in relationships]]
    if not characters:
        return []
    return [CharacterLockedResponse.from_orm(character) for character in characters]

# ストーリーを取得
def get_unlocked_stories(db: Session, character_id: int, user_id: int) -> List[StoryUnlockedResponse]:
    """
    指定したキャラクターのストーリーを取得をRelationshipのTrustLevelに紐づけて取得
    """
    relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()
    if not relationship:
        return []
    stories = db.query(Story).filter(
        Story.character_id == character_id,
        Story.required_trust_level <= relationship.trust_level_id
    ).all()
    if not stories:
        return []
    return [StoryUnlockedResponse.from_orm(story) for story in stories]

def get_locked_stories(db: Session, character_id: int, user_id: int) -> List[StoryLockedResponse]:
    """
    指定したキャラクターのストーリーを取得をRelationshipのTrustLevelに紐づけて取得
    """
    relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()
    if not relationship:
        return []
    stories = db.query(Story).filter(
        Story.character_id == character_id,
        Story.required_trust_level > relationship.trust_level_id
    ).all()
    if not stories:
        return []
    return [StoryLockedResponse.from_orm(story) for story in stories]

async def unlock_character_story(
    db: Session,
    character_id: int,
    user_id: int,
) -> StoryUnlockedResponse:
    """
    キャラクターのストーリーをアンロックする
    """
    relationship = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).first()
    
    if not relationship:
        raise ValueError("Relationship not found for the given user and character")

    story = db.query(Story).filter(
        Story.character_id == character_id,
        Story.required_trust_level == relationship.trust_level_id
    ).first()

    if not story:
        return None
        
    return StoryUnlockedResponse.from_orm(story)

async def get_character_nfc_uuid_by_nfc_uuid(db: Session, nfc_uuid: str) -> CharacterResponse:
    """
    指定したNFC UUIDに紐づくCharacterNfcUuid情報を非同期で取得
    """
    result = db.query(Character).join(CharacterNfcUuid).filter(
        CharacterNfcUuid.nfc_uuid == nfc_uuid
    ).first()

    if not result:
        return None

    return CharacterResponse.from_orm(result)
