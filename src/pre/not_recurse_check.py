from typing import List, Set
from pglast.ast import ResTarget, ColumnRef, A_Star, RangeVar, Alias
import src.pre.recommendations as recommendations


class NotRecourseCheck:
    def __init__(self, recs: List):
        self.recs = recs

    def star(self, table, val):
        targetList = getattr(val, "targetList", None)
        if targetList:
            for t in targetList:
                if isinstance(t, ResTarget):
                    val = t.val
                    if isinstance(val, ColumnRef):
                        self._columnRef_star_check(val, table)

    def many_table_from(self, mutable_props, inner_names, val):
        fromClause = getattr(val, "fromClause", None)
        if fromClause:
            for f in fromClause:
                if isinstance(f, RangeVar):
                    mutable_props["froms"] += 1
                    mutable_props["table"] = self._selector_check(f, inner_names)

    def _columnRef_star_check(self, val: ResTarget, table: str):
        print("VALUES,", val, table)
        fields = val.fields
        for field in fields:
            if isinstance(field, A_Star):
                self.recs.append(recommendations.select_star(table))

    def _selector_check(self, f: RangeVar, inner_name: Set[str]):
        if f.alias:
            alias = f.alias
            if isinstance(alias, Alias):
                inner_name.add(alias.aliasname)
        else:
            inner_name.add(f.relname)
        return f.relname
