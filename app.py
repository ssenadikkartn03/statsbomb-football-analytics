"""
Grimsby Town, Bromley & Crawley Town - Profesyonel Futbol Analitiği ve Scouting Paneli
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Sayfa Yapılandırması
st.set_page_config(page_title="Futbol Scouting ve Analitik Paneli", page_icon="⚽", layout="wide")

st.title("Futbol Kulüpleri Performans ve Scouting Paneli")
st.markdown("StatsBomb veri seti üzerinden maç dinamikleri, saha kırılımları ve ileri düzey xG (Beklenen Gol) analizi.")

@st.cache_data
def load_data():
    try:
        df_matches = pd.read_csv("output/cleaned_matches.csv")
    except FileNotFoundError:
        df_matches = None
        
    try:
        df_advanced = pd.read_csv("output/advanced_metrics.csv")
    except FileNotFoundError:
        df_advanced = None
        
    return df_matches, df_advanced

df, df_advanced = load_data()

if df is None:
    st.error("Hata: output/cleaned_matches.csv dosyası bulunamadı!")
else:
    TARGETS = ["Grimsby Town", "Bromley", "Crawley Town"]

    home_col = next((c for c in df.columns if 'home_team' in c and ('name' in c or c == 'home_team')), None)
    away_col = next((c for c in df.columns if 'away_team' in c and ('name' in c or c == 'away_team')), None)
    home_score_col = next((c for c in df.columns if 'home_score' in c), None)
    away_score_col = next((c for c in df.columns if 'away_score' in c), None)

    def is_target_match(row):
        h = str(row.get(home_col, ""))
        a = str(row.get(away_col, ""))
        return any(t.lower() in h.lower() for t in TARGETS) or any(t.lower() in a.lower() for t in TARGETS)

    sub_df = df[df.apply(is_target_match, axis=1)].copy()

    # Yan Menü
    st.sidebar.header("Filtreler")
    selected_team = st.sidebar.selectbox("Takım Seçin", ["Tümü"] + TARGETS)

    # Sekme Yapısı (Tabs)
    tab1, tab2 = st.tabs(["📊 Genel Performans ve Saha Kırılımı", "🔍 İleri Düzey Scouting ve xG Analizi"])

    # --- SEKME 1: GENEL PERFORMANS ---
    with tab1:
        def get_detailed_metrics():
            data = []
            for team in TARGETS:
                h_m = sub_df[sub_df[home_col].astype(str).str.contains(team, case=False, na=False)]
                a_m = sub_df[sub_df[away_col].astype(str).str.contains(team, case=False, na=False)]
                
                tot_h = len(h_m)
                tot_a = len(a_m)
                tot_m = tot_h + tot_a
                if tot_m == 0: continue

                h_wins = len(h_m[h_m[home_score_col] > h_m[away_score_col]])
                h_draws = len(h_m[h_m[home_score_col] == h_m[away_score_col]])
                h_scored = h_m[home_score_col].sum()
                h_conceded = h_m[away_score_col].sum()
                h_ppg = round(((h_wins * 3) + h_draws) / tot_h, 2) if tot_h > 0 else 0

                a_wins = len(a_m[a_m[away_score_col] > a_m[home_score_col]])
                a_draws = len(a_m[a_m[away_score_col] == a_m[home_score_col]])
                a_scored = a_m[away_score_col].sum()
                a_conceded = a_m[home_score_col].sum()
                a_ppg = round(((a_wins * 3) + a_draws) / tot_a, 2) if tot_a > 0 else 0

                tot_wins = h_wins + a_wins
                tot_draws = h_draws + a_draws
                tot_losses = tot_m - (tot_wins + tot_draws)
                tot_scored = h_scored + a_scored
                tot_conceded = h_conceded + a_conceded

                data.append({
                    "Takım": team,
                    "Toplam Maç": tot_m,
                    "İç Saha Maç": tot_h,
                    "Deplasman Maç": tot_a,
                    "Galibiyet Oranı (%)": round((tot_wins / tot_m) * 100, 1),
                    "Toplam PPG": round(((tot_wins * 3) + tot_draws) / tot_m, 2),
                    "İç Saha PPG": h_ppg,
                    "Deplasman PPG": a_ppg,
                    "İç Saha Maç Başı Atılan Gol": round(h_scored / tot_h, 2) if tot_h > 0 else 0,
                    "Deplasman Maç Başı Atılan Gol": round(a_scored / tot_a, 2) if tot_a > 0 else 0,
                    "İç Saha Maç Başı Yenilen Gol": round(h_conceded / tot_h, 2) if tot_h > 0 else 0,
                    "Deplasman Maç Başı Yenilen Gol": round(a_conceded / tot_a, 2) if tot_a > 0 else 0,
                    "Galibiyet": tot_wins,
                    "Beraberlik": tot_draws,
                    "Mağlubiyet": tot_losses
                })
            return pd.DataFrame(data)

        metrics_df = get_detailed_metrics()

        if selected_team == "Tümü":
            display_title = "Genel Görünüm: Tüm Kulüpler (Ev & Deplasman Özeti)"
            total_matches = len(sub_df)
            avg_ppg = round(metrics_df["Toplam PPG"].mean(), 2)
            avg_scored = round((metrics_df["İç Saha Maç Başı Atılan Gol"].mean() + metrics_df["Deplasman Maç Başı Atılan Gol"].mean()) / 2, 2)
            avg_conceded = round((metrics_df["İç Saha Maç Başı Yenilen Gol"].mean() + metrics_df["Deplasman Maç Başı Yenilen Gol"].mean()) / 2, 2)
            display_table = metrics_df[["Takım", "Toplam Maç", "İç Saha Maç", "Deplasman Maç", "Toplam PPG", "İç Saha PPG", "Deplasman PPG"]]
        else:
            display_title = f"Kulüp Analizi ve Saha Kırılımı: {selected_team}"
            team_row = metrics_df[metrics_df["Takım"] == selected_team].iloc[0]
            total_matches = int(team_row["Toplam Maç"])
            avg_ppg = team_row["Toplam PPG"]
            avg_scored = round((team_row["İç Saha Maç Başı Atılan Gol"] + team_row["Deplasman Maç Başı Atılan Gol"]) / 2, 2)
            avg_conceded = round((team_row["İç Saha Maç Başı Yenilen Gol"] + team_row["Deplasman Maç Başı Yenilen Gol"]) / 2, 2)
            display_table = metrics_df[metrics_df["Takım"] == selected_team][["Takım", "Toplam Maç", "İç Saha Maç", "Deplasman Maç", "Toplam PPG", "İç Saha PPG", "Deplasman PPG"]]

        st.subheader(display_title)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Maç", total_matches)
        c2.metric("Ortalama Puan (PPG)", avg_ppg)
        c3.metric("Ortalama Atılan Gol", avg_scored)
        c4.metric("Ortalama Yenilen Gol", avg_conceded)

        st.markdown("---")
        st.subheader("İç Saha / Deplasman Performans Matrisi")
        st.dataframe(display_table, use_container_width=True)
        
        csv = metrics_df.to_csv(index=False).encode('utf-8')
        st.download_button("Detaylı Raporu CSV Olarak İndir", csv, "ev_deplasman_analizi.csv", "text/csv")

        st.markdown("---")
        st.subheader("İç Saha vs. Deplasman Puan Verimliliği (PPG)")
        fig, ax = plt.subplots(figsize=(10, 4))
        melted_ppg = metrics_df.melt(id_vars=["Takım"], value_vars=["İç Saha PPG", "Deplasman PPG"], var_name="Saha Konumu", value_name="PPG Değeri")
        sns.barplot(data=melted_ppg, x="Takım", y="PPG Değeri", hue="Saha Konumu", palette="Set2", ax=ax)
        ax.set_ylabel("Maç Başına Puan (PPG)")
        ax.set_xlabel("")
        st.pyplot(fig)

    # --- SEKME 2: İLERİ DÜZEY SCOUTING VE xG ---
    with tab2:
        st.subheader("İleri Düzey Scouting ve xG (Beklenen Gol) Analizi")
        st.markdown("StatsBomb olay verilerinden türetilen şut, pas ve baskı sıklığı metrikleri.")

        try:
            df_adv = pd.read_csv("output/advanced_metrics.csv")
            adv_display = df_adv if selected_team == "Tümü" else df_adv[df_adv["Takım"] == selected_team]
            
            st.dataframe(adv_display, use_container_width=True)

            st.markdown("---")
            st.subheader("Kulüplerin xG (Beklenen Gol) Karşılaştırması")
            
            fig_xg, ax_xg = plt.subplots(figsize=(8, 3.5))
            sns.barplot(data=df_adv, x="Takım", y="xG Oranı", palette="viridis", ax=ax_xg)
            ax_xg.set_ylabel("Maç Başı xG Üretimi")
            ax_xg.set_xlabel("")
            st.pyplot(fig_xg)
            
        except Exception as e:
            st.error(f"Gelişmiş metrik yüklenirken bir hata oluştu: {e}")