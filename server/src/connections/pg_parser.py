from typing import List
from pglast import parse_sql
from pglast.ast import (
    SelectStmt,
    JoinExpr,
    ResTarget,
    ColumnRef,
    A_Star,
    RangeVar,
    SubLink,
    Node,
)

recs: List[str] = []

# --- НОРМ
# sql = "SELECT * FROM users INNER JOIN orders ON users.id = orders.user_id"
# --- CROSS JOIN
# sql = "SELECT * FROM users CROSS JOIN orders"
# --- Коррелированные подзапросы
sql = """
SELECT u.id,
       (SELECT COUNT(*)
        FROM orders o
        WHERE o.user_id = u.id) AS order_count
FROM users u;
"""
# --- НЕСКОЛЬКО ТАБЛИЦ
# sql = "SELECT * FROM users, orders"

ast_tree = parse_sql(sql)

stmt = ast_tree[0].stmt

# print("ПОЛНОЕ ДЕРЕВО", ast_tree)
# print("STMT", stmt)

# def findColumnRef():
subColumnRefs: List[str] = []


def find_columnRef(attr):
    if isinstance(attr, ColumnRef):
        subColumnRefs.append(getattr(attr.fields[0], "sval"))
        # for field in attr.fields:
        #     print(field)
    elif isinstance(attr, Node):
        for i in attr:
            attr_inside = getattr(attr, i)
            find_columnRef(attr_inside)
    elif isinstance(attr, tuple):
        for attr_inside in attr:
            find_columnRef(attr_inside)


def checkRecommendations(stmt: SelectStmt, outer_names: set = set()):
    fromClause = stmt.fromClause
    # Количество таблиц в FROM
    inter_name = set()
    froms = 0
    print("FromClause", fromClause)

    for f in fromClause:
        # НЕСКОЛЬКО ТАБЛИЦ В FROM
        if isinstance(f, RangeVar):
            inter_name.add(f.relname)
            froms += 1

        # ПРОВЕРКА JOIN
        if isinstance(f, JoinExpr):
            # print("JOIN", f)
            join_type = f.jointype
            quals = getattr(f, "quals", None)
            if join_type == 0 and quals == None:
                recs.append("CROSS JOIN")

    targetList = stmt.targetList
    # print("TargetList", targetList)
    for t in targetList:
        if isinstance(t, ResTarget):
            val = t.val
            if isinstance(val, SubLink):
                subSelect = val.subselect
                print("SubSelect", subSelect)
                for node in subSelect:
                    attr = getattr(subSelect, node)
                    find_columnRef(attr)
            if isinstance(val, ColumnRef):
                fields = val.fields
                # print("fields", fields)
                for field in fields:
                    # ПРОВЕРКА НА *
                    if isinstance(field, A_Star):
                        recs.append("Используется *")

    if froms > 1:
        recs.append("Несколько таблиц в from")
    print(inter_name, outer_names)


checkRecommendations(stmt)

print(recs, subColumnRefs)

# if isinstance(attr, Node):
#     # print("NODE", attr)
#     for i in attr:
#         attr_inside = getattr(attr, i)
#         if isinstance(attr_inside, ColumnRef):
#             print("COLUMN REF НАШЁЛСЯ")

# elif isinstance(attr, tuple):
#     print("TUPLE", attr)
#     for attr_inside in attr:
#         if isinstance(attr_inside, Node):
#             for i in attr_inside:
#                 attr_inside_inside = getattr(attr_inside, i)
#                 if isinstance(attr_inside_inside, ColumnRef):
#                     print("NODAD")
#                 # print(attr_inside_inside)
#                 # if isinstance(attr_inside_inside, ColumnRef):
#                 #     print("IN TUPPLE НАШЁЛСЯ")
# recursive_walk(attr)
