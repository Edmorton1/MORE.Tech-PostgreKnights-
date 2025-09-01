from src.common.common import Common
from pglast import parse_sql
from pglast.ast import RawStmt, SelectStmt
from src.types.types import AnalysisResult


class AnalyzeSyntaxData(Common):
    def __init__(self, query):
        self.query = query

    def getTableRows(self):
        print(self.query)
