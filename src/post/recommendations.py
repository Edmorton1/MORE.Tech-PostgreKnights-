from src.types.types import AnalysisIssue


def LONG_QUERY(time: str) -> AnalysisIssue:
    return {
        "severity": "low",
        "problem": f"Запрос выполняется дольше {time} секунд",
        "recommendation": "Улучшите оптимизацию",
    }


def full_table_scan(
    relation: str, rows_count_table: int, plan_rows: int
) -> AnalysisIssue:
    return {
        "severity": "high",
        "problem": f"Полное сканирование таблицы '{relation}', проходится по каждому значению из {rows_count_table}, хотя нужно {plan_rows}",
        "recommendation": "Создайте индекс по колонке из WHERE",
    }


def big_result_set(plan_rows: int, limit: int) -> AnalysisIssue:
    return {
        "severity": "medium",
        "problem": f"Возврат большого кол-ва значений, сейчас установлен лимит {limit}. Запрос вернёт {plan_rows} полей",
        "recommendation": "Установить LIMIT и делать запросы с пагинацией(метод с курсором)",
    }


JOIN_WITHOUT_INDEX: AnalysisIssue = {
    "severity": "high",
    "problem": "JOIN проходится по всем рядам без индекса. Что сильно тормозит запрос",
    "recommendation": "Поставьте индекс на одну из колонок, использующихся в JOIN",
}


def big_sort_with_limit(max_limit: int) -> AnalysisIssue:
    return {
        "severity": "high",
        "problem": f"Сортировка по большому объему данных без индекса с слишком большим лимитом. В приложении установлен лимит {max_limit}",
        "recommendation": "Установить небольшой лимит на сортировку, поставить индекс",
    }


def big_sort(max_limit: int) -> AnalysisIssue:
    return {
        "severity": "high",
        "problem": f"Сортировка по большому объему данных без индекса. В приложении установлен лимит {max_limit}",
        "recommendation": "Установить индекс",
    }
