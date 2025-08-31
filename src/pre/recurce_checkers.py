from typing import List, Set
from src.pre.common import Common

# fmt: off
from pglast.ast import ColumnRef, A_Expr, JoinExpr, SubLink
from pglast.enums import SubLinkType
from src.types.types import AnalysisResult

MAX_PARAMS_IN_IN = 2

class RecurseCheckers(Common):
	def __init__(self, recs) -> None:
		super().__init__()
		self.recs: AnalysisResult = recs

	# КОРЕЛЛИРОВАННЫЕ
	def _find_correlation(self, val, inner_names: Set[str]):
		def callback(node):
			if isinstance(node, ColumnRef):
				name = getattr(node.fields[0], "sval", None)
				# print(inner_names, name, node)
				if name in inner_names:
					self.recs["issues"].append(
						f"Коррелированный подзапрос. Включает в себя {name}, используйте JOIN"
					)

		if len(inner_names) > 0:
			self._recurse_without_subquery(val, callback)

	def _many_params_in_IN(self, val):
		def callback(node):
			if isinstance(node, A_Expr):
				rexpr = node.rexpr
				if rexpr:
					rexpr_list = rexpr if isinstance(rexpr, (tuple, list)) else [rexpr]
					if len(rexpr_list) > MAX_PARAMS_IN_IN:
						self.recs["issues"].append(
							f"Не используйте большое кол-во аргументов внутри IN. Сейчас ограничение {MAX_PARAMS_IN_IN}. Используйте CTE"
						)

		self._recurse(val, callback)
		
	# CROSS JOIN
	def _crossJoinCheck(self, val):
		def callback(node):
			if isinstance(node, JoinExpr):
				print(node)
				join_type = node.jointype
				quals = getattr(node, "quals", None)
				if join_type == 0 and quals is None:
					self.recs["issues"].append("CROSS JOIN")

		self._recurse_without_subquery(val, callback)

	def _subquery_in_IN(self, val):
		def callback(node):
			if isinstance(node, SubLink) and node.subLinkType == SubLinkType.ANY_SUBLINK and node.subselect is not None:
				self.recs["issues"].append("IN с подзапросом")
		
		self._recurse_without_subquery(val, callback)
