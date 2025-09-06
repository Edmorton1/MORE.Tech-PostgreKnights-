from typing import List
from src.common.logger import logger
from src.post.types import PlanNode
from src.common.request_to_db import SQLRequests
from src.types.types import AnalysisIssue, AnalysisResult, VolumeType
import src.post.recommendations as recommendations
from src.post.post_check import PostCheck
from settings import config
from src.common.push_to_recs import push_to_recs

LIMIT_ROWS = config["LIMIT_ROWS"] or 200
MAX_ROWS_WITHOUT_INDEX = config["MAX_ROWS_WITHOUT_INDEX"] or 10000
ANALYZE_TIMEOUT = config["ANALYZE_TIMEOUT"] or 3
MAKE_ANALYZE = config["MAKE_ANALYZE"] or False

class PostAnalyze:
    def __init__(self) -> None:
        self.SQLRequest = SQLRequests()
        self.volume: VolumeType = {}
        self.limit = 0
        self.issues: List[AnalysisIssue] = []
        self.postCheck = PostCheck(self.issues)

    def analyze_query(self, query: str) -> AnalysisResult:
        try:
            plan = self.SQLRequest.getExplainPlan(query)
            self._find_issues_in_plan(plan)
            plan_rows = plan.get("Plan Rows", 0)
            total_cost = plan.get("Total Cost")

            time = plan.get(
                "Actual Total Time",
                f"{ANALYZE_TIMEOUT}" if MAKE_ANALYZE else None,
            )

            if isinstance(time, str):
                push_to_recs(recommendations.LONG_QUERY(time), self.issues)

            if plan_rows > LIMIT_ROWS:
                push_to_recs(
                    recommendations.big_result_set(plan_rows, LIMIT_ROWS), self.issues
                )
            # return plan
            return {

                "query": query,
                "time": time,
                "volume": self.volume,
                "total_cost": total_cost,
                "issues": self.issues,
            }
        except Exception as e:
            logger.error({"POST_ANALYZE_ERROR": e})
            return {
                "query": query,
                "issues": ["ОШИБКА: Перепроверьте запрос"],
            }

    def _find_issues_in_plan(self, plan: PlanNode) -> None:
        node_type = plan.get("Node Type")
        plan_rows = plan.get("Plan Rows", 0)
        relation = plan.get("Relation Name")
        plans = plan.get("Plans", [])

        if isinstance(plan_rows, int) and isinstance(relation, str):
            relation_in_volume = self.volume.get(relation, None)
            if relation_in_volume is not None:
                self.volume[relation] += plan_rows
            else:
                self.volume[relation] = plan_rows

        if node_type == "Limit":
            self.limit = plan_rows

        self.postCheck.not_effective_sec_scan(node_type, relation, plan_rows)
        self.postCheck.join_without_index(node_type, plan_rows, plans)
        self.postCheck.sort_check(node_type, plans, self.limit)

        for subplan in plan.get("Plans", []):
            self._find_issues_in_plan(subplan)
