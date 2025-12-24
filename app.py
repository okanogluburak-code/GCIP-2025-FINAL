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

SCORE_GUIDE = {5: "🌟 5 - Excellent", 4: "✅ 4 - Good", 3: "⚖️ 3 - Average", 2: "🔸 2 - Work Needed", 1: "⚠️ 1 - Major Work Needed"}
SUST_SCORE_GUIDE = {5: "🦄 5 - Climate Unicorn", 3: "📈 3 - High Impact", 1: "🌱 1 - Positive Impact", 0: "❓ 0 - Insignificant"}

SESSIONS = {
    "1. İleri Malzemeler ve Kimyasallar Oturumu": {"teams": ["Bio4Life", "EKOHARMONI BIOCYCLING", "MicroExTech", "HELIOS BİLİM VE TEKNOLOJİ", "GMZ Enerji", "Umayana", "Chitolastic", "INOPOLYME KİMYA"]},
    "2. Atık Zenginleştirme Oturumu": {"teams": ["CHERRYMIC BİYOTEKNOLOJİ", "Main CEA Biyoteknoloji", "Evran Teknoloji", "COLORTECH ARGE", "Beaver-Nexus", "Bionova", "Vegg Foods", "Suje ARGE", "ATAK İleri Malzeme"]},
    "3. Yeşil Binalar+Ulaşım+Su Verimliliği Oturumu": {"teams": ["Ertech-Çıbık", "FURKHASA R&D", "Robeff Teknoloji", "Lentify", "Ardas Tech", "Plasmera", "İleriYZ"]},
    "4. Yenilenebilir Enerji+Enerji verimliliği Oturumu": {"teams": ["Ion Membranes", "Strategic Innovative Initiatives", "Unda Mühendislik", "MTM Biyoteknoloji", "ComfyAtelier", "Solis Technology", "Sonicpdt", "PhElSyM", "HELIOSTEAM", "Nesea Bio", "Zamia Kompozit", "Posamas", "Chambio Kimya", "Ramer Consulting", "ZincirX", "VEGUS BİYOTEKNOLOJİ", "ENVİCULTURE TARIM"]}
}

CRITERIA_DESC = {
    "1. Business Description": "Functional activities clarity?", "2. Customer Discovery": "Validated pain/market?",
    "3. Product/Technology Validation": "Third-party validated?", "4. Go-To-Market Tactics / Sales Model": "Sales model?",
    "5. Finances and Funding": "Credible projections?", "6. Legal": "IP/defensibility?",
    "7. Team": "Relevant skills?", "8. Sustainability": "Climate impact (0,1,3,5)?", "9. Presentation": "Pitch/Q&A?"
}

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, sep=';', encoding='utf-8-sig')
    return pd.DataFrame()

def save_all_data(df):
    df.to_csv(DATA_FILE, index=False, sep=';', encoding='utf-8-sig')

if 'editing_team' not in st.session_state: st.session_state.editing_team = None

master_df = load_data()

# --- SIDEBAR ---
st.sidebar.title("🏆 GCIP 2025 PORTAL")
page = st.sidebar.selectbox("Sayfa Seçin:", ["Scoring Panel", "Admin Dashboard"])
u_name = st.sidebar.text_input("Ad").strip()
u_surname = st.sidebar.text_input("Soyad").strip()
full_name = f"{u_name} {u_surname}"

if page == "Scoring Panel":
    if not u_name or not u_surname: st.warning("Ad-Soyad girerek giriş yapınız.")
    else:
        st.info("Presentation Scoring")
        sess_sel = st.selectbox("1. Oturum Seçin", ["Seçiniz..."] + list(SESSIONS.keys()))
        if sess_sel != "Seçiniz...":
            team_sel = st.selectbox("2. Takım Seçin", ["Seçiniz..."] + SESSIONS[sess_sel]["teams"])
            if team_sel != "Seçiniz...":
                # Veriyi Tazeleyerek Kontrol Et
                master_df = load_data()
                existing = master_df[(master_df['Judge'] == full_name) & (master_df['Team'] == team_sel)] if not master_df.empty else pd.DataFrame()
                is_locked = not existing.empty and st.session_state.editing_team != team_sel

                if is_locked:
                    st.success("✅ Puanlarınız kaydedilmiştir.")
                    if st.button("Puanları Düzenle (Unlock)"): 
                        st.session_state.editing_team = team_sel
                        st.rerun()
                else:
                    new_entries = {}
                    for title, desc in CRITERIA_DESC.items():
                        st.markdown(f"#### {title}")
                        st.caption(desc)
                        opts = [0,1,3,5] if "Sustainability" in title else [1,2,3,4,5]
                        val = st.select_slider(f"Score {title}", options=opts, key=f"s_{team_sel}_{title}")
                        if "Sustainability" in title: st.info(SUST_SCORE_GUIDE[val])
                        else: st.info(SCORE_GUIDE[val])
                        new_entries[f"{title}_Score"] = val
                        new_entries[f"{title}_Feedback"] = st.text_area(f"Notes {title}", key=f"f_{team_sel}_{title}")
                    
                    if st.button("💾 Kaydet ve Paylaş"):
                        total = sum([v for k,v in new_entries.items() if "_Score" in k])
                        entry = {"Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "Judge": full_name, "Session": sess_sel, "Team": team_sel, "Category": "Presentation Scoring", **new_entries, "Total_Score": total}
                        latest_df = load_data()
                        if not latest_df.empty: latest_df = latest_df[~((latest_df['Judge'] == full_name) & (latest_df['Team'] == team_sel))]
                        save_all_data(pd.concat([latest_df, pd.DataFrame([entry])], ignore_index=True))
                        st.session_state.editing_team = None
                        st.success("Kaydedildi!"); st.rerun()

elif page == "Admin Dashboard":
    if st.text_input("Yönetici Şifresi", type="password") == "GCIP2025*":
        master_df = load_data()
        if not master_df.empty:
            t1, t2, t3 = st.tabs(["📊 Genel Sıralama", "📅 Oturum Bazlı", "🎤 Detaylı Tablo"])
            with t1:
                res = master_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                st.table(res)
                st.download_button("Excel İndir", res.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), "Ranking.csv")
            with t2:
                s_sel = st.selectbox("Oturum", list(SESSIONS.keys()))
                st.table(master_df[master_df['Session'] == s_sel].groupby("Team")["Total_Score"].mean().sort_values(ascending=False))
            with t3:
                st.dataframe(master_df)

