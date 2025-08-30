from typing import List


class PreRecommendations:
    recs: List[str] = []

    def __init__(self, query: str):
        self.query = query

    def preprocessing(self) -> List[str]:
        self._select_star_check()
        return self.recs

    def _select_star_check(self) -> None:
        if "SELECT *" in self.query:
            self.recs.append("Лучше перечислять поля, которые нужно вернуть вместо *")
