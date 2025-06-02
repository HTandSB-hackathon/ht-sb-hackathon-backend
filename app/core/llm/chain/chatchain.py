import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

from app.core.llm.chain.base import BaseChain
from app.schemas.chat import ChatInput, ChatOutput

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
        
        return self.chain.invoke(formatted_input, **kwargs)