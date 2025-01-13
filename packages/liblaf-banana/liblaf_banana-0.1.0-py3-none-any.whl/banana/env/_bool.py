import functools
import os

import pydantic


def get_bool(key: str, default: bool = False) -> bool:  # noqa: FBT001, FBT002
    if val := os.getenv(key):
        return adapter(bool).validate_strings(val)
    return default


@functools.cache
def adapter(t: type) -> pydantic.TypeAdapter:
    return pydantic.TypeAdapter(t)
