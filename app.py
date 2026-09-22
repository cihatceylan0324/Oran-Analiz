import streamlit as st
import pandas as pd
import glob

# Sayfa Ayarları
st.set_page_config(page_title="Süper Lig Gerçek Oran Analiz Paneli", page_icon="⚽", layout="wide")

st.title("⚽ Türkiye Süper Lig - Gerçek Oran ve İstatistik Paneli")
st.markdown("---")

# Depodaki CSV dosyalarını bul
dosyalar = glob.glob("*.csv")

if not dosyalar:
    st.error("⚠️ Depoda hiç CSV dosyası bulunamadı! Lütfen CSV dosyasını GitHub deposuna yükle.")
else:
    # Sol Menüden Dosya Seçimi
    st.sidebar.header("⚙️ Veri ve Oran Filtreleri")
    secilen_dosya = st.sidebar.selectbox("CSV Dosyası Seç", dosyalar)
    
    @st.cache_data
    def veri_yukle(dosya_adi):
        return pd.read_csv(dosya_adi)
    
    with st.spinner("Veri seti yükleniyor..."):
        df = veri_yukle(secilen_dosya)
    
    st.success(f"📂 Yüklenen Dosya: {secilen_dosya} | Toplam Maç: {len(df):,}")
    
    # Oran sütunlarını otomatik tespit et (B365H, B365D, B365A, Avg, Odd vb.)
    oran_adaylari = [col for col in df.columns if any(o in col.lower() for o in ['b365', 'ps', 'max', 'avg', 'odd', 'oran', 'h', 'd', 'a'])]
    
    # Takım Arama
    aranan = st.sidebar.text_input("🔍 Takım Ara (Ev Sahibi / Deplasman):")
    if aranan:
        ev_col = next((col for col in ['HomeTeam', 'Ev Sahibi', 'ev_sahibi', 'Team1'] if col in df.columns), None)
        dep_col = next((col for col in ['AwayTeam', 'Deplasman', 'deplasman', 'Team2'] if col in df.columns), None)
        
        if ev_col and dep_col:
            df = df[df[ev_col].str.contains(aranan, case=False, na=False) | 
                    df[dep_col].str.contains(aranan, case=False, na=False)]
        else:
            df = df[df.astype(str).apply(lambda x: x.str.contains(aranan, case=False)).any(axis=1)]

    # --- ORAN İSTATİSTİKLERİ BÖLÜMÜ ---
    st.subheader("📊 Gerçek Oran İstatistikleri ve Ortalamalar")
    
    toplam_mac = len(df)
    if toplam_mac > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("Filtrelenen Maç Sayısı", f"{toplam_mac:,}")
        
        # Dosyadaki olası oran kolonlarını bulup ortalamalarını gösterelim
        bulunan_oranlar = [c for c in df.columns if df[c].dtype in ['float64', 'int64'] and any(k in c.lower() for k in ['h', 'd', 'a', '1', '2', 'oran', 'odd', 'avg', 'b365'])]
        
        if bulunan_oranlar:
            st.info(f"💡 Tespit Edilen Oran / Sayısal Sütunlar: {', '.join(bulunan_oranlar[:6])}")
            
            # İlk 2-3 oran sütununun ortalamasını göster
            col_list = st.columns(min(len(bulunan_oranlar), 3))
            for i, col_name in enumerate(bulunan_oranlar[:3]):
                ortalama_deger = df[col_name].mean()
                col_list[i].metric(f"Ortalama ({col_name})", f"{ortalama_deger:.2f}")
        else:
            st.warning("Bu veri setinde standart oran sütunları (B365H, Avg vb.) doğrudan tespit edilemedi. Ancak veriler aşağıdadır.")
    else:
        st.warning("Filtreleme sonucunda maç bulunamadı.")

    st.markdown("---")

    # Ana Tablo
    st.subheader("📋 Maç ve Oran Verileri Tablosu")
    st.dataframe(df.head(1000), use_container_width=True)
    if len(df) > 1000:
        st.info("💡 Performans için ilk 1000 satır gösteriliyor. Tümünü aşağıdaki butondan indirebilirsiniz.")

    # İndir
    csv_veri = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Tüm Veriyi İndir (CSV)", csv_veri, "oranlar_analiz.csv", "text/csv")
