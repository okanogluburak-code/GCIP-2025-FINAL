# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 16:30:08 2025

@author: burak.okanoglu
"""

import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="GCIP 2025 Jury Portal", layout="wide")
DATA_FILE = "gcip_master_results.csv"

# Orijinal Puan Rehberi
SCORE_GUIDE = {
    5: "🌟 **5 - Keep doing what you’re doing.** Focus on other areas.",
    4: "✅ **4 - Almost there.** Could be better if [……]",
    3: "⚖️ **3 - Mixed.** Key areas for improvement include […]",
    2: "🔸 **2 - Work needed in this area.** You should focus on [……]",
    1: "⚠️ **1 - Significant work needed here,** particularly […]"
}

# Oturum ve Takım Listesi
SESSIONS = {
    "1. İleri Malzemeler ve Kimyasallar Oturumu": {"date": "22.12.2025", "teams": ["Bio4Life", "EKOHARMONI BIOCYCLING", "MicroExTech", "HELIOS BİLİM VE TEKNOLOJİ", "GMZ Enerji", "Umayana", "Chitolastic", "INOPOLYME KİMYA"]},
    "2. Atık Zenginleştirme Oturumu": {"date": "23.12.2025", "teams": ["CHERRYMIC BİYOTEKNOLOJİ", "Main CEA Biyoteknoloji", "Evran Teknoloji", "COLORTECH ARGE", "Beaver-Nexus", "Bionova", "Vegg Foods", "Suje ARGE", "ATAK İleri Malzeme"]},
    "3. Yeşil Binalar+Ulaşım+Su Verimliliği Oturumu": {"date": "24.12.2025", "teams": ["Ertech-Çıbık", "FURKHASA R&D", "Robeff Teknoloji", "Lentify", "Ardas Tech", "Plasmera", "İleriYZ"]},
    "4. Yenilenebilir Enerji+Enerji verimliliği Oturumu": {"date": "25.12.2025", "teams": ["Ion Membranes", "Strategic Innovative Initiatives", "Unda Mühendislik", "MTM Biyoteknoloji", "ComfyAtelier", "Solis Technology", "Sonicpdt", "PhElSyM", "HELIOSTEAM", "Nesea Bio", "Zamia Kompozit", "Posamas", "Chambio Kimya", "Ramer Consulting", "ZincirX", "VEGUS BİYOTEKNOLOJİ", "ENVİCULTURE TARIM"]}
}

# Excel'den Gelen Orijinal Başlıklar ve Açıklamalar (Descriptions)
PRES_CRITERIA_DATA = {
    "1. Business Description": "Do they know what all the required functional activities are of their proposed business?",
    "2. Customer Discovery": "A. Clearly validated pain or problem? B. Specific beachhead segment? C. First $1 million revenue path? D. Pilot customers?",
    "3. Product/Technology Validation": "A. Third-party validated? B. Clear competitive advantage? C. Roadmap for prototype/commercial product? D. Profitable scaling?",
    "4. Go-To-Market Tactics / Sales Model": "A. Customer-validated model for sales growth? B. Channel/strategic partner strategy for adjacent segments?",
    "5. Finances and Funding": "A. Credible revenue/cost projections? B. Clear and logical strategy for the sources and uses of funds?",
    "6. Legal": "A. IP patentable and defensible? B. Corporate and cap structure free of issues?",
    "7. Team": "A. Relevant skills and appropriate connections? B. Aware of skill gaps and how to fill them?",
    "8. Sustainability": "A. Quantified environmental/social impact? B. Operations responsibility? C. SDG address?",
    "9. Presentation": "A. Clear presentation & Q&A? B. Complete Business Model elements? C. Compelling investment opportunity?"
}

# --- 2. VERİ YÖNETİMİ ---
def load_data():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE, sep=';', encoding='utf-8-sig')
        except: return pd.DataFrame()
    return pd.DataFrame()

def save_all_data(df):
    df.to_csv(DATA_FILE, index=False, sep=';', encoding='utf-8-sig')

# Session State Yönetimi (Unlock butonu için)
if 'editing_team' not in st.session_state:
    st.session_state.editing_team = None

master_df = load_data()

# --- 3. SIDEBAR ---
st.sidebar.title("🏆 GCIP 2025 PORTAL")
page = st.sidebar.selectbox("Sayfa Seçin:", ["Scoring Panel", "Admin Dashboard"])
st.sidebar.divider()
u_name = st.sidebar.text_input("Ad").strip()
u_surname = st.sidebar.text_input("Soyad").strip()
full_name = f"{u_name} {u_surname}"

# --- 4. JÜRİ PANELİ (SCORING) ---
if page == "Scoring Panel":
    if not u_name or not u_surname:
        st.warning("Lütfen sol menüden Ad ve Soyad giriniz.")
    else:
        st.info("Kategori: Presentation Scoring (Worksheet kaldırılmıştır)")
        sess_options = [f"{k} ({v['date']})" for k, v in SESSIONS.items()]
        sess_choice_raw = st.selectbox("1. Oturum Seçin", ["Seçiniz..."] + sess_options)
        
        if sess_choice_raw != "Seçiniz...":
            sess_key = sess_choice_raw.split(" (")[0]
            team_choice = st.selectbox("2. Takım Seçin", ["Seçiniz..."] + SESSIONS[sess_key]["teams"])
            
            if team_choice != "Seçiniz...":
                # Benzersiz kimlik
                mode = "Presentation Scoring"
                key_id = f"{full_name}_{team_choice}_{mode}".replace(" ", "_")
                
                # Veritabanı kontrolü
                existing = master_df[(master_df['Judge'] == full_name) & (master_df['Team'] == team_choice) & (master_df['Category'] == mode)] if not master_df.empty else pd.DataFrame()

                # Düzenleme modu kontrolü
                is_locked = not existing.empty and st.session_state.editing_team != team_choice
                
                if not is_locked and not existing.empty:
                    st.warning(f"⚠️ {team_choice} için mevcut puanlarınızı düzenliyorsunuz.")
                elif is_locked:
                    st.success(f"✅ {team_choice} kaydedildi. Puanlarınızı aşağıda görebilirsiniz.")
                    if st.button("Puanları Düzenle (Unlock)"):
                        st.session_state.editing_team = team_choice
                        st.rerun()

                st.subheader(f"{team_choice} Değerlendirmesi")
                new_entries = {}

                for title, desc in PRES_CRITERIA_DATA.items():
                    st.markdown(f"#### {title}")
                    st.caption(desc) # Excel'den gelen açıklama metni
                    
                    col1, col2 = st.columns([1, 1])
                    
                    score_col = f"{title}_Score"
                    fb_col = f"{title}_Feedback"
                    
                    # Varsayılan değerleri çek
                    def_sc = 3
                    if not existing.empty and score_col in existing.columns:
                        def_sc = int(existing[score_col].values[0])
                    
                    def_fb = ""
                    if not existing.empty and fb_col in existing.columns:
                        def_fb = str(existing[fb_col].values[0]) if not pd.isna(existing[fb_col].values[0]) else ""
                    
                    with col1:
                        v = st.select_slider(f"Puan ({title})", options=[1,2,3,4,5], value=def_sc, disabled=is_locked, key=f"s_{key_id}_{title}")
                        st.info(SCORE_GUIDE[v])
                        new_entries[score_col] = v
                    with col2:
                        f = st.text_area(f"Notlar ({title})", value=def_fb, disabled=is_locked, key=f"f_{key_id}_{title}")
                        new_entries[fb_col] = f
                    st.divider()

                if not is_locked and st.button("💾 Kaydet ve Paylaş"):
                    total = sum([val for k, val in new_entries.items() if "_Score" in k])
                    entry = {
                        "Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), 
                        "Judge": full_name, 
                        "Session": sess_key, 
                        "Team": team_choice, 
                        "Category": mode, 
                        **new_entries, 
                        "Total_Score": total
                    }
                    
                    # Mevcut kaydı güncelle (silip tekrar ekle)
                    if not master_df.empty:
                        master_df = master_df[~((master_df['Judge'] == full_name) & (master_df['Team'] == team_choice) & (master_df['Category'] == mode))]
                    
                    master_df = pd.concat([master_df, pd.DataFrame([entry])], ignore_index=True)
                    save_all_data(master_df)
                    st.session_state.editing_team = None # Düzenleme modunu kapat
                    st.success("Kaydedildi!"); st.balloons(); st.rerun()

# --- 5. ADMİN PANELİ ---
elif page == "Admin Dashboard":
    st.header("🔐 Yönetici Paneli")
    if st.text_input("Şifre", type="password") == "GCIP2025*":
        if not master_df.empty:
            t1, t2, t3, t4 = st.tabs(["📊 Genel Sıralama", "📅 Oturum Bazlı", "🎤 Sunum Detay", "⚙️ Yönetim"])
            
            base_cols = ["Timestamp", "Judge", "Session", "Team", "Category", "Total_Score"]

            with t1:
                st.subheader("Global Leaderboard")
                df_c = master_df[master_df['Category'] == "Presentation Scoring"]
                if not df_c.empty:
                    r = df_c.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                    r.index += 1; st.table(r)
                    st.download_button("Genel Sıralama Excel", r.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), "Global_Ranking_Presentation.csv")

            with t2:
                st.subheader("Oturum Bazlı Sıralama")
                for s in SESSIONS.keys():
                    s_df = master_df[(master_df['Category'] == "Presentation Scoring") & (master_df['Session'] == s)]
                    if not s_df.empty:
                        st.write(f"##### {s}")
                        sr = s_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                        sr.index += 1; st.table(sr)

            with t3:
                st.subheader("Detaylı Sunum Tablosu")
                p_full = master_df[master_df['Category'] == "Presentation Scoring"].copy()
                if not p_full.empty:
                    p_cols = base_cols + [f"{c}_Score" for c in PRES_CRITERIA_DATA.keys()] + [f"{c}_Feedback" for c in PRES_CRITERIA_DATA.keys()]
                    display_cols = [c for c in p_cols if c in p_full.columns]
                    st.dataframe(p_full[display_cols], use_container_width=True)
                    st.download_button("Detaylı Veri Excel", p_full[display_cols].to_csv(sep=';', index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Presentation_Detailed_Data.csv")

            with t4:
                st.subheader("Jüri Analizi & Kayıt Yönetimi")
                j_stats = master_df.groupby("Judge")["Total_Score"].agg(['mean', 'count']).reset_index()
                st.dataframe(j_stats)
                
                st.divider()
                to_del = st.selectbox("Kaydı Sıfırla:", ["Seçiniz..."] + master_df.apply(lambda r: f"{r['Judge']} | {r['Team']}", axis=1).tolist())
                if to_del != "Seçiniz..." and st.button("Sil"):
                    p = to_del.split(" | ")
                    master_df = master_df[~((master_df['Judge'] == p[0]) & (master_df['Team'] == p[1]))]
                    save_all_data(master_df); st.rerun()
                
                if st.button("⚠️ TÜM SİSTEMİ SIFIRLA"):
                    if os.path.exists(DATA_FILE): os.remove(DATA_FILE); st.rerun()
        else:
            st.info("Henüz veri yok.")

