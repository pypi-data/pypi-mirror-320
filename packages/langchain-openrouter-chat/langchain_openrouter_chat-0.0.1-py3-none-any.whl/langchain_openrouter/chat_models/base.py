from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic import Field


class ChatOpenRouter(ChatOpenAI):
    openai_api_base: Optional[str] = Field(
        default="https://openrouter.ai/api/v1", alias="base_url"
    )
