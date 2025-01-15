"""Package utilities."""

import importlib.metadata


def get_package_name() -> str:
    """Get package name.

    Returns:
        Package name
    """
    return "pepperpy"


def get_package_version() -> str:
    """Get package version.

    Returns:
        Package version
    """
    try:
        return importlib.metadata.version("pepperpy")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"
