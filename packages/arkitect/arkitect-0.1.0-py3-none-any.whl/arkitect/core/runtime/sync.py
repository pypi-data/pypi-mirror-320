import abc
from typing import Any, Callable, Iterable

from pydantic import BaseModel

from .model import RequestType, Response, ResponseType


class SyncRunner(BaseModel):
    invoke: Callable[[RequestType], Iterable[ResponseType]]

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        runnable_func: Callable[[RequestType], Iterable[ResponseType]],
        **kwargs: Any,
    ):
        super().__init__(invoke=runnable_func, **kwargs)

    @abc.abstractmethod
    def run(self, request: RequestType) -> Response:
        pass

    @abc.abstractmethod
    def generate(self, request: RequestType) -> Iterable[str]:
        pass
