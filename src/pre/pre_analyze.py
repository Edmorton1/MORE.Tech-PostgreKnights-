from typing import List, Set
from pglast import parse_sql

# from pglast.stream import IndentedStream
from src.pre.types import MutableProps
from src.pre.common import Common
from src.pre.recurse_check import RecurseCheckers
from pglast.ast import RawStmt, SelectStmt
from src.types.types import AnalysisIssue
import src.pre.recommendations as recommendations
from src.pre.not_recurse_check import NotRecourseCheck


class PreAnalyze(Common):
    def __init__(self):
        self.recs: List[AnalysisIssue] = []
        self.outer_names: Set[str] = set()
        self.recurseCheckers = RecurseCheckers(self.recs)
        self.notRecurseCheck = NotRecourseCheck(self.recs)

    def getRecommendations(self, query: str):
        ast_tree: List[RawStmt] = parse_sql(query)
        stmt: SelectStmt = ast_tree[0].stmt
        print("STMT", stmt)
        # sql_back = IndentedStream()(stmt).replace("\n", " ")
        # return sql_back

        def callback(val: object):
            if isinstance(val, SelectStmt):
                self.outer_names.update(
                    self._checkRecommendations(val, self.outer_names)
                )

        self.recurse(stmt, callback)
        return self.recs

    def _checkRecommendations(self, stmt: SelectStmt, outer_names: Set[str] = set()):
        inner_names: Set[str] = set()
        mutable_props: MutableProps = {"froms": 0, "table": None}

        self.notRecurseCheck.many_table_from(mutable_props, inner_names, stmt)
        self.notRecurseCheck.star(mutable_props["table"], stmt)
        self.recurseCheckers.func_in_where_having(stmt)
        self.recurseCheckers.find_correlation(stmt, outer_names)
        self.recurseCheckers.many_params_in_IN(stmt)
        self.recurseCheckers.crossJoinCheck(stmt)
        self.recurseCheckers.subquery_in_IN(stmt)

        print("FROMS", mutable_props["froms"])
        if mutable_props["froms"] > 1:
            print(mutable_props["table"])
            self.recs.append(recommendations.cross_join_multiple_tables)
        # print(inner_name, outer_names)

        return inner_names | outer_names
