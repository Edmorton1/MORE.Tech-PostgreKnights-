from typing import List, Literal, Optional, TypedDict

class AnalysisIssue(TypedDict):
    severity: Literal["low", "medium", "high"]
    problem: str
    recommendation: str


VolumeType = dict[str, int]

class AnalysisResult(TypedDict):
    query: str
    time: int | str
    volume: dict[str, int]
    total_cost: int
    issues: List[AnalysisIssue]
    frequent_and_voracious_requests: Optional[List]
    # risk_level: Literal["low", "medium", "high"]
    # risk_score: int
