from src.types.types import AnalysisIssue


def push_to_recs(issue: AnalysisIssue, recs: list[AnalysisIssue]):
    if len(recs):
        if not any(
            rec["problem"] == issue["problem"]
            and rec["recommendation"] == issue["recommendation"]
            for rec in recs
        ):
            recs.append(issue)
    else:
        recs.append(issue)
