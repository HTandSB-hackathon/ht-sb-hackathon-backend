import logging
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.core.aws.bedrock_client import BedrockClient
from app.core.llm.chain.chatchain import ChatChain, ConversationAnalysisChain, PositiveAnalysisChain
from app.core.tasuki.tasuki_client import TasukiClient
from app.schemas.chat import ChatCount, ChatMessage, ChatOutput
from app.schemas.tasuki import TasukiAuthCheckOutput

logger = logging.getLogger(__name__)


class TasukiService:
    def __init__(self, tasuki_client: TasukiClient, project_id: str):
        self.tasuki_client = tasuki_client
        self._setup_chain(project_id)

    def _setup_chain(self, project_id: str) -> None:
        """
        TASUKIプロジェクト用のチャットクライアントをセットアップ
        """
        if not project_id:
            raise ValueError("プロジェクトIDが指定されていません。")
        chat_llm = self.tasuki_client.get_chat_model(project_id)
        self.chain = ChatChain(
            chat_llm=chat_llm,
        )

    async def check_auth(self) -> TasukiAuthCheckOutput:
        """
        TASUKIの認証をチェックするメソッド
        """
        try:
            response = await self.tasuki_client.get("/auth_check")
            return response
        except Exception as e:
            logger.error(f"TASUKI認証チェックに失敗しました: {e}")
            raise TasukiAuthCheckOutput(status_code="500", message=f"TASUKI認証チェックに失敗しました。APIキーの設定を確認してください。str{e}")
        
    
    async def chat(self, inputs, character) -> ChatOutput:
        """
        TASUKIプロジェクトでチャットを実行するメソッド
        """
        try:
            result = self.chain.invoke(inputs, character)
            return ChatOutput(
                response=result.content,
                role=result.response_metadata.get("role", "assistant"),
                chunks=result.response_metadata.get("chunks", []),
            )
        except Exception as e:
            logger.error(f"TASUKIチャットに失敗しました: {e}")
            raise ChatOutput(
                response=f"TASUKIチャットに失敗しました。{str(e)}",
                role="assistant",
                chunks=[]
            )
        
class ConversationAnalysisService:
    def __init__(self, 
            tasuki_client: TasukiClient,
            project_id: str,
        ):
        self.tasuki_client = tasuki_client
        self._setup_chain(project_id)

    def _setup_chain(self, 
            project_id: str,
        ) -> None:
        """
        TASUKIプロジェクト用のチャットクライアントをセットアップ
        """
        if not project_id:
            raise ValueError("プロジェクトIDが指定されていません。")
        chat_llm = self.tasuki_client.get_chat_model(project_id)
        self.chain = ConversationAnalysisChain(
            chat_llm=chat_llm,
        ) 
    
    async def check(self, inputs, db: Session, mongodb: AsyncIOMotorDatabase) -> Any:
        """
        TASUKIプロジェクトで語句分析を実行するメソッド
        """
        try:
            result = await self.chain.invoke(inputs, db=db, mongodb=mongodb)
            return result
        except Exception as e:
            logger.error(f"TASUKIチャットに失敗しました: {e}")
            raise 

class PositiveAnalysisService:
    def __init__(self, 
            bedrock_client: BedrockClient,
        ):
        self.bedrock_client = bedrock_client
        self._setup_chain()

    def _setup_chain(self, 
        ) -> None:
        """
        Bedrockをセットアップ
        """
        chat_llm = self.bedrock_client.get_client()
        self.chain = PositiveAnalysisChain(
            chat_llm=chat_llm,
        )

    async def check(self, inputs, db: Session, mongodb: AsyncIOMotorDatabase):
        """
        Bedrockでポジティブ分析を実行するメソッド
        """
        try:
            result = await self.chain.invoke(inputs, db=db, mongodb=mongodb)
            return result
        except Exception as e:
            logger.error(f"TASUKIチャットに失敗しました: {e}")
            raise 

