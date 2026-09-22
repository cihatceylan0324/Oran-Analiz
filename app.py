import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Oranlı Futbol Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Geçmiş Oran ve İY/MS Analiz Paneli")

# Klasördeki CSV dosyalarını bul
dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.warning("⚠️ Hiç CSV dosyası bulunamadı! Lütfen oranları içeren Süper Lig CSV dosyasını depona yükle.")
else:
    # Sol Menüden Dosya Seçimi
    st.sidebar.header("⚙️ Veri ve Filtreler")
    secilen_dosya = st.sidebar.selectbox("Sezon / Lig Seçin", dosyalar)
    
    # Dosyayı Oku
    df = pd.read_csv(secilen_dosya)
    
    # Eğer ilk yarı (HT) ve maç sonu (FT) skorları varsa, İY/MS sonucunu (1/1, 1/0 vb.) otomatik hesapla
    if 'HTHG' in df.columns and 'HTAG' in df.columns and 'FTHG' in df.columns and 'FTAG' in df.columns:
        def iy_ms_hesapla(row):
            try:
                # İlk Yarı Sonucu
                if row['HTHG'] > row['HTAG']: iy = '1'
                elif row['HTHG'] < row['HTAG']: iy = '2'
                else: iy = '0'
                
                # Maç Sonu Sonucu
                if row['FTHG'] > row['FTAG']: ms = '1'
                elif row['FTHG'] < row['FTAG']: ms = '2'
                else: ms = '0'
                
                return f"{iy}/{ms}"
            except:
                return "-"
        
        df['IY/MS'] = df.apply(iy_ms_hesapla, axis=1)

    st.success(f"📂 Seçilen Dosya: {secilen_dosya} | Toplam Maç: {len(df)}")
    
    # Takım Arama
    aranan_takim = st.sidebar.text_input("🔍 Takım Ara (Ev Sahibi veya Deplasman):")
    if aranan_takim:
        # Sütun isimlerine göre arama yap (HomeTeam/AwayTeam veya Ev Sahibi/Deplasman)
        ev_col = 'HomeTeam' if 'HomeTeam' in df.columns else ('Ev Sahibi' if 'Ev Sahibi' in df.columns else None)
        dep_col = 'AwayTeam' if 'AwayTeam' in df.columns else ('Deplasman' if 'Deplasman' in df.columns else None)
        
        if ev_col and dep_col:
            df = df[df[ev_col].str.contains(aranan_takim, case=False, na=False) | 
                    df[dep_col].str.contains(aranan_takim, case=False, na=False)]

    # Tabloyu Göster (Oranlar ve İY/MS dahil)
    st.subheader("📊 Maçlar, Oranlar ve İY/MS Analiz Tablosu")
    st.dataframe(df, use_container_width=True)
        
    # İndirme Butonu
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Oranlı Verileri İndir (CSV)",
        data=csv_veri,
        file_name=f"analizli_{secilen_dosya}",
        mime="text/csv",
    )
