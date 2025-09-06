from typing import List, Set
from src.pre.common import Common
from src.types.types import AnalysisIssue

# fmt: off
from pglast.ast import ColumnRef, A_Expr, JoinExpr, SubLink, FuncCall
from pglast.enums import SubLinkType
import src.pre.recommendations as recommendations
from settings import config
from src.common.push_to_recs import push_to_recs

MAX_PARAMS_IN_IN: int = config["MAX_PARAMS_IN_IN"] or 2

class RecurseCheckers(Common):
    def __init__(self, recs: List[AnalysisIssue]) -> None:
        super().__init__()
        self.recs = recs

    def find_correlation(self, val: object, inner_names: Set[str]):
        def callback(node: object):
            if isinstance(node, ColumnRef):
                name = getattr(node.fields[0], "sval", None)
                if name in inner_names:
                    push_to_recs(recommendations.correlated_subquery(name), self.recs)

        if len(inner_names) > 0:
            self.recurse_without_subquery(val, callback)

    def many_params_in_IN(self, val: object):
        def callback(node: object):
            if isinstance(node, A_Expr):
                rexpr = node.rexpr
                if rexpr:
                    rexpr_list = rexpr if isinstance(rexpr, (tuple, list)) else [rexpr]
                    if len(rexpr_list) > MAX_PARAMS_IN_IN:
                        push_to_recs(recommendations.big_in_list(MAX_PARAMS_IN_IN), self.recs)

        self.recurse(val, callback)
        
    def crossJoinCheck(self, val: object):
        def callback(node: object):
            if isinstance(node, JoinExpr):
                join_type = node.jointype
                quals = getattr(node, "quals", None)
                if join_type == 0 and quals is None:
                    push_to_recs(recommendations.cross_join_usage, self.recs)

        self.recurse_without_subquery(val, callback)

    def subquery_in_IN(self, val: object):
        def callback(node: object):
            if isinstance(node, SubLink) and node.subLinkType == SubLinkType.ANY_SUBLINK and node.subselect is not None:
                push_to_recs(recommendations.in_subquery, self.recs)
        
        self.recurse_without_subquery(val, callback)

    def func_in_where_having(self, val: object):
        def callback(node: object):
            if isinstance(node, FuncCall):
                push_to_recs(recommendations.function_in_where_having, self.recs)

        nodes = ["whereClause", "havingClause"]
        for clauseName in nodes:
            clause = getattr(val, clauseName, None)
            if clause:
                self.recurse_without_subquery(val, callback)
