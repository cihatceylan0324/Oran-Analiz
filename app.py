import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Oran Analiz Merkezi", page_icon="⚽", layout="wide")

# Maçkolik Tarzı Karanlık Tema Tasarımı (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e0f11;
        color: #ffffff;
    }
    .stNumberInput input {
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
        margin-bottom: 15px;
        border: 1px solid #2d2f34;
        font-family: sans-serif;
    }
    .odd-box {
        flex: 1;
        min-width: 60px;
        text-align: center;
        border-radius: 6px;
        overflow: hidden;
        font-size: 12px;
    }
    .odd-header {
        background-color: #1976D2;
        color: white;
        font-weight: bold;
        padding: 3px 0;
    }
    .odd-header-blue2 {
        background-color: #0288D1;
        color: white;
        font-weight: bold;
        padding: 3px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Birebir Oran Analiz Sistemi")
st.caption("Maçkolik tarzı yeşil kazanan oran takibi")

# Örnek Maç Verileri
if 'veri' not in st.session_state:
    st.session_state.veri = {
        "maclar": [
            {
                "tarih": "2026-09-20", "lig_adi": "Süper Lig",
                "ev_sahibi": "Trabzonspor", "deplasman": "Galatasaray",
                "ms_skor": "4 - 0", "iy_skor": "3-0",
                "ms_sonuc": "1", "toplam_gol": 4.0, "kg_var": False,
                "oranlar": {"ms1": 2.91, "ms0": 3.71, "ms2": 2.30, "ust_2_5": 1.65, "alt_2_5": 1.85, "kg_var": 1.55, "kg_yok": 2.05}
            },
            {
                "tarih": "2026-09-18", "lig_adi": "Premier Lig",
                "ev_sahibi": "Arsenal", "deplasman": "Chelsea",
                "ms_skor": "2 - 1", "iy_skor": "1-0",
                "ms_sonuc": "1", "toplam_gol": 3.0, "kg_var": True,
                "oranlar": {"ms1": 2.91, "ms0": 3.71, "ms2": 2.30, "ust_2_5": 1.70, "alt_2_5": 1.80, "kg_var": 1.60, "kg_yok": 1.95}
            }
        ]
    }

# Sol Menü / Oran Filtreleri
st.sidebar.header("🎯 Oran Filtreleri")

col1, col2, col3 = st.sidebar.columns(3)
ms1 = col1.number_input("MS 1", value=0.0, step=0.01, format="%.2f")
ms0 = col2.number_input("MS X", value=0.0, step=0.01, format="%.2f")
ms2 = col3.number_input("MS 2", value=0.0, step=0.01, format="%.2f")

col4, col5 = st.sidebar.columns(2)
ust_2_5 = col4.number_input("2.5 ÜST", value=0.0, step=0.01, format="%.2f")
alt_2_5 = col5.number_input("2.5 ALT", value=0.0, step=0.01, format="%.2f")

col6, col7 = st.sidebar.columns(2)
kg_var = col6.number_input("KG VAR", value=0.0, step=0.01, format="%.2f")
kg_yok = col7.number_input("KG YOK", value=0.0, step=0.01, format="%.2f")

kriterler = {
    "ms1": ms1 if ms1 > 0 else None,
    "ms0": ms0 if ms0 > 0 else None,
    "ms2": ms2 if ms2 > 0 else None,
    "ust_2_5": ust_2_5 if ust_2_5 > 0 else None,
    "alt_2_5": alt_2_5 if alt_2_5 > 0 else None,
    "kg_var": kg_var if kg_var > 0 else None,
    "kg_yok": kg_yok if kg_yok > 0 else None
}
aktif_filtreler = {k: v for k, v in kriterler.items() if v is not None}

# Sonuç Ekranı
if not aktif_filtreler:
    st.info("👈 Sol taraftaki menüden aratmak istediğiniz oranları giriniz.")
else:
    esleseler = []
    for mac in st.session_state.veri.get("maclar", []):
        o = mac.get("oranlar", {})
        if all(o.get(k) == v for k, v in aktif_filtreler.items()):
            esleseler.append(mac)

    if not esleseler:
        st.warning("⚠️ Veritabanında bu oran kombinasyonuna uygun maç bulunamadı.")
    else:
        toplam = len(esleseler)
        ms1_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == '1')
        ms0_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == 'X')
        ms2_cnt = sum(1 for m in esleseler if m['ms_sonuc'] == '2')
        ust_cnt = sum(1 for m in esleseler if m['toplam_gol'] > 2.5)
        kg_cnt = sum(1 for m in esleseler if m['kg_var'])

        en_cok_ms = "MS 1" if ms1_cnt >= max(ms0_cnt, ms2_cnt) else ("MS X" if ms0_cnt >= ms2_cnt else "MS 2")
        en_cok_yuzde = round((max(ms1_cnt, ms0_cnt, ms2_cnt) / toplam) * 100)

        # Yeşil Özet Kartı
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size: 16px; font-weight: bold; color: #81c784; margin-bottom: 8px;">📊 BİREBİR ORAN ANALİZİ ({toplam} Maç Bulundu)</div>
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 12px; color: white;">
                🏆 En Çok Biten Sonuç: <span style="background-color: #2e7d32; color: white; padding: 4px 12px; border-radius: 6px;">{en_cok_ms} (%{en_cok_yuzde})</span>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 13px;">
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 1: %{round(ms1_cnt/toplam*100)} ({ms1_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS X: %{round(ms0_cnt/toplam*100)} ({ms0_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">MS 2: %{round(ms2_cnt/toplam*100)} ({ms2_cnt})</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">2.5 Üst: %{round(ust_cnt/toplam*100)}</span>
                <span style="background:#1e2720; color:#a5d6a7; padding:5px 10px; border-radius:6px; border:1px solid #2e7d32;">KG Var: %{round(kg_cnt/toplam*100)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Maç Kartları
        for m in esleseler:
            o = m.get("oranlar", {})
            
            ms1_bg, ms1_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == '1' else ("#dcdcdc", "#222")
            ms0_bg, ms0_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == 'X' else ("#dcdcdc", "#222")
            ms2_bg, ms2_fg = ("#2e7d32", "#fff") if m['ms_sonuc'] == '2' else ("#dcdcdc", "#222")

            ust_bg, ust_fg = ("#2e7d32", "#fff") if m['toplam_gol'] > 2.5 else ("#dcdcdc", "#222")
            alt_bg, alt_fg = ("#2e7d32", "#fff") if m['toplam_gol'] <= 2.5 else ("#dcdcdc", "#222")

            kgv_bg, kgv_fg = ("#2e7d32", "#fff") if m['kg_var'] else ("#dcdcdc", "#222")
            kgy_bg, kgy_fg = ("#2e7d32", "#fff") if not m['kg_var'] else ("#dcdcdc", "#222")

            html_card = f"""
            <div class="match-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2c30; padding-bottom: 10px; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 11px; color: #888; display: block;">{m['tarih']} • {m.get('lig_adi', 'Lig')}</span>
                        <span style="font-size: 16px; font-weight: bold; color: #fff;">{m['ev_sahibi']} - {m['deplasman']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="background-color: #000; color: #4caf50; font-size: 16px; font-weight: bold; padding: 4px 10px; border-radius: 6px;">{m['ms_skor']}</span>
                        <span style="font-size: 11px; color: #aaa; display: block; margin-top: 3px;">(İY {m['iy_skor']})</span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <div class="odd-box"><div class="odd-header">1</div><div style="background-color:{ms1_bg}; color:{ms1_fg}; font-weight:bold; padding:6px 0;">{o.get('ms1', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header">X</div><div style="background-color:{ms0_bg}; color:{ms0_fg}; font-weight:bold; padding:6px 0;">{o.get('ms0', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header">2</div><div style="background-color:{ms2_bg}; color:{ms2_fg}; font-weight:bold; padding:6px 0;">{o.get('ms2', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ÜST</div><div style="background-color:{ust_bg}; color:{ust_fg}; font-weight:bold; padding:6px 0;">{o.get('ust_2_5', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">2.5 ALT</div><div style="background-color:{alt_bg}; color:{alt_fg}; font-weight:bold; padding:6px 0;">{o.get('alt_2_5', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG VAR</div><div style="background-color:{kgv_bg}; color:{kgv_fg}; font-weight:bold; padding:6px 0;">{o.get('kg_var', '-')}</div></div>
                    <div class="odd-box"><div class="odd-header-blue2">KG YOK</div><div style="background-color:{kgy_bg}; color:{kgy_fg}; font-weight:bold; padding:6px 0;">{o.get('kg_yok', '-')}</div></div>
                </div>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
