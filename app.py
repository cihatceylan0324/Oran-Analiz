import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Tüm Ligler Oran Analiz Merkezi", page_icon="⚽", layout="wide")

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

st.title("⚽ Küresel Birebir Oran Analiz Sistemi")

# 25 Ülke / Lig Haritası (API-Football ID'leri)
LIGLER = {
    "🌐 TÜM LİGLER (Tüm Ülkeler Süzgeci)": "ALL",
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

# Tekil Lig & Sezon Verisi Çeken Fonksiyon (Önbellekli)
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
            url_odds = f"https://v3.football.api-sports.io/odds?league={lig_id}&season={sezon}&bookmaker=1&page={page}"
            res_odds = requests.get(url_odds, headers=headers)
            data_odds = res_odds.json()
            
            if "response" in data_odds:
                for o_item in data_odds["response"]:
                    f_id = o_item["fixture"]["id"]
                    bookmakers = o_item.get("bookmakers", [])
                    if bookmakers:
                        bets = bookmakers[0].get("bets", [])
                        m_odds = {}
                        for b in bets:
                            name = b.get("name")
                            values = b.get("values", [])
                            if name == "Match Winner":
                                for v in values:
                                    if v["value"] == "Home": m_odds["ms1"] = float(v["odd"])
                                    elif v["value"] == "Draw": m_odds["ms0"] = float(v["odd"])
                                    elif v["value"] == "Away": m_odds["ms2"] = float(v["odd"])
                            elif name == "Goals Over/Under":
                                for v in values:
                                    if v["value"] == "Over 2.5": m_odds["ust_2_5"] = float(v["odd"])
                                    elif v["value"] == "Under 2.5": m_odds["alt_2_5"] = float(v["odd"])
                            elif name == "Both Teams Score":
                                for v in values:
                                    if v["value"] == "Yes": m_odds["kg_var"] = float(v["odd"])
                                    elif v["value"] == "No": m_odds["kg_yok"] = float(v["odd"])
                        odds_map[f_id] = m_odds
            
            paging = data_odds.get("paging", {})
            total_pages = paging.get("total", 1)
            page += 1
            if page > 10:
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
                oranlar = odds_map.get(f_id, {
                    "ms1": None, "ms0": None, "ms2": None,
                    "ust_2_5": None, "alt_2_5": None,
                    "kg_var": None, "kg_yok": None
                })

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
st.sidebar.header("🎯 Oran Filtreleri")

col1, col2, col3 = st.sidebar.columns(3)
ms1 = col1.number_input("MS 1", value=0.0, step=0.01, format="%.2f")
ms0 = col2.number_input("MS X", value=0.0, step=0.01, format="%.2f")
ms2 = col3.number_input("MS 2", value=0.0, step=0.01, format="%.2f")

col4, col5 = st.sidebar.columns(2)
ust_2_5 = col4.number_input("2.5 ÜST", value=0.0, step=0.01, format="%.2f")
alt_2_5 = col5.number_input("2.5 ALT", value=0.0, step=0.01, format="%.2f")

col6, col7 = st.sidebar.columns(2)
kg_var = col6.number_input("KG VAR", value=0.0, step=0.01, format="%.2f")
kg_yok = col7.number_input("KG YOK", value=0.0, step=0.01, format="%.2f")

# Taranacak Ligler ve Sezonlar Listesini Belirle
target_ligler = [v for k, v in LIGLER.items() if v != "ALL"] if LIGLER[secilen_lig_key] == "ALL" else [LIGLER[secilen_lig_key]]
target_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if SEZON_SECENEKLERI[secilen_sezon_key] == "ALL" else [SEZON_SECENEKLERI[secilen_sezon_key]]

kriterler = {
    "ms1": ms1 if ms1 > 0 else None,
    "ms0": ms0 if ms0 > 0 else None,
    "ms2": ms2 if ms2 > 0 else None,
    "ust_2_5": ust_2_5 if ust_2_5 > 0 else None,
    "alt_2_5": alt_2_5 if alt_2_5 > 0 else None,
    "kg_var": kg_var if kg_var > 0 else None,
    "kg_yok": kg_yok if kg_yok > 0 else None
}
aktif_filtreler = {k: v for k, v in kriterler.items() if v is not None}

if not aktif_filtreler:
    st.info("👈 Analiz yapmak için sol menüden en az 1 tane oran filtresi girin.")
else:
    yuklenen_maclar = []
    toplam_hedef = len(target_ligler) * len(target_sezonlar)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    tamamlanan = 0
    for l_id in target_ligler:
        for s_val in target_sezonlar:
            status_text.text(f"⏳ Veriler çekiliyor ({tamamlanan + 1}/{toplam_hedef})...")
            m_list = api_tekil_lig_ve_sezon_getir(API_KEY, l_id, s_val)
            yuklenen_maclar.extend(m_list)
            tamamlanan += 1
            progress_bar.progress(tamamlanan / toplam_hedef)
            
    progress_bar.empty()
    status_text.empty()

    # Filtre Eşleme
    esleseler = []
    for mac in yuklenen_maclar:
        o = mac.get("oranlar", {})
        if all(o.get(k) == v for k, v in aktif_filtreler.items()):
            esleseler.append(mac)

    if not esleseler:
        st.warning("⚠️ Taranan liglerde girilen oran kombinasyonuna uygun maç bulunamadı.")
    else:
        toplam = len(esleseler)
        ms1_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == '1')
        ms0_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == 'X')
        ms2_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == '2')
        ust_cnt = sum(1 for m in esleseler if m['toplam_gol'] > 2.5)
        kg_cnt = sum(1 for m in esleseler if m['kg_var'])

        en_cok_ms = "MS 1" if ms1_cnt >= max(ms0_cnt, ms2_cnt) else ("MS X" if ms0_cnt >= ms2_cnt else "MS 2")
        en_cok_yuzde = round((max(ms1_cnt, ms0_cnt, ms2_cnt) / toplam) * 100)

        # Yeşil Özet Kartı
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 8px;">📊 BİREBİR KÜRESEL ORAN ANALİZİ ({toplam} Maç Bulundu)</div>
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 12px; color: white;">
                🏆 En Çok Biten Sonuç: <span style="background-color: #2e7d32; color: white; padding: 4px 12px; border-radius: 6px;">{en_cok_ms} (%{en_cok_yuzde})</span>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_cnt/toplam*100)} ({ms1_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_cnt/toplam*100)} ({ms0_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_cnt/toplam*100)} ({ms2_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_cnt/toplam*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_cnt/toplam*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Maç Kartları
        for m in esleseler:
            o = m.get("oranlar", {})
            
            ms1_bg, ms1_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == '1' else ("#dcdcdc", "#222")
            ms0_bg, ms0_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == 'X' else ("#dcdcdc", "#222")
            ms2_bg, ms2_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == '2' else ("#dcdcdc", "#222")

            ust_bg, ust_fg = ("#2e7d32", "#fff") if m['toplam_gol'] > 2.5 else ("#dcdcdc", "#222")
            alt_bg, alt_fg = ("#2e7d32", "#fff") if m['toplam_gol'] <= 2.5 else ("#dcdcdc", "#222")

            kgv_bg, kgv_fg = ("#2e7d32", "#fff") if m['kg_var'] else ("#dcdcdc", "#222")
            kgy_bg, kgy_fg = ("#2e7d32", "#fff") if not m['kg_var'] else ("#dcdcdc", "#222")

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
                    <div class="odd-box"><div class="odd-header">1</div><div style="background-color:{ms1_bg}; color:{ms1_fg}; font-weight:bold; padding:6px 0;">{o.get('ms1') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header">X</div><div style="background-color:{ms0_bg}; color:{ms0_fg}; font-weight:bold; padding:6px 0;">{o.get('ms0') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header">2</div><div style="background-color:{ms2_bg}; color:{ms2_fg}; font-weight:bold; padding:6px 0;">{o.get('ms2') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ÜST</div><div style="background-color:{ust_bg}; color:{ust_fg}; font-weight:bold; padding:6px 0;">{o.get('ust_2_5') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ALT</div><div style="background-color:{alt_bg}; color:{alt_fg}; font-weight:bold; padding:6px 0;">{o.get('alt_2_5') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG VAR</div><div style="background-color:{kgv_bg}; color:{kgv_fg}; font-weight:bold; padding:6px 0;">{o.get('kg_var') or '-'}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG YOK</div><div style="background-color:{kgy_bg}; color:{kgy_fg}; font-weight:bold; padding:6px 0;">{o.get('kg_yok') or '-'}</div></div>
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
