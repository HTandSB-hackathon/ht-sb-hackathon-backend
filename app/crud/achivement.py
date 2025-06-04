from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, join

from app.models.achivement import Achivement, UserAchivement
from app.schemas.achivement import UserAchivementCreate, UserAchivementUpdate


def get_user_achivement(db: Session, user_id: int, achivement_id: int) -> Optional[UserAchivement]:
    """指定したユーザーIDと実績IDのユーザー実績を取得 (関連する実績情報もEager Load)"""
    return db.query(UserAchivement).options(joinedload(UserAchivement.achivement)).filter(UserAchivement.user_id == user_id, UserAchivement.achivement_id == achivement_id).first()

def get_user_achivements_by_user_id(db: Session, user_id: int, is_unlocked: Optional[bool] = None) -> List[UserAchivement]:
    """指定したユーザーIDのユーザー実績一覧を取得 (is_unlockedでフィルタリング可能)"""
    query = db.query(UserAchivement).filter(UserAchivement.user_id == user_id)
    if is_unlocked is not None:
        query = query.filter(UserAchivement.is_unlocked == is_unlocked)
    return query.all()

def get_all_achivements_with_user_status(db: Session, user_id: int) -> List[dict]:
    """全ての実績と、指定ユーザーの取得状況を合わせて取得"""
    stmt = (
        select(
            Achivement.id.label("achivement_id"),
            Achivement.name,
            Achivement.description,
            Achivement.icon_image_url,
            UserAchivement.is_unlocked,
            UserAchivement.id.label("user_achivement_id") 
        )
        .select_from(Achivement)
        .outerjoin(UserAchivement, (Achivement.id == UserAchivement.achivement_id) & (UserAchivement.user_id == user_id))
        .order_by(Achivement.id)
    )
    results = db.execute(stmt).mappings().all()
    return results


def create_user_achivement(db: Session, obj_in: UserAchivementCreate) -> UserAchivement:
    """ユーザー実績を作成"""
    db_obj = UserAchivement(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_user_achivement(db: Session, db_obj: UserAchivement, obj_in: UserAchivementUpdate) -> UserAchivement:
    """ユーザー実績を更新"""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_achivement(db: Session, achivement_id: int) -> Optional[Achivement]:
    """実績IDで実績を取得"""
    return db.query(Achivement).filter(Achivement.id == achivement_id).first()

def get_unlocked_achivements_for_user(db: Session, user_id: int) -> List[Achivement]:
    """ユーザーがアンロックした実績のリストを取得"""
    return db.query(Achivement).join(UserAchivement).filter(
        UserAchivement.user_id == user_id,
        UserAchivement.is_unlocked == True
    ).all()

def get_locked_achivements_for_user(db: Session, user_id: int) -> List[Achivement]:
    """ユーザーがまだアンロックしていない実績のリストを取得"""
    # まずユーザーが既に何らかの形で関連している実績IDのセットを取得
    user_related_achivement_ids = db.query(UserAchivement.achivement_id).filter(UserAchivement.user_id == user_id).distinct().all()
    user_related_achivement_ids_set = {ua_id for (ua_id,) in user_related_achivement_ids}

    # is_unlocked = False の実績を取得
    locked_explicitly = db.query(Achivement).join(UserAchivement).filter(
        UserAchivement.user_id == user_id,
        UserAchivement.is_unlocked == False
    ).all()
    
    # UserAchivementにレコードが存在しない実績を取得
    achivements_not_in_userachivements = db.query(Achivement).filter(
        Achivement.id.notin_(user_related_achivement_ids_set)
    ).all()
    
    return locked_explicitly + achivements_not_in_userachivements
