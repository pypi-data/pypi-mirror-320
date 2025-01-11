from .client import Audiomatic

try:
    from importlib.metadata import version
    __version__ = version("audiomatic")
except ImportError:
    __version__ = "unknown"