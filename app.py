import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Maç ve Skor Analiz Paneli")
st.markdown("---")

API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
LEAGUE_ID = 203
sezonlar = [2021, 2022, 2023, 2024, 2025, 2026]

headers = {
    'x-apisports-key': API_KEY
}

@st.cache_data(show_spinner="⚽ Süper Lig maç arşivi yükleniyor...")
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
                for match in fixtures:
                    score_dict = match.get('score') or {}
                    halftime = score_dict.get('halftime') or {}
                    fulltime = score_dict.get('fulltime') or {}
                    
                    mac_detay = {
                        'Sezon': f"{sezon}-{sezon+1}",
                        'Tarih': match.get('fixture', {}).get('date', '')[:10],
                        'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                        'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
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
        return pd.DataFrame(columns=['Sezon', 'Tarih', 'Ev Sahibi', 'Deplasman', 'İY_Ev', 'İY_Dep', 'MS_Ev', 'MS_Dep', 'İY/MS'])

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
st.subheader("📊 Süper Lig Maç Arşivi ve İY/MS Sonuçları")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yüklenirken bir sorun oluştu.")

csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_arsiv.csv", "text/csv")
