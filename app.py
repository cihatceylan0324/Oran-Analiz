import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Oran ve Analiz Paneli")
st.markdown("---")

# API-Football Pro Bilgileri
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
ODDS_URL = "https://v3.football.api-sports.io/odds"
LEAGUE_ID = 203
sezonlar = [2024, 2025]  # Şimdilik en güncel 2 sezonla test edip hızı görelim, sonra artırırız

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Maçlar ve oranlar yükleniyor, lüften bekleyin...")
def verileri_getir():
    tum_maclar = []
    for sezon in sezonlar:
        params = {
            "league": LEAGUE_ID,
            "season": sezon
        }
        try:
            response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                fixtures = response.json().get("response", [])
                
                # Her sezon için toplu oran çekme (Tarih bazlı veya lig/sezon bazlı odds)
                odds_params = {
                    "league": LEAGUE_ID,
                    "season": sezon
                }
                odds_resp = requests.get(ODDS_URL, headers=headers, params=odds_params, timeout=15)
                odds_dict = {}
                
                if odds_resp.status_code == 200:
                    odds_data = odds_resp.json().get("response", [])
                    for odd_item in odds_data:
                        f_id = odd_item.get('fixture', {}).get('id')
                        bookmakers = odd_item.get("bookmakers", [])
                        if bookmakers:
                            # Genellikle ilk bookmaker (örn: Bet365 / Ortalama)
                            bets = bookmakers[0].get("bets", [])
                            for bet in bets:
                                if bet.get("id") == 1:  # 1X2 Oranları
                                    o1, o0, o2 = None, None, None
                                    for val in bet.get("values", []):
                                        if val.get("value") == "Home": o1 = val.get("odd")
                                        elif val.get("value") == "Draw": o0 = val.get("odd")
                                        elif val.get("value") == "Away": o2 = val.get("odd")
                                    odds_dict[f_id] = {'MS_1': o1, 'MS_0': o0, 'MS_2': o2}

                for match in fixtures:
                    f_id = match.get('fixture', {}).get('id')
                    match_odds = odds_dict.get(f_id, {'MS_1': None, 'MS_0': None, 'MS_2': None})
                    
                    mac_detay = {
                        'Sezon': f"{sezon}-{sezon+1}",
                        'Tarih': match.get('fixture', {}).get('date', '')[:10],
                        'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                        'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
                        'MS_1': match_odds['MS_1'],
                        'MS_0': match_odds['MS_0'],
                        'MS_2': match_odds['MS_2'],
                        'İY_Ev': match.get('score', {}).get('halftime', {}).get('home'),
                        'İY_Dep': match.get('score', {}).get('halftime', {}).get('away'),
                        'MS_Ev': match.get('score', {}).get('fulltime', {}).get('home'),
                        'MS_Dep': match.get('score', {}).get('fulltime', {}).get('away'),
                    }
                    tum_maclar.append(mac_detay)
        except Exception as e:
            continue
            
    if tum_maclar:
        df = pd.DataFrame(tum_maclar)
        df['İY/MS'] = df.apply(lambda r: f"{'1' if r['IY_Ev'] > r['IY_Dep'] else ('2' if r['IY_Ev'] < r['IY_Dep'] else '0')}/"
                                                    f"{'1' if r['MS_Ev'] > r['MS_Dep'] else ('2' if r['MS_Ev'] < r['MS_Dep'] else '0')}" 
                                                    if pd.notnull(r['IY_Ev']) and pd.notnull(r['MS_Ev']) else "-", axis=1)
        return df
    else:
        return pd.DataFrame()

df = verileri_getir()
import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Oran ve Analiz Paneli")
st.markdown("---")

