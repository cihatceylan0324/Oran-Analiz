<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tek Kare Futbol | Eliteserien Analiz</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --accent-color: #22c55e;
            --accent-hover: #16a34a;
            --border-color: #334155;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        header h1 {
            font-size: 2.5rem;
            color: var(--accent-color);
            margin-bottom: 10px;
        }

        header p {
            color: var(--text-muted);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            text-align: center;
        }

        .stat-card h3 {
            font-size: 1rem;
            color: var(--text-muted);
            margin-bottom: 10px;
        }

        .stat-card p {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--accent-color);
        }

        .controls {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            gap: 15px;
            flex-wrap: wrap;
        }

        input, select {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 1rem;
            outline: none;
            flex: 1;
            min-width: 200px;
        }

        input:focus, select:focus {
            border-color: var(--accent-color);
        }

        .table-container {
            background-color: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border-color);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            white-space: nowrap;
        }

        th, td {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background-color: rgba(255, 255, 255, 0.05);
            color: var(--accent-color);
            font-weight: 600;
        }

        tr:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }

        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: bold;
        }

        .badge-yes {
            background-color: rgba(34, 197, 94, 0.2);
            color: #4ade80;
        }

        .badge-no {
            background-color: rgba(239, 68, 68, 0.2);
            color: #f87171;
        }
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>⚽ Tek Kare Futbol</h1>
            <p>Norveç Eliteserien Ligi Maç Verileri ve İstatistikleri</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Toplam Maç</h3>
                <p id="totalMatches">0</p>
            </div>
            <div class="stat-card">
                <h3>Atılan Toplam Gol</h3>
                <p id="totalGoals">0</p>
            </div>
            <div class="stat-card">
                <h3>Maç Başı Ortalama Gol</h3>
                <p id="avgGoals">0.00</p>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="Takım veya tarih ara (Örn: Brann, Rosenborg)..." onkeyup="filterTable()">
            <select id="seasonFilter" onchange="filterTable()">
                <option value="">Tüm Sezonlar</option>
                <option value="2026">2026</option>
                <option value="2025">2025</option>
                <option value="2024">2024</option>
            </select>
        </div>

        <div class="table-container">
            <table id="matchTable">
                <thead>
                    <tr>
                        <th>Tarih</th>
                        <th>Sezon</th>
                        <th>Ev Sahibi</th>
                        <th>Deplasman</th>
                        <th>MS Skor</th>
                        <th>İİY Skor</th>
                        <th>Toplam Gol</th>
                        <th>KG Var</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <!-- JavaScript ile doldurulacak -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Verilen ham veriyi diziye aktarıyoruz[cite: 1]
        const rawData = `2026-03-14,2026,Eliteserien,Ham-Kam,Viking,2 - 1,2 - 1,1,3,Evet
2026-03-14,2026,Eliteserien,Molde,Rosenborg,2 - 0,1 - 0,1,2,Yok
2026-03-15,2026,Eliteserien,Kristiansund BK,Brann,3 - 2,1 - 1,1,5,Evet
2026-03-15,2026,Eliteserien,Valerenga,Sandefjord,1 - 0,1 - 0,1,1,Yok
2026-03-15,2026,Eliteserien,Aalesund,Lillestrom,1 - 3,1 - 1,2,4,Evet
2026-03-15,2026,Eliteserien,KFUM Oslo,Start,2 - 0,0 - 0,1,2,Yok
2026-03-15,2026,Eliteserien,Tromso,Fredrikstad,4 - 0,1 - 0,1,4,Yok
2026-03-21,2026,Eliteserien,Start,Aalesund,1 - 1,0 - 1,X,2,Evet
2026-03-21,2026,Eliteserien,Viking,Molde,4 - 1,3 - 1,1,5,Evet
2026-03-22,2026,Eliteserien,Rosenborg,Valerenga,0 - 2,0 - 0,2,2,Yok
2026-03-22,2026,Eliteserien,Brann,Tromso,1 - 2,1 - 1,2,3,Evet
2026-03-22,2026,Eliteserien,Sandefjord,Sarpsborg 08 FF,0 - 2,0 - 2,2,2,Yok
2026-03-22,2026,Eliteserien,Fredrikstad,KFUM Oslo,3 - 1,3 - 1,1,4,Evet
2026-04-06,2026,Eliteserien,Valerenga,Viking,0 - 1,0 - 1,2,1,Yok
2026-04-06,2026,Eliteserien,Kristiansund BK,Bodo/Glimt,0 - 3,0 - 2,2,3,Yok
2026-04-06,2026,Eliteserien,Molde,Lillestrom,0 - 1,0 - 0,2,1,Yok
2026-04-06,2026,Eliteserien,Sarpsborg 08 FF,Start,1 - 1,1 - 1,X,2,Evet
2026-04-06,2026,Eliteserien,Ham-Kam,Brann,1 - 5,0 - 2,2,6,Evet
2026-04-06,2026,Eliteserien,Tromso,Rosenborg,2 - 0,1 - 0,1,2,Yok
2026-04-07,2026,Eliteserien,Aalesund,Fredrikstad,2 - 3,1 - 1,2,5,Evet
2026-04-07,2026,Eliteserien,KFUM Oslo,Sandefjord,1 - 2,1 - 2,2,3,Evet
2026-04-11,2026,Eliteserien,Lillestrom,Start,3 - 1,2 - 0,1,4,Evet
2026-04-11,2026,Eliteserien,Tromso,Kristiansund BK,2 - 0,0 - 0,1,2,Yok
2026-04-11,2026,Eliteserien,Viking,Bodo/Glimt,5 - 0,3 - 0,1,5,Yok
2026-04-12,2026,Eliteserien,Rosenborg,Sarpsborg 08 FF,2 - 1,1 - 1,1,3,Evet
2026-04-12,2026,Eliteserien,Molde,Ham-Kam,4 - 1,3 - 0,1,5,Evet
2026-04-12,2026,Eliteserien,Aalesund,KFUM Oslo,2 - 2,1 - 1,X,4,Evet
2026-04-12,2026,Eliteserien,Fredrikstad,Valerenga,1 - 1,0 - 1,X,2,Evet
2026-04-12,2026,Eliteserien,Brann,Sandefjord,0 - 1,0 - 1,2,1,Yok
2026-04-15,2026,Eliteserien,Tromso,Lillestrom,0 - 0,0 - 0,X,0,Yok
2026-04-15,2026,Eliteserien,Sarpsborg 08 FF,Bodo/Glimt,1 - 1,1 - 0,X,2,Evet
2026-04-18,2026,Eliteserien,Bodo/Glimt,Aalesund,3 - 0,1 - 0,1,3,Yok
2026-04-18,2026,Eliteserien,Sandefjord,Rosenborg,0 - 0,0 - 0,X,0,Yok
2026-04-18,2026,Eliteserien,Viking,Brann,3 - 2,2 - 1,1,5,Evet
2026-04-19,2026,Eliteserien,Valerenga,Lillestrom,0 - 2,0 - 0,2,2,Yok
2026-04-19,2026,Eliteserien,Kristiansund BK,Fredrikstad,2 - 0,0 - 0,1,2,Yok
2026-04-19,2026,Eliteserien,Sarpsborg 08 FF,Tromso,0 - 1,0 - 0,2,1,Yok
2026-04-19,2026,Eliteserien,Ham-Kam,KFUM Oslo,4 - 0,2 - 0,1,4,Yok
2026-04-19,2026,Eliteserien,Start,Molde,1 - 1,1 - 0,X,2,Evet
2026-04-25,2026,Eliteserien,Fredrikstad,Viking,1 - 2,0 - 1,2,3,Evet
2026-04-25,2026,Eliteserien,Rosenborg,Brann,1 - 1,1 - 1,X,2,Evet
2026-04-26,2026,Eliteserien,Molde,Valerenga,5 - 1,1 - 1,1,6,Evet
2026-04-26,2026,Eliteserien,Tromso,Sandefjord,3 - 1,2 - 0,1,4,Evet
2026-04-26,2026,Eliteserien,Aalesund,Kristiansund BK,1 - 1,0 - 0,X,2,Evet
2026-04-26,2026,Eliteserien,KFUM Oslo,Sarpsborg 08 FF,1 - 0,1 - 0,1,1,Yok
2026-04-26,2026,Eliteserien,Ham-Kam,Start,2 - 1,0 - 0,1,3,Evet
2026-04-26,2026,Eliteserien,Lillestrom,Bodo/Glimt,0 - 2,0 - 1,2,2,Yok
2026-04-29,2026,Eliteserien,Tromso,Brann,0 - 5,0 - 3,2,5,Yok
2026-04-30,2026,Eliteserien,Bodo/Glimt,Start,5 - 0,2 - 0,1,5,Yok
2026-05-01,2026,Eliteserien,Viking,Rosenborg,3 - 0,2 - 0,1,3,Yok
2026-05-02,2026,Eliteserien,Brann,Fredrikstad,3 - 1,1 - 0,1,4,Evet
2026-05-03,2026,Eliteserien,Lillestrom,Sarpsborg 08 FF,4 - 0,2 - 0,1,4,Yok
2026-05-03,2026,Eliteserien,Kristiansund BK,Ham-Kam,1 - 1,0 - 0,X,2,Evet
2026-05-03,2026,Eliteserien,Sandefjord,Aalesund,1 - 0,0 - 0,1,1,Yok
2026-05-03,2026,Eliteserien,Start,Tromso,1 - 1,0 - 1,X,2,Evet
2026-05-03,2026,Eliteserien,Valerenga,KFUM Oslo,2 - 2,1 - 1,X,4,Evet
2026-05-04,2026,Eliteserien,Bodo/Glimt,Molde,0 - 1,0 - 1,2,1,Yok
2026-05-08,2026,Eliteserien,Ham-Kam,Valerenga,1 - 0,1 - 0,1,1,Yok
2026-05-09,2026,Eliteserien,Sarpsborg 08 FF,Fredrikstad,2 - 1,1 - 1,1,3,Evet
2026-05-10,2026,Eliteserien,Rosenborg,Lillestrom,2 - 0,2 - 0,1,2,Yok
2026-05-10,2026,Eliteserien,Tromso,Molde,2 - 0,0 - 0,1,2,Yok
2026-05-10,2026,Eliteserien,Sandefjord,Kristiansund BK,2 - 0,1 - 0,1,2,Yok
2026-05-10,2026,Eliteserien,KFUM Oslo,Viking,0 - 2,0 - 1,2,2,Yok
2026-05-16,2026,Eliteserien,Brann,KFUM Oslo,2 - 1,2 - 0,1,3,Evet
2026-05-16,2026,Eliteserien,Lillestrom,Sandefjord,3 - 1,1 - 0,1,4,Evet
2026-05-16,2026,Eliteserien,Molde,Kristiansund BK,1 - 0,1 - 0,1,1,Yok
2026-05-16,2026,Eliteserien,Rosenborg,Aalesund,2 - 3,1 - 1,2,5,Evet
2026-05-16,2026,Eliteserien,Viking,Start,6 - 3,1 - 3,1,9,Evet
2026-05-16,2026,Eliteserien,Fredrikstad,Ham-Kam,2 - 1,2 - 0,1,3,Evet
2026-05-16,2026,Eliteserien,Bodo/Glimt,Tromso,5 - 0,1 - 0,1,5,Yok
2026-05-16,2026,Eliteserien,Valerenga,Sarpsborg 08 FF,3 - 2,2 - 2,1,5,Evet
2026-05-20,2026,Eliteserien,Start,Bodo/Glimt,1 - 4,1 - 2,2,5,Evet
2026-05-20,2026,Eliteserien,Lillestrom,Kristiansund BK,1 - 2,0 - 1,2,3,Evet
2026-05-20,2026,Eliteserien,Aalesund,Brann,2 - 1,1 - 0,1,3,Evet
2026-05-24,2026,Eliteserien,Bodo/Glimt,Brann,3 - 1,2 - 0,1,4,Evet
2026-05-24,2026,Eliteserien,Kristiansund BK,Viking,1 - 2,0 - 1,2,3,Evet
2026-05-25,2026,Eliteserien,Start,Valerenga,2 - 0,2 - 0,1,2,Yok
2026-05-25,2026,Eliteserien,Tromso,Aalesund,1 - 1,1 - 0,X,2,Evet
2026-05-25,2026,Eliteserien,Sarpsborg 08 FF,Molde,2 - 1,1 - 1,1,3,Evet
2026-05-25,2026,Eliteserien,KFUM Oslo,Rosenborg,2 - 0,2 - 0,1,2,Yok
2026-05-25,2026,Eliteserien,Ham-Kam,Lillestrom,2 - 0,1 - 0,1,2,Yok
2026-05-25,2026,Eliteserien,Sandefjord,Fredrikstad,1 - 1,0 - 0,X,2,Evet
2026-05-29,2026,Eliteserien,Brann,Sarpsborg 08 FF,1 - 2,1 - 2,2,3,Evet
2026-05-29,2026,Eliteserien,Valerenga,Kristiansund BK,3 - 1,1 - 0,1,4,Evet
2026-05-29,2026,Eliteserien,Rosenborg,Bodo/Glimt,2 - 2,1 - 1,X,4,Evet
2026-05-29,2026,Eliteserien,Aalesund,Ham-Kam,2 - 2,1 - 1,X,4,Evet
2026-05-29,2026,Eliteserien,KFUM Oslo,Tromso,0 - 0,0 - 0,X,0,Yok
2026-05-29,2026,Eliteserien,Fredrikstad,Start,2 - 1,0 - 1,1,3,Evet
2026-05-30,2026,Eliteserien,Molde,Sandefjord,2 - 1,1 - 0,1,3,Evet
2026-07-11,2026,Eliteserien,Fredrikstad,Lillestrom,0 - 2,0 - 0,2,2,Yok
2026-07-11,2026,Eliteserien,Aalesund,Molde,2 - 2,1 - 2,X,4,Evet
2026-07-11,2026,Eliteserien,Tromso,Valerenga,4 - 0,3 - 0,1,4,Yok
2026-07-12,2026,Eliteserien,KFUM Oslo,Bodo/Glimt,0 - 2,0 - 1,2,2,Yok
2026-07-12,2026,Eliteserien,Brann,Start,2 - 1,0 - 0,1,3,Evet
2026-07-12,2026,Eliteserien,Rosenborg,Kristiansund BK,3 - 0,2 - 0,1,3,Yok
2026-07-12,2026,Eliteserien,Sandefjord,Ham-Kam,2 - 2,1 - 0,X,4,Evet
2026-07-12,2026,Eliteserien,Sarpsborg 08 FF,Viking,1 - 0,1 - 0,1,1,Yok
2026-07-16,2026,Eliteserien,Valerenga,Aalesund,6 - 1,3 - 0,1,7,Evet
2026-07-17,2026,Eliteserien,Bodo/Glimt,Fredrikstad,1 - 0,1 - 0,1,1,Yok
2026-07-18,2026,Eliteserien,Ham-Kam,Tromso,1 - 4,0 - 1,2,5,Evet
2026-07-18,2026,Eliteserien,Kristiansund BK,Sarpsborg 08 FF,0 - 0,0 - 0,X,0,Yok
2026-07-18,2026,Eliteserien,Lillestrom,KFUM Oslo,2 - 1,1 - 1,1,3,Evet
2026-07-18,2026,Eliteserien,Start,Rosenborg,0 - 3,0 - 1,2,3,Yok
2026-07-18,2026,Eliteserien,Molde,Brann,1 - 2,0 - 2,2,3,Evet
2026-07-18,2026,Eliteserien,Viking,Sandefjord,2 - 1,1 - 0,1,3,Evet
2026-07-22,2026,Eliteserien,Lillestrom,Viking,1 - 2,0 - 1,2,3,Evet
2026-07-22,2026,Eliteserien,Bodo/Glimt,Ham-Kam,3 - 0,1 - 0,1,3,Yok
2026-07-25,2026,Eliteserien,Kristiansund BK,Start,1 - 2,1 - 1,2,3,Evet
2026-07-26,2026,Eliteserien,Brann,Valerenga,2 - 3,0 - 3,2,5,Evet
2026-07-26,2026,Eliteserien,Sandefjord,Bodo/Glimt,0 - 3,0 - 1,2,3,Yok
2026-07-26,2026,Eliteserien,Sarpsborg 08 FF,Ham-Kam,1 - 0,1 - 0,1,1,Yok
2026-07-26,2026,Eliteserien,KFUM Oslo,Molde,2 - 4,1 - 1,2,6,Evet
2026-07-26,2026,Eliteserien,Aalesund,Viking,1 - 1,0 - 1,X,2,Evet
2026-07-27,2026,Eliteserien,Rosenborg,Fredrikstad,4 - 0,2 - 0,1,4,Yok
2026-07-31,2026,Eliteserien,Valerenga,Ham-Kam,0 - 3,0 - 1,2,3,Yok
2026-07-31,2026,Eliteserien,Bodo/Glimt,Lillestrom,4 - 0,2 - 0,1,4,Yok
2026-08-01,2026,Eliteserien,Fredrikstad,Sandefjord,1 - 0,1 - 0,1,1,Yok
2026-08-01,2026,Eliteserien,Start,Viking,0 - 3,0 - 3,2,3,Yok
2026-08-02,2026,Eliteserien,Molde,Sarpsborg 08 FF,3 - 3,1 - 1,X,6,Evet
2026-08-02,2026,Eliteserien,Aalesund,Tromso,2 - 6,1 - 1,2,8,Evet
2026-08-02,2026,Eliteserien,KFUM Oslo,Kristiansund BK,2 - 1,2 - 0,1,3,Evet
2026-08-02,2026,Eliteserien,Brann,Rosenborg,3 - 2,1 - 0,1,5,Evet
2026-08-07,2026,Eliteserien,Sandefjord,KFUM Oslo,0 - 1,0 - 1,2,1,Yok
2026-08-08,2026,Eliteserien,Valerenga,Bodo/Glimt,1 - 2,0 - 1,2,3,Evet
2026-08-08,2026,Eliteserien,Viking,Sarpsborg 08 FF,2 - 1,1 - 0,1,3,Evet
2026-08-08,2026,Eliteserien,Start,Fredrikstad,0 - 1,0 - 1,2,1,Yok
2026-08-09,2026,Eliteserien,Lillestrom,Rosenborg,0 - 2,0 - 1,2,2,Yok
2026-08-09,2026,Eliteserien,Ham-Kam,Aalesund,1 - 1,0 - 1,X,2,Evet
2026-08-09,2026,Eliteserien,Kristiansund BK,Molde,2 - 1,1 - 0,1,3,Evet
2026-08-14,2026,Eliteserien,Rosenborg,Viking,2 - 1,1 - 0,1,3,Evet
2026-08-15,2026,Eliteserien,KFUM Oslo,Lillestrom,1 - 1,0 - 0,X,2,Evet
2026-08-16,2026,Eliteserien,Aalesund,Valerenga,5 - 5,4 - 2,X,10,Evet
2026-08-16,2026,Eliteserien,Brann,Ham-Kam,3 - 0,1 - 0,1,3,Yok
2026-08-16,2026,Eliteserien,Molde,Tromso,3 - 2,1 - 0,1,5,Evet
2026-08-16,2026,Eliteserien,Sarpsborg 08 FF,Sandefjord,1 - 2,1 - 1,2,3,Evet
2026-08-16,2026,Eliteserien,Fredrikstad,Kristiansund BK,1 - 0,1 - 0,1,1,Yok
2026-08-30,2026,Eliteserien,Bodo/Glimt,Rosenborg,4 - 2,1 - 1,1,6,Evet
2026-08-30,2026,Eliteserien,Tromso,Sarpsborg 08 FF,0 - 0,0 - 0,X,0,Yok
2026-08-30,2026,Eliteserien,Valerenga,Molde,3 - 4,3 - 4,2,7,Evet
2026-08-30,2026,Eliteserien,Sandefjord,Brann,0 - 0,0 - 0,X,0,Yok
2026-08-30,2026,Eliteserien,Start,KFUM Oslo,4 - 1,2 - 1,1,5,Evet
2026-08-30,2026,Eliteserien,Viking,Aalesund,2 - 1,0 - 1,1,3,Evet
2026-08-30,2026,Eliteserien,Ham-Kam,Kristiansund BK,2 - 2,0 - 0,X,4,Evet
2026-08-30,2026,Eliteserien,Lillestrom,Fredrikstad,1 - 4,1 - 2,2,5,Evet
2026-09-04,2026,Eliteserien,Aalesund,Start,2 - 0,2 - 0,1,2,Yok
2026-09-04,2026,Eliteserien,Fredrikstad,Bodo/Glimt,1 - 2,0 - 1,2,3,Evet
2026-09-04,2026,Eliteserien,Sandefjord,Viking,1 - 1,0 - 0,X,2,Evet
2026-09-05,2026,Eliteserien,Rosenborg,Ham-Kam,4 - 0,1 - 0,1,4,Yok
2026-09-05,2026,Eliteserien,Brann,Lillestrom,1 - 2,0 - 2,2,3,Evet
2026-09-06,2026,Eliteserien,Molde,KFUM Oslo,2 - 0,1 - 0,1,2,Yok
2026-09-06,2026,Eliteserien,Sarpsborg 08 FF,Valerenga,2 - 2,1 - 0,X,4,Evet
2026-09-06,2026,Eliteserien,Kristiansund BK,Tromso,2 - 0,1 - 0,1,2,Yok
2026-09-12,2026,Eliteserien,Lillestrom,Valerenga,2 - 0,1 - 0,1,2,Yok
2026-09-12,2026,Eliteserien,Rosenborg,Tromso,5 - 3,4 - 0,1,8,Evet
2026-09-13,2026,Eliteserien,Viking,Kristiansund BK,8 - 1,5 - 1,1,9,Evet
2026-09-13,2026,Eliteserien,Start,Brann,2 - 0,1 - 0,1,2,Yok
2026-09-13,2026,Eliteserien,KFUM Oslo,Aalesund,2 - 1,2 - 1,1,3,Evet
2026-09-13,2026,Eliteserien,Ham-Kam,Molde,1 - 5,0 - 1,2,6,Evet
2026-09-13,2026,Eliteserien,Fredrikstad,Sarpsborg 08 FF,1 - 1,1 - 1,X,2,Evet
2026-09-14,2026,Eliteserien,Bodo/Glimt,Sandefjord,3 - 2,1 - 0,1,5,Evet
2026-09-18,2026,Eliteserien,Sarpsborg 08 FF,KFUM Oslo,1 - 3,1 - 2,2,4,Evet
2026-09-19,2026,Eliteserien,Kristiansund BK,Rosenborg,1 - 3,1 - 1,2,4,Evet
2026-09-19,2026,Eliteserien,Molde,Aalesund,1 - 2,0 - 2,2,3,Evet
2026-09-20,2026,Eliteserien,Valerenga,Fredrikstad,1 - 1,0 - 0,X,2,Evet
2026-09-20,2026,Eliteserien,Tromso,Ham-Kam,3 - 2,1 - 1,1,5,Evet
2026-09-20,2026,Eliteserien,Sandefjord,Start,3 - 0,0 - 0,1,3,Yok
2026-09-20,2026,Eliteserien,Viking,Lillestrom,3 - 0,2 - 0,1,3,Yok
2026-09-20,2026,Eliteserien,Brann,Bodo/Glimt,2 - 1,1 - 1,1,3,Evet`;

        let matches = [];

        // Veriyi parse etme
        function parseData() {
            const lines = rawData.trim().split('\n');
            matches = lines.map(line => {
                const parts = line.split(',');
                return {
                    date: parts[0],
                    season: parts[1],
                    league: parts[2],
                    home: parts[3],
                    away: parts[4],
                    score: parts[5],
                    htScore: parts[6],
                    result: parts[7],
                    totalGoals: parseInt(parts[8]),
                    btts: parts[9].trim()
                };
            });
        }

        // Tabloyu ve istatistikleri güncelleme
        function updateUI(filteredMatches) {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            let totalGoals = 0;

            filteredMatches.forEach(match => {
                totalGoals += match.totalGoals;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${match.date}</td>
                    <td>${match.season}</td>
                    <td><strong>${match.home}</strong></td>
                    <td><strong>${match.away}</strong></td>
                    <td>${match.score}</td>
                    <td>${match.htScore}</td>
                    <td>${match.totalGoals}</td>
                    <td><span class="badge ${match.btts === 'Evet' ? 'badge-yes' : 'badge-no'}">${match.btts}</span></td>
                `;
                tbody.appendChild(tr);
            });

            // İstatistik Kartları
            document.getElementById('totalMatches').innerText = filteredMatches.length;
            document.getElementById('totalGoals').innerText = totalGoals;
            document.getElementById('avgGoals').innerText = filteredMatches.length > 0 ? (totalGoals / filteredMatches.length).toFixed(2) : '0.00';
        }

        // Arama ve Filtreleme Fonksiyonu
        function filterTable() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const seasonTerm = document.getElementById('seasonFilter').value;

            const filtered = matches.filter(match => {
                const matchesSearch = match.home.toLowerCase().includes(searchTerm) || 
                                      match.away.toLowerCase().includes(searchTerm) || 
                                      match.date.includes(searchTerm);
                const matchesSeason = seasonTerm === "" || match.season === seasonTerm;

                return matchesSearch && matchesSeason;
            });

            updateUI(filtered);
        }

        // Sayfa yüklendiğinde çalıştır
        parseData();
        updateUI(matches);
    </script>
</body>
</html>
