from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseInput, BaseOutput


class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Role of the message sender (user, assistant)")
    content: str = Field(..., description="Content of the message")


class ChatInput(BaseInput):
    """Input schema for chat endpoint"""

    role: str = Field(..., description="Role of the current message")
    response: str = Field(..., description="Current message content")
    history: List[ChatMessage] = Field(default=[], description="Chat history")


class ChatOutput(BaseOutput):
    """Output schema for chat endpoint"""

    role: str = Field(..., description="Role of the response")
    response: str = Field(..., description="Response content")
    chunks: Optional[List[Dict]] = Field(
        default=None, description="chunksは、RAG が参照したチャンクの情報です。"
    )

class ChatCount(BaseModel):
    """Chat count model"""

    character_id: int = Field(..., description="Character ID")
    count: int = Field(..., ge=0, description="Number of chats with the character")
    last_chat_date: Optional[datetime] = Field(default=None, description="Date of the last chat with the character")

    class Config:
        orm_mode = True
        from_attributes = True

class VoiceReaderInput(BaseModel):
    """Input schema for voice chat"""

    text: str = Field(..., description="Text to be converted to speech")

class ConversationAnalysisChainInput(BaseModel):
    """Input schema for conversation analysis chain"""

    user_id: int = Field(..., description="User ID")
    character_id: int = Field(..., description="Character ID")