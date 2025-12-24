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
MASTER_FILE = "gcip_master_results.csv"
DETAILED_FILE = "gcip_detailed_results.csv"

SCORE_GUIDE = {5: "🌟 5 - Excellent", 4: "✅ 4 - Good", 3: "⚖️ 3 - Average", 2: "🔸 2 - Work Needed", 1: "⚠️ 1 - Major Work Needed"}
SUST_SCORE_GUIDE = {5: "🦄 5 - Climate Impact Unicorn", 3: "📈 3 - High Impact", 1: "🌱 1 - Positive Impact", 0: "❓ 0 - Insignificant"}

SESSIONS = {
    "1. İleri Malzemeler ve Kimyasallar Oturumu": {"teams": ["Bio4Life", "EKOHARMONI BIOCYCLING", "MicroExTech", "HELIOS BİLİM VE TEKNOLOJİ", "GMZ Enerji", "Umayana", "Chitolastic", "INOPOLYME KİMYA"]},
    "2. Atık Zenginleştirme Oturumu": {"teams": ["CHERRYMIC BİYOTEKNOLOJİ", "Main CEA Biyoteknoloji", "Evran Teknoloji", "COLORTECH ARGE", "Beaver-Nexus", "Bionova", "Vegg Foods", "Suje ARGE", "ATAK İleri Malzeme"]},
    "3. Yeşil Binalar+Ulaşım+Su Verimliliği Oturumu": {"teams": ["Ertech-Çıbık", "FURKHASA R&D", "Robeff Teknoloji", "Lentify", "Ardas Tech", "Plasmera", "İleriYZ"]},
    "4. Yenilenebilir Enerji+Enerji verimliliği Oturumu": {"teams": ["Ion Membranes", "Strategic Innovative Initiatives", "Unda Mühendislik", "MTM Biyoteknoloji", "ComfyAtelier", "Solis Technology", "Sonicpdt", "PhElSyM", "HELIOSTEAM", "Nesea Bio", "Zamia Kompozit", "Posamas", "Chambio Kimya", "Ramer Consulting", "ZincirX", "VEGUS BİYOTEKNOLOJİ", "ENVİCULTURE TARIM"]}
}

CRITERIA_DESC = {
    "1. Business Description": "Functional activities clarity?", "2. Customer Discovery": "Validated pain/market?",
    "3. Product/Technology Validation": "Tech validated?", "4. Go-To-Market Tactics / Sales Model": "Sales model?",
    "5. Finances and Funding": "Finances?", "6. Legal": "IP?", "7. Team": "Skills?",
    "8. Sustainability": "Climate impact (0,1,3,5)?", "9. Presentation": "Pitch/Q&A?"
}

def load_csv(file):
    if os.path.exists(file): return pd.read_csv(file, sep=';', encoding='utf-8-sig')
    return pd.DataFrame()

def save_csv(df, file):
    df.to_csv(file, index=False, sep=';', encoding='utf-8-sig')

if 'editing_team' not in st.session_state: st.session_state.editing_team = None

# --- SIDEBAR ---
st.sidebar.title("🏆 GCIP 2025 PORTAL")
page = st.sidebar.selectbox("Sayfa Seçin:", ["Scoring Panel", "Admin Dashboard"])
u_name = st.sidebar.text_input("Ad").strip()
u_surname = st.sidebar.text_input("Soyad").strip()
full_name = f"{u_name} {u_surname}"

