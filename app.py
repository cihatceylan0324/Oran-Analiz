import streamlit as st
import pandas as pd
import requests
import math

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

# Session State Tanımlamaları
if "selected_fixture" not in st.session_state:
    st.session_state.selected_fixture = None
if "fixtures_data" not in st.session_state:
    st.session_state.fixtures_data = []

# API İstek Fonksiyonu
def api_get(endpoint, params):
    url = f"{BASE_URL}{endpoint}"
    for key in API_KEYS:
        headers = {"x-apisports-key": key}
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            data = res.json()
            errors = data.get("errors", {})
            error_text = str(errors).lower()
            if errors and (any(k in error_text for k in ["limit", "quota", "rate", "suspend"])):
                continue
            return data
        except:
            continue
    return None

# --- ÜST KONTROL PANELİ (Lig, Sezon ve Maçları Yükle) ---
with st.container():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
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

    with col4:
        st.write("")
        if st.button("Key Durumu", use_container_width=True):
            st.info(f"{len(API_KEYS)} adet API Key tanımlı.")

if yukle_btn:
    with st.spinner("Maçlar yükleniyor..."):
        data = api_get("/fixtures", {"league": league_id, "season": season})
        if data and "response" in data:
            # Sadece tamamlanmış (FT) maçları al ve tarihe göre yeniden eskiye sırala
            fixtures = [f for f in data["response"] if f["fixture"]["status"]["short"] == "FT"]
            fixtures = sorted(fixtures, key=lambda x: x["fixture"]["date"], reverse=True)
            st.session_state.fixtures_data = fixtures
            st.session_state.selected_fixture = None
            st.success(f"{len(fixtures)} tamamlanmış maç yüklendi.")
        else:
            st.error("Maçlar yüklenirken bir hata oluştu veya veri bulunamadı.")

st.markdown("---")

# --- ESNEK ORAN ARAMA BÖLÜMÜ ---
with st.expander("🔍 Esnek Tek / Çoklu Oranlı Maç Arama"):
    st.markdown("MS1, MS0 veya MS2 değerlerinden dilediğini (istersen tek bir oranı) doldurarak tarama yapabilirsin. Boş/0 bırakılan oranlar dikkate alınmaz.")
    
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
        limit = st.selectbox("Tarama Sınırı", [20, 50, 100], index=0)
    with sc6:
        st.write("")
        ara_btn = st.button("Orana Göre Ara", use_container_width=True)

    if ara_btn:
        if h_hedef == 0.0 and d_hedef == 0.0 and a_hedef == 0.0:
            st.warning("Lütfen en az bir oran alanına değer girin.")
        else:
            with st.spinner("Oranlar taranıyor..."):
                data = api_get("/fixtures", {"league": league_id, "season": season})
                if data and "response" in data:
                    ft_matches = [f for f in data["response"] if f["fixture"]["status"]["short"] == "FT"][:limit]
                    bulunanlar = []
                    
                    prog = st.progress(0)
                    for i, f in enumerate(ft_matches):
                        prog.progress((i + 1) / len(ft_matches))
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
                            
                        match_h = h_hedef == 0.0 or abs(h_odd - h_hedef) <= tolerans
                        match_d = d_hedef == 0.0 or abs(d_odd - d_hedef) <= tolerans
                        match_a = a_def = a_hedef == 0.0 or abs(a_odd - a_hedef) <= tolerans
                        
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
                    prog.empty()
                    if bulunanlar:
                        st.success(f"{len(bulunanlar)} maç eşleşti!")
                        st.dataframe(pd.DataFrame(bulunanlar), use_container_width=True)
                    else:
                        st.info("Bu kriterlere uygun maç bulunamadı.")

# --- ANA YERLEŞİM (Sol: Maç Listesi, Sağ: Detay ve Poisson Analizi) ---
col_list, col_detail = st.columns([1, 1.3])

with col_list:
    st.subheader("📋 Maç Listesi")
    if not st.session_state.fixtures_data:
        st.info("Yukarıdan lig ve sezon seçip 'Maçları Yükle' butonuna basın.")
    else:
        # Maçları seçmek için liste kutusu
        fixture_options = {
            f"{f['teams']['home']['name']} {f['goals']['home']}-{f['goals']['away']} {f['teams']['away']['name']} ({f['fixture']['date'][:10]})": f 
            for f in st.session_state.fixtures_data
        }
        selected_label = st.selectbox("Maç Seçin", list(fixture_options.keys()))
        if selected_label:
            st.session_state.selected_fixture = fixture_options[selected_label]

