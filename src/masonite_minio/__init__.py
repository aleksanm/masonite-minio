from importlib.metadata import PackageNotFoundError, version

from .MinioDriver import MinioDriver
from .MinioProvider import MinioProvider

try:
    # Single source of truth is the [project] version in pyproject.toml, read
    # back from the installed distribution metadata.
    __version__ = version("masonite-minio")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+unknown"

__all__ = ["MinioDriver", "MinioProvider", "__version__"]
