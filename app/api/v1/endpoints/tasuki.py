from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.api import deps
from app.core.tasuki.tasuki_client import TasukiClient
from app.crud.character import get_character_by_id
from app.crud.tasuki import TasukiService, get_chat_history, save_chat_message
from app.schemas.chat import ChatInput, ChatMessage, ChatOutput

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


@router.get("/chat/{character_id}", tags=["tasuki"], response_model=List[ChatMessage])
async def tasuki_chat_history(
    character_id: int,
    db: Session = Depends(deps.get_db),
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    current_user = Depends(deps.get_current_user)
) -> List[ChatMessage]:
    """
    TASUKIプロジェクトのチャット履歴を取得するエンドポイント
    """

    # キャラクター情報を取得
    character = get_character_by_id(db, character_id)
    if not character:
        raise HTTPException(
            status_code=404, detail="指定されたキャラクターが見つかりません。"
        )

    # チャット履歴を取得
    chat_history = await get_chat_history(
        mongodb,
        user_id=current_user.id,
        character_id=character.id
    )

    return chat_history  

@router.post("/chat/{character_id}", tags=["tasuki"], response_model=ChatOutput)
async def tasuki_chat(
    inputs: ChatInput,
    character_id: int,
    db: Session = Depends(deps.get_db),
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    tasuki_client: TasukiClient = Depends(get_tasuki_client),
    current_user = Depends(deps.get_current_user)
) -> ChatOutput:
    """
    TASUKIプロジェクトでチャットを実行するエンドポイント
    """

    # キャラクター情報を取得
    character = get_character_by_id(db, character_id)
    if not character:
        raise HTTPException(
            status_code=404, detail="指定されたキャラクターが見つかりません。"
        )
        
    try:
        
        input_result = await save_chat_message(
            mongodb, 
            user_id=current_user.id, 
            character_id=character.id, 
            role=inputs.role,
            content=inputs.response,
        )

        print(f"入力メッセージ保存結果: {input_result}")

        tasuki_service = TasukiService(tasuki_client, character.tasuki_project_id)

        output = await tasuki_service.chat(inputs, character)

        output_result = await save_chat_message(
            mongodb, 
            user_id=current_user.id, 
            character_id=character.id, 
            role=output.role,
            content=output.response,
        )

        print(f"出力メッセージ保存結果: {output_result}")

        return output
    except Exception as e:
        print(f"TASUKIチャットに失敗しました: {e}")
        raise HTTPException(
            status_code=500, detail=f"TASUKIチャットに失敗しました。{str(e)}"
        )
