from typing import List
from src.connections.post_analyze import PostAnalyze


class PostRecommendations:
    recs: List[str] = []

    def __init__(self, query: str):
        self.explain = PostAnalyze().analyze_query(query)

    # def postprocessing(self) -> List[str]:
    def postprocessing(self):
        return self.explain
