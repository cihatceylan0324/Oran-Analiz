import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig 6 Sezon Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - 6 Sezonluk Arşiv ve Oran Paneli")
st.markdown("---")

API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
FIXTURES_URL = "https://v3.football.api-sports.io/fixtures"
ODDS_URL = "https://v3.football.api-sports.io/odds"
LEAGUE_ID = 203
# İstediğin tüm 6 sezon
sezonlar = [2024, 2025, 2026]

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Tüm 6 sezonun maçları ve oranları yükleniyor, lütfen bekleyin...")
def verileri_getir():
    tum_maclar = []
    
    for sezon in sezonlar:
        # 1. Adım: O sezondaki TÜM maçları çek (Garanti yol)
        params = {
            "league": LEAGUE_ID,
            "season": sezon
        }
        try:
            resp = requests.get(FIXTURES_URL, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                continue
            fixtures = resp.json().get("response", [])
            
            # 2. Adım: O sezonun oranlarını çekebiliyorsak çek (Güncel sezonlar için)
            odds_dict = {}
            page = 1
            total_pages = 1
            while page <= total_pages:
                odds_params = {
                    "league": LEAGUE_ID,
                    "season": sezon,
                    "page": page
                }
                odds_resp = requests.get(ODDS_URL, headers=headers, params=odds_params, timeout=10)
                if odds_resp.status_code == 200:
                    res_json = odds_resp.json()
                    paging = res_json.get("paging", {})
                    total_pages = paging.get("total", 1)
                    
                    for item in res_json.get("response", []):
                        f_id = item.get("fixture", {}).get("id")
                        o1, o0, o2 = None, None, None
                        bookmakers = item.get("bookmakers", [])
                        if bookmakers:
                            target_bm = bookmakers[0]
                            for bm in bookmakers:
                                if bm.get("id") == 8:  # Bet365
                                    target_bm = bm
                                    break
                            for bet in target_bm.get("bets", []):
                                if bet.get("id") == 1:
                                    for val in bet.get("values", []):
                                        v_name = val.get("value")
                                        if v_name == "Home": o1 = val.get("odd")
                                        elif v_name == "Draw": o0 = val.get("odd")
                                        elif v_name == "Away": o2 = val.get("odd")
                        odds_dict[f_id] = {'MS_1': o1, 'MS_0': o0, 'MS_2': o2}
                    page += 1
                else:
                    break

            # Maçları ve oranları birleştir
            for match in fixtures:
                f_id = match.get('fixture', {}).get('id')
                match_odds = odds_dict.get(f_id, {'MS_1': None, 'MS_0': None, 'MS_2': None})
                
                score_dict = match.get('score') or {}
                halftime = score_dict.get('halftime') or {}
                fulltime = score_dict.get('fulltime') or {}
                
                mac_detay = {
                    'Sezon': f"{sezon}-{sezon+1}",
                    'Tarih': match.get('fixture', {}).get('date', '')[:10],
                    'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                    'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
                    'MS 1': match_odds['MS_1'],
                    'MS 0': match_odds['MS_0'],
                    'MS 2': match_odds['MS_2'],
                    'İY_Ev': halftime.get('home'),
                    'İY_Dep': halftime.get('away'),
                    'MS_Ev': fulltime.get('home'),
                    'MS_Dep': fulltime.get('away'),
                }
                tum_maclar.append(mac_detay)
        except Exception:
            continue
            
    if tum_maclar:
        df = pd.DataFrame(tum_maclar)
        def hesapla_iyms(r):
            ie = r.get('İY_Ev')
            id_ = r.get('İY_Dep')
            me = r.get('MS_Ev')
            md = r.get('MS_Dep')
            if pd.notnull(ie) and pd.notnull(id_) and pd.notnull(me) and pd.notnull(md):
                iy_durum = '1' if ie > id_ else ('2' if ie < id_ else '0')
                ms_durum = '1' if me > md else ('2' if me < md else '0')
                return f"{iy_durum}/{ms_durum}"
            return "-"
            
        df['İY/MS'] = df.apply(hesapla_iyms, axis=1)
        return df
    else:
        return pd.DataFrame(columns=['Sezon', 'Tarih', 'Ev Sahibi', 'Deplasman', 'MS 1', 'MS 0', 'MS 2', 'İY/MS', 'MS_Ev', 'MS_Dep'])

df = verileri_getir()

# Sol Menü Filtreleri
st.sidebar.header("🔍 Filtreler")
secilen_sezon = st.sidebar.selectbox("Sezon Seç", ["Tümü"] + sorted(df['Sezon'].unique().tolist()) if not df.empty else ["Tümü"])
aranan = st.sidebar.text_input("Takım Ara (Örn: Galatasaray):")

if not df.empty:
    if secilen_sezon != "Tümü":
        df = df[df['Sezon'] == secilen_sezon]
    if aranan:
        df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
                df['Deplasman'].str.contains(aranan, case=False, na=False)]

c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")
st.subheader("📊 Tüm Sezonlar Maç ve Oran Matrisi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yükleniyor...")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_6_sezon_oranlar.csv", "text/csv")
