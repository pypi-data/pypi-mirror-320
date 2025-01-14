from typing import Any, Dict, Type

from pydantic import ValidationError

from arkitect.core.errors import parse_pydantic_error
from arkitect.core.runtime import Request, RequestType
from arkitect.telemetry.logger import gen_log_id
from arkitect.telemetry.trace import task
from arkitect.utils.context import (
    get_client_reqid,
    get_reqid,
    set_client_reqid,
    set_headers,
    set_reqid,
)


@task()
def parse_request(event: Dict[str, Any], request_cls: Type[RequestType]) -> Request:
    body = event.get("body", "")
    headers = event.get("headers", {})

    set_headers(headers)

    # here we generate request id instead of reading from headers
    set_reqid(
        headers.get("X-Faas-Request-Id", headers.get("X-Request-Id", gen_log_id()))
    )
    set_client_reqid(headers.get("X-Client-Request-Id", get_reqid()))

    try:
        return request_cls.model_validate_json(body, strict=True)
    except ValidationError as e:
        raise parse_pydantic_error(e)


@task()
def parse_response(status_code: int, content: str) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "x-client-request-id": get_client_reqid(),
            "x-request-id": get_reqid(),
        },
        "body": content,
    }
