from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests

dados_lojas = {}
app = Flask(__name__)

LOJAS_ESPERADAS = [
    "BRAGANÇA 1",
    "VALINHOS 07","VALINHOS 04",
    "ITATIBA","ITUPEVA", "JOÃO PAULO", "COSMOPOLIS",
    "BARAO GERALDO","JUNDIAÍ","SUMARÉ 1","SUMARÉ 02",
    "ELOY CHAVES","ELÍSIO","PAULINIA","JACARÉ"
]

TOKEN = "SEU_TOKEN"
CHAT_ID = "SEU_CHAT_ID"

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })


@app.route("/status", methods=["POST"])
def status():
    data = request.json
    loja = data.get("loja")
    dados = data.get("dados", {})

    ativo = dados.get("ativo", True)
    agora = datetime.utcnow() - timedelta(hours=3)

    ultimo_status = dados_lojas.get(loja, {}).get("dados", {}).get("ativo", True)

    if ultimo_status and not ativo:
        enviar_telegram(f"🚨 {loja} está OFFLINE")

    if not ultimo_status and ativo:
        enviar_telegram(f"✅ {loja} voltou ONLINE")

    dados_lojas[loja] = {
        "dados": dados,
        "ultima_atualizacao": agora
    }

    return jsonify({"message": "OK"}), 200


@app.route("/painel")
def painel():
    agora = datetime.utcnow() - timedelta(hours=3)

    total = len(dados_lojas)
    online = sum(1 for info in dados_lojas.values() if info["dados"].get("ativo"))
    offline = total - online

    cards = ""
    lista_lojas_html = ""

    for loja in LOJAS_ESPERADAS:
        cor = "#4ade80" if loja in dados_lojas else "#f87171"

        lista_lojas_html += f"""
        <div style="color: {cor}; font-weight: 600;">
            {loja}
        </div>
        """

    for loja, info in sorted(dados_lojas.items()):
        ativo = info["dados"].get("ativo", False)
        ultima = info["ultima_atualizacao"]

        diff = (agora - ultima).total_seconds()
        desatualizado = diff > 120

        if not ativo:
            status_class = "offline"
            status_text = "OFFLINE"
            dot = "🔴"
        elif desatualizado:
            status_class = "warning"
            status_text = "SEM RESPOSTA"
            dot = "🟡"
        else:
            status_class = "online"
            status_text = "ONLINE"
            dot = "🟢"

        tempo_str = ultima.strftime("%d/%m/%Y %H:%M:%S")

        cards += f"""
        <div class="card {status_class}">
            <h3>{loja}</h3>
            <p>{dot} {status_text}</p>
            <p>Atualizado: {tempo_str}</p>
        </div>
        """

    if not dados_lojas:
        cards = "<p>Nenhuma loja enviou dados ainda...</p>"

    html = f"""
    <html>
    <body style="font-family: Arial; background:#111; color:#fff;">

        <h1>Monitoramento VR</h1>

        <p>Total: {total}</p>
        <p>Online: {online}</p>
        <p>Offline: {offline}</p>

        <div>{cards}</div>

        <h2>Lojas</h2>
        {lista_lojas_html}

    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
