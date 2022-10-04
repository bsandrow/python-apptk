"""Miscellaneous Utilities"""

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
