"""Function- / Functional-related utilities."""

__all__ = ["cached_property"]

# noinspection PyPep8Naming
class _cached_property:
    """
    A @property that caches the returned value.

    Grabbed from django utils.
    """

    name = None

    @staticmethod
    def function(instance):
        raise TypeError("Cannot use cached_property instance without calling " "__set_name__() on it.")

    # noinspection PyUnusedLocal
    def __init__(self, function, name=None):
        self.original_function = function
        self.__doc__ = getattr(function, "__doc__")

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.function = self.original_function
        elif name != self.name:
            raise TypeError(
                "Cannot assign the same cached_property to two different names " "(%r and %r)." % (self.name, name)
            )

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        result = instance.__dict__[self.name] = self.function(instance)
        return result


#
# Use Python's standard cached_property if this is Python 3.8 or greater,
# otherwise fallback on Django's cached_property. If that doesn't work (e.g.
# Django isn't installed), use this implementation.
#
try:
    from functools import cached_property
except ImportError:
    cached_property = _cached_property
