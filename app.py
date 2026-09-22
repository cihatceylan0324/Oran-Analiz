import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Kapsamlı İstatistik ve Oran Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Detaylı İstatistik, Oran ve Yüzde Analiz Paneli")
st.markdown("---")

# Depodaki CSV dosyalarını bul
dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.error("⚠️ Depoda hiç CSV dosyası bulunamadı! Lütfen CSV dosyasını GitHub deposuna yükle.")
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

    # Skor sütunlarını bul ve İY/MS / 2.5 Alt-Üst / MS Sonuçlarını türet
    fthg = next((col for col in ['FTHG', 'MacSonuEv', 'ft_home', 'HG'] if col in df.columns), None)
    ftag = next((col for col in ['FTAG', 'MacSonuDep', 'ft_away', 'AG'] if col in df.columns), None)
    hthg = next((col for col in ['HTHG', 'IlkYariEv', 'ht_home'] if col in df.columns), None)
    htag = next((col for col in ['HTAG', 'IlkYariDep', 'ht_away'] if col in df.columns), None)
    
    if fthg and ftag:
        df['ToplamGol'] = pd.to_numeric(df[fthg], errors='coerce') + pd.to_numeric(df[ftag], errors='coerce')
        df['2.5 Üst'] = df['ToplamGol'] > 2.5
        df['2.5 Alt'] = df['ToplamGol'] <= 2.5
        
        def ms_sonuc(row):
            if row[fthg] > row[ftag]: return 'MS 1'
            elif row[fthg] < row[ftag]: return 'MS 2'
            else: return 'MS 0'
        df['MS_Sonuc'] = df.apply(ms_sonuc, axis=1)

    if hthg and htag and fthg and ftag:
        def iyms_hesapla(row):
            try:
                iy = '1' if row[hthg] > row[htag] else ('2' if row[hthg] < row[htag] else '0')
                ms = '1' if row[fthg] > row[ftag] else ('2' if row[fthg] < row[ftag] else '0')
                return f"{iy}/{ms}"
            except:
                return "-"
        df['IY/MS'] = df.apply(iyms_hesapla, axis=1)

    # --- İSTATİSTİK VE YÜZDE BÖLÜMÜ ---
    st.subheader("📈 Seçilen Maçların Yüzdesel İstatistik Dağılımı")
    
    toplam_mac = len(df)
    if toplam_mac > 0:
        # Üst Metrik Kartları
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Filtrelenen Toplam Maç", f"{toplam_mac:,}")
        
        if '2.5 Üst' in df.columns:
            ust_oran = (df['2.5 Üst'].sum() / toplam_mac) * 100
            alt_oran = (df['2.5 Alt'].sum() / toplam_mac) * 100
            c2.metric("2.5 Üst Oranı", f"%{ust_oran:.1f}")
            c3.metric("2.5 Alt Oranı", f"%{alt_oran:.1f}")
            
        st.markdown("---")
        
        # Detaylı Oran / Yüzde Dağılımları (Tablolar Halinde Yan Yana)
        col_sol, col_sag = st.columns(2)
        
        with col_sol:
            st.markdown("### 🏆 Maç Sonu (1X2) Yüzdeleri")
            if 'MS_Sonuc' in df.columns:
                ms_counts = df['MS_Sonuc'].value_counts(normalize=True) * 100
                ms_df = pd.DataFrame({'Sonuç': ms_counts.index, 'Yüzde (%)': ms_counts.values.round(1)})
                st.dataframe(ms_df, use_container_width=True, hide_index=True)
            else:
                st.info("Maç sonucu verisi bulunamadı.")
                
        with col_sag:
            st.markdown("### ⏱️ İlk Yarı / Maç Sonu (İY/MS) Yüzdeleri")
            if 'IY/MS' in df.columns:
                iyms_counts = df['IY/MS'].value_counts(normalize=True) * 100
                iyms_df = pd.DataFrame({'İY/MS': iyms_counts.index, 'Yüzde (%)': iyms_counts.values.round(1)})
                st.dataframe(iyms_df, use_container_width=True, hide_index=True)
            else:
                st.info("İlk yarı verisi bulunamadı.")
    else:
        st.warning("Filtreleme sonucunda eşleşen maç bulunamadı.")

    st.markdown("---")

    # Ana Tablo
    st.subheader("📊 Maç ve Detay Verileri")
    st.dataframe(df.head(1000), use_container_width=True)
    if len(df) > 1000:
        st.info("💡 Performans için ilk 1000 satır gösteriliyor. Tümünü aşağıdaki butondan indirebilirsiniz.")

    # İndir
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Filtrelenmiş Veriyi İndir (CSV)", csv_veri, "detayli_oran_istatistik.csv", "text/csv")
