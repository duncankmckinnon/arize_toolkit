from importlib.metadata import version, PackageNotFoundError

from arize_toolkit.client import Client

try:
    # Single-source the version from pyproject.toml / installed metadata
    __version__: str = version(__name__)
except PackageNotFoundError:
    # Package is not installed – fallback during local dev
    __version__ = "0.0.0"

__all__ = ["Client", "__version__"]
