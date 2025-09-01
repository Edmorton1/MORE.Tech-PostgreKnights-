from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import connect
from dotenv import load_dotenv
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

    def getExplainPlan(self, query):
        def callback():
            self.cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
            plan = self.cur.fetchall()[0]["QUERY PLAN"][0]["Plan"]
            return plan

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
