import datetime
import functools


@functools.cache
def start_time() -> datetime.datetime:
    return datetime.datetime.now()  # noqa: DTZ005
