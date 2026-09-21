import streamlit as st
import requests
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Premier League 5 Yıllık Arşiv ve Oranlar", page_icon="⚽", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("⚽ İngiltere Premier League 5 Yıllık Arşiv & Oranlar (2021 - 2026)")
st.caption("2021'den 2026'ya kadar tüm Premier League maçlarını ve bahis oranlarını Excel'e aktar.")

SEZON_SECENEKLERI = {
    "🗓️ TÜM SEZONLAR (2021 - 2026)": "ALL",
    "2026": 2026,
    "2025": 2025,
    "2024": 2024,
    "2023": 2023,
    "2022": 2022,
    "2021": 2021
}

# Premier League (Lig ID: 39) Maç ve Oran Çekme Fonksiyonu
@st.cache_data(ttl=86400)
def api_premierleague_mac_ve_oran_getir(api_key, sezon):
    headers = {
        'x-apisports-key': api_key,
        'x-rapidapi-key': api_key
    }
    # 39 numarası İngiltere Premier League ID'sidir
    url_fixtures = f"https://v3.football.api-sports.io/fixtures?league=39&season={sezon}"
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
            fixture_id = f["id"]

            if f["status"]["short"] in ["FT", "AET", "PEN"]:
                ev_gol = g["home"] if g["home"] is not None else 0
                dep_gol = g["away"] if g["away"] is not None else 0
                toplam_gol = ev_gol + dep_gol

                ms_sonuc = "1" if ev_gol > dep_gol else ("2" if dep_gol > ev_gol else "X")
                kg_var = (ev_gol > 0) and (dep_gol > 0)

                # Oran çekme sorgusu (Maç Sonucu 1x2 Oranları)
                oran_1, oran_x, oran_2 = "", "", ""
                try:
                    url_odds = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
                    res_odds = requests.get(url_odds, headers=headers)
                    data_odds = res_odds.json().get("response", [])
                    if data_odds:
                        bookmakers = data_odds[0].get("bookmakers", [])
                        if bookmakers:
                            bets = bookmakers[0].get("bets", [])
                            for bet in bets:
                                if bet.get("id") == 1: # 1: Match Winner (Maç Sonucu)
                                    values = bet.get("values", [])
                                    for v in values:
                                        if v.get("value") == "Home": oran_1 = v.get("odd")
                                        elif v.get("value") == "Draw": oran_x = v.get("odd")
                                        elif v.get("value") == "Away": oran_2 = v.get("odd")
                except Exception:
                    pass

                maclar.append({
                    "Tarih": f["date"][:10],
                    "Sezon": sezon,
                    "Lig": l["name"],
                    "Ev Sahibi": t["home"]["name"],
                    "Deplasman": t["away"]["name"],
                    "MS Skor": f"{ev_gol} - {dep_gol}",
                    "IY Skor": f"{score['halftime']['home'] or 0} - {score['halftime']['away'] or 0}",
                    "MS Oran 1": oran_1,
                    "MS Oran X": oran_x,
                    "MS Oran 2": oran_2,
                    "MS Sonucu": ms_sonuc,
                    "Toplam Gol": toplam_gol,
                    "KG Var": "Evet" if kg_var else "Yok"
                })
        return maclar
    except Exception:
        return []

# Sol Menü
st.sidebar.header("⚙️ Premier League Ayarları")
secilen_sezon_key = st.sidebar.selectbox("Sezon / Yıl Aralığı Seçin", list(SEZON_SECENEKLERI.keys()))
secim_degeri = SEZON_SECENEKLERI[secilen_sezon_key]

st.sidebar.markdown("---")
if st.sidebar.button("🔍 Premier League Arşivini Derle", type="primary"):
    hedef_sezonlar = [2026, 2025, 2024, 2023, 2022, 2021] if secim_degeri == "ALL" else [secim_degeri]
    
    tum_toplanan_maclar = []
    with st.spinner("Premier League maçları ve bahis oranları arka planda toplanıyor (Oran sorguları nedeniyle biraz sürebilir)..."):
        for s in hedef_sezonlar:
            m_list = api_premierleague_mac_ve_oran_getir(API_KEY, s)
            tum_toplanan_maclar.extend(m_list)
            
    st.session_state['premier_arsiv'] = tum_toplanan_maclar
    st.session_state['aktif_secim_adi'] = secilen_sezon_key

# Hafızada maç varsa göster ve Excel İndir butonu sun
if 'premier_arsiv' in st.session_state and st.session_state['premier_arsiv']:
    arsiv = st.session_state['premier_arsiv']
    toplam_mac = len(arsiv)
    
    if toplam_mac > 0:
        df = pd.DataFrame(arsiv)
        
        # CSV Verisi Hazırlığı
        csv_verisi = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        dosya_adi = f"PremierLeague_Arsiv_{st.session_state['aktif_secim_adi'].replace(' ', '_')}.csv"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"🎉 Premier League için toplam **{toplam_mac} adet maç** ve oranları başarıyla derlendi!")
        with col2:
            st.download_button(
                label="📥 Excel (CSV) Olarak İndir",
                data=csv_verisi,
                file_name=dosya_adi,
                mime="text/csv",
                type="primary"
            )

        # Özet İstatistikler
        ms1_sayisi = len(df[df['MS Sonucu'] == '1'])
        ms0_sayisi = len(df[df['MS Sonucu'] == 'X'])
        ms2_sayisi = len(df[df['MS Sonucu'] == '2'])
        ust_sayisi = len(df[df['Toplam Gol'] > 2.5])
        kg_sayisi = len(df[df['KG Var'] == 'Evet'])

        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 6px;">
                📊 Premier League — {st.session_state['aktif_secim_adi']} Genel İstatistikler
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px; margin-top: 10px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">Toplam Maç: {toplam_mac}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_sayisi/toplam_mac*100)} ({ms1_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_sayisi/toplam_mac*100)} ({ms0_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_sayisi/toplam_mac*100)} ({ms2_sayisi})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_sayisi/toplam_mac*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_sayisi/toplam_mac*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📋 Arşiv ve Oran Tablosu Önizlemesi")
        st.dataframe(df, use_container_width=True, height=450)
    else:
        st.warning("⚠️ Seçilen kriterde maç bulunamadı.")
else:
    st.info("👈 Sol menüden **'TÜM SEZONLAR (2021 - 2026)'** veya istediğin tek bir yılı seçip **'Premier League Arşivini Derle'** butonuna basarak tüm maçları ve oranları Excel'e indirebilirsin.")
