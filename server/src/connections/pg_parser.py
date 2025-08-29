from typing import List, Set
from pglast import parse_sql
from pglast.ast import RawStmt, SelectStmt

# fmt: off
from pglast.ast import SelectStmt, JoinExpr, ResTarget, ColumnRef, A_Star, RangeVar, SubLink, Node, Alias


class PgParser:
    def __init__(self):
        self.recs: List[str] = []
        self.outer_names: Set[str] = set()

    def getRecommendations(self, val):
        self._recurseCheck(val)
        return self.recs

    # РЕКУРСИЯ ВСЕХ SELECT
    def _recurseCheck(self, val):
        if isinstance(val, SelectStmt):
            self.outer_names = self._checkRecommendations(val, self.outer_names)
            for i in val:
                inside = getattr(val, i)
                self._recurseCheck(inside)
        elif isinstance(val, Node):
            for i in val:
                inside = getattr(val, i)
                self._recurseCheck(inside)
        elif isinstance(val, tuple):
            for inside in val:
                self._recurseCheck(inside)

    def _checkRecommendations(self, stmt: SelectStmt, outer_names: Set[str] = set()):
        # Количество таблиц в FROM
        inner_name: Set[str] = set()
        froms = 0

        # self._recurseCheck(stmt)

        fromClause = stmt.fromClause
        for f in fromClause:
            # НЕСКОЛЬКО ТАБЛИЦ В FROM
            if isinstance(f, RangeVar):
                self._selectorCheck(f, inner_name, froms)

            # ПРОВЕРКА JOIN
            if isinstance(f, JoinExpr):
                self._crossJoinCheck(f)

        targetList = stmt.targetList
        # print("TargetList", targetList)
        for t in targetList:
            if isinstance(t, ResTarget):
                val = t.val
                if isinstance(val, SubLink):
                    subSelect = val.subselect
                    for node in subSelect:
                        attr = getattr(subSelect, node)
                        # print("INNER", inner_name)
                        self._find_columnRef(attr, inner_name)
                if isinstance(val, ColumnRef):
                    self._columnRefStarCheck(val)

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

    def _find_columnRef(self, attr, outer_names: Set[str]):
        if isinstance(attr, ColumnRef):
            name = getattr(attr.fields[0], "sval")
            if name in outer_names:
                self.recs.append(
                    f"Коррелированный подзапрос. Включает в себя {name}, используйте JOIN"
                )
        elif isinstance(attr, Node):
            for i in attr:
                attr_inside = getattr(attr, i)
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
# SELECT u.id,
#        (SELECT COUNT(*)
#         FROM orders o
#         WHERE o.user_id = u.id) AS order_count
# FROM users u;
# """
# --- НЕСКОЛЬКО ТАБЛИЦ
# sql = "SELECT * FROM users, orders"

sql = """
SELECT
    c.customer_id,
    c.name,
    (
        SELECT COUNT(*)
        FROM orders o
        WHERE o.customer_id = c.customer_id
    ) AS orders_count,
    (
        SELECT SUM(oi.quantity)
        FROM order_items oi
        WHERE oi.order_id IN (
            SELECT o2.order_id
            FROM orders o2
            WHERE o2.customer_id = c.customer_id
        )
    ) AS total_items,
    (
        SELECT AVG(p.price)
        FROM products p
        WHERE p.product_id IN (
            SELECT oi2.product_id
            FROM order_items oi2
            WHERE oi2.order_id IN (
                SELECT o3.order_id
                FROM orders o3
                WHERE o3.customer_id = c.customer_id
            )
        )
    ) AS avg_product_price
FROM customers c;
"""

ast_tree: List[RawStmt] = parse_sql(sql)
stmt: SelectStmt = ast_tree[0].stmt

asd = PgParser()

print(asd.getRecommendations(stmt))
