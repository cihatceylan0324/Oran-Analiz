import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="Oranlı Futbol Arşivi", page_icon="⚽", layout="wide")

st.title("⚽ Gerçek Oranlı Maç ve Lig Arşivi")

# CSV dosyalarını bul
dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.warning("⚠️ Lütfen oranları içeren CSV dosyalarını repoya yükleyin.")
else:
    st.sidebar.header("⚙️ Veri Seçimi")
    secilen_dosya = st.sidebar.selectbox("Lig / Sezon Seçin", dosyalar)
    
    df = pd.read_csv(secilen_dosya)
    st.success(f"📂 Seçilen Dosya: {secilen_dosya} | Maç Sayısı: {len(df)}")
    
    # Oran sütunlarını otomatik bulma (Örn: B365H, B365D, B365A veya benzeri)
    oran_kolonlari = [col for col in df.columns if any(o in col.lower() for o in ['b365', 'ps', 'max', 'avg', 'odd', 'oran'])]
    
    if oran_kolonlari:
        st.sidebar.info(f"💡 Tespit Edilen Oran Sütunları: {', '.join(oran_kolonlari)}")
    
    # Takım Arama
    aranan = st.sidebar.text_input("🔍 Takım Ara:")
    if aranan and ('HomeTeam' in df.columns or 'Ev Sahibi' in df.columns):
        ev_col = 'HomeTeam' if 'HomeTeam' in df.columns else 'Ev Sahibi'
        dep_col = 'AwayTeam' in df.columns and 'AwayTeam' or 'Deplasman'
        df = df[df[ev_col].str.contains(aranan, case=False, na=False) | df[dep_col].str.contains(aranan, case=False, na=False)]
    
    # Tabloyu Göster
    st.subheader("📊 Maçlar ve Oran Verileri")
    st.dataframe(df, use_container_width=True)
    
    # İndir
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Güncel Veriyi İndir", csv_veri, file_name=f"oranli_{secilen_dosya}", mime="text/csv")
