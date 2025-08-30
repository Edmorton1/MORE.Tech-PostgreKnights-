from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
from psycopg2 import connect
from dotenv import load_dotenv
import os

load_dotenv()


def getExplainPlan(query: str):
    conn: connection = connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    cur: cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
        plan = cur.fetchall()[0]["QUERY PLAN"][0]["Plan"]
        return plan
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

