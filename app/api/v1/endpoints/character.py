from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import character as crud
from app.schemas import character as schemas

router = APIRouter()

# 全キャラクター情報を取得するエンドポイント
@router.get("/", response_model=List[schemas.CharacterResponse])
def read_all_characters(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user)
) -> List[schemas.CharacterResponse]:
    """
    全キャラクター情報を取得
    """
    characters = crud.get_all_characters(db)
    return characters