from typing import Any, Callable
from pglast.ast import Node

class Common:
    def _recurse(self, val, callback: Callable[[Any], None]):
        callback(val)

        if isinstance(val, Node):
            for i in val:
                inside = getattr(val, i, None)
                if inside:
                    self._recurse(inside, callback)
        elif isinstance(val, tuple):
            for inside in val:
                self._recurse(inside, callback)
