from typing import Any, Callable
from pglast.ast import Node, SubLink


class Common:
	def recurse(self, val, callback: Callable[[Any], None]):
		callback(val)

		if isinstance(val, Node):
			for i in val:
				inside = getattr(val, i, None)
				if inside:
					self.recurse(inside, callback)
		elif isinstance(val, tuple):
			for inside in val:
				self.recurse(inside, callback)

	# TODO: ДУБЛИРОВАНИЕ ПОТОМ УБРАТЬ
	def recurse_without_subquery(self, val, callback: Callable[[Any], None]):
		callback(val)

		if isinstance(val, Node):
			if not isinstance(val, SubLink):
				for i in val:
					inside = getattr(val, i, None)
					if inside:
						self.recurse_without_subquery(inside, callback)

		elif isinstance(val, tuple):
			for inside in val:
				self.recurse_without_subquery(inside, callback)

