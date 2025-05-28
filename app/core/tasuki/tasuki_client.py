import logging

import httpx

from app.core.config import settings

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