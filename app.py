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





TOKEN = "8630570120:AAHUTphBpCTBOghKEGHRm-Z8nYQVB7vvhXA"
CHAT_ID = "8523564012"

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

    # 🔑 pega status anterior
    ultimo_status = dados_lojas.get(loja, {}).get("dados", {}).get("ativo", True)

    # 🚨 ALERTA SOMENTE SE MUDAR DE ONLINE → OFFLINE
    if ultimo_status and not ativo:
        enviar_telegram(f"🚨 {loja} está OFFLINE")

    # (opcional) voltou ao normal
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
    total = len(dados_lojas)
    online = sum(1 for info in dados_lojas.values() if info["dados"].get("ativo"))
    offline = total - online

    cards = ""
    lista_lojas_html = ""

    for loja in LOJAS_ESPERADAS:
        if loja in dados_lojas:
            cor = "#4ade80"  # verde
        else:
            cor = "#f87171"  # vermelho

        lista_lojas_html += f"""
        <div style="color: {cor}; font-weight: 600;">
            {loja}
        </div>
        """


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

   def gerar_html(total, online, offline, warning, lista_lojas_html, cards):
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

        /* ===== TOPBAR ===== */
        .topbar {{
            background: linear-gradient(135deg, #151720 0%, #1a1d28 100%);
            border-bottom: 1px solid #2d3139;
            padding: 20px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .topbar-brand {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .topbar-icon {{
            width: 42px; height: 42px;
            background: rgba(59,130,246,0.12);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
        }}
        .topbar-icon svg {{ width: 22px; height: 22px; color: #3b82f6; }}
        .topbar h1 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
            line-height: 1.2;
        }}
        .topbar h1 span {{ color: #3b82f6; }}
        .topbar-subtitle {{
            font-size: 0.72rem;
            color: #4b5563;
            margin-top: 2px;
        }}
        .summary {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .pill {{
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.78rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .pill svg {{ width: 14px; height: 14px; }}
        .pill.total {{ background: #1e2028; color: #94a3b8; }}
        .pill.up {{ background: #0d3320; color: #4ade80; }}
        .pill.down {{ background: #3b1219; color: #f87171; }}
        .pill.warn {{ background: #3b2f08; color: #facc15; }}

        /* ===== FILTER & VIEW BAR ===== */
        .toolbar {{
            padding: 20px 32px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .search-box {{
            position: relative;
        }}
        .search-box input {{
            background: #1e2028;
            border: 1px solid #2d3139;
            border-radius: 8px;
            padding: 8px 12px 8px 36px;
            color: #e1e4e8;
            font-size: 0.82rem;
            width: 260px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box input:focus {{ border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.15); }}
        .search-box svg {{
            position: absolute;
            left: 10px; top: 50%;
            transform: translateY(-50%);
            width: 16px; height: 16px;
            color: #4b5563;
        }}
        .filter-btns {{
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .filter-btns .filter-icon {{ color: #4b5563; margin-right: 4px; }}
        .filter-btn {{
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 500;
            border: none;
            cursor: pointer;
            transition: all 0.15s;
            background: #1e2028;
            color: #94a3b8;
        }}
        .filter-btn:hover {{ background: #262830; }}
        .filter-btn.active {{ background: #3b82f6; color: #fff; }}
        .view-toggle {{
            display: flex;
            border: 1px solid #2d3139;
            border-radius: 8px;
            overflow: hidden;
        }}
        .view-btn {{
            padding: 7px 10px;
            background: transparent;
            border: none;
            color: #4b5563;
            cursor: pointer;
            transition: all 0.15s;
            display: flex; align-items: center; justify-content: center;
        }}
        .view-btn:hover {{ color: #94a3b8; }}
        .view-btn.active {{ background: #3b82f6; color: #fff; }}
        .view-btn svg {{ width: 16px; height: 16px; }}
        .toolbar-right {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .countdown {{
            font-size: 0.78rem;
            color: #4b5563;
        }}
        .countdown span {{
            font-family: 'Courier New', monospace;
            font-weight: 700;
            color: #3b82f6;
        }}

        /* ===== TABLE VIEW ===== */
        .table-section {{
            padding: 20px 32px;
        }}
        .table-section h2 {{
            font-size: 0.88rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 12px;
        }}
        .store-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
            border: 1px solid #2d3139;
            border-radius: 10px;
            overflow: hidden;
        }}
        .store-table thead tr {{
            background: rgba(30,32,40,0.6);
            border-bottom: 1px solid #2d3139;
        }}
        .store-table th {{
            padding: 10px 16px;
            text-align: left;
            font-weight: 500;
            color: #4b5563;
            font-size: 0.75rem;
        }}
        .store-table td {{
            padding: 10px 16px;
            border-bottom: 1px solid rgba(45,49,57,0.5);
        }}
        .store-table tbody tr {{
            transition: background 0.15s;
        }}
        .store-table tbody tr:hover {{
            background: rgba(30,32,40,0.4);
        }}
        .store-table .name {{ font-weight: 500; color: #fff; }}
        .store-table .ip {{ font-family: monospace; color: #4b5563; }}
        .status-dot {{
            display: inline-block;
            width: 6px; height: 6px;
            border-radius: 50%;
            margin-right: 6px;
        }}
        .status-dot.on {{ background: #4ade80; }}
        .status-dot.off {{ background: #f87171; }}
        .status-dot.warn {{ background: #facc15; }}
        .status-badge {{
            font-size: 0.65rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-flex;
            align-items: center;
        }}
        .status-badge.online {{ background: #0d3320; color: #4ade80; }}
        .status-badge.offline {{ background: #3b1219; color: #f87171; }}
        .status-badge.warning {{ background: #3b2f08; color: #facc15; }}

        /* ===== CARD GRID ===== */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding: 20px 32px 32px;
        }}
        .card {{
            background: #1a1d27;
            border: 1px solid #2d3139;
            border-radius: 12px;
            padding: 20px;
            border-left-width: 4px;
            transition: transform 0.2s, box-shadow 0.2s;
            animation: slideUp 0.4s ease-out backwards;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.35);
        }}
        .card.online {{ border-left-color: #4ade80; }}
        .card.offline {{ border-left-color: #f87171; }}
        .card.warning {{ border-left-color: #facc15; }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .card-header-left {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .pulse-dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            animation: pulseDot 2s ease-in-out infinite;
        }}
        .pulse-dot.on {{ background: #4ade80; }}
        .pulse-dot.off {{ background: #f87171; }}
        .pulse-dot.warn {{ background: #facc15; }}
        .card-header svg {{ width: 16px; height: 16px; color: #4b5563; }}
        .card h3 {{
            font-size: 0.92rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 3px;
        }}
        .card .location {{
            font-size: 0.75rem;
            color: #4b5563;
            display: flex;
            align-items: center;
            gap: 4px;
            margin-bottom: 14px;
        }}
        .card .location svg {{ width: 12px; height: 12px; }}
        .details {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 14px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
        }}
        .detail-row .label {{ color: #4b5563; }}
        .detail-row .value {{ font-weight: 600; color: #94a3b8; }}
        .detail-row .value.ok {{ color: #4ade80; }}
        .detail-row .value.fail {{ color: #f87171; }}
        .timestamp {{
            font-size: 0.7rem;
            color: #374151;
            border-top: 1px solid #2d3139;
            padding-top: 10px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .timestamp svg {{ width: 12px; height: 12px; }}

        .empty {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #4b5563;
            font-size: 1rem;
        }}

        /* ===== ANIMATIONS ===== */
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseDot {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.35; }}
        }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 640px) {{
            .topbar, .toolbar, .grid, .table-section {{ padding-left: 16px; padding-right: 16px; }}
            .search-box input {{ width: 100%; }}
            .toolbar {{ flex-direction: column; align-items: stretch; }}
            .toolbar-right {{ justify-content: space-between; }}
        }}
    </style>
    <script>
        // Countdown timer
        let seconds = 15;
        setInterval(() => {{
            seconds--;
            const el = document.getElementById('countdown');
            if (el) el.textContent = seconds + 's';
            if (seconds <= 0) seconds = 15;
        }}, 1000);

        // Search filter
        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filter = document.querySelector('.filter-btn.active')?.dataset.filter || 'all';
            document.querySelectorAll('.card').forEach(card => {{
                const name = card.dataset.name?.toLowerCase() || '';
                const status = card.dataset.status || '';
                const matchSearch = name.includes(query);
                const matchFilter = filter === 'all' || status === filter;
                card.style.display = (matchSearch && matchFilter) ? '' : 'none';
            }});
            // Also filter table rows
            document.querySelectorAll('.store-table tbody tr').forEach(row => {{
                const name = row.dataset.name?.toLowerCase() || '';
                const status = row.dataset.status || '';
                const matchSearch = name.includes(query);
                const matchFilter = filter === 'all' || status === filter;
                row.style.display = (matchSearch && matchFilter) ? '' : 'none';
            }});
        }}

        function setFilter(btn) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCards();
        }}

        function setView(type) {{
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById('gridView').style.display = type === 'grid' ? 'grid' : 'none';
            document.getElementById('tableView').style.display = type === 'table' ? 'block' : 'none';
        }}
    </script>
</head>
<body>

    <!-- TOPBAR -->
    <div class="topbar">
        <div class="topbar-brand">
            <div class="topbar-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div>
                <h1><span>SÓ OFERTAS</span> · Monitoramento</h1>
                <div class="topbar-subtitle">VR-Concentrador · Atualização automática</div>
            </div>
        </div>
        <div class="summary">
            <span class="pill total">{total} lojas</span>
            <span class="pill up">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/></svg>
                {online} online
            </span>
            <span class="pill down">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55M5 12.55a10.94 10.94 0 0 1 5.17-2.39M10.71 5.05A16 16 0 0 1 22.56 9M1.42 9a15.91 15.91 0 0 1 4.7-2.88M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/></svg>
                {offline} offline
            </span>
        </div>
    </div>

    <!-- TOOLBAR -->
    <div class="toolbar">
        <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
            <div class="search-box">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" id="searchInput" placeholder="Buscar loja..." oninput="filterCards()">
            </div>
            <div class="filter-btns">
                <svg class="filter-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
                <button class="filter-btn active" data-filter="all" onclick="setFilter(this)">Todas</button>
                <button class="filter-btn" data-filter="online" onclick="setFilter(this)">Online</button>
                <button class="filter-btn" data-filter="offline" onclick="setFilter(this)">Offline</button>
                <button class="filter-btn" data-filter="warning" onclick="setFilter(this)">Alerta</button>
            </div>
        </div>
        <div class="toolbar-right">
            <div class="countdown">Atualização em <span id="countdown">15s</span></div>
            <div class="view-toggle">
                <button class="view-btn active" onclick="setView('grid')">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                </button>
                <button class="view-btn" onclick="setView('table')">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                </button>
            </div>
        </div>
    </div>

    <!-- TABLE VIEW (hidden by default) -->
    <div id="tableView" class="table-section" style="display:none;">
        <h2>Lojas Monitoradas</h2>
        {lista_lojas_html}
    </div>

    <!-- CARD GRID -->
    <div id="gridView" class="grid">
        {cards}
    </div>

</body>
</html>"""
    return html



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
