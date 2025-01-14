from importlib import metadata

from ark import core, launcher

__all__ = ["core", "launcher"]

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
