from typing import List

from sqlalchemy.orm import Session

from app.models.character import Character
from app.schemas.character import CharacterResponse


# 全キャラクター情報を取得
def get_all_characters(db: Session) -> List[CharacterResponse]:
    """
    全キャラクター情報を取得
    """
    characters = db.query(Character).all()
    if not characters:
        return []
    return [CharacterResponse.from_orm(character) for character in characters]