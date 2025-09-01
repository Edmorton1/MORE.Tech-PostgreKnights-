from typing import List
from src.post.cost_model import CostModel
from src.post.getExplainPlan import SQLRequests

# from src.post.getSyntaxData import AnalyzeSyntaxData
from src.types.types import AnalysisResult, AnalysisIssue
# ЗАВТРА ДОСТАТЬ КОЛИЧЕСВТО ROW В ТАБЛИЦЕ И СДЕЛАТЬ ФЛАГ ЧТО ИСПОЛЬЗУЮТСЯ SORT WHERE И Т.Д. ЗАПРОСЫ НА ОСНОВЕ ЭТОГО СДЕЛАТЬ ВЫВОД НУЖЕН ЛИ ИНДЕС

LIMIT_ROWS = 200
BIG_TABLE_ROWS = 10000
MAX_SORT_LIMIT = 300000


class PostAnalyze:
    def __init__(self) -> None:
        self.SQLRequest = SQLRequests()
        self.cost_model = CostModel()
        self.limit = 0

    def analyze_query(self, query: str) -> dict:
        try:
            plan: dict = self.SQLRequest.getExplainPlan(query)
            issues = self._find_issues_in_plan(plan)
            risk_score = self.cost_model.calculate_plan_score(plan)
            plan_rows = plan.get("Plan Rows", 0)
            relation = plan.get("Relation Name")
            node_type = plan.get("Node Type")
            print(issues, risk_score)

            if relation and plan_rows and node_type == "Seq Scan":
                rows_count_table = self.SQLRequest.getTableRows(relation)
                print(rows_count_table)
                if plan_rows < rows_count_table / 2:
                    issues.append(
                        {
                            "severity": "high",
                            "problem": f"Полное сканирование таблицы '{relation}', проходится по каждому значению из {rows_count_table}, хотя нужно {plan_rows}",
                            "recommendation": "Создайте индекс по колонке из WHERE.",
                        }
                    )

            if plan_rows > LIMIT_ROWS:
                issues.append(
                    {
                        "severity": "medium",
                        "problem": f"Возврат большого кол-ва значений, сейчас установлен лимит {LIMIT_ROWS}. Запрос вернёт {plan_rows} полей",
                        "recommendation": "Установить LIMIT и делать запросы с пагинацией(метод с курсором)",
                    }
                )

            return plan
            return {
                "query": query,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "issues": issues,
            }
        except Exception as e:
            return {"error": str(e), "query": query}

    def _find_issues_in_plan(self, plan: dict) -> list:
        issues: List[AnalysisIssue] = []
        node_type = plan.get("Node Type")
        plan_rows = plan.get("Plan Rows", 0)
        relation = plan.get("Relation Name")

        print(relation, plan_rows)

        if (
            node_type in ("Nested Loop", "Hash Join", "Merge Join")
            and plan_rows > BIG_TABLE_ROWS
        ):
            isUsesIndex = False

            for node in plan.get("Plans", []):
                if node.get("Node Type") == "Index Scan":
                    isUsesIndex = True
                    break

            if not isUsesIndex:
                issues.append(
                    {
                        "severity": "high",
                        "problem": "JOIN проходится по всем рядам без индекса. Что сильно тормозит запрос",
                        "recommendation": "Поставьте индекс на одну из колонок, использующихся в JOIN",
                    }
                )

        # if node_type == "Sort" and plan_rows > 5000:
        #     issues.append(
        #         {
        #             "severity": "low",
        #             "problem": "Сортировка большого объема данных",
        #             "recommendation": "Добавьте индекс по полю сортировки.",
        #         }
        #     )
        if node_type == "Limit":
            self.limit = plan_rows

        if node_type == "Gather Merge":
            gather_merge_plans = plan.get("Plans")
            if isinstance(gather_merge_plans, List):
                node_type_gather_merge = gather_merge_plans[0].get("Node Type")
                if node_type_gather_merge == "Sort":
                    isManyRowsSorting = gather_merge_plans[0].get("Plan Rows", 0) > MAX_SORT_LIMIT
                    if isManyRowsSorting and self.limit > MAX_SORT_LIMIT:
                        issues.append(
                            {
                                "severity": "high",
                                "problem": f"Сортировка по большому объему данных без индекса с слишком большим лимитом. В приложении установлен лимит {MAX_SORT_LIMIT}",
                                "recommendation": "Установить небольшой лимит на сортировку, поставить индекс",
                            }
                        )
                    elif isManyRowsSorting:
                        issues.append(
                            {
                                "severity": "high",
                                "problem": f"Сортировка по большому объему данных без индекса. В приложении установлен лимит {MAX_SORT_LIMIT}",
                                "recommendation": "Установить индекс",
                            }
                        )        

        for subplan in plan.get("Plans", []):
            issues.extend(self._find_issues_in_plan(subplan))
        return issues

    def _get_risk_level(self, score: int) -> str:
        if score >= 70:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
