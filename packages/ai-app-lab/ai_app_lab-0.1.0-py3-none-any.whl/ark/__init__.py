from importlib import metadata

from ark import component, core
from ark.core import idl, launcher

__all__ = ["core", "component", "idl", "launcher"]

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
