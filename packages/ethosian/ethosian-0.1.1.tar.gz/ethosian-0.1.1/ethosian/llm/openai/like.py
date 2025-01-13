from typing import Optional
from ethosian.llm.openai.chat import OpenAIChat


class OpenAILike(OpenAIChat):
    name: str = "OpenAILike"
    model: str = "not-provided"
    api_key: Optional[str] = "not-provided"
