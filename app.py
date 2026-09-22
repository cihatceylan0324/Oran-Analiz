import streamlit as st
import pandas as pd
import requests

# Sayfa Yapılandırması
st.set_page_config(page_title="Tahmin Paneli", page_icon="⚽", layout="wide")

# Özel CSS Tasarımı
st.markdown("""
<style>
    :root {
        --bg: #0d1117;
        --panel: #151b23;
        --panel2: #1c2530;
        --line: #2a3542;
        --text: #e6edf3;
        --muted: #8b98a5;
        --accent: #3fb950;
        --accent2: #58a6ff;
        --warn: #e3b341;
        --danger: #f85149;
    }
    .main { background-color: var(--bg); color: var(--text); }
    .stMetric { background-color: var(--panel); padding: 10px; border-radius: 8px; border: 1px solid var(--line); }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Gelişmiş Tahmin ve Oran Analiz Paneli")
st.markdown("Poisson modeli · H2H · Bet365 oran karşılaştırması · Esnek Oranlı Geçmiş Maç Arama")

# API Ayarları
API_KEYS = [
    "3b90f0de19091dbf6593732af60ccb25",
    "8782d0553955500b2d68552bfa5fe531c"
]
BASE_URL = "https://v3.football.api-sports.io"
BET365_ID = 8

# Lig ve Sezon Seçim Paneli
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    league_id = st.selectbox("Lig Seç", [
        (203, "Süper Lig (Türkiye)"),
        (39, "Premier League"),
        (140, "La Liga"),
        (135, "Serie A"),
        (78, "Bundesliga"),
        (61, "Ligue 1")
    ], format_func=lambda x: x[1])[0]

with col2:
    season = st.selectbox("Sezon Seç", [2024, 2023, 2022], index=0)

with col3:
    st.write("")
    yukle_btn = st.button("Maçları Yükle", use_container_width=True)

# API İstek Fonksiyonu
def api_get(endpoint, params):
    url = f"{BASE_URL}{endpoint}"
    for key in API_KEYS:
        headers = {"x-apisports-key": key}
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            data = res.json()
            if "errors" in data and data["errors"]:
                continue
            return data
        except:
            continue
    return None

st.markdown("---")

# --- ESNEK ORAN ARAMA BÖLÜMÜ (Tek veya Çoklu Oran) ---
st.subheader("🔍 Tek veya Çoklu Oranlı Maç Arama")
st.markdown("MS1, MS0 veya MS2 değerlerinden dilediğini (istersen sadece tek bir oranı) doldurarak tarama yapabilirsin. Boş bıraktığın oranlar eşleşmede dikkate alınmaz.")

sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
with sc1:
    h_hedef = st.number_input("MS1 (Ev)", value=0.0, step=0.01, format="%.2f")
with sc2:
    d_hedef = st.number_input("MS0 (Beraberlik)", value=0.0, step=0.01, format="%.2f")
with sc3:
    a_hedef = st.number_input("MS2 (Deplasman)", value=0.0, step=0.01, format="%.2f")
with sc4:
    tolerans = st.selectbox("Tolerans (±)", [0.05, 0.10, 0.25, 0.50], index=1)
with sc5:
    limit = st.selectbox("Maç Sınırı", [20, 50, 100], index=0)
with sc6:
    st.write("")
    ara_btn = st.button("Orana Göre Ara", use_container_width=True)

if ara_btn:
    if h_hedef == 0.0 and d_hedef == 0.0 and a_hedef == 0.0:
        st.warning("Lütfen en az bir oran alanına değer girin.")
    else:
        with st.spinner("Sezon maçları ve oranlar taranıyor..."):
            data = api_get("/fixtures", {"league": league_id, "season": season})
            if data and "response" in data:
                ft_matches = [f for f in data["response"] if f["fixture"]["status"]["short"] == "FT"][:limit]
                bulunanlar = []
                
                progress_bar = st.progress(0)
                for i, f in enumerate(ft_matches):
                    progress_bar.progress((i + 1) / len(ft_matches))
                    fix_id = f["fixture"]["id"]
                    odds_data = api_get("/odds", {"fixture": fix_id, "bookmaker": BET365_ID})
                    
                    if not odds_data or not odds_data.get("response"):
                        continue
                    
                    bookmakers = odds_data["response"][0].get("bookmakers", [])
                    bet365 = next((b for b in bookmakers if b["id"] == BET365_ID), None)
                    if not bet365:
                        continue
                        
                    mw = next((b for b in bet365.get("bets", []) if b["name"] == "Match Winner"), None)
                    if not mw:
                        continue
                        
                    values = mw.get("values", [])
                    h_odd = next((float(v["odd"]) for v in values if v["value"] == "Home"), None)
                    d_odd = next((float(v["odd"]) for v in values if v["value"] == "Draw"), None)
                    a_odd = next((float(v["odd"]) for v in values if v["value"] == "Away"), None)
                    
                    if h_odd is None or d_odd is None or a_odd is None:
                        continue
                        
                    # Esnek Karşılaştırma (0.0 olan / boş bırakılan alanlar filtrelenmez)
                    match_h = h_hedef == 0.0 or abs(h_odd - h_hedef) <= tolerans
                    match_d = d_hedef == 0.0 or abs(d_odd - d_hedef) <= tolerans
                    match_a = a_hedef == 0.0 or abs(a_odd - a_hedef) <= tolerans
                    
                    if match_h and match_d and match_a:
                        bulunanlar.append({
                            "Tarih": f["fixture"]["date"][:10],
                            "Ev Sahibi": f["teams"]["home"]["name"],
                            "Deplasman": f["teams"]["away"]["name"],
                            "MS1": h_odd,
                            "MS0": d_odd,
                            "MS2": a_odd,
                            "Skor": f"{f['goals']['home']}-{f['goals']['away']}"
                        })
                
                progress_bar.empty()
                if bulunanlar:
                    st.success(f"{len(bulunanlar)} maç eşleşti!")
                    st.dataframe(pd.DataFrame(bulunanlar), use_container_width=True)
                else:
                    st.info("Bu kriterlere ve toleransa uygun maç bulunamadı.")

st.markdown("---")
