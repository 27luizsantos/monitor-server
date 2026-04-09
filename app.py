from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/status", methods=["POST"])
def status():
    data = request.json
    print("Recebido:", data)
    return jsonify({"message": "OK"}), 200

@app.route("/")
def home():
    return "Servidor rodando!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
