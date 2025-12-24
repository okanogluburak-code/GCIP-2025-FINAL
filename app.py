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

# Genel Puan Rehberi
SCORE_GUIDE = {
    5: "🌟 **5 - Keep doing what you’re doing.** Focus on other areas.",
    4: "✅ **4 - Almost there.** Could be better if [……]",
    3: "⚖️ **3 - Mixed.** Key areas for improvement include […]",
    2: "🔸 **2 - Work needed in this area.** You should focus on [……]",
    1: "⚠️ **1 - Significant work needed here,** particularly […]"
}

# 8. Sustainability Rehberi
SUST_SCORE_GUIDE = {
    5: "🦄 **5 - Climate Impact Unicorn:** (>1Mt CO2eq per year in year 3)",
    3: "📈 **3 - High positive climate impact:** (>1Kt CO2eq per year in year 3)",
    1: "🌱 **1 - Positive climate impact:** (>6.8t CO2eq per year in year 1)",
    0: "❓ **0 - Insignificant climate impact:** (<6.8t CO2eq per year)"
}

SESSIONS = {
    "1. İleri Malzemeler ve Kimyasallar Oturumu": {"teams": ["Bio4Life", "EKOHARMONI BIOCYCLING", "MicroExTech", "HELIOS BİLİM VE TEKNOLOJİ", "GMZ Enerji", "Umayana", "Chitolastic", "INOPOLYME KİMYA"]},
    "2. Atık Zenginleştirme Oturumu": {"teams": ["CHERRYMIC BİYOTEKNOLOJİ", "Main CEA Biyoteknoloji", "Evran Teknoloji", "COLORTECH ARGE", "Beaver-Nexus", "Bionova", "Vegg Foods", "Suje ARGE", "ATAK İleri Malzeme"]},
    "3. Yeşil Binalar+Ulaşım+Su Verimliliği Oturumu": {"teams": ["Ertech-Çıbık", "FURKHASA R&D", "Robeff Teknoloji", "Lentify", "Ardas Tech", "Plasmera", "İleriYZ"]},
    "4. Yenilenebilir Enerji+Enerji verimliliği Oturumu": {"teams": ["Ion Membranes", "Strategic Innovative Initiatives", "Unda Mühendislik", "MTM Biyoteknoloji", "ComfyAtelier", "Solis Technology", "Sonicpdt", "PhElSyM", "HELIOSTEAM", "Nesea Bio", "Zamia Kompozit", "Posamas", "Chambio Kimya", "Ramer Consulting", "ZincirX", "VEGUS BİYOTEKNOLOJİ", "ENVİCULTURE TARIM"]}
}

