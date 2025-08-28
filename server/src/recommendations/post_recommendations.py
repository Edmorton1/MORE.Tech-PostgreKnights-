from typing import List
from ..connections.requestToPostgres import requestToPostgres


class PostRecommendations:
    recs: List[str] = []

    def __init__(self, query: str):
        self.request = requestToPostgres(query)

    def postprocessing(self) -> List[str]:
        return self.recs
