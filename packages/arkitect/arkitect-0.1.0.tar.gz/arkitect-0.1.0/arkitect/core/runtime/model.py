from typing import Optional, TypeVar, Union

from pydantic import BaseModel

from arkitect.core.errors import ArkError, Error


class Request(BaseModel):
    stream: bool = False


class Response(BaseModel):
    error: Optional[Union[Error, ArkError]] = None


RequestType = TypeVar("RequestType", bound=Request, contravariant=True)
ResponseType = TypeVar("ResponseType", bound=Response, covariant=True)


class Context(BaseModel):
    request_id: str = ""
    client_request_id: str = ""
    account_id: str = ""
    resource_id: str = ""
    resource_type: str = ""
