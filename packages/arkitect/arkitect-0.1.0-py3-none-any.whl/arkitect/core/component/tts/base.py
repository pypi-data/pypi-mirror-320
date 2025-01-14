from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, Optional, Union

from pydantic import BaseModel

from arkitect.core.component.llm.model import ArkChatCompletionChunk, ArkChatResponse


class TTSResponseChunk(BaseModel):
    event: Optional[int] = None
    audio: Optional[bytes] = None
    transcript: Optional[str] = None


class AsyncBaseTTSClient(ABC):
    @abstractmethod
    async def tts(
        self,
        source: AsyncIterable[Union[ArkChatCompletionChunk, ArkChatResponse, str]],
        stream: bool = True,
        **kwargs: Any,
    ) -> AsyncIterable[TTSResponseChunk]:
        ...
