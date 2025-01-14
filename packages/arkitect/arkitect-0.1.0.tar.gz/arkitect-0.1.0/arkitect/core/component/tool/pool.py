from typing import Dict, List, Optional

from .manifest import ToolManifest


def tool_key(action_name: str, tool_name: str) -> str:
    return action_name + "/" + tool_name


class ToolPool:
    _tools: Dict[str, ToolManifest] = {}

    @classmethod
    def register(cls, tm: ToolManifest) -> None:
        if not tm:
            return

        cls._tools[tool_key(tm.action_name, tm.tool_name)] = tm

    @classmethod
    def all(cls, tool_names: Optional[List[str]] = None) -> Dict[str, ToolManifest]:
        """ """
        if not tool_names:
            return cls._tools

        return {name: tm for name, tm in cls._tools.items() if name in tool_names}

    @classmethod
    def get(cls, action_name: str, tool_name: str) -> Optional[ToolManifest]:
        """ """
        return cls._tools.get(tool_key(action_name, tool_name))
