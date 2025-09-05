from typing import TypedDict


class Config(TypedDict):
    LIMIT_ROWS: int
    MAX_ROWS_WITHOUT_INDEX: int
    MAX_SORT_LIMIT: int
    MAKE_ANALYZE: bool
    ANALYZE_TIMEOUT: int
    MAX_PARAMS_IN_IN: int
    COUNT_FREQUENT_AND_VORACIOUS_REQUESTS: int


config: Config = {
    "LIMIT_ROWS": 200,
    "MAX_ROWS_WITHOUT_INDEX": 10000,
    "MAX_SORT_LIMIT": 300000,
    "MAKE_ANALYZE": False,
    "ANALYZE_TIMEOUT": 3,
    "MAX_PARAMS_IN_IN": 2,
    "COUNT_FREQUENT_AND_VORACIOUS_REQUESTS": 0,
}
