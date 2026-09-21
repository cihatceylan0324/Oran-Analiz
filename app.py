import streamlit as st
import requests
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Avrupa Futbol Arşivi & Excel İndirici", page_icon="⚽", layout="wide")

# API-Football Anahtarınız
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"

# Maçkolik Tarzı Karanlık Tema Tasarımı (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e0f11;
        color: #ffffff;
    }
    .stSelectbox div {
        background-color: #1a1b1e !important;
        color: #ffffff !important;
        border: 1px solid #2d2f34 !important;
        border-radius: 8px !important;
    }
    .summary-card {
        background-color: #121315;
        border: 1px solid #2e7d32;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    .match-card {
        background-color: #1a1b1e;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid #2d2f34;
        font-family: sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Avrupa Futbol Arşivi & Excel Veri Üretici (2021 - 2026)")
st.caption("Seçilen ligin 5 yıllık tüm maçlarını arka planda derler ve Excel/CSV dosyasına dönüştürür.")

# Avrupa'nın önde gelen 20 ligi
LIGLER = {
    "🇹🇷 Türkiye - Süper Lig": 203,
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere - Premier League": 39,
    "🇪🇸 İspanya - La Liga": 140,
    "🇮🇹 İtalya - Serie A": 135,
    "🇩🇪 Almanya - Bundesliga": 78,
    "🇫🇷 Fransa - Ligue 1": 61,
    "🇳🇱 Hollanda - Eredivisie": 88,
    "🇵🇹 Portekiz - Liga Portugal": 94,
    "🇧🇪 Belçika - Pro League": 144,
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 İskoçya - Premiership": 179,
    "🇦🇹 Avusturya - Bundesliga": 218,
    "🇨🇭 İsviçre - Super League": 207,
    "🇬🇷 Yunanistan - Super League": 197,
    "🇩🇰 Danimarka - Superliga": 119,
    "🇸🇪 İsveç - Allsvenskan": 113,
    "🇳🇴 Norveç - Eliteserien": 103,
    "🇵🇱 Polonya - Ekstraklasa": 106,
    "🇨🇿 Çekya - 1. Liga": 345,
    "🇭🇷 Hırvatistan - HNL": 210,
    "🇪🇺 UEFA Şampiyonlar Ligi": 2
}

SEZON_SECENEKLERI = {
    "🗓️ TÜM SEZONLAR (2021 - 2026)": "ALL",
    "2026": 2026,
    "2025": 2025,
    "2024": 2024,
    "2023": 2023,
    "2022": 2022,
    "2021": 2021
}

# Tekil Sezon Veri Çekme Fonksiyonu
@st.cache_data(ttl=86400)
def api_maclari_getir_tekil(api_key, lig_id, sezon):
    headers = {
        'x-apisports-key': api_key,
        'x-rapidapi-key': api_key
    }
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?league={lig_id}&season={sezon}"
    try:
        res_fix = requests.get(url_fixtures, headers=headers)
        data_fix = res_fix.json()
        fixtures_raw = data_fix.get("response", [])
        if not fixtures_raw:
            return []

        maclar = []
        for item in fixtures_raw:
            f = item["fixture"]
            l = item["league"]
            t = item["teams"]
            g = item["goals"]
            score = item["score"]

            if f["status"]["short"] in ["FT", "AET", "PEN"]:
                ev_gol = g["home"] if g["home"] is not None else 0
                dep_gol = g["away"] if g["away"] is not None else 0
                toplam_gol = ev_gol + dep_gol

                ms_sonuc = "1" if ev_gol > dep_gol else ("2" if dep_gol > ev_gol else "X")
                kg_var = (ev_gol > 0) and (dep_gol > 0)

                maclar.append({
                    "Tarih": f["date"][:10],
                    "Sezon": sezon,
                    "Lig": l["name"],
                    "Ev Sahibi": t["home"]["name"],
                    "Deplasman": t["away"]["name"],
                    "MS Skor": f"{ev_gol} - {dep_gol}",
                    "IY Skor": f"{score['halftime']['home'] or 0} - {score['halftime']['away'] or 0}",
                    "MS Sonucu": ms_sonuc,
                    "Toplam Gol": toplam_gol,
                    "KG Var": "Evet" if kg_var else "Yok"
                })
        return maclar
    except Exception:
        return []

# Sol Menü / Seçimler
st.sidebar.header("🌍 Lig & Sezon Seçimi")
secilen_lig_key = st.sidebar.selectbox("Avrupa Ligi Seçin", list(LIGLER.keys()))
secilen_sezon_key = st.sidebar.selectbox("Sezon / Yıl Seçin", list(SEZON_SECENEKLERI.keys()))

lig_id = LIGLER[secilen_lig_key]
secim_degeri = SEZON_SECENEKLERI[secilen_sezon_key]

st.sidebar.markdown("---")
st.sidebar.info("💡 'TÜM SEZONLAR' seçilip arşivi getirdiğinizde, verileri doğrudan Excel (CSV) olarak indirebilirsiniz.")

# Verileri Yükle Butonu
if st.sidebar.button("🔍 Arşivi Derle ve Hazırla", type="primary"):
    hedef_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if secim_degeri == "ALL" else [secim_degeri]
    
    tum_toplanan_maclar = []
    with st.spinner(f"Arka planda {secilen_lig_key} maçları taranıyor ve birleştiriliyor..."):
        for s in hedef_sezonlar:
            m_list = api_maclari_getir_tekil(API_KEY, lig_id, s)
            tum_toplanan_maclar.extend(m_list)
            
    st.session_state['yuklenen_arsiv'] = tum_toplanan_maclar
    st.session_state['aktif_lig'] = secilen_lig_key
    st.session_state['aktif_sezon_bilgi'] = secilen_sezon_key

# Hafızada maç varsa göster ve indirme butonu sun
if 'yuklenen_arsiv' in st.session_state and st.session_state['yuklenen_arsiv']:
    arsiv = st.session_state['yuklenen_arsiv']
    toplam_mac = len(arsiv)
    
    if toplam_mac > 0:
        # Pandas DataFrame'e çevir
        df = pd.DataFrame(arsiv)
        
        # Excel / CSV İndirme Butonu Hazırlığı
        csv_verisi = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        dosya_adi = f"{secilen_lig_key.replace(' ', '_').replace('-', '')}_Arsiv.csv"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"🎉 Toplam **{toplam_mac} adet maç** başarıyla derlendi ve Excel formatına hazırlandı!")
        with col2:
            st.download_button(
                label="📥 Excel (CSV) İndir",
                data=csv_verisi,
                file_name=dosya_adi,
                mime="text/csv",
                type="primary"
            )

        ms1_sayisi = sum(1 for m in arsiv if m['MS Sonucu'] == '1')
        ms0_sayisi = sum(1 for m in arsiv if m['MS Sonucu'] == 'X')
        ms2_sayisi = sum(1 for m in arsiv if m['MS Sonucu'] == '2')
        ust_sayisi = sum(1 for m in arsiv if m['Toplam Gol'] > 2.5)
        kg_sayisi = sum(1 for m in arsiv if m['KG Var'] == 'Evet')

        # Özet Kartı
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 6px;">
                📊 {st.session_state['aktif_lig']} — {st.session_state['aktif_sezon_bilgi']} Genel İstatistikler
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px; margin-top: 10px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_sayisi/toplam_mac*100)} ({ms1_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_sayisi/toplam_mac*100)} ({ms0_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_sayisi/toplam_mac*100)} ({ms2_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_sayisi/toplam_mac*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_sayisi/toplam_mac*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Arşivden Örnek Maçlar (İlk 100 Satır)")
        
        # Tablo görünümü
        st.dataframe(df, use_container_width=True, height=400)
        
    else:
        st.warning("⚠️ Bu kriterlere uygun maç bulunamadı.")
else:
    st.info("👈 Sol menüden ligi ve sezonu seçip **'Arşivi Derle ve Hazırla'** butonuna basarak maçları arka planda toplayabilir ve Excel olarak indirebilirsin.")
