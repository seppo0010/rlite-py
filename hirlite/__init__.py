import functools

from hirlite.hirlite import Rlite as RliteExtension, HirliteError
from hirlite.version import __version__

__all__ = ["Rlite", "HirliteError", "__version__"]


class Rlite(RliteExtension):
    def __getattr__(self, command):
        return functools.partial(self.command, command)
