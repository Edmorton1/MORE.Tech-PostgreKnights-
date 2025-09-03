from typing import Any

# from src.pre.pg_parser import PgParser
from src.pre.pg_parser import PgParser
from src.post.post_analyze import PostAnalyze


def getRecommendations(query: str) -> Any:
    preRecsList = PgParser().getRecommendations(query)
    postRecsList = PostAnalyze().analyze_query(query)
    recsList = {"pre": preRecsList, "post": postRecsList}

    return recsList
