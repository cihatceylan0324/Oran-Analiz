import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="Veri Kontrol Paneli", layout="wide")
st.title("🔍 CSV Sütun ve Veri Kontrol Aracı")

dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.error("⚠️ Hiç CSV dosyası bulunamadı!")
else:
    secilen = st.selectbox("Dosya Seç", dosyalar)
    df = pd.read_csv(secilen)
    
    st.warning(f"💡 **{secilen}** dosyasında bulunan gerçek sütun isimleri:")
    st.write(list(df.columns))  # Dosyada hangi sütunlar varsa buraya liste olarak dökecek
    
    st.subheader("Dosyanın İlk 5 Satırı:")
    st.dataframe(df.head(), use_container_width=True)