with col_detail:
    st.subheader("🔍 Maç Detayı & Poisson Modeli")
    fx = st.session_state.selected_fixture
    
    if not fx:
        st.markdown("<div style='color:var(--muted); text-align:center; padding:50px;'>Soldan bir maç seçin.</div>", unsafe_allow_html=True)
    else:
        home_team = fx["teams"]["home"]
        away_team = fx["teams"]["away"]
        home_name = home_team["name"]
        away_name = away_name = away_team["name"]
        
        st.markdown(f"### {home_name} vs {away_name}")
        st.markdown(f"**Tarih:** {fx['fixture']['date'][:10]} | **Gerçek Skor:** {fx['goals']['home']} - {fx['goals']['away']}")
        
        with st.spinner("İstatistikler ve Bet365 oranları çekiliyor..."):
            home_stats = api_get("/teams/statistics", {"team": home_team["id"], "league": league_id, "season": season})
            away_stats = api_get("/teams/statistics", {"team": away_team["id"], "league": league_id, "season": season})
            odds_data = api_get("/odds", {"fixture": fx["fixture"]["id"], "bookmaker": BET365_ID})
            
        if not home_stats or not away_stats or not home_stats.get("response") or not away_stats.get("response"):
            st.warning("Bu takımlar için detaylı istatistik bulunamadı.")
        else:
            h_res = home_stats["response"]
            a_res = away_stats["response"]
            
            # Poisson Beklenen Gol Hesaplama
            h_atk = float(h_res.get("goals", {}).get("for", {}).get("average", {}).get("home", 1.3) or 1.3)
            a_def = float(a_res.get("goals", {}).get("against", {}).get("average", {}).get("away", 1.3) or 1.3)
            a_atk = float(a_res.get("goals", {}).get("for", {}).get("average", {}).get("away", 1.1) or 1.1)
            h_def = float(h_res.get("goals", {}).get("against", {}).get("average", {}).get("home", 1.1) or 1.1)
            
            home_exp = (h_atk + a_def) / 2
            away_exp = (a_atk + h_def) / 2
            
            # Poisson Olasılık Dağılımı
            def poisson(l, k):
                return math.exp(-l) * (l ** k) / math.factorial(k)
            
            p_home, p_draw, p_away = 0, 0, 0
            for h_g in range(7):
                for a_g in range(7):
                    p = poisson(home_exp, h_g) * poisson(away_exp, a_g)
                    if h_g > a_g: p_home += p
                    elif h_g == a_g: p_draw += p
                    else: p_away += p
            
            st.markdown("#### 📊 Model Tahmini (Poisson)")
            m1, m2, m3 = st.columns(3)
            m1.metric(home_name, f"%{p_home*100:.0f}")
            m2.metric("Beraberlik", f"%{p_draw*100:.0f}")
            m3.metric(away_name, f"%{p_away*100:.0f}")
            
            # Bet365 Oranları ve Değerlendirme
            st.markdown("#### 🎯 Bet365 Oran & Değer Karşılaştırması")
            bet365 = None
            if odds_data and odds_data.get("response"):
                bookmakers = odds_data["response"][0].get("bookmakers", [])
                bet365 = next((b for b in bookmakers if b["id"] == BET365_ID), None)
            
            mw = bet365.get("bets", []) if bet365 else []
            match_winner = next((b for b in mw if b["name"] == "Match Winner"), None)
            
            if match_winner:
                vals = match_winner.get("values", [])
                h_odd = next((float(v["odd"]) for v in vals if v["value"] == "Home"), None)
                d_odd = next((float(v["odd"]) for v in vals if v["value"] == "Draw"), None)
                a_odd = next((float(v["odd"]) for v in vals if v["value"] == "Away"), None)
                
                def render_row(lbl, model_p, odd):
                    if not odd:
                        return f"- **{lbl}**: Model: %{model_p*100:.0f} | Bet365: Oran yok"
                    imp = 1 / odd
                    diff = (model_p - imp) * 100
                    color = "🟢" if diff >= 0 else "🔴"
                    return f"- **{lbl}**: Model: %{model_p*100:.0f} | Bet365: %{imp*100:.0f} (Oran: {odd}) {color} {diff:+.1f}p"
                
                st.markdown(render_row(home_name, p_home, h_odd))
                st.markdown(render_row("Beraberlik", p_draw, d_odd))
                st.markdown(render_row(away_name, p_away, a_odd))
            else:
                st.info("Bu maç için Bet365 oran verisi bulunamadı.")
