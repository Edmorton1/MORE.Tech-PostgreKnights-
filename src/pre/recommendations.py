from src.common.request_to_db import SQLRequests

SQLReq = SQLRequests()

cross_join_multiple_tables = {
    "severity": "high",
    "problem": "Несколько таблиц в FROM. Это выполняет CROSS JOIN",
    "recommendation": "Не указывать в FROM несколько таблиц, а использовать JOIN ON",
}


def select_star(table: str | None):
    return {
        "severity": "medium",
        "problem": "Используется * в FROM",
        "recommendation": f"Указать конкретные поля, которые нужны, все поля: {str(SQLReq.getColumns(table)) if table else ''}",
    }


cross_join_usage = {
    "severity": "high",
    "problem": "Использование CROSS JOIN",
    "recommendation": "Используйте другой JOIN, а CROSS JOIN только при необходимости",
}

in_subquery = {
    "severity": "low",
    "problem": "IN с подзапросом",
    "recommendation": "Используйте EXISTS или JOIN DISTINCT. Но лучше JOIN DISTINCT",
}


def correlated_subquery(name: str):
    return {
        "severity": "high",
        "problem": f"Коррелированный подзапрос. Включает в себя {name}",
        "recommendation": "Используйте JOIN вместо подзапросов. Это очень ускоряет запрос",
    }


def big_in_list(max_params: int):
    return {
        "severity": "low",
        "problem": f"Большое кол-во аргументов внутри IN. Сейчас ограничение {max_params}",
        "recommendation": "Используйте CTE",
    }


function_in_where_having = {
    "severity": "medium",
    "problem": "Использование функций в WHERE или HAVING. Из-за этого не используется индекс",
    "recommendation": "Используйте функции в WHERE или HAVING только если без них не обойтись",
}
