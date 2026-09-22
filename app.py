import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Canlı Oran ve Analiz Paneli")
st.markdown("---")

API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/odds"
LEAGUE_ID = 203
SEASON = 2024  # Güncel aktif sezon üzerinden oran ve maç matrisi

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Maçlar ve oranlar yükleniyor, lütfen bekleyin...")
def verileri_getir():
    tum_maclar = []
    params = {
        "league": LEAGUE_ID,
        "season": SEASON
    }
    try:
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json().get("response", [])
            for item in data:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                goals = item.get("goals", {})
                
                f_id = fixture.get("id")
                tarih = fixture.get("date", "")[:10]
                ev_sahibi = teams.get("home", {}).get("name")
                deplasman = teams.get("away", {}).get("name")
                
                ms_ev = goals.get("home")
                ms_dep = goals.get("away")
                
                # Oranları Çekme (1X2 Market)
                o1, o0, o2 = None, None, None
                bookmakers = item.get("bookmakers", [])
                if bookmakers:
                    # Genellikle Bet365 (ID: 8) veya ilk bookmaker
                    target_bm = bookmakers[0]
                    for bm in bookmakers:
                        if bm.get("id") == 8:
                            target_bm = bm
                            break
                    
                    bets = target_bm.get("bets", [])
                    for bet in bets:
                        if bet.get("id") == 1:  # 1X2
                            for val in bet.get("values", []):
                                v_name = val.get("value")
                                if v_name == "Home": o1 = val.get("odd")
                                elif v_name == "Draw": o0 = val.get("odd")
                                elif v_name == "Away": o2 = val.get("odd")

                mac_detay = {
                    'Tarih': tarih,
                    'Ev Sahibi': ev_sahibi,
                    'Deplasman': deplasman,
                    'MS 1': o1,
                    'MS 0': o0,
                    'MS 2': o2,
                    'MS Ev': ms_ev,
                    'MS Dep': ms_dep
                }
                tum_maclar.append(mac_detay)
        
        if tum_maclar:
            return pd.DataFrame(tum_maclar)
    except Exception as e:
        pass
        
    return pd.DataFrame(columns=['Tarih', 'Ev Sahibi', 'Deplasman', 'MS 1', 'MS 0', 'MS 2', 'MS Ev', 'MS Dep'])

df = verileri_getir()

# Sol Menü Filtreleri
st.sidebar.header("🔍 Filtreler")
aranan = st.sidebar.text_input("Takım Ara (Örn: Galatasaray):")
if aranan and not df.empty:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")
st.subheader("📊 Maçlar ve Oran Matrisi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yüklenirken bir sorun oluştu veya oran aralığı boş döndü.")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_oranlar_matris.csv", "text/csv")
