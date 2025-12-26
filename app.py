# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 16:30:08 2025

@author: burak.okanoglu
"""

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="GCIP 2025 Jury Portal", layout="wide")
MASTER_FILE = "gcip_master_results.csv"
DETAILED_FILE = "gcip_detailed_results.csv"

# Rehberler
SCORE_GUIDE = {5: "🌟 5 - Excellent", 4: "✅ 4 - Good", 3: "⚖️ 3 - Average", 2: "🔸 2 - Work Needed", 1: "⚠️ 1 - Major Work Needed"}
SUST_SCORE_GUIDE = {5: "🦄 5 - Climate Impact Unicorn", 3: "📈 3 - High Impact", 1: "🌱 1 - Positive Impact", 0: "❓ 0 - Insignificant"}

SESSIONS = {
    "1. İleri Malzemeler ve Kimyasallar Oturumu": {"teams": ["Bio4Life", "EKOHARMONI BIOCYCLING", "MicroExTech", "HELIOS BİLİM VE TEKNOLOJİ", "GMZ Enerji", "Umayana", "Chitolastic", "INOPOLYME KİMYA"]},
    "2. Atık Zenginleştirme Oturumu": {"teams": ["CHERRYMIC BİYOTEKNOLOJİ", "Main CEA Biyoteknoloji", "Evran Teknoloji", "COLORTECH ARGE", "Beaver-Nexus", "Bionova", "Vegg Foods", "Suje ARGE", "ATAK İleri Malzeme"]},
    "3. Yeşil Binalar+Ulaşım+Su Verimliliği Oturumu": {"teams": ["Ertech-Çıbık", "FURKHASA R&D", "Robeff Teknoloji", "Lentify", "Ardas Tech", "Plasmera", "İleriYZ"]},
    "4. Yenilenebilir Enerji+Enerji verimliliği Oturumu": {"teams": ["Ion Membranes", "Strategic Innovative Initiatives", "Unda Mühendislik", "MTM Biyoteknoloji", "ComfyAtelier", "Solis Technology", "Sonicpdt", "PhElSyM", "HELIOSTEAM", "Nesea Bio", "Zamia Kompozit", "Posamas", "Chambio Kimya", "Ramer Consulting", "ZincirX", "VEGUS BİYOTEKNOLOJİ", "ENVİCULTURE TARIM"]}
}

PRES_CRITERIA_DATA = {
    "1. Business Description": "Activities clarity?", "2. Customer Discovery": "Pain validated?", 
    "3. Product/Technology Validation": "Tech validated?", "4. Go-To-Market Tactics / Sales Model": "Sales model?",
    "5. Finances and Funding": "Finances?", "6. Legal": "IP?", "7. Team": "Skills?",
    "8. Sustainability": "Climate impact (0,1,3,5)?", "9. Presentation": "Pitch/Q&A?"
}

def load_csv(file):
    if os.path.exists(file): return pd.read_csv(file, sep=';', encoding='utf-8-sig')
    return pd.DataFrame()

def save_csv(df, file):
    df.to_csv(file, index=False, sep=';', encoding='utf-8-sig')

# Genel Sıralamayı (Master) Detaylı Tablodan Yeniden Hesapla (Silme/Düzenleme Sonrası)
def refresh_master():
    det = load_csv(DETAILED_FILE)
    if not det.empty:
        master = det.groupby(['Team', 'Session'])['Total_Score'].mean().reset_index()
        save_csv(master, MASTER_FILE)
    else:
        if os.path.exists(MASTER_FILE): os.remove(MASTER_FILE)

if 'editing_team' not in st.session_state: st.session_state.editing_team = None

# --- SIDEBAR ---
st.sidebar.title("🏆 GCIP 2025 PORTAL")
page = st.sidebar.selectbox("Sayfa Seçin:", ["Scoring Panel", "Admin Dashboard"])
u_name = st.sidebar.text_input("Ad").strip()
u_surname = st.sidebar.text_input("Soyad").strip()
full_name = f"{u_name} {u_surname}"

if page == "Scoring Panel":
    if not u_name or not u_surname: st.warning("Lütfen giriş yapınız.")
    else:
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
                        opts = [0, 1, 3, 5] if "Sustainability" in title else [1, 2, 3, 4, 5]
                        
                        # Eğer eski puan varsa onu getir, yoksa default 3
                        default_val = 3
                        if not existing.empty:
                            default_val = int(existing[f"{title}_Score"].values[0])
                        
                        val = st.select_slider(f"Puan {title}", options=opts, value=default_val, key=f"s_{team_sel}_{title}")
                        new_entries[f"{title}_Score"] = val
                        
                        default_fb = ""
                        if not existing.empty:
                            default_fb = str(existing[f"{title}_Feedback"].values[0])
                        new_entries[f"{title}_Feedback"] = st.text_area(f"Notlar {title}", value=default_fb, key=f"f_{team_sel}_{title}")
                    
                    if st.button("💾 Kaydet"):
                        total = sum([v for k,v in new_entries.items() if "_Score" in k])
                        entry = {"Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"), "Judge": full_name, "Session": sess_sel, "Team": team_sel, "Category": "Presentation Scoring", **new_entries, "Total_Score": total}
                        
                        latest_det = load_csv(DETAILED_FILE)
                        if not latest_det.empty: 
                            latest_det = latest_det[~((latest_det['Judge'] == full_name) & (latest_det['Team'] == team_sel))]
                        
                        save_csv(pd.concat([latest_det, pd.DataFrame([entry])], ignore_index=True), DETAILED_FILE)
                        refresh_master() # Genel tabloyu da güncelle
                        st.session_state.editing_team = None
                        st.success("Kaydedildi!"); st.rerun()

elif page == "Admin Dashboard":
    if st.text_input("Şifre", type="password") == "GCIP2025*":
        master_df = load_csv(MASTER_FILE)
        detailed_df = load_csv(DETAILED_FILE)
        t1, t2, t3, t4 = st.tabs(["📊 Genel", "📅 Oturum Bazlı", "🎤 Detay Sunum", "⚙️ Yönetim"])
        
        with t1:
            if not master_df.empty:
                res = master_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index(); res.index += 1
                st.table(res)
        with t2:
            for s in SESSIONS.keys():
                s_df = master_df[master_df['Session'] == s]
                if not s_df.empty:
                    st.write(f"##### {s}")
                    sr = s_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index(); sr.index += 1
                    st.table(sr)
        with t3:
            st.subheader("🎤 Detaylı Sunum Tablosu")
            if not detailed_df.empty:
                for s_name in SESSIONS.keys():
                    s_det_df = detailed_df[detailed_df['Session'] == s_name]
                    if not s_det_df.empty:
                        st.write(f"##### {s_name}")
                        st.dataframe(s_det_df, use_container_width=True)
        
        with t4:
            st.subheader("⚙️ Kayıt ve Puan Yönetimi")
            if not detailed_df.empty:
                st.write("Mevcut jüri oylarını buradan silebilirsiniz (Örn: Tuğçe Öztürk'ün hatalı puanı):")
                
                # Silme işlemi için liste oluştur
                record_list = [f"{r['Judge']} | {r['Team']} | {r['Session']}" for _, r in detailed_df.iterrows()]
                to_delete = st.selectbox("Silinecek Kaydı Seçin:", ["Seçiniz..."] + record_list)
                
                if to_delete != "Seçiniz...":
                    if st.button("Seçili Puanı Sil"):
                        j_name, t_name, _ = to_delete.split(" | ")
                        detailed_df = detailed_df[~((detailed_df['Judge'] == j_name) & (detailed_df['Team'] == t_name))]
                        save_csv(detailed_df, DETAILED_FILE)
                        refresh_master() # Sıralamayı yeniden hesapla
                        st.success(f"Başarıyla silindi: {to_delete}")
                        st.rerun()

            st.divider()
            if st.button("⚠️ TÜM SİSTEMİ SIFIRLA (DİKKAT!)"):
                if os.path.exists(MASTER_FILE): os.remove(MASTER_FILE)
                if os.path.exists(DETAILED_FILE): os.remove(DETAILED_FILE)
                st.warning("Tüm veriler temizlendi.")
                st.rerun()

