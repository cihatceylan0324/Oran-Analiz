import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Canlı Oran ve Analiz Paneli")
st.markdown("---")

# API-Football Pro Bilgileri (Sana özel gömülü sistem)
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/fixtures"
LEAGUE_ID = 203
sezonlar = [2021, 2022, 2023, 2024, 2025, 2026]

headers = {
    'x-apisports-key': API_KEY
}

# Verileri önbelleğe alarak API'yi yormayan ve hızlı açılan sistem
@st.cache_data(show_spinner="⚽ Süper Lig maçları API-Football'dan yükleniyor, lütfen bekleyin...")
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
                veri = response.json()
                fixtures = veri.get("response", [])
                for match in fixtures:
                    mac_detay = {
                        'Sezon': f"{sezon}-{sezon+1}",
                        'Tarih': match.get('fixture', {}).get('date', '')[:10],
                        'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                        'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
                        'IY_Ev': match.get('score', {}).get('halftime', {}).get('home'),
                        'IY_Dep': match.get('score', {}).get('halftime', {}).get('away'),
                        'MS_Ev': match.get('score', {}).get('fulltime', {}).get('home'),
                        'MS_Dep': match.get('score', {}).get('fulltime', {}).get('away'),
                    }
                    tum_maclar.append(mac_detay)
        except Exception:
            continue
            
    if tum_maclar:
        df = pd.DataFrame(tum_maclar)
        # İY/MS Hesaplama
        df['İY/MS'] = df.apply(lambda r: f"{'1' if r['IY_Ev'] > r['IY_Dep'] else ('2' if r['IY_Ev'] < r['IY_Dep'] else '0')}/"
                                                    f"{'1' if r['MS_Ev'] > r['MS_Dep'] else ('2' if r['MS_Ev'] < r['MS_Dep'] else '0')}" 
                                                    if pd.notnull(r['IY_Ev']) and pd.notnull(r['MS_Ev']) else "-", axis=1)
        return df
    else:
        return pd.DataFrame(columns=['Sezon', 'Tarih', 'Ev Sahibi', 'Deplasman', 'İY/MS', 'MS_Ev', 'MS_Dep'])

# Veriyi Yükle
df = verileri_getir()

# Sol Menü Filtreleri
st.sidebar.header("🔍 Filtreler")
aranan = st.sidebar.text_input("Takım Ara (Örn: Galatasaray):")

if aranan and not df.empty:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

# Üst Metrikler
c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")

# Tablo
st.subheader("📊 Maç ve Skor Listesi")
if not df.empty:
    st.dataframe(df, use_container_width=True, height=500)
else:
    st.warning("Veriler yüklenirken bir bağlantı sorunu oluştu.")

# İndir
csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Verileri İndir (CSV)", csv_veri, "super_lig_analiz.csv", "text/csv")
