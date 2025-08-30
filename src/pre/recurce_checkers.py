from typing import List, Set
from common import Common

# fmt: off
from pglast.ast import SelectStmt, JoinExpr, ResTarget, ColumnRef, A_Star, RangeVar, SubLink, Node, Alias, A_Expr

MAX_PARAMS_IN_IN = 2

class RecurseCheckers(Common):
    def __init__(self, recs) -> None:
        super().__init__()
        self.recs: List[str] = recs

    # КОРЕЛЛИРОВАННЫЕ
    def _find_correlation(self, val, inner_names: Set[str]):
        def callback(node):
            if isinstance(node, ColumnRef):
                name = getattr(node.fields[0], "sval", None)
                # print(inner_names, name, node)
                if name in inner_names:
                    self.recs.append(
                        f"Коррелированный подзапрос. Включает в себя {name}, используйте JOIN"
                    )

        if len(inner_names) > 0:
            self._recurse(val, callback)

    def _many_params_in_IN(self, val):
        def callback(node):
            if isinstance(node, A_Expr):
                rexpr = node.rexpr
                if rexpr:
                    rexpr_list = rexpr if isinstance(rexpr, (tuple, list)) else [rexpr]
                    if len(rexpr_list) > MAX_PARAMS_IN_IN:
                        self.recs.append(
                            f"Не используйте большое кол-во аргументов внутри IN. Сейчас ограничение {MAX_PARAMS_IN_IN}. Используйте CTE"
                        )

        self._recurse(val, callback)
