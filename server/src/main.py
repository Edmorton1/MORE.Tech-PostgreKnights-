from flask import Flask, jsonify
from  services.service import Service

app = Flask(__name__)

@app.route("/test")
def test():
    return jsonify(Service.test())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
# flask --app main run