# API-Football Pro Bilgileri
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
ODDS_URL = "https://v3.football.api-sports.io/odds"
LEAGUE_ID = 203
sezonlar = [2024, 2025]  # Şimdilik en güncel 2 sezonla test edip hızı görelim, sonra artırırız

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Maçlar ve oranlar yükleniyor, lüften bekleyin...")
def verileri_getir():
    tum_maclar = []
    for sezon in sezonlar:
        params = {
            "league": LEAGUE_ID,
            "season": sezon
        }
        try:
            response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                fixtures = response.json().get("response", [])
                
                # Her sezon için toplu oran çekme (Tarih bazlı veya lig/sezon bazlı odds)
                odds_params = {
                    "league": LEAGUE_ID,
                    "season": sezon
                }
                odds_resp = requests.get(ODDS_URL, headers=headers, params=odds_params, timeout=15)
                odds_dict = {}
                
                if odds_resp.status_code == 200:
                    odds_data = odds_resp.json().get("response", [])
                    for odd_item in odds_data:
                        f_id = odd_item.get('fixture', {}).get('id')
                        bookmakers = odd_item.get("bookmakers", [])
                        if bookmakers:
                            # Genellikle ilk bookmaker (örn: Bet365 / Ortalama)
                            bets = bookmakers[0].get("bets", [])
                            for bet in bets:
                                if bet.get("id") == 1:  # 1X2 Oranları
                                    o1, o0, o2 = None, None, None
                                    for val in bet.get("values", []):
                                        if val.get("value") == "Home": o1 = val.get("odd")
                                        elif val.get("value") == "Draw": o0 = val.get("odd")
                                        elif val.get("value") == "Away": o2 = val.get("odd")
                                    odds_dict[f_id] = {'MS_1': o1, 'MS_0': o0, 'MS_2': o2}

                for match in fixtures:
                    f_id = match.get('fixture', {}).get('id')
                    match_odds = odds_dict.get(f_id, {'MS_1': None, 'MS_0': None, 'MS_2': None})
                    
                    mac_detay = {
                        'Sezon': f"{sezon}-{sezon+1}",
                        'Tarih': match.get('fixture', {}).get('date', '')[:10],
                        'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                        'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
                        'MS_1': match_odds['MS_1'],
                        'MS_0': match_odds['MS_0'],
                        'MS_2': match_odds['MS_2'],
                        'İY_Ev': match.get('score', {}).get('halftime', {}).get('home'),
                        'İY_Dep': match.get('score', {}).get('halftime', {}).get('away'),
                        'MS_Ev': match.get('score', {}).get('fulltime', {}).get('home'),
                        'MS_Dep': match.get('score', {}).get('fulltime', {}).get('away'),
                    }
                    tum_maclar.append(mac_detay)
        except Exception as e:
            continue
            
    if tum_maclar:
        df = pd.DataFrame(tum_maclar)
        df['İY/MS'] = df.apply(lambda r: f"{'1' if r['IY_Ev'] > r['IY_Dep'] else ('2' if r['IY_Ev'] < r['IY_Dep'] else '0')}/"
                                                    f"{'1' if r['MS_Ev'] > r['MS_Dep'] else ('2' if r['MS_Ev'] < r['MS_Dep'] else '0')}" 
                                                    if pd.notnull(r['IY_Ev']) and pd.notnull(r['MS_Ev']) else "-", axis=1)
        return df
    else:
        return pd.DataFrame()

df = verileri_getir()

# Filtreler ve Arama
st.sidebar.header("🔍 Filtreler")
aranan = st.sidebar.text_input("Takım Ara:")
if aranan and not df.empty:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")
st.subheader("📊 Maç ve Oran Listesi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yükleniyor veya bağlantı bekleniyor...")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_oranlar.csv", "text/csv")
# Filtreler ve Arama
st.sidebar.header("🔍 Filtreler")
aranan = st.sidebar.text_input("Takım Ara:")
if aranan and not df.empty:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")
st.subheader("📊 Maç ve Oran Listesi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yükleniyor veya bağlantı bekleniyor...")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_oranlar.csv", "text/csv")
