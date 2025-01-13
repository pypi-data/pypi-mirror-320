from typing import Optional
from ethosian.model.openai.chat import OpenAIChat


class OpenAILike(OpenAIChat):
    id: str = "not-provided"
    name: str = "OpenAILike"
    api_key: Optional[str] = "not-provided"
