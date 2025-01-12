"""ShellContexts"""

__version__ = "1.0.0"

from .base import ModificationContext
from .contexts import (
    chdir, set_umask, increase_umask, decrease_umask, seteuid, setegid
)

__all__ = [
    "ModificationContext",
    "chdir",
    "set_umask", "increase_umask", "decrease_umask",
    "seteuid", "setegid",
]
