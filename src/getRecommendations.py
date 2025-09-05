from typing import Any
from src.pre.pre_analyze import PreAnalyze
from src.post.post_analyze import PostAnalyze
from src.statistic.statistic_analyze import StatisticAnalyze


def getRecommendations(query: str) -> Any:
    preRecsList = PreAnalyze().getRecommendations(query)
    postRecsList = PostAnalyze().analyze_query(query)
    frequent_and_voracious_requests = StatisticAnalyze().analyze_statistic()
    recsList = {
        "pre_analyze": preRecsList,
        "post_analyze": postRecsList,
    }
    
    if frequent_and_voracious_requests:
        recsList["statistic"] = frequent_and_voracious_requests

    return recsList
