"""
StatsBomb Futbol Analitiği - Gelişmiş Metrik Hesaplama Scripti
"""

import pandas as pd

def analyze_advanced_metrics():
    try:
        df = pd.read_csv("output/cleaned_matches.csv")
    except FileNotFoundError:
        print("⚠️ cleaned_matches.csv bulunamadı! Önce clean_data.py çalıştırın.")
        return

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

    print("\n" + "="*20 + " GELİŞMİŞ TAKIM ANALİZİ VE İLERİ DÜZEY METRİKLER " + "="*20)

    for team in TARGETS:
        h_matches = sub_df[sub_df[home_col].astype(str).str.contains(team, case=False, na=False)].copy()
        a_matches = sub_df[sub_df[away_col].astype(str).str.contains(team, case=False, na=False)].copy()
        
        tot_h = len(h_matches)
        tot_a = len(a_matches)
        tot_m = tot_h + tot_a
        
        if tot_m == 0:
            continue

        # Ev ve Deplasman Sonuçları
        h_wins = len(h_matches[h_matches[home_score_col] > h_matches[away_score_col]])
        a_wins = len(a_matches[a_matches[away_score_col] > a_matches[home_score_col]])
        tot_wins = h_wins + a_wins

        h_draws = len(h_matches[h_matches[home_score_col] == h_matches[away_score_col]])
        a_draws = len(a_matches[a_matches[away_score_col] == a_matches[home_score_col]])
        tot_draws = h_draws + a_draws

        tot_losses = tot_m - (tot_wins + tot_draws)

        # Puan ve PPG (Points Per Game)
        total_points = (tot_wins * 3) + (tot_draws * 1)
        ppg = round(total_points / tot_m, 2)

        # Goller ve Averaj
        h_scored = h_matches[home_score_col].sum() if tot_h > 0 else 0
        h_conceded = h_matches[away_score_col].sum() if tot_h > 0 else 0
        a_scored = a_matches[away_score_col].sum() if tot_a > 0 else 0
        a_conceded = a_matches[home_score_col].sum() if tot_a > 0 else 0

        tot_scored = h_scored + a_scored
        tot_conceded = h_conceded + a_conceded
        goal_diff = tot_scored - tot_conceded
        gd_per_match = round(goal_diff / tot_m, 2)

        # Clean Sheet (Gol Yememe) Hesaplama
        h_clean = len(h_matches[h_matches[away_score_col] == 0])
        a_clean = len(a_matches[a_matches[home_score_col] == 0])
        clean_sheet_pct = round(((h_clean + a_clean) / tot_m) * 100, 1)

        # Failed to Score (Gol Atamama) Hesaplama
        h_failed = len(h_matches[h_matches[home_score_col] == 0])
        a_failed = len(a_matches[a_matches[away_score_col] == 0])
        failed_score_pct = round(((h_failed + a_failed) / tot_m) * 100, 1)

        # 2.5 Gol Üstü Oranı
        h_matches['total_goals'] = h_matches[home_score_col] + h_matches[away_score_col]
        a_matches['total_goals'] = a_matches[home_score_col] + a_matches[away_score_col]
        all_team_matches = pd.concat([h_matches, a_matches])
        over_25_count = len(all_team_matches[all_team_matches['total_goals'] > 2.5])
        over_25_pct = round((over_25_count / tot_m) * 100, 1)

        print(f"\n--- {team.upper()} ---")
        print(f"Toplam Maç: {tot_m} | Galibiyet: {tot_wins} | Beraberlik: {tot_draws} | Mağlubiyet: {tot_losses}")
        print(f"Maç Başına Puan (PPG): {ppg}")
        print(f"Maç Başı Net Averaj: {gd_per_match} (Atılan: {tot_scored}, Yenilen: {tot_conceded})")
        print(f"Clean Sheet (Gol Yememe) Oranı: %{clean_sheet_pct}")
        print(f"Gol Atamadan Tamamlama Oranı: %{failed_score_pct}")
        print(f"2.5 Gol Üstü Maç Oranı: %{over_25_pct}")

if __name__ == "__main__":
    analyze_advanced_metrics()