from typing import List, Literal, TypedDict

class AnalysisIssue(TypedDict):
    severity: Literal["low", "medium", "high"]
    problem: str
    recommendation: str


class AnalysisResult(TypedDict):
    issues: List[AnalysisIssue]
    query: str
    time: int
    total_cost: int
    # risk_level: Literal["low", "medium", "high"]
    # risk_score: int
