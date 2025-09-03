from typing import List, Set
from src.types.types import AnalysisIssue
from pglast.ast import ResTarget, ColumnRef, A_Star, RangeVar, Alias
import src.pre.recommendations as recommendations
from src.pre.types import MutableProps


class NotRecourseCheck:
    def __init__(self, recs: List[AnalysisIssue]):
        self.recs = recs

    def star(self, table: str | None, val: object) -> None:
        targetList = getattr(val, "targetList", None)
        if targetList:
            for t in targetList:
                if isinstance(t, ResTarget):
                    target = t.val
                    if isinstance(target, ColumnRef):
                        self._columnRef_star_check(target.fields, table)

    def many_table_from(
        self, mutable_props: MutableProps, inner_names: Set[str], val: object
    ) -> None:
        fromClause = getattr(val, "fromClause", None)
        if fromClause:
            for f in fromClause:
                if isinstance(f, RangeVar):
                    mutable_props["froms"] += 1
                    mutable_props["table"] = self._selector_check(f, inner_names)

    def _columnRef_star_check(self, fields: list[object], table: str) -> None:
        for field in fields:
            if isinstance(field, A_Star):
                self.recs.append(recommendations.select_star(table))

    def _selector_check(self, f: RangeVar, inner_name: Set[str]) -> str:
        if f.alias:
            alias = f.alias
            if isinstance(alias, Alias):
                inner_name.add(alias.aliasname)
        else:
            inner_name.add(f.relname)
        return f.relname
