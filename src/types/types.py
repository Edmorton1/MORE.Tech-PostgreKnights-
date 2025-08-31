from typing import List, Literal, TypedDict


class AnalysisResult(TypedDict):
    issues: List[str]
    query: str
    risk_level: Literal["low", "medium", "high"]
    risk_score: int