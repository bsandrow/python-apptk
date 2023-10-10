"""Miscellaneous Utilities"""

from collections.abc import Mapping, Sequence
import re
from typing import Any


def slugify(value: Any) -> str:
    """
    Convert a value to a slug-ified string.

    Replace non-alphanumeric characters with -. Also shaves multiple -'s in a row down to
    a single -.

    :param value: A value to be string-ified, then slug-ified.
    """
    value = str(value)
    value = value.lower()
    value = re.sub(r"[^\d\w-]|_", "-", value)
    value = re.sub(r"--+", "-", value)
    value = value.strip("-")
    return value


def get_path(obj: Any, path: str, default: Any = None, path_separator: str = ".") -> Any:
    """
    Return a value from an object specified by a string path.

    Examples::
        >>> dict_1 = {"a": {"b": {"c": 1}, "d": [4, 5, 6]}}
        >>> dummy_obj = object()
        >>> assert get_path(dict_1, "a.b.c") == 1
        >>> assert get_path(dict_1, "a.b.d.1") == 5
        >>> assert get_path(dict_1, "a.b.e", default=dummy_obj) is dummy_obj
        >>> assert get_path(dict_1, "a__b__c", path_separator="__") == 1
        >>> obj_2 = object()
        >>> obj_2.a = {"c": [{"5": dummy_obj}]}
        >>> assert get_path(obj_2, "a.c.0.5") is dummy_obj
        >>> assert get_path(obj_2, "a.does_not_exist") is None

    :param obj:  An object to use path to pull a value from.
    :param path: A string path.
    :param default: (optional) The default value to return if following the path fails. (Default to None)
    :param path_separator: (optional) The separator string to use when breaking the path into parts. (Defaults to '.')
    """

    path_parts = path.split(path_separator)
    value = obj

    for part in path_parts:
        #
        # At this point, there are still path parts to process, but if the value is None then there is no
        # way to continue processing the path deeper. Return the default since path processing needs to prematurely
        # abort.
        #
        if value is None:
            return default

        #
        # If it's a mapping like a dict (i.e. supports __getitem__ / __setitem__ / __contains__), then we check if
        # part is a key in the mapping. If so, we proceed to use the value of that key as the new value, otherwise we
        # return the default value.
        #
        if isinstance(value, Mapping):
            if part in value:
                value = value[part]
            else:
                return default

        #
        # This allows us to support indexing lists (or other Sequences) in the path, by proving an integer. If part
        # cannot be converted to an integer or is an out-of-bound index, we return the default value. Otherwise, we use
        # the value at the index as the new value.
        #
        elif isinstance(value, Sequence):
            try:
                index = int(part)
                value = value[index]
            except (ValueError, IndexError):
                return default

        #
        # If other methods of processing don't apply, then we just treat part as an attribute name and use getattr,
        # returning default if the attribute doesn't exist.
        #
        else:
            try:
                value = getattr(value, part)
            except AttributeError:
                return default

    return value
