import logging
from datetime import datetime
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.event import EventResponse, FukushimaWeekResponse

logger = logging.getLogger(__name__)


async def save_event(mongodb: AsyncIOMotorDatabase, user_id: str, character_id: str, event_type: str, title :str, detail: str) -> None:
    """
    イベントをMongoDBに保存する関数
    evemt_type: "level_up", "relationship_change", "item_acquired"
    """
    try:

        # eventsのコレクションが存在しない場合は作成
        try:
            collections = await mongodb.create_collection("events")
            logger.info("コレクション 'events' を作成しました。")
        except Exception as e:
            logger.info(f"コレクション 'events' は既に存在します: {e}")

        collections = mongodb["events"]

        insert_data = {
            "user_id": user_id,
            "character_id": character_id,
            "title": title,
            "event_type": event_type,
            "timestamp": datetime.utcnow(),
            "details": detail
        }

        result = await collections.insert_one(insert_data)
        logger.info(f"イベントを保存しました: user_id={user_id}, character_id={character_id}, event_type={event_type}")
        return result
        
    except Exception as e:
        logger.error(f"イベントの保存に失敗しました: {e}")
        raise

# 最新のイベントを3件取得する関数
async def get_latest_events(mongodb: AsyncIOMotorDatabase, user_id: str, limit: int = 3) -> list[EventResponse]:
    """
    ユーザーの特定キャラクターに関連する最新のイベントを取得する関数
    """
    try:
        collections = mongodb["events"]
        events = await collections.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)

        # MongoDB documentをEventResponseスキーマに変換
        event_responses = []
        for event in events:
            event_response = EventResponse(
                id=str(event["_id"]),  # ObjectIdを文字列に変換
                user_id=str(event["user_id"]),  # intを文字列に変換
                character_id=str(event["character_id"]),  # intを文字列に変換
                title=event["title"],
                event_type=event["event_type"],
                timestamp=event["timestamp"],
                details=event["details"]
            )
            event_responses.append(event_response)
        
        logger.info(f"最新のイベントを取得しました: user_id={user_id}, count={len(event_responses)}")
        return event_responses
        
    except Exception as e:
        logger.error(f"最新のイベントの取得に失敗しました: {e}")
        raise

async def get_fukushima_week(mongodb: AsyncIOMotorDatabase) -> List[FukushimaWeekResponse]:
    """
    福島ウィークのイベントを取得する関数
    """
    try:
        collections = mongodb["fukushima-weeks"]
        # 最新の福島ウィークイベントを3件取得
        fukushima_weeks = await collections.find().sort("date", -1).limit(3).to_list(length=3)
        fukushima_week_responses = []
        for week in fukushima_weeks:
            fukushima_week_response = FukushimaWeekResponse(
                id=str(week["_id"]),  # ObjectIdを文字列に変換
                date=week["date"],
                title=week["title"],
                municipality=week["municipality"],
                url=week["url"]
            )
            fukushima_week_responses.append(fukushima_week_response)
        logger.info(f"福島ウィークイベントを取得しました: count={len(fukushima_week_responses)}")
        return fukushima_week_responses
    except Exception as e:
        logger.error(f"福島ウィークイベントの取得に失敗しました: {e}")
        raise