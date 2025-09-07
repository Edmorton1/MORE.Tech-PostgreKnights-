import json
from pathlib import Path
from src.pre.pre_analyze import PreAnalyze
from src.getRecommendations import getRecommendations

SQL_EXT = ".sql"
JSON_EXT = ".json"

queries_path = Path(__file__).parent / "queries"
file_names = [f.stem for f in queries_path.iterdir() if f.is_file()]

for file_name in file_names:
    file_path = Path(__file__).parent / "queries" / (file_name + SQL_EXT)
    output_path = Path(__file__).parent / "results" / (file_name + JSON_EXT)

    with open(file_path, "r", encoding="utf-8") as f:
        query = f.read()
        result = PreAnalyze().getRecommendations(query)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
