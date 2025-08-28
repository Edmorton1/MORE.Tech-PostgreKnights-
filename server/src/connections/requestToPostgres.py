from postgres import cur, conn


def requestToPostgres(query: str):
    try:
        cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
    except Exception as e:
        conn.rollback()
        raise e

    return cur.fetchall()
