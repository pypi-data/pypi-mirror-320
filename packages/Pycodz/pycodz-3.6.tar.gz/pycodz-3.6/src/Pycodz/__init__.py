import g4f
from importlib import metadata
import logging

try:
    __version__ = metadata.version("Pycodz")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "z44d"

tgpt_providers = [
    "ai"
]

gpt4free_providers = [
    provider.__name__ for provider in g4f.Provider.__providers__
]

available_providers = tgpt_providers + gpt4free_providers

__all__ = [
    "appdir"
] + available_providers

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("websocket").setLevel(logging.ERROR)