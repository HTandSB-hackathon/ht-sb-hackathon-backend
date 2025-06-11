import json
import logging
import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.core.llm.chain.base import BaseChain
from app.core.llm.chain.jschema import SCHEMA_CNVERSATION_ANALYSIS, SCHEMA_POSITIVE_ANALYSIS
from app.schemas.chat import ChatInput, ChatMessage, ChatOutput, ConversationAnalysisChainInput

logger = logging.getLogger(__name__)


class ChatChain(BaseChain):
    """Custom chat chain that handles history formatting"""

    def __init__(self, chat_llm: BaseChatModel):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template="""あなたはこれから以下の内容の人になりきってください。

会話履歴:
{history}

現在のメッセージ役割: {role}
現在のメッセージ: {response}

キャラクター情報:
- 名前: {character_name}
- 年齢: {character_age}歳
- 性格: {character_personality}
- 趣味: {character_hobbies}
- 特技: {character_specialties}
- 自己紹介: {character_introduction}

このキャラクターの特性を反映した自然な回答をしてください。

回答で使用可能な言語は日本語のみとします。
回答は必ず福島県の方言を使ってください。
回答は200文字程度とします。

上記の情報に基づいて、日本語の回答を提供してください。""",
            input_variables=[
                "role", 
                "response", 
                "history", 
                "character_name",
                "character_age",
                "character_personality",
                "character_hobbies",
                "character_specialties",
                "character_introduction"
            ],
        )
        self.chain = self.prompt | self.chat_llm

    def get_prompt(self, inputs: ChatInput, character, **kwargs) -> str:
        """Get the prompt string with formatted history."""
        # Format history
        history_text = ""
        for msg in inputs.history:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "role": inputs.role,
            "response": inputs.response,
            "history": history_text,
            "character_name": character.name,
            "character_age": character.age,
            "character_personality": ', '.join(character.personality or []),
            "character_hobbies": ', '.join(character.hobbies or []),
            "character_specialties": ', '.join(character.specialties or []),
            "character_introduction": character.introduction,
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()

    def invoke(self, inputs: ChatInput, character, **kwargs) -> ChatOutput:
        """Invoke the chain with history formatting."""
        # Format history
        history_text = ""
        #20 会話まで
        for msg in inputs.history[-20:]:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "role": inputs.role,
            "response": inputs.response,
            "history": history_text,
            "character_name": character.name,
            "character_age": character.age,
            "character_personality": ', '.join(character.personality or []),
            "character_hobbies": ', '.join(character.hobbies or []),
            "character_specialties": ', '.join(character.specialties or []),
            "character_introduction": character.introduction,
        }
        
        return self.chain.invoke(formatted_input, **kwargs)
    
class ConversationAnalysisChain(BaseChain):
    """Chain for analyzing conversation history"""

    def __init__(self, 
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''あなたは福島の方言・文化・特産品に詳しい専門家AIです。

以下のユーザーの会話文を読み取り、福島に関連する語句（方言、地名、文化、特産品など）を抽出してください。
ただし、会話履歴の**"user" の発言だけ**を対象とし、"assistant" の発言は必ず無視してください。
それ以外のことは絶対に出力しないでください。

会話履歴:"""
{history}
"""

出力形式:"""
{schema}
"""
''',
    input_variables=["history", "schema"]
    )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)

    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for conversation analysis."""
        # Format history
        history_text = ""
        for msg in inputs.history:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "history": history_text,
            "schema": SCHEMA_CNVERSATION_ANALYSIS,
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()
        
    async def invoke(self, 
            inputs: ConversationAnalysisChainInput,            
            db: Session,
            mongodb: AsyncIOMotorDatabase
        ):
        """Invoke the chain for conversation analysis."""

        collections = mongodb["chats"]
        chat_history = await collections.find({"user_id": inputs.user_id, "character_id": inputs.character_id}).to_list(length=None)

        message = [
            ChatMessage(role=msg['role'], content=msg['content']) for msg in chat_history
        ]

        history_text = ""
        for msg in message[-10:]:
            history_text += f"{msg.role}: {msg.content}\n"

        formatted_input = {
            "history": history_text,
            "schema": SCHEMA_CNVERSATION_ANALYSIS,
        }
      
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)
    
    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output
    
class PositiveAnalysisChain(BaseChain):
    """Chain for analyzing positive aspects of conversation"""

    def __init__(self, 
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''以下の日本語の文章のポジティブ度を数値（0〜1）で評価してください。
- 数値が 0 に近いほど"Negative"、
- 0.5 付近なら"Neutral"、
- 1 に近いほど"Positive"です。

さらに、その判断理由も1〜2文で説明してください。
ただし、会話履歴の**"user" の発言だけ**を対象とし、"assistant" の発言は必ず無視してください。
出力形式以外のことは絶対に出力しないでください。

会話内容:"""
{history}
"""

出力形式:"""
{schema}
"""
''',
    input_variables=["history", "schema"]
        )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)

    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for positive analysis."""
        # Format history
        history_text = ""
        for msg in inputs.history:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "history": history_text,
            "schema": SCHEMA_POSITIVE_ANALYSIS,
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()

    async def invoke(self, 
            inputs: ConversationAnalysisChainInput,            
            db: Session,
            mongodb: AsyncIOMotorDatabase
        ):
        """Invoke the chain for conversation analysis."""

        collections = mongodb["chats"]
        chat_history = await collections.find({"user_id": inputs.user_id, "character_id": inputs.character_id}).to_list(length=None)

        message = [
            ChatMessage(role=msg['role'], content=msg['content']) for msg in chat_history
        ]

        history_text = ""
        for msg in message[-10:]:
            history_text += f"{msg.role}: {msg.content}\n"

        formatted_input = {
            "history": history_text,
            "schema": SCHEMA_POSITIVE_ANALYSIS,
        }
      
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)

    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output