PRES_CRITERIA_DATA = {
    "1. Business Description": "Do they know what all the required functional activities are of their proposed business?",
    "2. Customer Discovery": "A. Clearly validated pain or problem? B. Specific beachhead segment? C. First $1 million revenue path? D. Pilot customers?",
    "3. Product/Technology Validation": "A. Third-party validated? B. Clear competitive advantage? C. Roadmap for prototype/commercial product? D. Profitable scaling?",
    "4. Go-To-Market Tactics / Sales Model": "A. Customer-validated model for sales growth? B. Channel/strategic partner strategy for adjacent segments?",
    "5. Finances and Funding": "A. Credible revenue/cost projections? B. Clear and logical strategy for the sources and uses of funds?",
    "6. Legal": "A. IP patentability and defensible? B. Corporate and cap structure free of issues?",
    "7. Team": "A. Relevant skills and appropriate connections? B. Aware of skill gaps and how to fill them?",
    "8. Sustainability": "Climate impact potential and SDG address. (Scoring: 0, 1, 3, 5)",
    "9. Presentation": "A. Clear presentation & Q&A? B. Complete Business Model elements? C. Compelling investment opportunity?"
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
    if not u_name or not u_surname: st.warning("Lütfen Ad ve Soyad girerek giriş yapınız.")
    else:
        st.info("Kategori: Presentation Scoring")
        sess_sel = st.selectbox("1. Oturum Seçin", ["Seçiniz..."] + list(SESSIONS.keys()))
        if sess_sel != "Seçiniz...":
            team_sel = st.selectbox("2. Takım Seçin", ["Seçiniz..."] + SESSIONS[sess_sel]["teams"])
            if team_sel != "Seçiniz...":
                detailed_df = load_csv(DETAILED_FILE)
                existing = detailed_df[(detailed_df['Judge'] == full_name) & (detailed_df['Team'] == team_sel)] if not detailed_df.empty else pd.DataFrame()
                is_locked = not existing.empty and st.session_state.editing_team != team_sel

                if is_locked:
                    st.success(f"✅ {team_sel} için puanlarınız kaydedilmiştir.")
                    if st.button("Puanları Düzenle (Unlock)"): 
                        st.session_state.editing_team = team_sel
                        st.rerun()
                else:
                    new_entries = {}
                    for title, desc in PRES_CRITERIA_DATA.items():
                        st.markdown(f"### {title}")
                        st.caption(desc)
                        
                        col1, col2 = st.columns([1, 1])
                        opts = [0, 1, 3, 5] if "Sustainability" in title else [1, 2, 3, 4, 5]
                        
                        # Varsayılan puan
                        def_sc = 3 if "Sustainability" not in title else 1
                        if not existing.empty and f"{title}_Score" in existing.columns:
                            try: def_sc = int(float(existing[f"{title}_Score"].values[0]))
                            except: pass
                        
                        with col1:
                            val = st.select_slider(f"Puan ({title})", options=opts, value=def_sc, key=f"s_{team_sel}_{title}")
                            if "Sustainability" in title: st.info(SUST_SCORE_GUIDE[val])
                            else: st.info(SCORE_GUIDE[val])
                            new_entries[f"{title}_Score"] = val
                        
                        with col2:
                            def_fb = str(existing[f"{title}_Feedback"].values[0]) if not existing.empty and f"{title}_Feedback" in existing.columns and not pd.isna(existing[f"{title}_Feedback"].values[0]) else ""
                            new_entries[f"{title}_Feedback"] = st.text_area(f"Notlar ({title})", value=def_fb, key=f"f_{team_sel}_{title}")
                        st.divider()
                    
                    if st.button("💾 Kaydet ve Paylaş"):
                        total = sum([v for k,v in new_entries.items() if "_Score" in k])
                        entry = {"Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "Judge": full_name, "Session": sess_sel, "Team": team_sel, "Category": "Presentation Scoring", **new_entries, "Total_Score": total}
                        
                        latest_det = load_csv(DETAILED_FILE)
                        if not latest_det.empty: latest_det = latest_det[~((latest_det['Judge'] == full_name) & (latest_det['Team'] == team_sel))]
                        save_csv(pd.concat([latest_det, pd.DataFrame([entry])], ignore_index=True), DETAILED_FILE)
                        
                        current_det = load_csv(DETAILED_FILE)
                        team_avg = current_det[current_det['Team'] == team_sel]['Total_Score'].mean()
                        latest_mast = load_csv(MASTER_FILE)
                        if not latest_mast.empty: latest_mast = latest_mast[~((latest_mast['Team'] == team_sel) & (latest_mast['Session'] == sess_sel))]
                        m_entry = {"Team": team_sel, "Total_Score": round(team_avg, 2), "Session": sess_sel}
                        save_csv(pd.concat([latest_mast, pd.DataFrame([m_entry])], ignore_index=True), MASTER_FILE)
                        
                        st.session_state.editing_team = None
                        st.success("Kaydedildi!"); st.balloons(); st.rerun()

elif page == "Admin Dashboard":
    if st.text_input("Yönetici Şifresi", type="password") == "GCIP2025*":
        master_df = load_csv(MASTER_FILE)
        detailed_df = load_csv(DETAILED_FILE)
        
        t1, t2, t3, t4 = st.tabs(["📊 Genel Sıralama", "📅 Oturum Bazlı", "🎤 Sunum Detay Tablosu", "⚙️ Yönetim"])
        
        with t1:
            st.subheader("Global Leaderboard")
            if not master_df.empty:
                res = master_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                res.index += 1
                st.table(res)
                st.download_button("Genel Sıralama Excel İndir", res.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), "Global_Ranking.csv")
        
        with t2:
            st.subheader("Oturum Bazlı Sıralama")
            if not master_df.empty:
                for s in SESSIONS.keys():
                    s_df = master_df[master_df['Session'] == s]
                    if not s_df.empty:
                        st.write(f"##### {s}")
                        sr = s_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                        sr.index += 1
                        st.table(sr)
                        st.download_button(f"Excel İndir ({s})", sr.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), f"{s}_Ranking.csv")
        
        with t3:
            st.subheader("Sunum Detay Tablosu")
            if not detailed_df.empty:
                for s_name in SESSIONS.keys():
                    s_det_df = detailed_df[detailed_df['Session'] == s_name]
                    if not s_det_df.empty:
                        st.write(f"##### {s_name}")
                        st.dataframe(s_det_df, use_container_width=True)
                        st.download_button(f"Excel İndir ({s_name})", s_det_df.to_csv(sep=';', index=False, encoding='utf-8-sig').encode('utf-8-sig'), f"{s_name}_Detayli.csv", key=f"dl_{s_name}")
            else:
                st.info("Detaylı veri bulunamadı.")

        with t4:
            st.subheader("⚙️ Kayıt ve Puan Yönetimi")
            if not detailed_df.empty:
                st.write("Mevcut jüri oylarını buradan silebilirsiniz:")
                # Kayıt Silme
                record_list = [f"{r['Judge']} | {r['Team']} | {r['Session']}" for _, r in detailed_df.iterrows()]
                to_delete = st.selectbox("Silinecek Kaydı Seçin:", ["Seçiniz..."] + record_list)
                
                if to_delete != "Seçiniz...":
                    if st.button("Seçili Puanı Sil"):
                        j_name, t_name, s_name = to_delete.split(" | ")
                        # Detailed Sil
                        detailed_df = detailed_df[~((detailed_df['Judge'] == j_name) & (detailed_df['Team'] == t_name))]
                        save_csv(detailed_df, DETAILED_FILE)
                        # Master Güncelle
                        new_avg = detailed_df[detailed_df['Team'] == t_name]['Total_Score'].mean()
                        master_df = load_csv(MASTER_FILE)
                        master_df = master_df[~(master_df['Team'] == t_name)]
                        if not pd.isna(new_avg):
                            m_entry = {"Team": t_name, "Total_Score": round(new_avg, 2), "Session": s_name}
                            master_df = pd.concat([master_df, pd.DataFrame([m_entry])], ignore_index=True)
                        save_csv(master_df, MASTER_FILE)
                        st.success("Kayıt başarıyla silindi.")
                        st.rerun()
            
            st.divider()
            st.warning("Tehlikeli Bölge")
            if st.button("⚠️ TÜM PUANLARI SIFIRLA"):
                if os.path.exists(MASTER_FILE): os.remove(MASTER_FILE)
                if os.path.exists(DETAILED_FILE): os.remove(DETAILED_FILE)
                st.error("Tüm veritabanı sıfırlandı. Sayfa yenileniyor...")
                st.rerun()