async def get_chat_history(mongodb: AsyncIOMotorDatabase, user_id: str, character_id: str):
    """
    ユーザーの特定キャラクターとのチャット履歴を取得するヘルパーメソッド
    MongoDB構造: users[collection] -> user_id[document] -> character_id[subcollection] -> chat_messages[documents]
    """
    try:
        collections = mongodb["chats"]

        # ユーザーのチャット履歴を取得
        chat_history = await collections.find({"user_id": user_id, "character_id": character_id}).to_list(length=None)

        if not chat_history:
            logger.info(f"チャット履歴が見つかりません: user_id={user_id}, character_id={character_id}")
            return []

        # チャットメッセージをChatMessageモデルに変換
        messages = [ChatMessage(**msg) for msg in chat_history]

        logger.info(f"チャット履歴を取得しました: user_id={user_id}, character_id={character_id}, count={len(messages)}")
        return messages

    except Exception as e:
        logger.error(f"チャット履歴の取得に失敗しました: {e}")
        raise
    
async def save_chat_message(mongodb: AsyncIOMotorDatabase, user_id: str, character_id: str, role: str, content: str) -> Any:
    """
    チャットメッセージをMongoDB に保存するヘルパーメソッド
    MongoDB構造: users[collection] -> user_id[document] -> characters[subcollection] -> messages[documents]
    """
    try:

        collections = mongodb["chats"]
        
        chat_doc = {
            "user_id": user_id,
            "character_id": character_id,
            "content": content,
            "role": role,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"チャットメッセージを保存します: user_id={user_id}, character_id={character_id}, content={content}")

        # ユーザーのチャットメッセージを保存
        result = await collections.insert_one(chat_doc)
        
        logger.info(f"チャットメッセージを保存しました: user_id={user_id}, character_id={character_id}, message_id={result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"チャットメッセージの保存に失敗しました: {e}")
        raise

async def check_connection(mongodb: AsyncIOMotorDatabase):
    try:
        await mongodb.command("ping")
        print("✅ MongoDB に正常接続されています")
    except Exception as e:
        print(f"❌ 接続エラー: {e}")

async def get_chat_count(mongodb: AsyncIOMotorDatabase, user_id: str, character_id: str) -> int:
    """
    ユーザーの特定キャラクターとのチャットメッセージ数を取得するヘルパーメソッド
    """
    try:
        collections = mongodb["chats"]
        count = await collections.count_documents({"user_id": user_id, "character_id": character_id})
        logger.info(f"チャットメッセージ数を取得しました: user_id={user_id}, character_id={character_id}, count={count}")
        return count
    except Exception as e:
        logger.error(f"チャットメッセージ数の取得に失敗しました: {e}")
        raise

async def get_all_chat_count(mongodb: AsyncIOMotorDatabase, user_id: str) -> int:
    """
    ユーザーの特定キャラクターとの全チャットメッセージを取得するヘルパーメソッド
    """
    try:
        collections = mongodb["chats"]
        count = await collections.count_documents({"user_id": user_id})
        print(f"全チャットメッセージ数を取得しました: user_id={user_id}, count={count}")
        logger.info(f"全チャットメッセージ数を取得しました: user_id={user_id}, count={count}")
        return count

    except Exception as e:
        logger.error(f"全チャットメッセージの取得に失敗しました: {e}")
        raise

async def get_all_chat_count_by_character(
    mongodb: AsyncIOMotorDatabase, user_id: str
) -> ChatCount:
    """
    ユーザーの全てのキャラクターごとのチャットメッセージ数を取得するヘルパーメソッド
    """
    try:
        collections = mongodb["chats"]
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$character_id",
                    "count": {"$sum": 1},
                    "last_chat_date": {"$max": "$timestamp"},
                }
            },
            {
                "$project": {
                    "character_id": "$_id",
                    "count": 1,
                    "last_chat_date": 1,
                    "_id": 0,
                }
            },
        ]
        results = await collections.aggregate(pipeline).to_list(length=None)

        chat_counts = []
        for result in results:
            last_chat_date_obj = None
            if result.get("last_chat_date"):
                try:
                    last_chat_date_obj = datetime.fromisoformat(result["last_chat_date"].replace("Z", "+00:00"))
                except ValueError:
                    logger.warning(f"Could not parse timestamp: {result['last_chat_date']} for character_id: {result['character_id']}")
            chat_counts.append(
                ChatCount(
                    character_id=result["character_id"],
                    count=result["count"],
                    last_chat_date=last_chat_date_obj,
                )
            )
        
        logger.info(f"全キャラクターのチャットメッセージ数を取得しました: user_id={user_id}, counts={chat_counts}")
        return chat_counts

    except Exception as e:
        logger.error(f"全キャラクターのチャットメッセージ数の取得に失敗しました: {e}")
        raise
