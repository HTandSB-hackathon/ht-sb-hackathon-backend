from typing import List

from sqlalchemy.orm import Session

from app.models.character import Character, Story
from app.models.relationship import Relationship
from app.schemas.character import CharacterLockedResponse, CharacterResponse, StoryResponse


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
def get_character_stories(db: Session, character_id: int, user_id: int) -> List[CharacterResponse]:
    """
    指定したキャラクターのストーリーを取得
    """
    relationships = db.query(Relationship).filter(
        Relationship.user_id == user_id,
        Relationship.character_id == character_id
    ).all()
    if not relationships:
        return []
    stories = db.query(Story).filter(Story.character_id == character_id).all()
    if not stories:
        return []
    return [StoryResponse.from_orm(story) for story in stories]