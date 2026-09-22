import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Oran ve Analiz Paneli")
st.markdown("---")

API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
ODDS_URL = "https://v3.football.api-sports.io/odds"
LEAGUE_ID = 203
SEASON = 2025  # En güncel ve oran arşivi tam olan aktif sezon

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Güncel sezon maçları ve oranlar API-Football'dan çekiliyor...")
def verileri_getir():
    tum_maclar = []
    # Sayfalama desteğiyle güncel sezonun tüm oranlarını çekelim
    page = 1
    total_pages = 1
    
    try:
        while page <= total_pages:
            params = {
                "league": LEAGUE_ID,
                "season": SEASON,
                "page": page
            }
            response = requests.get(ODDS_URL, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                paging = res_json.get("paging", {})
                total_pages = paging.get("total", 1)
                
                data = res_json.get("response", [])
                for item in data:
                    fixture = item.get("fixture", {})
                    teams = item.get("teams", {})
                    goals = item.get("goals", {})
                    
                    tarih = fixture.get("date", "")[:10]
                    ev_sahibi = teams.get("home", {}).get("name")
                    deplasman = teams.get("away", {}).get("name")
                    
                    ms_ev = goals.get("home")
                    ms_dep = goals.get("away")
                    
                    # Oranlar (1X2 Market)
                    o1, o0, o2 = None, None, None
                    bookmakers = item.get("bookmakers", [])
                    if bookmakers:
                        target_bm = bookmakers[0]
                        for bm in bookmakers:
                            if bm.get("id") == 8: # Bet365
                                target_bm = bm
                                break
                        
                        bets = target_bm.get("bets", [])
                        for bet in bets:
                            if bet.get("id") == 1:
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
                page += 1
            else:
                break
                
        if tum_maclar:
            df = pd.DataFrame(tum_maclar)
            # Maç Sonucu Durumu (1, 0, 2)
            df['MS'] = df.apply(lambda r: '1' if r['MS Ev'] is not None and r['MS Dep'] is not None and r['MS Ev'] > r['MS Dep'] 
                                else ('2' if r['MS Ev'] is not None and r['MS Dep'] is not None and r['MS Ev'] < r['MS Dep'] 
                                      else ('0' if r['MS Ev'] is not None and r['MS Dep'] is not None else '-')), axis=1)
            return df
    except Exception as e:
        pass
        
    return pd.DataFrame(columns=['Tarih', 'Ev Sahibi', 'Deplasman', 'MS 1', 'MS 0', 'MS 2', 'MS Ev', 'MS Dep', 'MS'])

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
st.subheader("📊 Canlı Oran ve Maç Matrisi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yükleniyor veya oran aralığı bekleniyor...")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_canli_oranlar.csv", "text/csv")
