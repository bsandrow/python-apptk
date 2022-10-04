"""File-related Utilities"""

from contextlib import contextmanager
from os import chdir, getcwd
import pathlib
from typing import Union


@contextmanager
def cwd(path: Union[str, pathlib.Path]):
    """
    A context manager around changing the current working directory.

    Allows you to change the working directory temporarily without needing to record the previous working directory
    and switch back manually.
    """
    old_cwd = getcwd()
    chdir(path)
    yield
    chdir(old_cwd)


