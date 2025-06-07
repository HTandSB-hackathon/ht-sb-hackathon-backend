from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import occupation as crud
from app.models import user as user_model
from app.schemas import occupation as schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.OccupationResponse])
def read_occupations(
    db: Session = Depends(deps.get_db),
    current_user: user_model.User = Depends(deps.get_current_active_user),
) -> List[schemas.OccupationResponse]:
    """
    職業一覧を取得
    """
    occupations = crud.get_occupations(db)
    return occupations

@router.get("/{occupation_id}", response_model=schemas.OccupationResponse)
def read_occupation(
    *,
    db: Session = Depends(deps.get_db),
    occupation_id: int,
    current_user: user_model.User = Depends(deps.get_current_active_user),
) -> schemas.OccupationResponse:
    """
    特定の職業情報を取得
    """
    occupation = crud.get_occupation(db, occupation_id=occupation_id)
    if not occupation:
        raise HTTPException(status_code=404, detail="Occupation not found")
    return occupation
