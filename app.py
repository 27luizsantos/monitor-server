from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

dados_lojas = {}

LOJAS_ESPERADAS = [
    "BRAGANÇA 1","BRAGANÇA 2",
    "VALINHOS 07","VALINHOS 04",
    "ITATIBA","ITUPEVA","JOÃO PAULO","COSMOPOLIS",
    "BARAO GERALDO","JUNDIAÍ","SUMARÉ 1","SUMARÉ 02",
    "ELOY CHAVES","ELÍSIO","PAULINIA","JACARÉ"
]

TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"

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

    print("📩 Recebido:", data, flush=True)

    return jsonify({"message": "OK"}), 200


@app.route("/painel")
def painel():
    agora = datetime.utcnow() - timedelta(hours=3)

    total = len(LOJAS_ESPERADAS)
    online = 0
    offline = 0

    cards = ""
    lista_lojas_html = ""

    # 🔎 Lista lateral de lojas
    for loja in LOJAS_ESPERADAS:
        info = dados_lojas.get(loja)

        if not info:
            cor = "#f87171"
            offline += 1
        else:
            diff = (agora - info["ultima_atualizacao"]).total_seconds()
            if diff > 120 or not info["dados"].get("ativo"):
                cor = "#f87171"
                offline += 1
            else:
                cor = "#4ade80"
                online += 1

        lista_lojas_html += f"""
        <div style="color: {cor}; font-weight: 600;">
            {loja}
        </div>
        """

    # 🎯 Cards principais
    for loja, info in sorted(dados_lojas.items()):
        ativo = info["dados"].get("ativo", False)
        processo = info["dados"].get("processo", False)
        porta = info["dados"].get("porta", False)

        ultima = info["ultima_atualizacao"]
        diff = (agora - ultima).total_seconds()

        if not ativo:
            status_class = "offline"
            status_text = "OFFLINE"
            dot = "🔴"
        elif diff > 120:
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
            <div class="card-header">
                <span>{dot}</span>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            <h3>{loja}</h3>
            <div class="details">
                <div class="detail-row">
                    <span>Processo</span>
                    <span class="{'ok' if processo else 'fail'}">{'✔' if processo else '✘'}</span>
                </div>
                <div class="detail-row">
                    <span>Porta</span>
                    <span class="{'ok' if porta else 'fail'}">{'✔' if porta else '✘'}</span>
                </div>
            </div>
            <p class="timestamp">Atualizado: {tempo_str}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="15">
<title>Monitoramento</title>
<style>
body {{ background:#0f1117;color:#e1e4e8;font-family:sans-serif }}
.topbar {{ padding:20px }}
.grid {{ display:grid;grid-template-columns:repeat(auto-fill,280px);gap:16px;padding:20px }}
.card {{ background:#1a1d27;padding:15px;border-radius:10px }}
.online {{ border-left:4px solid #4ade80 }}
.offline {{ border-left:4px solid #f87171 }}
.warning {{ border-left:4px solid #facc15 }}
.ok {{ color:#4ade80 }}
.fail {{ color:#f87171 }}
</style>
</head>
<body>

<div class="topbar">
<h2>Monitoramento VR</h2>
<p>Total: {total} | Online: {online} | Offline: {offline}</p>
</div>

<div style="padding:20px">
<h3>Lojas Monitoradas</h3>
{lista_lojas_html}
</div>

<div class="grid">
{cards}
</div>

</body>
</html>"""

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
