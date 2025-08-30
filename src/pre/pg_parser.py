from typing import List, Set
from pglast import parse_sql
from pglast.ast import RawStmt, SelectStmt

# ЕСЛИ ЗАПУСКАТЬ ИЗ main
# from src.pre.common import Common
from common import Common
from recurce_checkers import RecurseCheckers

# fmt: off
from pglast.ast import SelectStmt, JoinExpr, ResTarget, ColumnRef, A_Star, RangeVar, SubLink, Alias


class PgParser(Common):
    def __init__(self):
        self.recs: List[str] = []
        self.outer_names: Set[str] = set()
        self.recurceCheckers = RecurseCheckers(self.recs)

    def getRecommendations(self, val):
        # print(val)
        def callback(val):
            if isinstance(val, SelectStmt):
                self.outer_names.update(self._checkRecommendations(val, self.outer_names))

        self._recurse(val, callback)
        return self.recs

    def _checkRecommendations(self, stmt: SelectStmt, outer_names: Set[str] = set()):
        # Количество таблиц в FROM
        inner_names: Set[str] = set()
        froms = 0

        # self._recurseCheck(stmt)

        fromClause = getattr(stmt, "fromClause", None)
        if fromClause:
            for f in fromClause:
                # НЕСКОЛЬКО ТАБЛИЦ В FROM
                if isinstance(f, RangeVar):
                    self._selectorCheck(f, inner_names, froms)

            # ПРОВЕРКА JOIN
            if isinstance(f, JoinExpr):
                self._crossJoinCheck(f)

        targetList = getattr(stmt, "targetList", None)
        if targetList:
            for t in targetList:
                if isinstance(t, ResTarget):
                    val = t.val
                    # if isinstance(val, SubLink):
                    #     subSelect = val.subselect
                    #     for node in subSelect:
                    #         attr = getattr(subSelect, node, None)
                    #         if attr:
                    #             self.recurceCheckers._find_correlation(attr, inner_names)
                    if isinstance(val, ColumnRef):
                        self._columnRefStarCheck(val)

        self.recurceCheckers._find_correlation(stmt, outer_names)
        self.recurceCheckers._many_params_in_IN(stmt)

        if froms > 1:
            self.recs.append("Несколько таблиц в from")
        # print(inner_name, outer_names)

        return inner_names | outer_names


    # * IN SELECT
    def _columnRefStarCheck(self, val: ColumnRef):
        fields = val.fields
        for field in fields:
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

    # CROSS JOIN
    def _crossJoinCheck(self, f: JoinExpr):
        join_type = f.jointype
        quals = getattr(f, "quals", None)
        if join_type == 0 and quals == None:
            self.recs.append("CROSS JOIN")

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
SELECT department_id, name
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.department_id  -- d.department_id из внешнего запроса
      AND e.salary > 50000
);
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
# МНОГО КОРЕЛЯЦИЙ
# sql = """
# SELECT
#     c.customer_id,
#     c.name,
#     (
#         SELECT COUNT(*)
#         FROM orders o
#         WHERE o.customer_id = c.customer_id
#     ) AS orders_count,
#     (
#         SELECT SUM(oi.quantity)
#         FROM order_items oi
#         WHERE oi.order_id IN (
#             SELECT o2.order_id
#             FROM orders o2
#             WHERE o2.customer_id = c.customer_id
#         )
#     ) AS total_items,
#     (
#         SELECT AVG(p.price)
#         FROM products p
#         WHERE p.product_id IN (
#             SELECT oi2.product_id
#             FROM order_items oi2
#             WHERE oi2.order_id IN (
#                 SELECT o3.order_id
#                 FROM orders o3
#                 WHERE o3.customer_id = c.customer_id
#             )
#         )
#     ) AS avg_product_price
# FROM customers c;
# """
