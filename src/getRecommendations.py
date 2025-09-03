from typing import Any
from src.pre.pre_analyze import PreAnalyze
from src.post.post_analyze import PostAnalyze


def getRecommendations(query: str) -> Any:
    preRecsList = PreAnalyze().getRecommendations(query)
    postRecsList = PostAnalyze().analyze_query(query)
    recsList = {"pre": preRecsList, "post": postRecsList}

    return recsList
