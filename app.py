from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from threading import Thread, Lock
import time

app = Flask(__name__)

dados_lojas = {}
lojas_alerta = {}
lock = Lock()


def enviar_alerta(mensagem):
    """Envia alerta (por enquanto apenas print, futuramente Telegram/email)."""
    print(f"⚠️ ALERTA: {mensagem}", flush=True)
    # TODO: integrar com Telegram, WhatsApp ou email


@app.route("/status", methods=["POST"])
def status():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON inválido"}), 400

        loja = data.get("loja", "").strip()
        dados = data.get("dados", {})

        if not loja or not isinstance(dados, dict):
            return jsonify({"error": "Campos 'loja' e 'dados' são obrigatórios"}), 400

        agora = datetime.utcnow() - timedelta(hours=3)

        with lock:
            dados_lojas[loja] = {
                "dados": dados,
                "ultima_atualizacao": agora,
            }

            if loja not in lojas_alerta:
                lojas_alerta[loja] = {
                    "ultimo_status": time.time(),
                    "alerta_enviado": False,
                }
            lojas_alerta[loja]["ultimo_status"] = time.time()

        print(f"📩 Recebido: {loja} → ativo={dados.get('ativo')}", flush=True)
        return jsonify({"message": "OK"}), 200

    except Exception as e:
        print(f"❌ Erro no /status: {e}", flush=True)
        return jsonify({"error": "Erro interno"}), 500


@app.route("/painel")
def painel():
    agora = datetime.utcnow() - timedelta(hours=3)

    with lock:
        snapshot = dict(sorted(dados_lojas.items()))

    total = len(snapshot)
    online = 0
    cards = ""

    for loja, info in snapshot.items():
        dados = info.get("dados", {})
        ativo = dados.get("ativo", False)
        processo = dados.get("processo", False)
        porta = dados.get("porta", False)
        ultima = info["ultima_atualizacao"]
        diff = (agora - ultima).total_seconds()
        desatualizado = diff > 120

        if not ativo:
            status_class, status_text, dot = "offline", "OFFLINE", "🔴"
        elif desatualizado:
            status_class, status_text, dot = "warning", "SEM RESPOSTA", "🟡"
        else:
            status_class, status_text, dot = "online", "ONLINE", "🟢"
            online += 1

        tempo_str = ultima.strftime("%d/%m/%Y %H:%M:%S")
        proc_icon = "✔" if processo else "✘"
        proc_class = "check-ok" if processo else "check-fail"
        porta_icon = "✔" if porta else "✘"
        porta_class = "check-ok" if porta else "check-fail"

        cards += f"""
        <div class="card {status_class}">
            <div class="card-status">
                <span class="dot">{dot}</span>
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

    offline = total - online

    if not snapshot:
        cards = '<p class="empty">Nenhuma loja enviou dados ainda. Aguardando conexões...</p>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="15">
    <title>Monitoramento VR</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #0f1117;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1d2e, #252a3a);
            padding: 24px 32px;
            border-bottom: 1px solid #2a2f42;
        }}
        .header h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }}
        .summary {{
            display: flex;
            gap: 16px;
            font-size: 0.85rem;
        }}
        .summary span {{
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .summary .total {{ background: #2a2f42; color: #94a3b8; }}
        .summary .on {{ background: #064e3b; color: #34d399; }}
        .summary .off {{ background: #450a0a; color: #f87171; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding: 24px 32px;
        }}
        .card {{
            background: #1a1d2e;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #444;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); }}
        .card.online {{ border-left-color: #34d399; }}
        .card.offline {{ border-left-color: #f87171; }}
        .card.warning {{ border-left-color: #fbbf24; }}
        .card-status {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 0.85rem;
            margin-bottom: 8px;
        }}
        .card h2 {{
            font-size: 1rem;
            color: #fff;
            margin-bottom: 12px;
        }}
        .details {{
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
        }}
        .detail-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            font-size: 0.8rem;
            color: #94a3b8;
        }}
        .check-ok {{ color: #34d399; font-size: 1.1rem; }}
        .check-fail {{ color: #f87171; font-size: 1.1rem; }}
        .timestamp {{
            font-size: 0.75rem;
            color: #64748b;
        }}
        .empty {{
            grid-column: 1 / -1;
            text-align: center;
            color: #64748b;
            padding: 60px 0;
            font-size: 1rem;
        }}
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
</html>"""
    return html


def monitorar_lojas():
    """Thread que verifica lojas sem resposta e envia alertas."""
    while True:
        try:
            agora = time.time()
            with lock:
                items = list(lojas_alerta.items())

            for loja, info in items:
                tempo = agora - info["ultimo_status"]

                if tempo > 5:
                    if not info["alerta_enviado"]:
                        enviar_alerta(f"🚨 {loja} está OFFLINE há {int(tempo)}s")
                        with lock:
                            lojas_alerta[loja]["alerta_enviado"] = True
                else:
                    if info["alerta_enviado"]:
                        enviar_alerta(f"✅ {loja} VOLTOU ao normal")
                        with lock:
                            lojas_alerta[loja]["alerta_enviado"] = False

        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}", flush=True)

        time.sleep(10)


if __name__ == "__main__":
    Thread(target=monitorar_lojas, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
