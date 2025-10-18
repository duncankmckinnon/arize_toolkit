from importlib.metadata import PackageNotFoundError, version

from arize_toolkit.async_client import Client as AsyncClient
from arize_toolkit.client import Client

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["Client", "AsyncClient", "__version__"]
