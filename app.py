import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Oran Aralığı Analiz Merkezi", page_icon="⚽", layout="wide")

# API-Football Anahtarınız
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"

# Maçkolik Tarzı Karanlık Tema Tasarımı (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e0f11;
        color: #ffffff;
    }
    .stNumberInput input, .stSelectbox div {
        background-color: #1a1b1e !important;
        color: #ffffff !important;
        border: 1px solid #2d2f34 !important;
        border-radius: 8px !important;
    }
    .summary-card {
        background-color: #121315;
        border: 1px solid #2e7d32;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    .match-card {
        background-color: #1a1b1e;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 15px;
        border: 1px solid #2d2f34;
        font-family: sans-serif;
    }
    .odd-box {
        flex: 1;
        min-width: 60px;
        text-align: center;
        border-radius: 6px;
        overflow: hidden;
        font-size: 12px;
    }
    .odd-header {
        background-color: #1976D2;
        color: white;
        font-weight: bold;
        padding: 3px 0;
    }
    .odd-header-blue2 {
        background-color: #0288D1;
        color: white;
        font-weight: bold;
        padding: 3px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Oran Aralığı Filtreleme & Analiz Sistemi")

# 25 Ülke / Lig Haritası
LIGLER = {
    "🌐 TÜM LİGLER": "ALL",
    "🇹🇷 Türkiye - Süper Lig": 203,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere - Premier League": 39,
    "🇪🇸 İspanya - La Liga": 140,
    "🇮🇹 İtalya - Serie A": 135,
    "🇩🇪 Almanya - Bundesliga": 78,
    "🇫🇷 Fransa - Ligue 1": 61,
    "🇳🇱 Hollanda - Eredivisie": 88,
    "🇵🇹 Portekiz - Liga Portugal": 94,
    "🇧🇪 Belçika - Pro League": 144,
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya - Premiership": 179,
    "🇦🇹 Avusturya - Bundesliga": 218,
    "🇨🇭 İsviçre - Super League": 207,
    "🇬🇷 Yunanistan - Super League": 197,
    "🇩🇰 Danimarka - Superliga": 119,
    "🇸🇪 İsveç - Allsvenskan": 113,
    "🇳🇴 Norveç - Eliteserien": 103,
    "🇵🇱 Polonya - Ekstraklasa": 106,
    "🇨🇿 Çekya - 1. Liga": 345,
    "🇭🇷 Hırvatistan - HNL": 210,
    "🇧🇷 Brezilya - Série A": 71,
    "🇦🇷 Arjantin - Liga Profesional": 128,
    "🇺🇸 ABD - MLS": 253,
    "🇪🇺 UEFA Şampiyonlar Ligi": 2,
    "🇪🇺 UEFA Avrupa Ligi": 3,
    "🇪🇺 UEFA Konferans Ligi": 848
}

SEZON_SECENEKLERI = {
    "🗓️ TÜM SEZONLAR (2021 - 2026)": "ALL",
    "2026": 2026,
    "2025": 2025,
    "2024": 2024,
    "2023": 2023,
    "2022": 2022,
    "2021": 2021
}

# Veri Çekme Fonksiyonu
@st.cache_data(ttl=3600)
def api_tekil_lig_ve_sezon_getir(api_key, lig_id, sezon):
    headers = {
        'x-apisports-key': api_key,
        'x-rapidapi-key': api_key
    }
    
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={lig_id}&season={sezon}"
    try:
        res_fix = requests.get(url_fixtures, headers=headers)
        data_fix = res_fix.json()
        
        fixtures_raw = data_fix.get("response", [])
        if not fixtures_raw:
            return []

        odds_map = {}
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            url_odds = f"https://v3.football.api-sports.io/odds?league={lig_id}&season={sezon}&page={page}"
            res_odds = requests.get(url_odds, headers=headers)
            data_odds = res_odds.json()
            
            if "response" in data_odds and data_odds["response"]:
                for o_item in data_odds["response"]:
                    f_id = o_item["fixture"]["id"]
                    bookmakers = o_item.get("bookmakers", [])
                    if bookmakers:
                        bm = bookmakers[0]
                        bets = bm.get("bets", [])
                        m_odds = {}
                        for b in bets:
                            name = b.get("name")
                            values = b.get("values", [])
                            if name in ["Match Winner", "1X2 Market"]:
                                for v in values:
                                    if str(v["value"]).lower() in ["home", "1"]: m_odds["MS 1"] = float(v["odd"])
                                    elif str(v["value"]).lower() in ["draw", "x"]: m_odds["MS X"] = float(v["odd"])
                                    elif str(v["value"]).lower() in ["away", "2"]: m_odds["MS 2"] = float(v["odd"])
                            elif name in ["Goals Over/Under", "Second Half Goals Over/Under"]:
                                for v in values:
                                    if v["value"] == "Over 2.5": m_odds["2.5 Üst"] = float(v["odd"])
                                    elif v["value"] == "Under 2.5": m_odds["2.5 Alt"] = float(v["odd"])
                            elif name in ["Both Teams Score", "Both Teams To Score"]:
                                for v in values:
                                    if str(v["value"]).lower() in ["yes", "kg var"]: m_odds["KG Var"] = float(v["odd"])
                                    elif str(v["value"]).lower() in ["no", "kg yok"]: m_odds["KG Yok"] = float(v["odd"])
                        odds_map[f_id] = m_odds
            
            paging = data_odds.get("paging", {})
            total_pages = paging.get("total", 1)
            page += 1
            if page > 15:
                break

        maclar = []
        for item in fixtures_raw:
            f = item["fixture"]
            l = item["league"]
            t = item["teams"]
            g = item["goals"]
            score = item["score"]

            if f["status"]["short"] in ["FT", "AET", "PEN"]:
                ev_gol = g["home"] if g["home"] is not None else 0
                dep_gol = g["away"] if g["away"] is not None else 0
                toplam_gol = ev_gol + dep_gol

                ms_sonuc = "1" if ev_gol > dep_gol else ("2" if dep_gol > ev_gol else "X")
                kg_var = (ev_gol > 0) and (dep_gol > 0)

                f_id = f["id"]
                oranlar = odds_map.get(f_id, {})

                maclar.append({
                    "id": f_id,
                    "tarih": f["date"][:10],
                    "lig_adi": l["name"],
                    "ev_sahibi": t["home"]["name"],
                    "deplasman": t["away"]["name"],
                    "ms_skor": f"{ev_gol} - {dep_gol}",
                    "iy_skor": f"{score['halftime']['home'] or 0}-{score['halftime']['away'] or 0}",
                    "ms_sonuc": ms_sonuc,
                    "toplam_gol": toplam_gol,
                    "kg_var": kg_var,
                    "oranlar": oranlar
                })
        return maclar
    except Exception:
        return []

# Sol Menü / Filtreler
st.sidebar.header("🌍 Lig & Sezon Seçimi")
secilen_lig_key = st.sidebar.selectbox("Lig Seçin", list(LIGLER.keys()))
secilen_sezon_key = st.sidebar.selectbox("Sezon / Yıl Seçin", list(SEZON_SECENEKLERI.keys()))

st.sidebar.markdown("---")
st.sidebar.header("🎯 Oran Aralığı Belirleyin")

col_min, col_max = st.sidebar.columns(2)
min_oran = col_min.number_input("Min Oran", value=1.40, step=0.01, format="%.2f")
max_oran = col_max.number_input("Max Oran", value=2.40, step=0.01, format="%.2f")

target_ligler = [v for k, v in LIGLER.items() if v != "ALL"] if LIGLER[secilen_lig_key] == "ALL" else [LIGLER[secilen_lig_key]]
target_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if SEZON_SECENEKLERI[secilen_sezon_key] == "ALL" else [SEZON_SECENEKLERI[secilen_sezon_key]]

if min_oran >= max_oran:
    st.error("⚠️ Minimum oran, maksimum orandan küçük olmalıdır.")
else:
    yuklenen_maclar = []
    toplam_hedef = len(target_ligler) * len(target_sezonlar)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    tamamlanan = 0
    for l_id in target_ligler:
        for s_val in target_sezonlar:
            status_text.text(f"⏳ Veriler taranıyor ({tamamlanan + 1}/{toplam_hedef})...")
            m_list = api_tekil_lig_ve_sezon_getir(API_KEY, l_id, s_val)
            yuklenen_maclar.extend(m_list)
            tamamlanan += 1
            progress_bar.progress(tamamlanan / toplam_hedef)
            
    progress_bar.empty()
    status_text.empty()

    # Oran Aralığı Algoritması
    esleseler = []
    for mac in yuklenen_maclar:
        o = mac.get("oranlar", {})
        yakalanan_kategoriler = []
        
        for k_adi, val in o.items():
            if val is not None and min_oran <= val <= max_oran:
                yakalanan_kategoriler.append((k_adi, val))
        
        if yakalanan_kategoriler:
            mac["yakalananlar"] = yakalanan_kategoriler
            esleseler.append(mac)

    if not esleseler:
        st.warning(f"⚠️ Herhangi bir bahis seçeneğinde **{min_oran:.2f} - {max_oran:.2f}** aralığında orana sahip maç bulunamadı.")
    else:
        toplam = len(esleseler)
        
        # Hangi kategoride kaç defa geçtiğini hesapla
        kategori_sayaclari = {}
        for m in esleseler:
            for k_adi, _ in m["yakalananlar"]:
                kategori_sayaclari[k_adi] = kategori_sayaclari.get(k_adi, 0) + 1

        ozet_str = " • ".join([f"<b>{k}:</b> {v} Maç" for k, v in kategori_sayaclari.items()])

        # Özet Kartı
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 8px;">📊 [{min_oran:.2f} - {max_oran:.2f}] ARALIĞINDA ORANI OLAN MAÇLAR ({toplam} Maç)</div>
            <div style="font-size: 14px; color: #ffffff; margin-bottom: 10px;">
                <b>Aradaki Oranların Dağılımı:</b> {ozet_str}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Maç Kartları
        for m in esleseler:
            o = m.get("oranlar", {})
            yakalanan_turler = [k for k, _ in m["yakalananlar"]]

            def get_box_style(tur_adi, val):
                is_hit = tur_adi in yakalanan_turler
                bg_color = "#fbc02d" if is_hit else "#2d2f34"
                text_color = "#000000" if is_hit else "#ffffff"
                return f"background-color:{bg_color}; color:{text_color}; font-weight:bold; padding:6px 0;"

            html_card = f"""
            <div class="match-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2c30; padding-bottom: 10px; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 11px; color: #888; display: block;">{m['tarih']} • {m.get('lig_adi', 'Lig')}</span>
                        <span style="font-size: 16px; font-weight: bold; color: #fff;">{m['ev_sahibi']} - {m['deplasman']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="background-color: #000; color: #4caf50; font-size: 16px; font-weight: bold; padding: 4px 10px; border-radius: 6px;">{m['ms_skor']}</span>
                        <span style="font-size: 11px; color: #aaa; display: block; margin-top: 3px;">(İY {m['iy_skor']})</span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <div class="odd-box"><div class="odd-header">MS 1</div><div style="{get_box_style('MS 1', o.get('MS 1'))}">{o.get('MS 1') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header">MS X</div><div style="{get_box_style('MS X', o.get('MS X'))}">{o.get('MS X') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header">MS 2</div><div style="{get_box_style('MS 2', o.get('MS 2'))}">{o.get('MS 2') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ÜST</div><div style="{get_box_style('2.5 Üst', o.get('2.5 Üst'))}">{o.get('2.5 Üst') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ALT</div><div style="{get_box_style('2.5 Alt', o.get('2.5 Alt'))}">{o.get('2.5 Alt') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG VAR</div><div style="{get_box_style('KG Var', o.get('KG Var'))}">{o.get('KG Var') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG YOK</div><div style="{get_box_style('KG Yok', o.get('KG Yok'))}">{o.get('KG Yok') or '-'}</div></div>
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
