"""Utilities related to importing Python packages."""

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any, Callable, Generator, Optional, Union

PackageArg = Union[ModuleType, str]
FilterArg = Callable[[Any], bool]
ModuleGenerator = Generator[ModuleType, None, None]
ImportedNamespace = dict[str, Any]
BaseClassArg = Optional[Union[type, tuple]]


def calculate_depth(name: str, base_pkg: str | None = None):
    """
    Calculate the depth of a Python package.

    Calculate how many packages deep a package is.  If a base package is
    provided, then the depth is calculated starting at the level of that
    package (so long as the package is a sub-package of the base package).
    """
    base_depth: int = len(base_pkg.split(".")) if base_pkg and name.startswith(base_pkg) else 0
    pkg_depth: int = len(name.split("."))
    return pkg_depth - base_depth


def iter_submodules(package: PackageArg, maxdepth: int | None = 1) -> ModuleGenerator:
    """
    Return a generator that iterates over the submodules found for a particular package.

    This is useful for automatically collecting all submodules of a package to
    perform some sort of action on each module found.  This is the base
    component needed for more advanced functionality such as collecting all
    classes that subclass a particular class in the submodules.

    :param maxdepth: (optional) Controls how deep into packages to iterate.  Defaults to 1 - only iterating over the top-level of modules / packages.
    """

    if isinstance(package, str):
        package = importlib.import_module(package)

    for _, name, _ in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
        depth = calculate_depth(name, base_pkg=package.__name__)
        if depth > maxdepth:
            continue

        try:
            submodule = importlib.import_module(name)
            yield submodule
        except ModuleNotFoundError:
            continue


def import_all_from_submodules(
    package: PackageArg, filter: FilterArg = None, maxdepth: int | None = 1
) -> ImportedNamespace:
    """
    Emulate the functionality "from MODULE import *".

    Returns all of the (name, object) pairs as a dictionary.  To truely emulate
    the import behaviour just pass this dictionary to globals() after you run it::

        namespace = import_all_from_submodule("mypackage.commands")
        globals().update(namespace)

    :param package: A direct reference to the package or a string specifying the name of the package.
    :param filter: (optional) A filter to apply to all items being imported. Defaults to no filter.
    :param maxdepth: (optional) The maximum depth to parse into. Defaults to 1.
    """
    namespace = {}

    for submodule in iter_submodules(package=package, maxdepth=maxdepth):
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
    package: PackageArg, base_class: BaseClassArg, maxdepth: int | None = 1
) -> ImportedNamespace:
    """
    Import all subclasses of base_class in the submodules under a package.

    :param package: A direct reference to the package or a string specifying the name of the package.
    :param base_class: The base class to filter all items in submodules by.
    :param maxdepth: (optional) Control the maximum depth to parse into package structure. Defaults to 1.
    """
    return import_all_from_submodules(
        package=package,
        filter=lambda x: inspect.isclass(x) and issubclass(x, base_class),
        maxdepth=maxdepth,
    )
