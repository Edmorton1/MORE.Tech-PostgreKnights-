from typing import TypedDict


class Config(TypedDict):
    LIMIT_ROWS: int
    BIG_TABLE_ROWS: int
    MAX_SORT_LIMIT: int
    MAKE_ANALYZE: bool
    ANALYZE_TIMEOUT: int
    MAX_PARAMS_IN_IN: int

config: Config = {
    "LIMIT_ROWS": 200,
    # МАКСИМАЛЬНОЕ КОЛИЧЕСТВО РЯДОВ БЕЗ ИНДЕКСА
    "BIG_TABLE_ROWS": 10000,
    "MAX_SORT_LIMIT": 300000,
    "MAKE_ANALYZE": False,
    "ANALYZE_TIMEOUT": 3,
    "MAX_PARAMS_IN_IN": 2,
}
