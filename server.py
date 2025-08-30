from flask import Flask, jsonify, request, abort
from werkzeug.exceptions import HTTPException
from src.getRecommendations import getRecommendations


app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = {"error": e.name, "code": e.code, "description": e.description}
    return jsonify(response), e.code


@app.route("/test", methods=["POST"])
def test():
    data: dict = request.get_json()
    if not data or "query" not in data:
        abort(400, description="Нет обязательного параметра query")
    query: str = data.get("query")

    print(query)

    recsList = getRecommendations(query)

    return jsonify(recsList)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

# ЗАПУСК ЧЕРЕЗ py main.py
