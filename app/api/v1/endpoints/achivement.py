from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import achivement as crud_achivement
from app.schemas.achivement import AchivementResponse, UserAchivementCreate, UserAchivementResponse, UserAchivementUnlockRequest

router = APIRouter()


@router.get("/locked", response_model=List[AchivementResponse])
def get_user_locked_achivements(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    ユーザーが取得していない実績をすべて返す
    """
    achivements = crud_achivement.get_locked_achivements_for_user(db, user_id=current_user.id)
    return achivements


@router.get("/unlocked", response_model=List[AchivementResponse])
def get_user_unlocked_achivements(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    ユーザーが取得している実績をすべて返す
    """
    achivements = crud_achivement.get_unlocked_achivements_for_user(db, user_id=current_user.id)
    return achivements


@router.post("/unlock", response_model=UserAchivementResponse)
async def unlock_user_achivement(
    payload: UserAchivementUnlockRequest = Body(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db)
) -> Any:
    """
    ユーザーが実績をアンロックできるか検証し、可能であればアンロックする
    achivement_id に応じたロジックで検証 (現在は仮実装)
    """
    achivement_id_to_unlock = payload.achivement_id

    # 対象の実績が存在するか確認
    achivement = await crud_achivement.get_achivement(db, achivement_id=achivement_id_to_unlock)
    if not achivement:
        raise HTTPException(status_code=404, detail=f"Achivement with id {achivement_id_to_unlock} not found")

    # ユーザー実績が既に存在するか確認、なければ作成
    user_achivement = crud_achivement.get_user_achivement(db, user_id=current_user.id, achivement_id=achivement_id_to_unlock)
    if not user_achivement:
        user_achivement = crud_achivement.create_user_achivement(
            db,
            obj_in=UserAchivementCreate(user_id=current_user.id, achivement_id=achivement_id_to_unlock, is_unlocked=False)
        )

    if user_achivement.is_unlocked:
        # 既にアンロック済み
        # UserAchivementResponseに実績詳細を含めるために、achivementモデルをセット
        user_achivement.achivement = achivement
        return user_achivement

    # 実績ごとのアンロック条件判定ロジック（実績ごとに増やしていく）
    can_unlock = await crud_achivement.check_achivement_unlockable(
        db=db, mongodb=mongodb, user_id=current_user.id, achivement_id=achivement_id_to_unlock
    )
    

    if can_unlock:
        updated_user_achivement = crud_achivement.update_user_achivement(
            db, db_obj=user_achivement, obj_in={"is_unlocked": True}
        )
        # UserAchivementResponseに実績詳細を含めるために、achivementモデルをセット
        updated_user_achivement.achivement = achivement
        return updated_user_achivement
    else:
        # アンロック条件未達
        # UserAchivementResponseに実績詳細を含めるために、achivementモデルをセット
        user_achivement.achivement = achivement
        return user_achivement
