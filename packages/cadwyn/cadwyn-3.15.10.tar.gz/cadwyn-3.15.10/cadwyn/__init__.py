import importlib.metadata

from .applications import Cadwyn
from .codegen import generate_code_for_versioned_packages
from .route_generation import (
    InternalRepresentationOf,  # pyright: ignore[reportDeprecated]
    VersionedAPIRouter,
    generate_versioned_routers,
)
from .structure import HeadVersion, Version, VersionBundle

__version__ = importlib.metadata.version("cadwyn")
__all__ = [
    "Cadwyn",
    "VersionedAPIRouter",
    "generate_code_for_versioned_packages",
    "VersionBundle",
    "HeadVersion",
    "Version",
    "generate_versioned_routers",
    "InternalRepresentationOf",
]
