from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.core.tasuki.tasuki_client import TasukiClient
from app.crud.tasuki import TasukiService
from app.schemas import tasuki as schemas

router = APIRouter()

def get_tasuki_client():
    """TASUKIクライアントを取得"""
    try:
        return TasukiClient()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize LLM client. Please check API key configuration."
        )

def get_tasuki_service(tasuki_client: TasukiClient = Depends(get_tasuki_client)) -> Any:
    """TASUKIサービスを取得"""
    try:
        return TasukiService(tasuki_client)
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize TASUKI service. Please check API key configuration."
        )


@router.get("/check", tags=["tasuki"], response_model=schemas.TasukiAuthCheckOutput)
async def tasuki_check(tasuki_service = Depends(get_tasuki_service), current_user = Depends(deps.get_current_user)) -> schemas.TasukiAuthCheckOutput:
    """
    TASUKIに接続できるか確認するエンドポイント
    """
    try:
        response = await tasuki_service.check_auth()
        return response
    except Exception:
        raise HTTPException(
            status_code=500, detail="TASUKIの認証チェックに失敗しました。APIキーの設定を確認してください。"
        )
