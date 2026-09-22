import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig 40K Oran ve İY/MS Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - 40.000 Maçlık Gerçek Oran ve İY/MS Analiz Paneli")
st.markdown("---")

# Depodaki CSV dosyalarını bul
dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.error("⚠️ Depoda hiç CSV dosyası bulunamadı! Lütfen 40.000 maçlık CSV dosyasını GitHub deposuna yükle.")
else:
    # Sol Menüden Dosya Seçimi
    st.sidebar.header("⚙️ Veri ve Filtreler")
    secilen_dosya = st.sidebar.selectbox("CSV Dosyası Seç", dosyalar)
    
    @st.cache_data
    def veri_yukle(dosya_adi):
        return pd.read_csv(dosya_adi)
    
    with st.spinner("40.000 maçlık dev veri seti yükleniyor, lütfen bekleyin..."):
        df = veri_yukle(secilen_dosya)
    
    st.success(f"📂 Yüklenen Dosya: {secilen_dosya} | Toplam Maç Sayısı: {len(df):,}")
    
    # Takım Arama
    aranan = st.sidebar.text_input("🔍 Takım Ara (Ev Sahibi veya Deplasman):")
    if aranan:
        ev_col = next((col for col in ['HomeTeam', 'Ev Sahibi', 'ev_sahibi', 'Team1'] if col in df.columns), None)
        dep_col = next((col for col in ['AwayTeam', 'Deplasman', 'deplasman', 'Team2'] if col in df.columns), None)
        
        if ev_col and dep_col:
            df = df[df[ev_col].str.contains(aranan, case=False, na=False) | 
                    df[dep_col].str.contains(aranan, case=False, na=False)]
        else:
            # Eğer sütun adı tam eşleşmezse genel arama yap
            df = df[df.astype(str).apply(lambda x: x.str.contains(aranan, case=False)).any(axis=1)]

    # İY/MS Sütunu yoksa ama skorlar varsa otomatik türetelim
    iyms_col = next((col for col in ['IY/MS', 'iyms', 'HTFT', 'ht_ft'] if col in df.columns), None)
    if not iyms_col:
        hthg = next((col for col in ['HTHG', 'IlkYariEv', 'ht_home'] if col in df.columns), None)
        htag = next((col for col in ['HTAG', 'IlkYariDep', 'ht_away'] if col in df.columns), None)
        fthg = next((col for col in ['FTHG', 'MacSonuEv', 'ft_home'] if col in df.columns), None)
        ftag = next((col for col in ['FTAG', 'MacSonuDep', 'ft_away'] if col in df.columns), None)
        
        if hthg and htag and fthg and ftag:
            def hesapla_iyms(row):
                try:
                    iy = '1' if row[hthg] > row[htag] else ('2' if row[hthg] < row[htag] else '0')
                    ms = '1' if row[fthg] > row[ftag] else ('2' if row[fthg] < row[ftag] else '0')
                    return f"{iy}/{ms}"
                except:
                    return "-"
            df['IY/MS'] = df.apply(hesapla_iyms, axis=1)

    # İY/MS Filtresi
    if 'IY/MS' in df.columns:
        secilen_iyms = st.sidebar.selectbox("İY/MS Kombinasyonu Filtrele", ["Tümü"] + list(df['IY/MS'].unique()))
        if secilen_iyms != "Tümü":
            df = df[df['IY/MS'] == secilen_iyms]

    # Metrikler
    st.metric("Filtrelenen Maç Sayısı", f"{len(df):,}")

    # Ana Tablo
    st.subheader("📊 Maç ve Oran Verileri")
    st.dataframe(df.head(1000), use_container_width=True) # Sayfa kilitlenmesin diye ilk 1000 satırı gösterir, tümü indirilebilir
    if len(df) > 1000:
        st.info("💡 Performans için ekranda ilk 1000 satır gösterilmektedir. Tüm filtrelenmiş veriyi aşağıdaki butondan indirebilirsiniz.")

    # İndir
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Filtrelenmiş 40K Veriyi İndir (CSV)", csv_veri, "filtrelenmis_oranlar.csv", "text/csv")
