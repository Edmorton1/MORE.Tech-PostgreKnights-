from src.connections.cost_model import CostModel
from src.connections.postgres import getExplainPlan


class PostAnalyze:
    def __init__(self) -> None:
        self.cost_model = CostModel()

    def analyze_query(self, query: str) -> dict:
        try:
            plan = getExplainPlan(query)
            issues = self._find_issues_in_plan(plan)
            risk_score = self.cost_model.calculate_plan_score(plan)
            return {
                "query": query,
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "issues": issues,
            }
        except Exception as e:
            return {"error": str(e), "query": query}

    def _find_issues_in_plan(self, plan: dict) -> list:
        issues = []
        node_type = plan.get("Node Type")
        relation = plan.get("Relation Name")
        plan_rows = plan.get("Plan Rows", 0)

        if node_type == "Seq Scan" and plan_rows > 1000:
            issues.append(
                {
                    "severity": "high",
                    "problem": f"Полное сканирование таблицы '{relation}'",
                    "recommendation": "Создайте индекс по колонке из WHERE.",
                }
            )

        if node_type == "Nested Loop" and plan_rows > 10000:
            issues.append(
                {
                    "severity": "medium",
                    "problem": "Неэффективный Nested Loop Join",
                    "recommendation": "Проверьте индексы или используйте Hash Join.",
                }
            )

        if node_type == "Sort" and plan_rows > 5000:
            issues.append(
                {
                    "severity": "low",
                    "problem": "Сортировка большого объема данных",
                    "recommendation": "Добавьте индекс по полю сортировки.",
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