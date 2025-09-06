import os
from flask import Flask, jsonify, request, abort, send_from_directory
from werkzeug.exceptions import HTTPException
from src.getRecommendations import getRecommendations
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"), static_url_path="")
CORS(app, origins=["http://127.0.0.1:5500"])

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = {"error": e.name, "code": e.code, "description": e.description}
    return jsonify(response), e.code


@app.route("/", methods=["POST"])
def post():
    data: dict = request.get_json()
    if not data or "query" not in data:
        abort(400, description="Нет обязательного параметра query")
    query: str = data.get("query")

    print(query)

    recsList = getRecommendations(query)

    return jsonify(recsList)


@app.route("/", methods=["GET"])
def get():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000)), debug=True)

# ЗАПУСК ЧЕРЕЗ py main.py
