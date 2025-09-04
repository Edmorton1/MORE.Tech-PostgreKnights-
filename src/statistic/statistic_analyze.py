from src.common.request_to_db import SQLRequests
from settings import config

COUNT_FREQUENT_AND_VORACIOUS_REQUESTS = (
    config["COUNT_FREQUENT_AND_VORACIOUS_REQUESTS"] or 0
)


class StatisticAnalyze:
    def __init__(self) -> None:
        self.SQLRequest = SQLRequests()

    def analyze_statistic(self):
        statistic = self.SQLRequest.getStatistic(COUNT_FREQUENT_AND_VORACIOUS_REQUESTS)
        return statistic
