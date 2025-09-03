from typing import List
from src.common.request_to_db import SQLRequests

# from src.post.getSyntaxData import AnalyzeSyntaxData
from src.types.types import AnalysisIssue
import src.post.recommendations as recommendations
from settings import config

LIMIT_ROWS = config["LIMIT_ROWS"] or 200
BIG_TABLE_ROWS = config["BIG_TABLE_ROWS"] or 10000
MAX_SORT_LIMIT = config["MAX_SORT_LIMIT"] or 300000
ANALYZE_TIMEOUT = config["ANALYZE_TIMEOUT"] or 3
MAKE_ANALYZE = config["MAKE_ANALYZE"] or False


class PostAnalyze:
    def __init__(self) -> None:
        self.SQLRequest = SQLRequests()
        self.volume: dict = {}
        self.limit = 0

    def analyze_query(self, query: str) -> dict:
        try:
            plan: dict = self.SQLRequest.getExplainPlan(query)
            issues: List[AnalysisIssue] = self._find_issues_in_plan(plan)
            plan_rows = plan.get("Plan Rows", 0)
            relation = plan.get("Relation Name")
            node_type = plan.get("Node Type")
            total_cost = plan.get("Total Cost")
            time = plan.get(
                "Actual Total Time",
                f"Больше {ANALYZE_TIMEOUT} секунд" if MAKE_ANALYZE else None,
            )
            if isinstance(time, str):
                issues.append(recommendations.LONG_QUERY(time))

            if relation and plan_rows and node_type == "Seq Scan":
                rows_count_table = self.SQLRequest.getTableRows(relation)
                print(rows_count_table)
                if plan_rows < rows_count_table / 2:
                    issues.append(
                        recommendations.full_table_scan(
                            relation, rows_count_table, plan_rows
                        )
                    )

            if plan_rows > LIMIT_ROWS:
                issues.append(recommendations.big_result_set(plan_rows, LIMIT_ROWS))

            # return plan
            return {
                "query": query,
                "time": time,
                "volume": self.volume,
                "total_cost": total_cost,
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

        if isinstance(plan_rows, int) and isinstance(relation, str):
            print(plan_rows, relation)
            relation_in_volume = self.volume.get(relation, None)
            if relation_in_volume is not None:
                self.volume[relation] += plan_rows
            else:
                self.volume[relation] = plan_rows

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
                issues.append(recommendations.JOIN_WITHOUT_INDEX)
        if node_type == "Limit":
            self.limit = plan_rows

        if node_type == "Gather Merge":
            gather_merge_plans = plan.get("Plans")
            if isinstance(gather_merge_plans, List):
                node_type_gather_merge = gather_merge_plans[0].get("Node Type")
                if node_type_gather_merge == "Sort":
                    isManyRowsSorting = (
                        gather_merge_plans[0].get("Plan Rows", 0) > MAX_SORT_LIMIT
                    )
                    if isManyRowsSorting and self.limit > MAX_SORT_LIMIT:
                        issues.append(
                            recommendations.big_sort_with_limit(MAX_SORT_LIMIT)
                        )
                    elif isManyRowsSorting:
                        issues.append(recommendations.big_sort(MAX_SORT_LIMIT))

        for subplan in plan.get("Plans", []):
            issues.extend(self._find_issues_in_plan(subplan))
        return issues
