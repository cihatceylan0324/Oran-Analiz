import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Süper Lig Oran Paneli", page_icon="⚽", layout="wide")
st.title("⚽ Türkiye Süper Lig - Oran ve Analiz Paneli")
st.markdown("---")

API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
URL = "https://v3.football.api-sports.io/odds"
headers = {'x-apisports-key': API_KEY}

@st.cache_data(show_spinner="Güncel oranlar yükleniyor...")
def oranlari_getir():
    # Güncel sezon (2025/2026) üzerinden test edelim
    params = {"league": 203, "season": 2025}
    try:
        r = requests.get(URL, headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json().get("response", [])
            liste = []
            for item in data:
                fix = item.get("fixture", {})
                teams = item.get("teams", {})
                tarih = fix.get("date", "")[:10]
                ev = teams.get("home", {}).get("name")
                dep = teams.get("away", {}).get("name")
                
                o1, o0, o2 = None, None, None
                for bm in item.get("bookmakers", []):
                    for bet in bm.get("bets", []):
                        if bet.get("id") == 1:
                            for val in bet.get("values", []):
                                if val.get("value") == "Home": o1 = val.get("odd")
                                elif val.get("value") == "Draw": o0 = val.get("odd")
                                elif val.get("value") == "Away": o2 = val.get("odd")
                
                liste.append({
                    'Tarih': tarih,
                    'Ev Sahibi': ev,
                    'Deplasman': dep,
                    'MS 1': o1,
                    'MS 0': o0,
                    'MS 2': o2
                })
            return pd.DataFrame(liste)
    except Exception:
        pass
    return pd.DataFrame()

df = oranlari_getir()

st.metric("Toplam Maç/Oran Sayısı", len(df))
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("API şu an bu istek için oran döndürmedi. Lütfen API paket limitlerini veya aktif maç takvimini kontrol edin.")
