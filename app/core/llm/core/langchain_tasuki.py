from typing import Optional

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.schemas.chat import ChatOutput


class LangchainTasuki(BaseChatModel):

    api_url: str
    api_key: Optional[str] = None
    project_id: Optional[str] = None

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        prompt = "\n".join([m.content for m in messages if isinstance(m, HumanMessage)])
        output = self._call(prompt)  # あなたの _call ロジック
        return  ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=output["choices"][0]["delta"]["content"]),
                )
            ],
            llm_output={
                "role": "assistant",
                "chunks": output.get("chunks", []),
            }
        )

    def _call(self, prompt: str, **kwargs) -> ChatOutput:

        headers = {
            "Authorization": f"{self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "max_completion_tokens": 512,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0
        }
        response = requests.post(f"{self.api_url}/project/{self.project_id}/ragchat", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    @property
    def _llm_type(self) -> str:
        return "langchain_tasuki"
