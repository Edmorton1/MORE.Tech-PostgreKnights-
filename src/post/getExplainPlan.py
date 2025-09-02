from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import connect
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os

load_dotenv()


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

    def makeRequest(self, callback):
        try:
            return callback()
        except Exception as e:
            self.conn.rollback()
            raise e

    def _run_explain_analyze(self, query: str, analyze: bool):
        plan = None
        if analyze:
            self.cur.execute(f"EXPLAIN (FORMAT JSON, ANALYZE TRUE) {query}")
        else:
            self.cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
        plan = self.cur.fetchall()[0]["QUERY PLAN"][0]["Plan"]
        return plan

    def getExplainPlan(self, query):
        def callback():
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_explain_analyze, query, True)
                try:
                    plan = future.result(timeout=3)
                    print("ANALYZE ВЫПОЛНИЛСЯ")
                    return plan
                except TimeoutError:
                    future.cancel()
                    print("НЕ ВЫПОЛНИЛСЯ ANALYZE")
                    self.conn.cancel()
                    self.conn.rollback()
                    return self._run_explain_analyze(query, False)

        return self.makeRequest(callback)

    def getTableRows(self, table):
        def callback():
            self.cur.execute(f"""
			SELECT relname, reltuples::bigint AS row_count, relpages AS pages
				FROM pg_class
				WHERE relname = '{table}';
			""")
            info = self.cur.fetchall()[0]["row_count"]
            return info

        return self.makeRequest(callback)
