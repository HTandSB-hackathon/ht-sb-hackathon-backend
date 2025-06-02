import logging

from app.core.llm.chain.chatchain import ChatChain
from app.core.tasuki.tasuki_client import TasukiClient
from app.schemas.chat import ChatOutput
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
        
    
    def chat(self, inputs, character) -> ChatOutput:
        """
        TASUKIプロジェクトでチャットを実行するメソッド
        """
        try:
            print(self.chain.get_prompt(inputs, character))
            result =  self.chain.invoke(inputs, character)
            return {
                "response": result.content,
                "role": result.response_metadata.get("role", "assistant"),
                "chunks": result.response_metadata.get("chunks", []),
            }
        except Exception as e:
            logger.error(f"TASUKIチャットに失敗しました: {e}")
            raise ChatOutput(
                response=f"TASUKIチャットに失敗しました。{str(e)}",
                role="assistant",
                chunks=[]
            )