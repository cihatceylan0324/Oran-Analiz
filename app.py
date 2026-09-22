import streamlit as st
import pandas as pd
import numpy as np

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran ve İY/MS Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Gerçek Oran ve İY/MS Analiz Paneli")
st.markdown("---")

# Eğer repoda CSV yoksa, sistemin çökmemesi ve hemen test edebilmen için örnek veritabanı oluşturalım
@st.cache_data
def veri_getir():
    # Örnek Süper Lig Maçları ve Oranları
    data = {
        'Sezon': ['2023-2024', '2023-2024', '2023-2024', '2024-2025', '2024-2025', '2024-2025', '2025-2026', '2025-2026'],
        'Ev Sahibi': ['Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor', 'Galatasaray', 'Beşiktaş', 'Fenerbahçe', 'Başakşehir'],
        'Deplasman': ['Fenerbahçe', 'Beşiktaş', 'Galatasaray', 'Fenerbahçe', 'Trabzonspor', 'Fenerbahçe', 'Galatasaray', 'Trabzonspor'],
        'İY_Skor': ['1-0', '0-0', '1-1', '0-1', '2-0', '0-0', '1-0', '0-1'],
        'MS_Skor': ['2-1', '1-1', '2-3', '1-2', '3-0', '1-1', '2-2', '0-0'],
        'IY/MS': ['1/1', '0/0', '1/2', '2/2', '1/1', '0/0', '1/0', '2/0'],
        'MS_1': [2.10, 1.85, 2.50, 2.90, 1.65, 2.40, 2.20, 2.60],
        'MS_0': [3.30, 3.40, 3.20, 3.10, 3.60, 3.25, 3.30, 3.15],
        'MS_2': [2.80, 3.50, 2.40, 2.30, 4.20, 2.70, 2.90, 2.55],
        'Alt_2.5': [1.90, 1.75, 1.80, 1.95, 2.10, 1.85, 1.90, 1.80],
        'Ust_2.5': [1.70, 1.85, 1.80, 1.65, 1.55, 1.75, 1.70, 1.80]
    }
    return pd.DataFrame(data)

df = veri_getir()

# Sol Menü Filtreleri
st.sidebar.header("⚙️ Oran ve Maç Filtreleri")

# Takım Arama
aranan = st.sidebar.text_input("🔍 Takım Ara (Örn: Galatasaray):")
if aranan:
    df = df[df['Ev Sahibi'].str.contains(aranan, case=False, na=False) | 
            df['Deplasman'].str.contains(aranan, case=False, na=False)]

# İY/MS Filtresi
secilen_iyms = st.sidebar.selectbox("İY/MS Sonucu Seç", ["Tümü", "1/1", "0/0", "1/2", "2/2", "1/0", "2/0"])
if secilen_iyms != "Tümü":
    df = df[df['IY/MS'] == secilen_iyms]

# Oran Aralığı Filtresi
max_oran = st.sidebar.slider("Maksimum MS 1 Oranı", 1.0, 5.0, 5.0)
df = df[df['MS_1'] <= max_oran]

# Metrikler
col1, col2, col3 = st.columns(3)
col1.metric("Listelenen Maç Sayısı", len(df))
col2.metric("Ortalama MS 1 Oranı", f"{df['MS_1'].mean():.2f}" if len(df) > 0 else "0")
col3.metric("Ortalama MS 2 Oranı", f"{df['MS_2'].mean():.2f}" if len(df) > 0 else "0")

# Ana Tablo
st.subheader("📊 Maçlar, Oranlar ve İY/MS Kombinasyonları")
st.dataframe(df, use_container_width=True)

# İndir
csv_veri = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Analiz Verilerini İndir (CSV)", csv_veri, "oran_analiz_raporu.csv", "text/csv")
