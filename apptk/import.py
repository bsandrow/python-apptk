"""Utilities related to importing Python packages."""

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any, Callable, Generator, Optional, Union

PackageArg = Union[ModuleType, str]
FilterArg = Callable[[Any], bool]
ModuleGenerator = Generator[ModuleType]
ImportedNamespace = dict[str, Any]
BaseClassArg = Optional[Union[type, tuple]]


def iter_submodules(package: PackageArg, recursive: bool = False) -> ModuleGenerator:
    """
    Return a generator that iterates over the submodules found for a particular package.

    This is useful for automatically collecting all submodules of a package to
    perform some sort of action on each module found.  This is the base
    component needed for more advanced functionality such as collecting all
    classes that subclass a particular class in the submodules.

    :param recursive: (optional) Controls whether or not to descend into any
        subpackages found. Defaults to False.
    """

    if isinstance(package, str):
        package = importlib.import_module(package)

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
        try:
            submodule = importlib.import_module(name)
            yield submodule
        except ModuleNotFoundError:
            continue

        if recursive and is_pkg:
            for _submodule in iter_submodules(submodule, recursive=True):
                yield _submodule


def import_all_from_submodules(
    package: PackageArg, filter: FilterArg = None, recursive: bool = False
) -> ImportedNamespace:
    """
    Emulate the functionality "from MODULE import *".

    Returns all of the (name, object) pairs as a dictionary.  To truely emulate
    the import behaviour just pass this dictionary to globals() after you run it::

        namespace = import_all_from_submodule("mypackage.commands")
        globals().update(namespace)

    :param package: A direct reference to the package or a string specifying the name of the package.
    :param recursive: (optional) Control whether or not to descend into subpackages that are found. Defaults to False.
    :param filter: (optional) A filter to apply to all items being imported. Defaults to no filter.
    """
    namespace = {}

    for submodule in iter_submodules(package=package, recursive=recursive):
        try:
            keys = submodule.__dict__["__all__"]
        except KeyError:
            keys = [key for key in submodule.__dict__ if not key.startswith("_")]

        namespace.update(
            {
                name: value
                for name, value in zip(keys, [getattr(submodule, name) for name in keys])
                if filter is None or filter(value)
            }
        )

    return namespace


def import_subclasses_from_submodules(
    package: PackageArg, base_class: BaseClassArg, recursive: bool = False
) -> ImportedNamespace:
    """
    Import all subclasses of base_class in the submodules under a package.

    :param package: A direct reference to the package or a string specifying the name of the package.
    :param base_class: The base class to filter all items in submodules by.
    :param recursive: (optional) Control whether or not to descend into subpackages that are found. Defaults to False.
    """
    return import_all_from_submodules(
        package=package,
        filter=lambda x: inspect.isclass(x) and issubclass(x, base_class),
        recursive=recursive,
    )
