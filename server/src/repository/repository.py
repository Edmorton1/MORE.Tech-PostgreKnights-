from db.postgres import cur

class Repository:
    @staticmethod
    def test():
        cur.execute("EXPLAIN SELECT * FROM users")
        return cur.fetchall()