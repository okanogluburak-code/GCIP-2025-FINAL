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

# Excel'deki Orijinal Başlıklar (Topic Names)
PRES_CRITERIA = [
    "1. Business Description", 
    "2. Customer Discovery", 
    "3. Product/Technology Validation", 
    "4. Go-To-Market Tactics / Sales Model", 
    "5. Finances and Funding", 
    "6. Legal", 
    "7. Team", 
    "8. Sustainability", 
    "9. Presentation"
]

WORK_CRITERIA = [
    "1. Business Model Canvas (İş Modeli Kanvası)", 
    "2. Product/Market Fit (Ürün/Pazar Uyumu)", 
    "3. Markets and Getting To Them (Pazar ve Pazarlara Ulaşım)", 
    "4. Product/Technology Validation (Ürün/Teknoloji Doğrulama)", 
    "5. Finances and Funding (Finans ve Fonlama)", 
    "6. Legal (Yasal Hususlar)", 
    "7. Team (Takım)", 
    "8. Sustainability (Sürdürülebilirlik)"
]

# --- 2. VERİ YÖNETİMİ ---
def load_data():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE, sep=';', encoding='utf-8-sig')
        except: return pd.DataFrame()
    return pd.DataFrame()

def save_all_data(df):
    df.to_csv(DATA_FILE, index=False, sep=';', encoding='utf-8-sig')

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
        mode = st.radio("Kategori:", ["Presentation Scoring", "Worksheet Scoring"], horizontal=True)
        sess_options = [f"{k} ({v['date']})" if mode == "Presentation Scoring" else k for k, v in SESSIONS.items()]
        sess_choice_raw = st.selectbox("1. Oturum Seçin", ["Seçiniz..."] + sess_options)
        
        if sess_choice_raw != "Seçiniz...":
            sess_key = sess_choice_raw.split(" (")[0]
            team_choice = st.selectbox("2. Takım Seçin", ["Seçiniz..."] + SESSIONS[sess_key]["teams"])
            
            if team_choice != "Seçiniz...":
                key_id = f"{full_name}_{team_choice}_{mode}".replace(" ", "_")
                existing = master_df[(master_df['Judge'] == full_name) & (master_df['Team'] == team_choice) & (master_df['Category'] == mode)] if not master_df.empty else pd.DataFrame()

                is_locked = not existing.empty
                if is_locked:
                    st.success(f"✅ {team_choice} kaydedildi. Puanlarınızı aşağıda görebilirsiniz.")
                    if st.button("Puanları Düzenle (Unlock)"): is_locked = False; st.rerun()

                st.subheader(f"{team_choice} Değerlendirmesi")
                criteria_list = PRES_CRITERIA if mode == "Presentation Scoring" else WORK_CRITERIA
                new_entries = {}

                for title in criteria_list:
                    st.markdown(f"#### {title}")
                    col1, col2 = st.columns([1, 1])
                    
                    score_col = f"{title}_Score"
                    fb_col = f"{title}_Feedback"
                    
                    def_sc = 3
                    if is_locked and score_col in existing.columns:
                        def_sc = int(existing[score_col].values[0])
                    
                    def_fb = ""
                    if is_locked and fb_col in existing.columns:
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
                    if not master_df.empty:
                        master_df = master_df[~((master_df['Judge'] == full_name) & (master_df['Team'] == team_choice) & (master_df['Category'] == mode))]
                    master_df = pd.concat([master_df, pd.DataFrame([entry])], ignore_index=True)
                    save_all_data(master_df)
                    st.success("Kaydedildi!"); st.balloons(); st.rerun()

# --- 5. ADMİN PANELİ ---
elif page == "Admin Dashboard":
    st.header("🔐 Yönetici Paneli")
    if st.text_input("Şifre", type="password") == "GCIP2025*":
        if not master_df.empty:
            t1, t2, t3, t4, t5 = st.tabs(["📊 Genel Sıralama", "📅 Oturum Bazlı", "🎤 Sunum Detay", "📝 Ödev Detay", "⚙️ Yönetim"])
            
            base_cols = ["Timestamp", "Judge", "Session", "Team", "Category", "Total_Score"]

            with t1:
                st.subheader("Global Leaderboards")
                for c in ["Presentation Scoring", "Worksheet Scoring"]:
                    st.write(f"#### {c}")
                    df_c = master_df[master_df['Category'] == c]
                    if not df_c.empty:
                        r = df_c.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                        r.index += 1; st.table(r)
                        st.download_button(f"{c} Sıralama Excel İndir", r.to_csv(sep=';', index=True, encoding='utf-8-sig').encode('utf-8-sig'), f"Global_Siralama_{c}.csv")

            with t2:
                st.subheader("Oturum Bazlı Sıralama")
                s_cat = st.selectbox("Kategori", ["Presentation Scoring", "Worksheet Scoring"])
                for s in SESSIONS.keys():
                    s_df = master_df[(master_df['Category'] == s_cat) & (master_df['Session'] == s)]
                    if not s_df.empty:
                        st.write(f"##### {s}")
                        sr = s_df.groupby("Team")["Total_Score"].mean().sort_values(ascending=False).reset_index()
                        sr.index += 1; st.table(sr)

            with t3:
                st.subheader("Detaylı Sunum Tablosu")
                p_full = master_df[master_df['Category'] == "Presentation Scoring"].copy()
                if not p_full.empty:
                    # Sadece Sunum sütunlarını filtrele
                    p_cols = base_cols + [f"{c}_Score" for c in PRES_CRITERIA] + [f"{c}_Feedback" for c in PRES_CRITERIA]
                    display_cols = [c for c in p_cols if c in p_full.columns]
                    st.dataframe(p_full[display_cols], use_container_width=True)
                    st.download_button("Sunum Detay Excel İndir", p_full[display_cols].to_csv(sep=';', index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Sunum_Detay.csv")

            with t4:
                st.subheader("Detaylı Worksheet Tablosu")
                w_full = master_df[master_df['Category'] == "Worksheet Scoring"].copy()
                if not w_full.empty:
                    # Sadece Worksheet sütunlarını filtrele
                    w_cols = base_cols + [f"{c}_Score" for c in WORK_CRITERIA] + [f"{c}_Feedback" for c in WORK_CRITERIA]
                    display_cols = [c for c in w_cols if c in w_full.columns]
                    st.dataframe(w_full[display_cols], use_container_width=True)
                    st.download_button("Worksheet Detay Excel İndir", w_full[display_cols].to_csv(sep=';', index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Worksheet_Detay.csv")

            with t5:
                st.subheader("Jüri Analizi & Kayıt Yönetimi")
                j_stats = master_df.groupby("Judge")["Total_Score"].agg(['mean', 'count']).reset_index()
                st.dataframe(j_stats)
                
                st.divider()
                st.subheader("Kayıt Silme (Düzenleme Yetkisi)")
                to_del = st.selectbox("Silinecek Kaydı Seçin:", ["Seçiniz..."] + master_df.apply(lambda r: f"{r['Judge']} | {r['Team']} | {r['Category']}", axis=1).tolist())
                if to_del != "Seçiniz..." and st.button("Kaydı Sil ve Jürinin Sayfasını Aç"):
                    p = to_del.split(" | ")
                    master_df = master_df[~((master_df['Judge'] == p[0]) & (master_df['Team'] == p[1]) & (master_df['Category'] == p[2]))]
                    save_all_data(master_df); st.rerun()
                
                if st.button("⚠️ SİSTEMİ SIFIRLA"):
                    if os.path.exists(DATA_FILE): os.remove(DATA_FILE); st.rerun()
        else:
            st.info("Henüz veri yok.")
