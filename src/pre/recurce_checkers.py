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
    
    def push_to_recs(self, issue):
        if len(self.recs):
            if not any(rec["problem"] == issue["problem"] and rec["recommendation"] == issue["recommendation"] for rec in self.recs):
                self.recs.append(issue)
        else:
            self.recs.append(issue)

    # КОРЕЛЛИРОВАННЫЕ
    def _find_correlation(self, val, inner_names: Set[str]):
        def callback(node):
            if isinstance(node, ColumnRef):
                name = getattr(node.fields[0], "sval", None)
                # print(inner_names, name, node)
                if name in inner_names:
                    self.push_to_recs(recommendations.correlated_subquery(name))

        if len(inner_names) > 0:
            self.recurse_without_subquery(val, callback)

    def _many_params_in_IN(self, val):
        def callback(node):
            if isinstance(node, A_Expr):
                rexpr = node.rexpr
                if rexpr:
                    rexpr_list = rexpr if isinstance(rexpr, (tuple, list)) else [rexpr]
                    if len(rexpr_list) > MAX_PARAMS_IN_IN:
                        self.push_to_recs(recommendations.big_in_list(MAX_PARAMS_IN_IN))

        self.recurse(val, callback)
        
    # CROSS JOIN
    def _crossJoinCheck(self, val):
        def callback(node):
            if isinstance(node, JoinExpr):
                # print(node)
                join_type = node.jointype
                quals = getattr(node, "quals", None)
                if join_type == 0 and quals is None:
                    self.push_to_recs(recommendations.cross_join_usage)

        self.recurse_without_subquery(val, callback)

    def _subquery_in_IN(self, val):
        def callback(node):
            if isinstance(node, SubLink) and node.subLinkType == SubLinkType.ANY_SUBLINK and node.subselect is not None:
                self.push_to_recs(recommendations.in_subquery)
        
        self.recurse_without_subquery(val, callback)

    def _func_in_where_having(self, val, where):
        def callback(node):
            if isinstance(node, FuncCall):
                self.push_to_recs(recommendations.function_in_where_having(where))

        self.recurse_without_subquery(val, callback)