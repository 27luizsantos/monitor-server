from flask import Flask, request, jsonify
from datetime import datetime, timedelta

dados_lojas = {}
app = Flask(__name__)

@app.route("/status", methods=["POST"])
def status():
    data = request.json

    loja = data.get("loja")
    agora = datetime.utcnow() - timedelta(hours=3)

    dados_lojas[loja] = {
        "dados": data.get("dados"),
        "ultima_atualizacao": agora
    }

    print("📩 Recebido:", data, flush=True)

    return jsonify({"message": "OK"}), 200


@app.route("/painel")
def painel():
    html = "<h1>Monitoramento Concentradores</h1>"

    for loja, info in dados_lojas.items():
        status = "🟢 ONLINE" if info["dados"]["ativo"] else "🔴 OFFLINE"

        html += f"""
        <p>
        <b>{loja}</b><br>
        Status: {status}<br>
        Última atualização: {info['ultima_atualizacao']}
        </p>
        <hr>
        """

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
