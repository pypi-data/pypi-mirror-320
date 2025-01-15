from .typing import Any


def if_none(value: Any, default: Any):
    return default if value is None else value
