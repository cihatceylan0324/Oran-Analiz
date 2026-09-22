import streamlit as st
import pandas as pd
import glob
import os

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Oran Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Oran ve Analiz Paneli")
st.markdown("---")

# CSV Dosyası Kontrolü
if os.path.exists("oran_analiz.csv"):
    df = pd.read_csv("oran_analiz.csv")
    st.sidebar.success("✅ Gerçek 'oran_analiz.csv' dosyası yüklendi!")
else:
    st.sidebar.warning("⚠️ 'oran_analiz.csv' henüz bulunamadı. Yedek mod aktif.")
    # Dosya yoksa bile çökmemesi için boş/örnek şema
    df = pd.DataFrame(columns=['Sezon', 'Tarih', 'Ev Sahibi', 'Deplasman', 'IY/MS', 'MS_Ev', 'MS_Dep'])

# Arama ve Filtreleme
st.sidebar.header("🔍 Filtreler")
aranan = st.sidebar.text_input("Takım Ara:")

if aranan and not df.empty:
    df = df[df.astype(str).apply(lambda x: x.str.contains(aranan, case=False)).any(axis=1)]

# Ana ekran göstergeleri
c1, c2 = st.columns(2)
c1.metric("Toplam Maç Sayısı", f"{len(df):,}")

st.markdown("---")

# Tablo
st.subheader("📊 Maç Verileri")
if not df.empty:
    st.dataframe(df.head(1000), use_container_width=True)
else:
    st.info("Henüz görüntülenecek veri yok. Bilgisayarında veri botunu çalıştırıp `oran_analiz.csv` dosyasını GitHub'a yüklediğinde veriler burada belirecek.")
