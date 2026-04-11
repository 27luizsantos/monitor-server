html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="15">
    <title>Monitoramento VR-Concentrador</title>

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', system-ui;
            background: #0f1117;
            color: #e1e4e8;
        }}

        /* TOPO */
        .topbar {{
            background: #1a1d27;
            border-bottom: 1px solid #2d3139;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .topbar h1 {{
            font-size: 1.3rem;
        }}

        .topbar span {{
            color: #3b82f6;
        }}

        .summary {{
            display: flex;
            gap: 10px;
        }}

        .pill {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .pill.total {{ background: #23272f; color: #94a3b8; }}
        .pill.up {{ background: #0d3320; color: #4ade80; }}
        .pill.down {{ background: #3b1219; color: #f87171; }}

        /* LISTA DE LOJAS */
        .lojas-box {{
            padding: 20px 30px;
        }}

        .lojas-box h2 {{
            margin-bottom: 12px;
            font-size: 1rem;
            color: #94a3b8;
        }}

        .lojas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 8px;
        }}

        .loja-item {{
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .loja-online {{
            background: rgba(74, 222, 128, 0.1);
            color: #4ade80;
        }}

        .loja-offline {{
            background: rgba(248, 113, 113, 0.1);
            color: #f87171;
        }}

        /* CARDS */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding: 20px 30px;
        }}

        .card {{
            background: #1a1d27;
            border: 1px solid #2d3139;
            border-radius: 12px;
            padding: 20px;
        }}

        .card.online {{ border-left: 4px solid #4ade80; }}
        .card.offline {{ border-left: 4px solid #f87171; }}
        .card.warning {{ border-left: 4px solid #facc15; }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}

        .status-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
        }}

        .status-badge.online {{ background: #0d3320; color: #4ade80; }}
        .status-badge.offline {{ background: #3b1219; color: #f87171; }}
        .status-badge.warning {{ background: #3b2f08; color: #facc15; }}

        .details {{
            margin-top: 10px;
            font-size: 0.85rem;
        }}

        .timestamp {{
            margin-top: 10px;
            font-size: 0.7rem;
            color: #4b5563;
        }}
    </style>
</head>

<body>

    <div class="topbar">
        <h1><span>SÓ OFERTAS</span> · Monitoramento</h1>

        <div class="summary">
            <div class="pill total">{total} lojas</div>
            <div class="pill up">{online} online</div>
            <div class="pill down">{offline} offline</div>
        </div>
    </div>

    <!-- LISTA DE LOJAS -->
    <div class="lojas-box">
        <h2>Lojas Monitoradas</h2>
        <div class="lojas-grid">
            {lista_lojas_html}
        </div>
    </div>

    <!-- CARDS -->
    <div class="grid">
        {cards}
    </div>

</body>
</html>"""
