import os
from typing import overload


@overload
def get_str(key: str) -> str | None: ...
@overload
def get_str(key: str, default: str) -> str: ...
def get_str(key: str, default: str | None = None) -> str | None:
    return os.getenv(key, default)
