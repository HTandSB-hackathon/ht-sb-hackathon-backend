import logging

from app.core.tasuki.tasuki_client import TasukiClient
from app.schemas.tasuki import TasukiAuthCheckOutput

logger = logging.getLogger(__name__)


class TasukiService:
    def __init__(self, tasuki_client: TasukiClient):
        self.tasuki_client = tasuki_client

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