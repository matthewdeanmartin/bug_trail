"""
Another module to avoid Circular Import
"""
import datetime
from types import NoneType
from typing import Any, Optional, Union

SqliteTypes = Union[None, int, float, str, bytes, datetime.date, datetime.datetime]


def serialize_to_sqlite_supported(value: Optional[Any]) -> SqliteTypes:
    """
    sqlite supports None, int, float, str, bytes by default, and also knows how to adapt datetime.date and datetime.datetime
    everything else is str(value)
    >>> serialize_to_sqlite_supported(1)
    1
    >>> serialize_to_sqlite_supported(1.0)
    1.0
    """
    if isinstance(value, NoneType):
        return None
    if isinstance(value, (int, float, str, bytes)):
        return value
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value
    return str(value)
