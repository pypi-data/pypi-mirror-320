from abc import abstractmethod
from typing import Any, Optional, TypeVar

from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate
from pydantic.v1 import BaseModel, Field
from volcenginesdkarkruntime import AsyncArk

from arkitect.core.client import default_ark_client

T = TypeVar("T")


class BaseLanguageModel(BaseModel):
    endpoint_id: str
    client: AsyncArk = Field(default_factory=default_ark_client)
    template: Optional[BasePromptTemplate] = None
    output_parser: Optional[BaseOutputParser] = None

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
