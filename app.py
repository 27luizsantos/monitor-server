from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from threading import Thread, Lock
import requests
import time

lock = Lock()
lojas_alertadas = {}
dados_lojas = {}
app = Flask(__name__)

TOKEN = "8630570120:AAHUTphBpCTBOghKEGHRm-Z8nYQVB7vvhXA"
CHAT_ID = "8523564012"

def enviar_alerta(loja, status):
    mensagem = f"🚨 {loja} - {status}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": mensagem
        })
    except:
        pass

@app.route("/status", methods=["POST"])
def status():
    data = request.json
    loja = data.get("loja")
    agora = datetime.utcnow() - timedelta(hours=3)

    with lock:
        dados_lojas[loja] = {
            "dados": data.get("dados"),
            "ultima_atualizacao": agora
        }

    print("📩 Recebido:", data, flush=True)
    return jsonify({"message": "OK"}), 200


@app.route("/painel")
def painel():
    agora = datetime.utcnow() - timedelta(hours=3)

    with lock:
        snapshot = dict(dados_lojas)

    total = len(snapshot)
    online = sum(1 for info in snapshot.values() if info["dados"].get("ativo"))
    offline = total - online

    cards = ""
    for loja, info in sorted(snapshot.items()):
        ativo = info["dados"].get("ativo", False)
        processo = info["dados"].get("processo", False)
        porta = info["dados"].get("porta", False)
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
        proc_icon = "✔" if processo else "✘"
        proc_class = "check" if processo else "cross"
        porta_icon = "✔" if porta else "✘"
        porta_class = "check" if porta else "cross"

        cards += f"""
        <div class="card {status_class}">
            <div class="status-badge">
                <span>{dot}</span>
                <span>{status_text}</span>
            </div>
            <h2>{loja}</h2>
            <div class="details">
                <div class="detail-item">
                    <span>Processo</span>
                    <span class="{proc_class}">{proc_icon}</span>
                </div>
                <div class="detail-item">
                    <span>Porta</span>
                    <span class="{porta_class}">{porta_icon}</span>
                </div>
            </div>
            <p class="timestamp">Atualizado: {tempo_str}</p>
        </div>
        """

    if not snapshot:
        cards = '<p style="text-align:center;color:#aaa;grid-column:1/-1;">Nenhuma loja enviou dados ainda. Aguardando conexões...</p>'

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="15">
        <title>Monitoramento VR</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ font-size: 1.6rem; color: #fff; }}
            .summary {{ display: flex; justify-content: center; gap: 20px; margin-top: 10px; }}
            .summary span {{ padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }}
            .summary .total {{ background: #1e1e2e; color: #ccc; }}
            .summary .on {{ background: #0d3320; color: #4ade80; }}
            .summary .off {{ background: #3b1111; color: #f87171; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; }}
            .card {{ background: #1a1a2e; border-radius: 12px; padding: 20px; border-left: 4px solid #555; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-3px); }}
            .card.online {{ border-left-color: #4ade80; }}
            .card.offline {{ border-left-color: #f87171; }}
            .card.warning {{ border-left-color: #facc15; }}
            .status-badge {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 700; font-size: 0.9rem; }}
            .card h2 {{ font-size: 1rem; color: #fff; margin-bottom: 12px; }}
            .details {{ display: flex; gap: 16px; margin-bottom: 10px; }}
            .detail-item {{ display: flex; flex-direction: column; align-items: center; font-size: 0.8rem; gap: 2px; }}
            .check {{ color: #4ade80; font-weight: bold; }}
            .cross {{ color: #f87171; font-weight: bold; }}
            .timestamp {{ font-size: 0.75rem; color: #888; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SO OFERTAS · Monitoramento VR-Concentrador</h1>
            <div class="summary">
                <span class="total">{total} lojas</span>
                <span class="on">{online} online</span>
                <span class="off">{offline} offline</span>
            </div>
        </div>
        <div class="grid">
            {cards}
        </div>
    </body>
    </html>
    """

    return html


def monitorar():
    while True:
        try:
            agora = datetime.utcnow() - timedelta(hours=3)

            with lock:
                items = list(dados_lojas.items())

            for loja, info in items:
                ultima = info["ultima_atualizacao"]
                diff = (agora - ultima).total_seconds()
                ativo = info["dados"].get("ativo", False)

                if not ativo:
                    if not lojas_alertadas.get(loja):
                        enviar_alerta(loja, "OFFLINE")
                        lojas_alertadas[loja] = True

                elif diff > 120:
                    if not lojas_alertadas.get(loja):
                        enviar_alerta(loja, "SEM RESPOSTA")
                        lojas_alertadas[loja] = True

                else:
                    if lojas_alertadas.get(loja):
                        enviar_alerta(loja, "VOLTOU")
                        lojas_alertadas[loja] = False
        except Exception as e:
            print(f"Erro no monitor: {e}", flush=True)
        print("monitorando...", flush=True)
        time.sleep(10)


if __name__ == "__main__":
    Thread(target=monitorar, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
