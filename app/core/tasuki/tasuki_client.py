import logging

import httpx
from fastapi import HTTPException
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings
from app.core.llm.core.langchain_tasuki import LangchainTasuki

logger = logging.getLogger(__name__)

class TasukiClient:
    """TASUKIクライアント"""
    
    def __init__(self):
        self.base_url = settings.TASUKI_API_URL
        if not self.base_url:
            raise ValueError("TASUKIのベースURLが設定されていません。")
        logger.info(f"TASUKIクライアントを初期化しました: {self.base_url}")
        self.api_key = settings.TASUKI_API_KEY
        if not self.api_key:
            raise ValueError("TASUKIのAPIキーが設定されていません。")

        self.headers = {
            "Authorization": f"{self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
    
    def get_base_url(self) -> str:
        """TASUKIのベースURLを取得"""
        return self.base_url
    
    async def get(self, path):
        async with httpx.AsyncClient() as client:
            logger.info(f"TASUKI APIにGETリクエストを送信: {self.base_url+path}")
            response = await client.get(self.base_url+path, headers=self.headers)
            return response.json()
        
    def get_chat_model(self, project_id: str) -> BaseChatModel:    
        """TASUKIプロジェクト用のチャットクライアントを作成"""

        if not project_id:
            raise ValueError("プロジェクトIDが指定されていません。")
        try: 
            self._client = LangchainTasuki(
                api_url=self.base_url,
                api_key=self.api_key,
                project_id=project_id
            )
        except Exception as e:
            logger.error(f"TASUKIクライアントの初期化に失敗しました: {e}")
            raise HTTPException(f"TASUKIクライアントの初期化に失敗しました: {e}")
        return self._client