import streamlit as st
import pandas as pd
import numpy as np

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve İY/MS Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Kapsamlı Oran ve İY/MS Analiz Paneli (2021-2026)")
st.markdown("---")

# Zenginleştirilmiş ve gerçekçi maç havuzu (2021-2026)
@st.cache_data
def genis_veri_getir():
    np.random.seed(42)
    takimlar = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir", "Adana Demirspor", "Alanyaspor", "Antalyaspor", "Konyaspor", "Kayserispor", "Sivasspor", "Kasımpaşa", "Hatayspor", "Gaziantep FK", "Samsunspor", "Rizespor"]
    sezonlar = ["2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"]
    
    veri_listesi = []
    for i in range(1, 201): # 200 Maçlık geniş arşiv
        ev = np.random.choice(takimlar)
        dep = np.random.choice(takimlar)
        while ev == dep:
            dep = np.random.choice(takimlar)
            
        sezon = np.random.choice(sezonlar)
        iy_h = np.random.randint(0, 3)
        iy_a = np.random.randint(0, 3)
        ms_h = iy_h + np.random.randint(0, 3)
        ms_a = iy_a + np.random.randint(0, 3)
        
        # İY / MS Belirleme
        if iy_h > iy_a: iy_str = "1"
        elif iy_h < iy_a: iy_str = "2"
        else: iy_str = "0"
        
        if ms_h > ms_a: ms_str = "1"
        elif ms_h < ms_a: ms_str = "2"
        else: ms_str = "0"
        
        iyms = f"{iy_str}/{ms_str}"
        
        veri_listesi.append({
            'Sezon': sezon,
            'Ev Sahibi': ev,
            'Deplasman': dep,
            'İY_Skor': f"{iy_h}-{iy_a}",
            'MS_Skor': f"{ms_h}-{ms_a}",
            'İY/MS': iyms,
            'MS_1': round(np.random.uniform(1.30, 4.50), 2),
            'MS_0': round(np.random.uniform(3.10, 3.80), 2),
            'MS_2': round(np.random.uniform(1.60, 5.00), 2),
            'Alt_2.5': round(np.random.uniform(1.65, 2.25), 2),
            'Ust_2.5': round(np.random.uniform(1.50, 2.10), 2)
        })
    
    return pd.DataFrame(veri_listesi)

df = genis_veri_getir()

# Sol Menü Filtreleri
st.sidebar.header("⚙️ Filtreler ve Arama")

# Sezon Filtresi
secilen_sezon = st.sidebar.selectbox("Sezon Seç", ["Tümü"] + list(df['Sezon'].unique()))
if secilen_sezon != "Tümü":
    df = df[df['Sezon'] == secilen_sezon]

# Takım Arama
aranan = st.sidebar.text_input("🔍 Takım Ara:")
if aranan:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

# İY/MS Filtresi
secilen_iyms = st.sidebar.selectbox("İY/MS Kombinasyonu Filtrele", ["Tümü"] + list(df['İY/MS'].unique()))
if secilen_iyms != "Tümü":
    df = df[df['İY/MS'] == secilen_iyms]

# Oran Aralığı Filtresi
max_oran = st.sidebar.slider("Maksimum MS 1 Oranı", 1.0, 5.0, 5.0)
df = df[df['MS_1'] <= max_oran]

# Metrikler
col1, col2, col3, col4 = st.columns(4)
col1.metric("Listelenen Maç Sayısı", len(df))
col2.metric("Ortalama MS 1 Oranı", f"{df['MS_1'].mean():.2f}" if len(df) > 0 else "0")
col3.metric("Ortalama MS 0 Oranı", f"{df['MS_0'].mean():.2f}" if len(df) > 0 else "0")
col4.metric("Ortalama MS 2 Oranı", f"{df['MS_2'].mean():.2f}" if len(df) > 0 else "0")

# Ana Tablo
st.subheader("📊 Maçlar, Oranlar ve İY/MS Analiz Tablosu")
st.dataframe(df, use_container_width=True)

# İndir
csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Analiz Verilerini İndir (CSV)", csv_veri, "superlig_oran_analiz.csv", "text/csv")
