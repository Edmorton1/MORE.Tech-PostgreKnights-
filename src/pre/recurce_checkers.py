from typing import List, Set
from src.common.common import Common

# fmt: off
from pglast.ast import ColumnRef, A_Expr, JoinExpr, SubLink, FuncCall
from pglast.enums import SubLinkType
from src.types.types import AnalysisResult
import src.pre.recommendations as recommendations

MAX_PARAMS_IN_IN = 2

class RecurseCheckers(Common):
    def __init__(self, recs: List) -> None:
        super().__init__()
        self.recs = recs

    # КОРЕЛЛИРОВАННЫЕ
    def _find_correlation(self, val, inner_names: Set[str]):
        def callback(node):
            if isinstance(node, ColumnRef):
                name = getattr(node.fields[0], "sval", None)
                # print(inner_names, name, node)
                if name in inner_names:
                    self.recs.append(recommendations.correlated_subquery(name))

        if len(inner_names) > 0:
            self.recurse_without_subquery(val, callback)

    def _many_params_in_IN(self, val):
        def callback(node):
            if isinstance(node, A_Expr):
                rexpr = node.rexpr
                if rexpr:
                    rexpr_list = rexpr if isinstance(rexpr, (tuple, list)) else [rexpr]
                    if len(rexpr_list) > MAX_PARAMS_IN_IN:
                        self.recs.append(recommendations.big_in_list(MAX_PARAMS_IN_IN))

        self.recurse(val, callback)
        
    # CROSS JOIN
    def _crossJoinCheck(self, val):
        def callback(node):
            if isinstance(node, JoinExpr):
                # print(node)
                join_type = node.jointype
                quals = getattr(node, "quals", None)
                if join_type == 0 and quals is None:
                    self.recs.append(recommendations.cross_join_usage)

        self.recurse_without_subquery(val, callback)

    def _subquery_in_IN(self, val):
        def callback(node):
            if isinstance(node, SubLink) and node.subLinkType == SubLinkType.ANY_SUBLINK and node.subselect is not None:
                self.recs.append(recommendations.in_subquery)
        
        self.recurse_without_subquery(val, callback)

    def _func_in_where_having(self, val, where):
        def callback(node):
            if isinstance(node, FuncCall):
                self.recs.append(recommendations.function_in_where_having(where))

        self.recurse_without_subquery(val, callback)