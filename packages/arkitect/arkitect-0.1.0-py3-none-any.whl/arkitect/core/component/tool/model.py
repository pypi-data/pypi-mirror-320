from typing import Any, Dict, Optional

from pydantic import BaseModel


class ArkToolRequest(BaseModel):
    """ """

    action_name: str
    tool_name: str

    dry_run: Optional[bool] = False
    timeout: Optional[int] = 60
    parameters: Optional[Dict[str, Any]] = None


class ArkToolResponse(BaseModel):
    status_code: Optional[int] = None
    data: Optional[Any] = None
