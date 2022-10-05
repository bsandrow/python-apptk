import datetime
import re
from typing import Union

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

    # TODO deal with optionally pulling in dateutil
    # if isinstance(datetime_in, str):
    #     return dt_parser.parse(datetime_in)

    if isinstance(datetime_in, datetime.date) and isinstance(datetime_in, datetime.datetime):
        return datetime.datetime(datetime_in)

    if isinstance(datetime_in, datetime.datetime):
        return datetime_in

    raise ValueError(f"Unknown datetime input type: {type(datetime_in)}")
