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
sezonlar = [2024, 2025]  # Test için güncel sezonlar

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Maçlar ve tüm oran sayfaları yükleniyor, lütfen bekleyin...")
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
                
                # --- SAYFALAMA (PAGINATION) İLE TÜM ORANLARI ÇEKME ---
                odds_dict = {}
                page = 1
                total_pages = 1
                
                while page <= total_pages:
                    odds_params = {
                        "league": LEAGUE_ID,
                        "season": sezon,
                        "page": page
                    }
                    odds_resp = requests.get(ODDS_URL, headers=headers, params=odds_params, timeout=15)
                    if odds_resp.status_code == 200:
                        res_json = odds_resp.json()
                        paging = res_json.get("paging", {})
                        total_pages = paging.get("total", 1)
                        
                        odds_data = res_json.get("response", [])
                        for odd_item in odds_data:
                            f_id = odd_item.get('fixture', {}).get('id')
                            bookmakers = odd_item.get("bookmakers", [])
                            if bookmakers:
                                # Bahis şirketi seçimi (Örn: Bet365 veya ilk bulunan)
                                target_bm = bookmakers[0]
                                for bm in bookmakers:
                                    if bm.get("id") == 8:  # Bet365 ID genelde 8'dir
                                        target_bm = bm
                                        break
                                        
                                bets = target_bm.get("bets", [])
                                for bet in bets:
                                    if bet.get("id") == 1:  # 1X2 Oranları
                                        o1, o0, o2 = None, None, None
                                        for val in bet.get("values", []):
                                            if val.get("value") == "Home": o1 = val.get("odd")
                                            elif val.get("value") == "Draw": o0 = val.get("odd")
                                            elif val.get("value") == "Away": o2 = val.get("odd")
                                        odds_dict[f_id] = {'MS_1': o1, 'MS_0': o0, 'MS_2': o2}
                        page += 1
                    else:
                        break

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
                        'MS_1': match_odds['MS_1'],
                        'MS_0': match_odds['MS_0'],
                        'MS_2': match_odds['MS_2'],
                        'İY_Ev': halftime.get('home'),
                        'İY_Dep': halftime.get('away'),
                        'MS_Ev': fulltime.get('home'),
                        'MS_Dep': fulltime.get('away'),
                    }
                    tum_maclar.append(mac_detay)
        except Exception as e:
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
        return pd.DataFrame(columns=['Sezon', 'Tarih', 'Ev Sahibi', 'Deplasman', 'MS_1', 'MS_0', 'MS_2', 'İY/MS', 'MS_Ev', 'MS_Dep'])

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
    st.warning("Veriler yükleniyor...")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_oranlar.csv", "text/csv")
