from typing import Callable, List, TypeVar
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import connect
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os
from src.common.logger import logger
from src.post.types import PlanNode
from settings import config

load_dotenv()

MAKE_ANALYZE = config["MAKE_ANALYZE"] or False
ANALYZE_TIMEOUT = config["ANALYZE_TIMEOUT"] or 3

T = TypeVar("T")


class SQLRequests:
    def __init__(self):
        self.conn: connection = connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        self.cur: cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def makeRequest(self, callback: Callable[[], T]) -> T:
        try:
            return callback()
        except Exception as e:
            self.conn.rollback()
            raise e

    def _run_explain_analyze(self, query: str, analyze: bool) -> PlanNode:
        plan = None
        if analyze and MAKE_ANALYZE:
            self.cur.execute(f"EXPLAIN (FORMAT JSON, ANALYZE TRUE) {query}")
        else:
            self.cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
        plan = self.cur.fetchall()[0]["QUERY PLAN"][0]["Plan"]
        return plan

    def getExplainPlan(self, query: str) -> PlanNode:
        def callback() -> PlanNode:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_explain_analyze, query, True)
                try:
                    plan = future.result(timeout=ANALYZE_TIMEOUT)
                    logger.info("ANALYZE ВЫПОЛНИЛСЯ")
                    return plan
                except TimeoutError:
                    future.cancel()
                    logger.info("ANALYZE ВЫПОЛНИЛСЯ")
                    self.conn.cancel()
                    self.conn.rollback()
                    return self._run_explain_analyze(query, False)

        return self.makeRequest(callback)

    def getTableRows(self, table: str) -> int:
        def callback() -> int:
            self.cur.execute(f"""
			SELECT reltuples::bigint AS row_count
				FROM pg_class
				WHERE relname = '{table}';
			""")
            info = self.cur.fetchall()[0]["row_count"]
            return info

        return self.makeRequest(callback)

    def getColumns(self, table: str) -> List[str]:
        def callback() -> List[str]:
            self.cur.execute(f"""
                SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            ORDER BY ordinal_position;
            """)

            result = self.cur.fetchall()

            cols = [row["column_name"] for row in result]

            return cols

        return self.makeRequest(callback)

    def getStatistic(self, limit: int) -> List[object]:
        def callback() -> List[str]:
            self.cur.execute(f"""
            SELECT
                REPLACE(query, E'\n', ' ') AS query_single_line,
                calls,
                ROUND(total_exec_time) AS total_exec_time,
                ROUND(mean_exec_time) AS mean_exec_time,
                rows
            FROM pg_stat_statements
            WHERE query LIKE 'SELECT%'
            ORDER BY total_exec_time DESC
            LIMIT {limit}
            """)
            result = self.cur.fetchall()

            return result

        return self.makeRequest(callback)
