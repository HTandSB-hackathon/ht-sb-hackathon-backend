from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import event as crud
from app.schemas import event as schemas
from app.schemas.user import User

router = APIRouter()

# 最新のイベントを3件取得するエンドポイント
@router.get("", response_model=List[schemas.EventResponse], tags=["event"])
async def get_latest_events(
    mongodb: Session = Depends(deps.get_mongo_db),
    current_user: User = Depends(deps.get_current_user)
) -> List[schemas.EventResponse]:
    """
    ユーザーの最新のイベントを3件取得するエンドポイント
    """
    events = await crud.get_latest_events(mongodb, user_id=current_user.id, limit=3)
    return events