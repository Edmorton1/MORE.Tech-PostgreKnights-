from typing import List, Set
from pglast import parse_sql
from pglast.ast import RawStmt, SelectStmt

# fmt: off
from pglast.ast import SelectStmt, JoinExpr, ResTarget, ColumnRef, A_Star, RangeVar, SubLink, Node, Alias, A_Expr

MAX_PARAMS_IN_IN = 2

class PgParser:
    def __init__(self):
        self.recs: List[str] = []
        self.outer_names: Set[str] = set()

    def getRecommendations(self, val):
        # print(val)
        self._recurseCheck(val)
        return self.recs

    # РЕКУРСИЯ ВСЕХ SELECT
    def _recurseCheck(self, val):
        if isinstance(val, SelectStmt):
            self.outer_names.update(self._checkRecommendations(val, self.outer_names))
            for i in val:
                inside = getattr(val, i, None)
                if inside:
                    self._recurseCheck(inside)

        elif isinstance(val, Node):
            for i in val:
                inside = getattr(val, i, None)
                if inside:
                    self._recurseCheck(inside)
        elif isinstance(val, tuple):
            for inside in val:
                self._recurseCheck(inside)

    def _checkRecommendations(self, stmt: SelectStmt, outer_names: Set[str] = set()):
        # Количество таблиц в FROM
        inner_name: Set[str] = set()
        froms = 0

        # self._recurseCheck(stmt)

        fromClause = getattr(stmt, "fromClause", None) or ()
        for f in fromClause:
            # НЕСКОЛЬКО ТАБЛИЦ В FROM
            if isinstance(f, RangeVar):
                self._selectorCheck(f, inner_name, froms)

            # ПРОВЕРКА JOIN
            if isinstance(f, JoinExpr):
                self._crossJoinCheck(f)

        targetList = getattr(stmt, "targetList", None) or ()
        for t in targetList:
            if isinstance(t, ResTarget):
                val = t.val
                if isinstance(val, SubLink):
                    subSelect = val.subselect
                    for node in subSelect:
                        attr = getattr(subSelect, node, None)
                        if attr:
                            self._find_columnRef(attr, inner_name)
                if isinstance(val, ColumnRef):
                    self._columnRefStarCheck(val)

        whereClause = getattr(stmt, "whereClause", None) or ()
        rexpr = getattr(whereClause, "rexpr", None)
        if rexpr and len(rexpr) > MAX_PARAMS_IN_IN:
            self.recs.append(f"Не используйте большое кол-во аргументов внутри IN. Сейчас ограничение {MAX_PARAMS_IN_IN}. Используйте CTE")

        if froms > 1:
            self.recs.append("Несколько таблиц в from")
        # print(inner_name, outer_names)

        return inner_name | outer_names

    def _columnRefStarCheck(self, val: ColumnRef):
        fields = val.fields
        # print("fields", fields)
        for field in fields:
            # ПРОВЕРКА НА *
            if isinstance(field, A_Star):
                self.recs.append("Используется *")

    def _selectorCheck(self, f: RangeVar, inner_name: Set[str], froms: int):
        if f.alias:
            alias = f.alias
            if isinstance(alias, Alias):
                inner_name.add(alias.aliasname)
        elif f.relname:
            inner_name.add(f.relname)
        froms += 1

    def _crossJoinCheck(self, f: JoinExpr):
        join_type = f.jointype
        quals = getattr(f, "quals", None)
        if join_type == 0 and quals == None:
            self.recs.append("CROSS JOIN")

    # КОРЕЛЛИРОВАННЫЕ
    def _find_columnRef(self, attr, outer_names: Set[str]):
        if isinstance(attr, ColumnRef):
            name = getattr(attr.fields[0], "sval")
            if name in outer_names:
                self.recs.append(
                    f"Коррелированный подзапрос. Включает в себя {name}, используйте JOIN"
                )
        elif isinstance(attr, Node):
            for i in attr:
                attr_inside = getattr(attr, i, None)
                if attr_inside:
                    self._find_columnRef(attr_inside, outer_names)
        elif isinstance(attr, tuple):
            for attr_inside in attr:
                self._find_columnRef(attr_inside, outer_names)


# --- НОРМ
# sql = "SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id"
# --- CROSS JOIN
# sql = "SELECT * FROM users CROSS JOIN orders"
# --- Коррелированные подзапросы
# sql = """
# SELECT e.employee_id,
#        e.name,
#        d.budget AS dept_budget,
#        COUNT(p.project_id) AS project_count
# FROM employees e
# JOIN departments d ON d.department_id = e.department_id
# LEFT JOIN projects p ON p.manager_id = e.employee_id
# GROUP BY e.employee_id, e.name, d.budget;
# """
# --- НЕСКОЛЬКО ТАБЛИЦ
# sql = "SELECT * FROM users, orders"
# --- ЕЩЁ НА КОРРЕЛИРОВАНИЕ
# sql = """
# SELECT e.employee_id,
#        e.name,
#        d.budget AS dept_budget,
#        COUNT(p.project_id) AS project_count
# FROM employees e
# JOIN departments d ON d.department_id = e.department_id
# LEFT JOIN projects p ON p.manager_id = e.employee_id
# GROUP BY e.employee_id, e.name, d.budget;
# """
# Много в IN
sql = """
SELECT *
FROM employees
WHERE employee_id IN (101, 102, 103);
"""

ast_tree: List[RawStmt] = parse_sql(sql)
stmt: SelectStmt = ast_tree[0].stmt

asd = PgParser()

print(asd.getRecommendations(stmt))

# WITH ids(id) AS (
#     VALUES (101), (102), (103)
# )
# SELECT e.*
# FROM employees e
# JOIN ids i ON e.employee_id = i.id;

# --- CTE
# sql = """
# WITH ids(id) AS (
#     VALUES (101), (102), (103)
# )
# SELECT e.*
# FROM employees e
# JOIN ids i ON e.employee_id = i.id;
# """
