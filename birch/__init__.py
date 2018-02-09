"""Utilities for pandas."""

from .core import Birch  # noqa: F401

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

for name in ['get_versions', '_version', 'core', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
