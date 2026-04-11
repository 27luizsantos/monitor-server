from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests

dados_lojas = {}
app = Flask(__name__)

LOJAS_ESPERADAS = [
    "BRAGANÇA 1","BRAGANÇA 2",
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
        if loja in dados_lojas:
            cor_dot = "#22c55e"
            cor_bg = "rgba(34,197,94,0.1)"
            cor_border = "rgba(34,197,94,0.3)"
        else:
            cor_dot = "#ef4444"
            cor_bg = "rgba(239,68,68,0.08)"
            cor_border = "rgba(239,68,68,0.25)"

        lista_lojas_html += f"""
        <div style="
            display:flex; align-items:center; gap:10px;
            padding:10px 16px; border-radius:10px;
            background:{cor_bg}; border:1px solid {cor_border};
        ">
            <span style="width:10px;height:10px;border-radius:50%;background:{cor_dot};display:inline-block;flex-shrink:0;"></span>
            <span style="font-size:14px;font-weight:500;color:#e2e8f0;">{loja}</span>
        </div>
        """

    for loja, info in sorted(dados_lojas.items()):
        ativo = info["dados"].get("ativo", False)
        ultima = info["ultima_atualizacao"]

        diff = (agora - ultima).total_seconds()
        desatualizado = diff > 120

        if not ativo:
            status_text = "OFFLINE"
            dot = "🔴"
            badge_bg = "rgba(239,68,68,0.15)"
            badge_color = "#fca5a5"
            card_border = "rgba(239,68,68,0.3)"
        elif desatualizado:
            status_text = "SEM RESPOSTA"
            dot = "🟡"
            badge_bg = "rgba(234,179,8,0.15)"
            badge_color = "#fde047"
            card_border = "rgba(234,179,8,0.3)"
        else:
            status_text = "ONLINE"
            dot = "🟢"
            badge_bg = "rgba(34,197,94,0.15)"
            badge_color = "#86efac"
            card_border = "rgba(34,197,94,0.3)"

        tempo_str = ultima.strftime("%d/%m/%Y %H:%M:%S")

        cards += f"""
        <div style="
            background:linear-gradient(135deg, rgba(30,41,59,0.8), rgba(15,23,42,0.9));
            border:1px solid {card_border};
            border-radius:16px; padding:24px;
            backdrop-filter:blur(10px);
            transition:transform 0.2s, box-shadow 0.2s;
        " onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 40px rgba(0,0,0,0.3)'"
           onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
            <div style="font-size:16px;font-weight:700;color:#f1f5f9;margin-bottom:12px;">{loja}</div>
            <div style="
                display:inline-flex;align-items:center;gap:6px;
                background:{badge_bg};color:{badge_color};
                padding:4px 12px;border-radius:20px;font-size:13px;font-weight:600;
                margin-bottom:12px;
            ">{dot} {status_text}</div>
            <div style="font-size:12px;color:#94a3b8;">🕐 {tempo_str}</div>
        </div>
        """

    if not dados_lojas:
        cards = """<div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:#64748b;font-size:15px;">
            <div style="font-size:48px;margin-bottom:16px;">📡</div>
            Nenhuma loja enviou dados ainda...
        </div>"""

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monitoramento VR</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <meta http-equiv="refresh" content="30">
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{
                font-family:'Inter',system-ui,sans-serif;
                background:linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                min-height:100vh; color:#e2e8f0;
            }}
            .container {{ max-width:1200px; margin:0 auto; padding:32px 24px; }}
            h1 {{
                font-size:28px; font-weight:800; text-align:center;
                background:linear-gradient(135deg, #60a5fa, #a78bfa, #60a5fa);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:8px;
            }}
            .subtitle {{ text-align:center; color:#64748b; font-size:13px; margin-bottom:32px; }}
            .stats {{
                display:flex; justify-content:center; gap:16px;
                flex-wrap:wrap; margin-bottom:40px;
            }}
            .stat {{
                padding:16px 32px; border-radius:14px; text-align:center;
                backdrop-filter:blur(10px); min-width:140px;
            }}
            .stat-total {{ background:rgba(96,165,250,0.1); border:1px solid rgba(96,165,250,0.25); }}
            .stat-online {{ background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.25); }}
            .stat-offline {{ background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.25); }}
            .stat-number {{ font-size:32px; font-weight:800; line-height:1; }}
            .stat-total .stat-number {{ color:#60a5fa; }}
            .stat-online .stat-number {{ color:#4ade80; }}
            .stat-offline .stat-number {{ color:#f87171; }}
            .stat-label {{ font-size:12px; color:#94a3b8; margin-top:4px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }}
            .section-title {{
                font-size:18px; font-weight:700; color:#cbd5e1;
                margin-bottom:20px; display:flex; align-items:center; gap:8px;
            }}
            .grid {{
                display:grid;
                grid-template-columns:repeat(auto-fill, minmax(260px, 1fr));
                gap:16px; margin-bottom:48px;
            }}
            .lojas-grid {{
                display:grid;
                grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));
                gap:10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ Monitoramento VR-Concentrador</h1>
            <div class="subtitle">Atualização automática a cada 30s</div>

            <div class="stats">
                <div class="stat stat-total">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat stat-online">
                    <div class="stat-number">{online}</div>
                    <div class="stat-label">Online</div>
                </div>
                <div class="stat stat-offline">
                    <div class="stat-number">{offline}</div>
                    <div class="stat-label">Offline</div>
                </div>
            </div>

            <div class="section-title">📊 Status das Lojas</div>
            <div class="grid">{cards}</div>

            <div class="section-title">🏪 Lojas Esperadas</div>
            <div class="lojas-grid">{lista_lojas_html}</div>
        </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