if page == "Scoring Panel":
    if not u_name or not u_surname: st.warning("Giriş yapınız.")
    else:
        st.info("Presentation Scoring")
        sess_sel = st.selectbox("1. Oturum Seçin", ["Seçiniz..."] + list(SESSIONS.keys()))
        if sess_sel != "Seçiniz...":
            team_sel = st.selectbox("2. Takım Seçin", ["Seçiniz..."] + SESSIONS[sess_sel]["teams"])
            if team_sel != "Seçiniz...":
                detailed_df = load_csv(DETAILED_FILE)
                existing = detailed_df[(detailed_df['Judge'] == full_name) & (detailed_df['Team'] == team_sel)] if not detailed_df.empty else pd.DataFrame()
                is_locked = not existing.empty and st.session_state.editing_team != team_sel

                if is_locked:
                    st.success("✅ Kayıtlı.")
                    if st.button("Puanları Düzenle (Unlock)"): st.session_state.editing_team = team_sel; st.rerun()
                else:
                    new_entries = {}
                    for title, desc in CRITERIA_DESC.items():
                        st.markdown(f"#### {title}")
                        st.caption(desc)
                        opts = [0,1,3,5] if "Sustainability" in title else [1,2,3,4,5]
                        
                        def_sc = 3 if "Sustainability" not in title else 1
                        if not existing.empty and f"{title}_Score" in existing.columns:
                            try: def_sc = int(float(existing[f"{title}_Score"].values[0]))
                            except: pass
                        
                        val = st.select_slider(f"Score {title}", options=opts, value=def_sc, key=f"s_{team_sel}_{title}")
                        st.info(SUST_SCORE_GUIDE[val] if "Sustainability" in title else SCORE_GUIDE[val])
                        new_entries[f"{title}_Score"] = val
                        
                        def_fb = str(existing[f"{title}_Feedback"].values[0]) if not existing.empty and f"{title}_Feedback" in existing.columns and not pd.isna(existing[f"{title}_Feedback"].values[0]) else ""
                        new_entries[f"{title}_Feedback"] = st.text_area(f"Notes {title}", value=def_fb, key=f"f_{team_sel}_{title}")
                    
                    if st.button("💾 Kaydet ve Paylaş"):
                        total = sum([v for k,v in new_entries.items() if "_Score" in k])
                        entry = {"Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "Judge": full_name, "Session": sess_sel, "Team": team_sel, "Category": "Presentation Scoring", **new_entries, "Total_Score": total}
                        
                        # 1. Update Detailed CSV (Session 3 & 4 only)
                        latest_det = load_csv(DETAILED_FILE)
                        if not latest_det.empty: latest_det = latest_det[~((latest_det['Judge'] == full_name) & (latest_det['Team'] == team_sel))]
                        save_csv(pd.concat([latest_det, pd.DataFrame([entry])], ignore_index=True), DETAILED_FILE)
                        
                        # 2. Update Master Ranking CSV (Calculated Mean)
                        current_det = load_csv(DETAILED_FILE)
                        team_avg = current_det[current_det['Team'] == team_sel]['Total_Score'].mean()
                        
                        latest_mast = load_csv(MASTER_FILE)
                        if not latest_mast.empty: latest_mast = latest_mast[~((latest_mast['Team'] == team_sel) & (latest_mast['Session'] == sess_sel))]
                        m_entry = {"Team": team_sel, "Total_Score": round(team_avg, 2), "Session": sess_sel}
                        save_csv(pd.concat([latest_mast, pd.DataFrame([m_entry])], ignore_index=True), MASTER_FILE)
                        
                        st.session_state.editing_team = None
                        st.success("Kaydedildi!"); st.rerun()

elif page == "Admin Dashboard":
    if st.text_input("Şifre", type="password") == "GCIP2025*":
        master_df = load_csv(MASTER_FILE)
        detailed_df = load_csv(DETAILED_FILE)
        
        t1, t2, t3 = st.tabs(["📊 Genel Sıralama", "📅 Oturum Bazlı", "🎤 Sunum Detay Tablosu"])
        with t1:
            if not master_df.empty:
                res = master_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                res.index += 1
                st.table(res)
                st.download_button("Excel İndir", res.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), "Global_Ranking.csv")
        with t2:
            if not master_df.empty:
                for s in SESSIONS.keys():
                    s_df = master_df[master_df['Session'] == s]
                    if not s_df.empty:
                        st.write(f"##### {s}")
                        sr = s_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                        sr.index += 1
                        st.table(sr)
                        st.download_button(f"Excel ({s})", sr.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), f"{s}_Rank.csv")
        with t3:
            if not detailed_df.empty:
                st.dataframe(detailed_df)
                st.download_button("Excel İndir", detailed_df.to_csv(sep=';', index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Detailed_Report.csv")
