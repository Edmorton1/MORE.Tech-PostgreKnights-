from src.post.types import PlanType
from src.common.request_to_db import SQLRequests
import src.post.recommendations as recommendations
from settings import config
from src.types.types import AnalysisIssue
from src.common.push_to_recs import push_to_recs

BIG_TABLE_ROWS = config["BIG_TABLE_ROWS"] or 10000
MAX_SORT_LIMIT = config["MAX_SORT_LIMIT"] or 300000


class PostCheck:
    def __init__(self, issues: list[AnalysisIssue]):
        self.issues: list[AnalysisIssue] = issues
        self.SQLRequest = SQLRequests()

    def not_effective_sec_scan(
        self, node_type: str, relation: None | str, plan_rows: None | int
    ):
        if relation and plan_rows and node_type == "Seq Scan":
            rows_count_table = self.SQLRequest.getTableRows(relation)
            if plan_rows < rows_count_table / 2:
                push_to_recs(
                    recommendations.full_table_scan(
                        relation, rows_count_table, plan_rows
                    ),
                    self.issues,
                )

    def join_without_index(self, node_type: str, plan_rows: int, plans: PlanType):
        if (
            node_type in ("Nested Loop", "Hash Join", "Merge Join")
            and plan_rows > BIG_TABLE_ROWS
        ):
            isUsesIndex = False

            if isinstance(plans, list):
                for node in plans:
                    if node.get("Node Type") == "Index Scan":
                        isUsesIndex = True
                        break

            if not isUsesIndex:
                push_to_recs(recommendations.JOIN_WITHOUT_INDEX, self.issues)

    def sort_check(self, node_type: str, plans: PlanType, limit: int):
        if node_type == "Gather Merge":
            gather_merge_plans = plans
            if isinstance(gather_merge_plans, list):
                node_type_gather_merge = gather_merge_plans[0].get("Node Type")
                if node_type_gather_merge == "Sort":
                    isManyRowsSorting = (
                        gather_merge_plans[0].get("Plan Rows", 0) > MAX_SORT_LIMIT
                    )
                    if isManyRowsSorting and limit > MAX_SORT_LIMIT:
                        push_to_recs(
                            recommendations.big_sort_with_limit(MAX_SORT_LIMIT),
                            self.issues,
                        )
                    elif isManyRowsSorting:
                        push_to_recs(
                            recommendations.big_sort(MAX_SORT_LIMIT), self.issues
                        )
