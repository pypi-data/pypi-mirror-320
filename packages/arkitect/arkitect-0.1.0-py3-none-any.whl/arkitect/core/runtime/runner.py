import importlib
from typing import AsyncIterable, Callable

from .model import RequestType, ResponseType


def load_function(
    module_name: str, func_name: str
) -> Callable[[RequestType], AsyncIterable[ResponseType]]:
    """
    Loads a function from a specified module.
    """
    package = importlib.import_module(module_name)
    module = getattr(package, func_name)
    return module
