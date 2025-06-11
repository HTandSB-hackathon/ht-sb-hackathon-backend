from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.api import deps
from app.core.aws.bedrock_client import BedrockClient
from app.core.aws.polly_client import PollyClient
from app.core.tasuki.tasuki_client import TasukiClient
from app.crud.character import get_character_by_id
from app.crud.redis import RedisCacheService
from app.crud.relationship import update_relationship_total_point
from app.crud.tasuki import (
    ConversationAnalysisService,
    PositiveAnalysisService,
    TasukiService,
    get_all_chat_count,
    get_all_chat_count_by_character,
    get_chat_count,
    get_chat_history,
    save_chat_message,
)
from app.schemas.chat import ChatCount, ChatInput, ChatMessage, ChatOutput, ConversationAnalysisChainInput, VoiceReaderInput

router = APIRouter()

def get_tasuki_client():
    """TASUKIクライアントを取得"""
    try:
        return TasukiClient()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize LLM client. Please check API key configuration."
        )

def get_bedrock_client() -> BedrockClient:
    """Amazon Bedrockクライアントを取得"""
    try:
        return BedrockClient()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Amazon Bedrock client. Please check AWS credentials."
        )

def get_tasuki_service(project_id: str, character, tasuki_client: TasukiClient = Depends(get_tasuki_client)) -> Any:
    """TASUKIサービスを取得"""
    try:
        return TasukiService(tasuki_client, project_id, character)
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize TASUKI service. Please check API key configuration."
        )
    
def get_redis_service() -> RedisCacheService:
    """Redisキャッシュサービスを取得"""
    try:
        return RedisCacheService()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Redis cache service. Please check configuration."
        )
    
def get_polly_client():
    """Amazon Polly clientを取得"""
    try:
        polly_client = PollyClient()
        return polly_client.get_client()
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Amazon Polly client. Please check AWS credentials."
        )

def get_bedrock_service(
    bedrock_client: BedrockClient = Depends(get_bedrock_client)
):
    """Amazon Bedrockサービスを取得"""
    try:
        return PositiveAnalysisService(
            bedrock_client=bedrock_client,
        )
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize Amazon Bedrock service. Please check AWS credentials."
        )


def get_conversation_analysis_service(
    tasuki_client: TasukiClient = Depends(get_tasuki_client)
) -> Any:
    """会話分析チェーンを取得"""
    try:
        conversation_analysis_service = ConversationAnalysisService(
            tasuki_client=tasuki_client,
            project_id="010d6606-c5f8-485c-8acb-278efd65b2c2",
        )

        return conversation_analysis_service
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Failed to initialize conversation analysis service. Please check API key configuration."
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
    cache_service: RedisCacheService = Depends(get_redis_service),
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

        updated_relationship = await update_relationship_total_point(
            db, cache_service, user_id=current_user.id, character_id=character.id,
            points_to_add=1
        )
        print(f"更新された信頼関係: {updated_relationship}")

        return output
    except Exception as e:
        print(f"TASUKIチャットに失敗しました: {e}")
        raise HTTPException(
            status_code=500, detail=f"TASUKIチャットに失敗しました。{str(e)}"
        )

@router.get("/chat/count/all", tags=["tasuki"], response_model=int)
async def tasuki_chat_count(
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    current_user = Depends(deps.get_current_user)
) -> int:
    """
    ユーザーのチャット履歴の件数を取得するエンドポイント
    """
    try:
        count = await get_all_chat_count(mongodb, user_id=current_user.id)
        print(f"ユーザーのチャット履歴件数: {count}")
        return count
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"チャット履歴の件数取得に失敗しました。{str(e)}"
        )
    
@router.get("/chat/count/character/{character_id}", tags=["tasuki"], response_model=int)
async def tasuki_chat_count_by_character(
    character_id: int,
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    current_user = Depends(deps.get_current_user)
) -> int:
    """
    ユーザーの特定キャラクターとのチャット履歴の件数を取得するエンドポイント
    """
    try:
        count = await get_chat_count(mongodb, user_id=current_user.id, character_id=character_id)
        return count
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"チャット履歴の件数取得に失敗しました。{str(e)}"
        )
    
@router.get("/chat/count/all_by_characters", tags=["tasuki"], response_model=List[ChatCount])
async def tasuki_chat_count_all_by_characters(
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    current_user = Depends(deps.get_current_user)
) -> List[ChatCount]:
    """
    ユーザーの全キャラクターとのチャット履歴の件数を取得するエンドポイント
    """
    try:
        counts = await get_all_chat_count_by_character(mongodb, user_id=current_user.id)
        return counts
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"全キャラクターのチャット履歴件数取得に失敗しました。{str(e)}"
        )
    
@router.post("/chat/{character_id}/voice_reader", tags=["tasuki"])
def tasuki_voice_reader(
    input: VoiceReaderInput, 
    character_id: int,
    polly_client = Depends(get_polly_client),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> StreamingResponse:

    character = get_character_by_id(db, character_id)

    if not character:
        raise HTTPException(
            status_code=404, detail="指定されたキャラクターが見つかりません。"
        )
    
    if not input.text:
        raise HTTPException(
            status_code=400, detail="音声化するテキストが指定されていません。"
        )
    
    gender = character.gender

    if gender == 0:
        voice = "Takumi"
    elif gender == 1:
        voice = "Mizuki"

    try:
        # Amazon Pollyを使用して音声を生成
        response = polly_client.synthesize_speech(
            Text=input.text,
            OutputFormat='mp3',
            VoiceId=voice,
            LanguageCode='ja-JP'
        )

        audio_stream = response.get("AudioStream")
        if not audio_stream:
            raise HTTPException(
                status_code=500, detail="音声の生成に失敗しました。"
            )
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=voice.mp3"}
        )
    except Exception as e:
        print(f"音声生成に失敗しました: {e}")
        raise HTTPException(
            status_code=500, detail=f"音声生成に失敗しました。{str(e)}"
        )
    
@router.get("/chat/conversation_analysis/{character_id}", tags=["tasuki"])
async def tasuki_conversation_analysis(
    character_id: int,
    bedrock_service: PositiveAnalysisService = Depends(get_bedrock_service),
    conversation_analysis: ConversationAnalysisService = Depends(get_conversation_analysis_service),
    db: Session = Depends(deps.get_db),
    mongodb: AsyncIOMotorDatabase = Depends(deps.get_mongo_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    会話分析を実行するエンドポイント
    """

    inputs = ConversationAnalysisChainInput(
        user_id=current_user.id,
        character_id=character_id
    )

    try:
        conversation_analysis_result = await conversation_analysis.check(
            inputs=inputs, 
            db=db,
            mongodb=mongodb
        )

        positive = await bedrock_service.check(
            inputs=inputs,
            db=db,
            mongodb=mongodb
        )

        return {
            "conversation_analysis": conversation_analysis_result,
            "positive_analysis": positive
        }
        
    except Exception as e:
        print(f"会話分析に失敗しました: {e}")
        raise HTTPException(
            status_code=500, detail=f"会話分析に失敗しました。{str(e)}"
        )
    