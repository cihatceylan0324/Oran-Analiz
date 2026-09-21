import streamlit as st
import requests
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Sezon Sezon Futbol Arşivi ve Yükleyici", page_icon="⚽", layout="wide")

# API-Football Anahtarınız
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"

# Maçkolik Tarzı Karanlık Tema Tasarımı (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e0f11;
        color: #ffffff;
    }
    .stSelectbox div, .stFileUploader div {
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

st.title("⚽ Sezonluk Futbol Arşivi & Excel Yönetim Merkezi")
st.caption("İstediğin sezonu tek tek indir, sonra elindeki CSV dosyalarını sisteme yükleyip birleştir!")

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

# Sol Menü
st.sidebar.header("📥 1. Adım: Sezon Sezon Veri İndir")
secilen_lig_key = st.sidebar.selectbox("Avrupa Ligi Seçin", list(LIGLER.keys()))
secilen_sezon_key = st.sidebar.selectbox("Tekil Sezon Seçin", list(SEZON_SECENEKLERI.keys()))

lig_id = LIGLER[secilen_lig_key]
secim_sezon = SEZON_SECENEKLERI[secilen_sezon_key]

if st.sidebar.button("🔍 Bu Sezonu Çek ve İndir", type="primary"):
    with st.spinner(f"{secilen_lig_key} ({secim_sezon}) maçları taranıyor..."):
        m_list = api_maclari_getir_tekil(API_KEY, lig_id, secim_sezon)
        if m_list:
            df_tekil = pd.DataFrame(m_list)
            st.session_state['son_indirilen_df'] = df_tekil
            st.session_state['son_dosya_adi'] = f"{secilen_lig_key.replace(' ', '_').replace('-', '')}_{secim_sezon}.csv"
            st.success(f"✅ {len(m_list)} maç başarıyla çekildi!")
        else:
            st.warning("⚠️ Bu sezona ait maç bulunamadı.")

# Eğer indirilecek veri varsa butonu göster
if 'son_indirilen_df' in st.session_state:
    csv_data = st.session_state['son_indirilen_df'].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.sidebar.download_button(
        label=f"💾 {secilen_sezon} Dosyasını İndir",
        data=csv_data,
        file_name=st.session_state['son_dosya_adi'],
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.header("📂 2. Adım: Dosyaları Geri Yükle")
yuklenen_dosyalar = st.sidebar.file_uploader("Daha önce indirdiğin CSV dosyalarını seç (Birden fazla seçebilirsin)", type=["csv"], accept_multiple_files=True)

# Yüklenen dosyaları işleme
aktif_veri_kaynagi = None
if yuklenen_dosyalar:
    tum_df_listesi = []
    for dosya in yuklenen_dosyalar:
        df_temp = pd.read_csv(dosya)
        tum_df_listesi.append(df_temp)
    if tum_df_listesi:
        aktif_veri_kaynagi = pd.concat(tum_df_listesi, ignore_index=True)

# Ana Ekran Gösterimi
if aktif_veri_kaynagi is not None and not aktif_veri_kaynagi.empty:
    toplam_mac = len(aktif_veri_kaynagi)
    st.success(f"📁 Sisteme yüklenen dosyalardan toplam **{toplam_mac} adet maç** başarıyla birleştirildi!")
    
    ms1_sayisi = sum(1 for m in aktif_veri_kaynagi['MS Sonucu'] if m == '1')
    ms0_sayisi = sum(1 for m in aktif_veri_kaynagi['MS Sonucu'] == 'X' if m) # Güvenli sayım
    # Alternatif temiz sayım:
    ms0_sayisi = len(aktif_veri_kaynagi[aktif_veri_kaynagi['MS Sonucu'] == 'X'])
    ms2_sayisi = len(aktif_veri_kaynagi[aktif_veri_kaynagi['MS Sonucu'] == '2'])
    ust_sayisi = len(aktif_veri_kaynagi[aktif_veri_kaynagi['Toplam Gol'] > 2.5])
    kg_sayisi = len(aktif_veri_kaynagi[aktif_veri_kaynagi['KG Var'] == 'Evet'])

    st.markdown(f"""
    <div class="summary-card">
        <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 6px;">
            📊 Yüklenen Tüm Sezonların Birleşik İstatistikleri
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

    st.subheader("📋 Birleştirilmiş Maç Tablosu")
    st.dataframe(aktif_veri_kaynagi, use_container_width=True, height=500)
else:
    st.info("👈 Sol menüden sezon seçip tek tek indirebilir, ya da indirdiğin dosyaları **'2. Adım'** kısmından yükleyerek birleşik olarak ekranda görebilirsin.")
