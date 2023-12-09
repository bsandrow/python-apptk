import datetime
import re
from typing import Union

try:
    from dateutil.parser import parse as dt_parse
except ImportError:
    dt_parse = None

DatetimeType = Union[str, datetime.datetime, datetime.date, int, float]
PatternType = Union[str, re.Pattern]


def to_pattern(pattern: PatternType) -> re.Pattern:
    return pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)


def to_dataclass(value, dataclass):
    if isinstance(value, dataclass):
        return value
    if isinstance(value, dict):
        return dataclass(**value)
    raise ValueError(f"Not an instance of {dataclass} or dict: {value}")


def to_datetime(datetime_in: DatetimeType) -> datetime.datetime:
    if isinstance(datetime_in, (int, float)):
        return datetime.datetime.utcfromtimestamp(datetime_in)

    if isinstance(datetime_in, str):
        return dt_parse(datetime_in) if dt_parse else datetime.datetime.fromisoformat(datetime_in)

    if isinstance(datetime_in, datetime.datetime):
        return datetime_in

    # note: order is important because datetime instances are also date
    # instances, but date instances are not datetime instances.
    if isinstance(datetime_in, datetime.date):
        return datetime.datetime.combine(datetime_in, datetime.datetime.min.time())

    raise ValueError(f"Unknown datetime input type: {type(datetime_in)}")
