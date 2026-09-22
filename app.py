import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig 40K Oran ve Yüzde Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Detaylı Oran, İY/MS ve Yüzde Analiz Paneli")
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
    
    with st.spinner("Veri seti yükleniyor..."):
        df = veri_yukle(secilen_dosya)
    
    st.success(f"📂 Yüklenen Dosya: {secilen_dosya} | Toplam Maç: {len(df):,}")
    
    # Takım Arama
    aranan = st.sidebar.text_input("🔍 Takım Ara (Ev Sahibi veya Deplasman):")
    if aranan:
        ev_col = next((col for col in ['HomeTeam', 'Ev Sahibi', 'ev_sahibi', 'Team1'] if col in df.columns), None)
        dep_col = next((col for col in ['AwayTeam', 'Deplasman', 'deplasman', 'Team2'] if col in df.columns), None)
        
        if ev_col and dep_col:
            df = df[df[ev_col].str.contains(aranan, case=False, na=False) | 
                    df[dep_col].str.contains(aranan, case=False, na=False)]
        else:
            df = df[df.astype(str).apply(lambda x: x.str.contains(aranan, case=False)).any(axis=1)]

    # Gol sütunlarını tespit et ve 2.5 Alt/Üst ile İY/MS hesapla
    fthg = next((col for col in ['FTHG', 'MacSonuEv', 'ft_home', 'HG'] if col in df.columns), None)
    ftag = next((col for col in ['FTAG', 'MacSonuDep', 'ft_away', 'AG'] if col in df.columns), None)
    
    if fthg and ftag:
        # Toplam golleri bul
        df['ToplamGol'] = pd.to_numeric(df[fthg], errors='coerce') + pd.to_numeric(df[ftag], errors='coerce')
        df['2.5 Üst'] = df['ToplamGol'] > 2.5
        df['2.5 Alt'] = df['ToplamGol'] <= 2.5
        
        # Maç Sonu Sonucu (1, 0, 2)
        def ms_sonuc(row):
            if row[fthg] > row[ftag]: return '1'
            elif row[fthg] < row[ftag]: return '2'
            else: return '0'
        df['MS_Sonuc'] = df.apply(ms_sonuc, axis=1)

    # --- İSTATİSTİK VE YÜZDE BÖLÜMÜ ---
    st.subheader("📈 Seçilen Maçların Yüzdesel Oran Analizi")
    
    toplam_mac = len(df)
    if toplam_mac > 0:
        c1, c2, c3, c4, c5 = st.columns(5)
        
        c1.metric("Toplam Maç", f"{toplam_mac:,}")
        
        if '2.5 Üst' in df.columns:
            ust_oran = (df['2.5 Üst'].sum() / toplam_mac) * 100
            alt_oran = (df['2.5 Alt'].sum() / toplam_mac) * 100
            c2.metric("2.5 Üst Yüzdesi", f"%{ust_oran:.1f}")
            c3.metric("2.5 Alt Yüzdesi", f"%{alt_oran:.1f}")
            
        if 'MS_Sonuc' in df.columns:
            ev_kazanma = (df['MS_Sonuc'] == '1').sum() / toplam_mac * 100
            dep_kazanma = (df['MS_Sonuc'] == '2').sum() / toplam_mac * 100
            c4.metric("Ev Sahibi Kazanma", f"%{ev_kazanma:.1f}")
            c5.metric("Deplasman Kazanma", f"%{dep_kazanma:.1f}")
    else:
        st.warning("Filtreleme sonucunda maç bulunamadı.")

    st.markdown("---")

    # Ana Tablo
    st.subheader("📊 Maç ve Oran Verileri Detayları")
    st.dataframe(df.head(1000), use_container_width=True)
    if len(df) > 1000:
        st.info("💡 Performans için ilk 1000 satır gösteriliyor. Tamamını aşağıdaki butondan indirebilirsiniz.")

    # İndir
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Filtrelenmiş Veriyi İndir (CSV)", csv_veri, "detayli_analiz.csv", "text/csv")
