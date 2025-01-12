from contextlib import AbstractContextManager

class ModificationContext(AbstractContextManager):
    """
    An abstract base class for context managers designed to change a state
    or attribute to `value` on entry and revert it on exit.

    Designed to be reentry safe.
    """

    def __init__(self, value):
        self._applied_value = value
        self._values = []

    @property
    def applied_value(self):
        """
        Property to get the value that the context manager applies when active
        """
        return self._applied_value

    def __repr__(self):
        return f"{type(self).__qualname__}({self._applied_value!r})"

    def __enter__(self):
        self._values.append(self._apply())
        return self._applied_value

    def __exit__(self, *exc_info):
        self._revert(self._values.pop())

    def _apply(self):
        """
        Context managers inheriting this class should set the state
        to `_applied_value` in this function, and must return the old value
        that will be restored on exit.
        """
        raise NotImplementedError("must be implemented in subclass")

    def _revert(self, previous_value):
        """
        Context managers inheriting this class should restore the state
        to `previous_value` in this function.
        """
        raise NotImplementedError("must be implemented in subclass")
