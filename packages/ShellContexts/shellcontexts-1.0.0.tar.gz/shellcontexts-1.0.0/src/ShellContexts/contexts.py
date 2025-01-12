import os

from .base import ModificationContext

class chdir(ModificationContext):
    """Set the process's cwd."""

    def _apply(self):
        old_cwd = os.getcwd()
        os.chdir(self._applied_value)
        return old_cwd

    def _revert(self, previous_value):
        os.chdir(previous_value)

class set_umask(ModificationContext):
    """Set the process's umask."""

    def _apply(self):
        return os.umask(self._applied_value)

    def _revert(self, previous_value):
        os.umask(previous_value)

class increase_umask(ModificationContext):
    """\
    Increase the process's umask.

    That is perform a bitwise union of the context's value with the existing umask.
    """

    def _apply(self):
        old_mask = os.umask(0)
        new_mask = old_mask | self._applied_value
        os.umask(new_mask)
        return old_mask

    def _revert(self, previous_value):
        os.umask(previous_value)

class decrease_umask(ModificationContext):
    """\
    Decrease the process's umask.

    That is perform a bitwise exclusion of the context's value with the existing umask.
    """

    def _apply(self):
        old_mask = os.umask(0)
        new_mask = old_mask & ~self._applied_value
        os.umask(new_mask)
        return old_mask

    def _revert(self, previous_value):
        os.umask(previous_value)

class seteuid(ModificationContext):
    """Set the process's effective user id."""

    def _apply(self):
        old_euid = os.geteuid()
        os.seteuid(self._applied_value)
        return old_euid

    def _revert(self, previous_value):
        os.seteuid(previous_value)

class setegid(ModificationContext):
    """Set the process's effective group id."""

    def _apply(self):
        old_egid = os.getegid()
        os.setegid(self._applied_value)
        return old_egid

    def _revert(self, previous_value):
        os.setegid(previous_value)
