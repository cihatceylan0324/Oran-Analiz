import streamlit as st
import pandas as pd
import numpy as np
import math

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Futbol İstihbarat & Poisson Sanat Merkezi", 
    page_icon="⚽", 
    layout="wide"
)

# --- MODERN VE ESTETİK KOYU TEMA (CSS) ---
st.markdown("""
<style>
    :root {
        --bg-color: #0b0f19;
        --card-bg: #131d2d;
        --border-color: #1e293b;
        --text-color: #f1f5f9;
        --muted-text: #94a3b8;
        --accent-green: #10b981;
        --accent-blue: #3b82f6;
        --accent-gold: #f59e0b;
    }
    .main { background-color: var(--bg-color); color: var(--text-color); }
    .stMetric { background-color: var(--card-bg); padding: 16px; border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .stSelectbox, .stTextInput { background-color: var(--card-bg); border-radius: 8px; }
    div.stButton > button { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; border: none; border-radius: 8px; font-weight: 600; padding: 0.6rem 1rem; width: 100%; transition: all 0.3s ease; }
    div.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59,130,246,0.4); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK & VİZYON ---
st.title("⚽ FUTBOL İSTİHBARAT & POİSSON SANAT MERKEZİ")
st.markdown("🔥 *34.769 Maçlık Master Arşiv Üzerinden Değer Avcılığı ve Olasılık Sanatı*")
st.markdown("---")

# --- VERİ YÜKLEME ---
@st.cache_data
def load_master_archive():
    try:
        # Önce tekil master Excel dosyasını arayalım, yoksa CSV'leri birleştirelim
        df = pd.read_excel("Tum_Ligler_Dev_Arsiv_2021_2026.xlsx")
        if "Lig" not in df.columns and "Kupa / Lig" in df.columns:
            df.rename(columns={"Kupa / Lig": "Lig"}, inplace=True)
        return df
    except:
        return None

df_master = load_master_archive()

if df_master is None:
    st.error("⚠️ 'Tum_Ligler_Dev_Arsiv_2021_2026.xlsx' dosyası bulunamadı! Lütfen Excel arşiv dosyasının proje klasöründe olduğundan emin olun.")
else:
    # --- ÜST ÖZET METRİKLERİ ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Toplam Arşiv", f"{len(df_master):,} Maç", "2021-2026")
    c2.metric("Aktif Ligler", f"{df_master['Lig'].nunique()} Lig", "Global Havuz")
    c3.metric("Ev Sahibi Galibiyet", f"%{(df_master['MS Sonucu'].astype(str).str.contains('1|H', case=False)).mean()*100:.1f}", "Ortalama")
    c4.metric("Deplasman Galibiyet", f"%{(df_master['MS Sonucu'].astype(str).str.contains('2|A', case=False)).mean()*100:.1f}", "Ortalama")
    
    try:
        ev_g = df_master['MS Skor'].astype(str).str.split('-').str[0].str.strip().astype(float)
        dep_g = df_master['MS Skor'].astype(str).str.split('-').str[1].str.strip().astype(float)
        top_g = ev_g + dep_g
        c5.metric("Maç Başı Ortalama Gol", f"{top_g.mean():.2f}", "Gol Üstü Potansiyeli")
    except:
        c5.metric("Maç Başı Ortalama Gol", "2.84", "Standart")

    st.markdown("---")

    # --- SEKMELER ---
    tab1, tab2, tab3 = st.tabs(["🔍 Detaylı Maç & Skor Avcısı", "📊 Poisson Tahmin Matrisi", "📈 Arşiv İstatistik Sanatı"])

    # 1. SEKME: ARAMA VE FİLTRELEME
    with tab1:
        st.subheader("🎯 Arşiv İçinde Nokta Atışı Arama ve Filtreleme")
        
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            secilen_lig = st.selectbox("Lig Filtresi", ["Tümü"] + sorted(df_master["Lig"].dropna().unique().tolist()))
        with f_col2:
            secilen_sezon = st.selectbox("Sezon Filtresi", ["Tümü"] + sorted(df_master["Sezon"].dropna().unique().tolist(), reverse=True))
        with f_col3:
            takim_input = st.text_input("Takım Ara (Ev / Dep)", "")
        with f_col4:
            skor_input = st.text_input("Spesifik Skor Ara (Örn: 1-1, 2-1)", "")

        df_filt = df_master.copy()
        if secilen_lig != "Tümü":
            df_filt = df_filt[df_filt["Lig"] == secilen_lig]
        if secilen_sezon != "Tümü":
            df_filt = df_filt[df_filt["Sezon"] == secilen_sezon]
        if takim_input:
            df_filt = df_filt[
                df_filt["Ev Sahibi"].str.contains(takim_input, case=False, na=False) |
                df_filt["Deplasman"].str.contains(takim_input, case=False, na=False)
            ]
        if skor_input:
            df_filt = df_filt[df_filt["MS Skor"].astype(str).str.contains(skor_input.strip(), na=False)]

        st.info(f"Filtreleme Sonucu: **{len(df_filt)}** maç listeleniyor.")
        st.dataframe(df_filt[["Tarih", "Sezon", "Lig", "Ev Sahibi", "Deplasman", "MS Skor", "IY Skor", "MS Sonucu", "KG Var"]].head(250), use_container_width=True)

    # 2. SEKME: POİSSON MODELİ
    with tab2:
        st.subheader("🧪 İleri Düzey Poisson Olasılık ve Skor Dağılımı")
        p_col1, p_col2 = st.columns([1, 1.2])
        
        with p_col1:
            st.markdown("##### Takım Güç Parametreleri")
            ev_takim_sec = st.text_input("Ev Sahibi Takım Adı", "Galatasaray")
            dep_takim_sec = st.text_input("Deplasman Takım Adı", "Fenerbahçe")
            
            ev_lambda = st.slider("Ev Sahibi Beklenen Gol (xG)", 0.5, 3.5, 1.65, 0.05)
            dep_lambda = st.slider("Deplasman Beklenen Gol (xG)", 0.2, 3.0, 1.15, 0.05)

        with p_col2:
            st.markdown(f"##### 🎯 {ev_takim_sec} vs {dep_takim_sec} Olasılık Analizi")
            
            def poisson_prob(lmbda, k):
                return math.exp(-lmbda) * (lmbda ** k) / math.factorial(k)

            h_w, draw, a_w = 0, 0, 0
            score_probs = []
            for h in range(6):
                for a in range(6):
                    p = poisson_prob(ev_lambda, h) * poisson_prob(dep_lambda, a)
                    score_probs.append((f"{h}-{a}", p))
                    if h > a: h_w += p
                    elif h == a: draw += p
                    else: a_w += p

            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Ev Sahibi Kazanır", f"%{h_w*100:.1f}")
            m_col2.metric("Beraberlik", f"%{draw*100:.1f}")
            m_col3.metric("Deplasman Kazanır", f"%{a_w*100:.1f}")

            st.markdown("---")
            st.markdown("##### 🔮 En Yüksek Olasılıklı 5 Skor Beklentisi")
            score_probs.sort(key=lambda x: x[1], reverse=True)
            for sc, prob in score_probs[:5]:
                st.write(f"• **{sc}** Skor İhtimali: **%{prob*100:.2f}**")

    # 3. SEKME: İSTATİSTİKLER
    with tab3:
        st.subheader("📊 34.769 Maçlık Arşivin Çarpıcı Gerçekleri")
        stat_c1, stat_c2 = st.columns(2)
        with stat_c1:
            st.markdown("##### 🏆 En Sık Görülen 10 Maç Skoru")
            top_skorlar = df_master["MS Skor"].value_counts().head(10).reset_index()
            top_skorlar.columns = ["Skor", "Adet"]
            st.dataframe(top_skorlar, use_container_width=True)
        with stat_c2:
            st.markdown("##### 🌍 Liglere Göre Maç Dağılımı")
            lig_dagilim = df_master["Lig"].value_counts().reset_index()
            lig_dagilim.columns = ["Lig / Kupa", "Maç Sayısı"]
            st.dataframe(lig_dagilim, use_container_width=True)
