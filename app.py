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
    agora = datetime.utcnow() - timedelta(hours=3)
    total = len(dados_lojas)
    online = sum(1 for info in dados_lojas.values() if info["dados"].get("ativo"))
    offline = total - online

    cards = ""
    for loja, info in sorted(dados_lojas.items()):
        ativo = info["dados"].get("ativo", False)
        processo = info["dados"].get("processo", False)
        porta = info["dados"].get("porta", False)
        ultima = info["ultima_atualizacao"]
        diff = (agora - ultima).total_seconds()
        desatualizado = diff > 120  # mais de 2 min sem atualizar

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
            <div class="card-header">
                <span class="dot">{dot}</span>
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

    if not dados_lojas:
        cards = '<div class="empty">Nenhuma loja enviou dados ainda. Aguardando conexões...</div>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="15">
    <title>Monitoramento VR-Concentrador - Só Ofertas</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0f1117;
            color: #e1e4e8;
            min-height: 100vh;
        }}
        .topbar {{
            background: linear-gradient(135deg, #1a1d27 0%, #22262f 100%);
            border-bottom: 1px solid #2d3139;
            padding: 20px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .topbar h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #fff;
        }}
        .topbar h1 span {{ color: #3b82f6; }}
        .summary {{
            display: flex;
            gap: 16px;
            font-size: 0.85rem;
        }}
        .summary .pill {{
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .pill.total {{ background: #23272f; color: #94a3b8; }}
        .pill.up {{ background: #0d3320; color: #4ade80; }}
        .pill.down {{ background: #3b1219; color: #f87171; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding: 24px 32px;
        }}
        .card {{
            background: #1a1d27;
            border: 1px solid #2d3139;
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.15s, box-shadow 0.15s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}
        .card.online {{ border-left: 4px solid #4ade80; }}
        .card.offline {{ border-left: 4px solid #f87171; }}
        .card.warning {{ border-left: 4px solid #facc15; }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .dot {{ font-size: 1rem; }}
        .status-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-badge.online {{ background: #0d3320; color: #4ade80; }}
        .status-badge.offline {{ background: #3b1219; color: #f87171; }}
        .status-badge.warning {{ background: #3b2f08; color: #facc15; }}
        .card h3 {{
            font-size: 1rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 14px;
        }}
        .details {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 12px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: #94a3b8;
        }}
        .ok {{ color: #4ade80; font-weight: 700; }}
        .fail {{ color: #f87171; font-weight: 700; }}
        .timestamp {{
            font-size: 0.72rem;
            color: #4b5563;
            border-top: 1px solid #2d3139;
            padding-top: 10px;
        }}
        .empty {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #4b5563;
            font-size: 1rem;
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <h1><span>SO OFERTAS</span> &middot; Monitoramento VR-Concentrador</h1>
        <div class="summary">
            <span class="pill total">{total} lojas</span>
            <span class="pill up">{online} online</span>
            <span class="pill down">{offline} offline</span>
        </div>
    </div>
    <div class="grid">
        {cards}
    </div>
</body>
</html>"""

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
