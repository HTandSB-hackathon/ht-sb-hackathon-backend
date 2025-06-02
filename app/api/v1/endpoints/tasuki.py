from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.tasuki.tasuki_client import TasukiClient
from app.crud.character import get_character_by_id
from app.crud.tasuki import TasukiService
from app.schemas.chat import ChatInput, ChatOutput

router = APIRouter()

def get_tasuki_client():
    """TASUKIクライアントを取得"""
    try:
        return TasukiClient()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize LLM client. Please check API key configuration."
        )

def get_tasuki_service(project_id: str, character, tasuki_client: TasukiClient = Depends(get_tasuki_client)) -> Any:
    """TASUKIサービスを取得"""
    try:
        return TasukiService(tasuki_client, project_id, character)
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize TASUKI service. Please check API key configuration."
        )


# @router.get("/check", tags=["tasuki"], response_model=schemas.TasukiAuthCheckOutput)
# async def tasuki_check(
#     tasuki_service = Depends(get_tasuki_client), 
#     # current_user = Depends(deps.get_current_user)
# ) -> schemas.TasukiAuthCheckOutput:
#     """
#     TASUKIに接続できるか確認するエンドポイント
#     """
#     try:
#         response = await tasuki_service.check_auth()
#         return response
#     except Exception:
#         raise HTTPException(
#             status_code=500, detail="TASUKIの認証チェックに失敗しました。APIキーの設定を確認してください。"
#         )
    
@router.post("/chat/{character_id}", tags=["tasuki"], response_model=ChatOutput)
async def tasuki_chat(
    inputs: ChatInput,
    character_id: int,
    db: Session = Depends(deps.get_db),
    tasuki_client: TasukiClient = Depends(get_tasuki_client),
    current_user = Depends(deps.get_current_user)
) -> ChatOutput:
    """
    TASUKIプロジェクトでチャットを実行するエンドポイント
    """
    try:
        # キャラクター情報を取得
        character = get_character_by_id(db, character_id)
        if not character:
            raise HTTPException(
                status_code=404, detail="指定されたキャラクターが見つかりません。"
            )
        # TASUKIサービスを取得
        print(f"Character TASUKI Project ID: {character.tasuki_project_id}")
        tasuki_service = TasukiService(tasuki_client, "bfb33a20-e896-4006-8505-e0776c3563ba")
        return tasuki_service.chat(inputs, character)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"TASUKIチャットに失敗しました。{str(e)}"
        )
