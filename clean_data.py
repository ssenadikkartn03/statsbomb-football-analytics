"""
StatsBomb Doğru Maç Birleştirme Script'i
"""

import json
import glob
import os
import pandas as pd

TEAM_PATHS = {
    "Bromley": r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Bromley_StatsBomb_Data",
    "Crawley Town": r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Crawley_Town_StatsBomb_Data",
    "Grimsby Town": r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Grimsby_StatsBomb_Data",
}

TARGET_TEAMS = ["Bromley", "Crawley Town", "Grimsby Town"]

def normalize_name(val):
    if isinstance(val, dict):
        return val.get("name", "")
    return str(val)

def main():
    all_matches = []

    for team_key, base_path in TEAM_PATHS.items():
        if not os.path.isdir(base_path):
            continue
        
        match_files = glob.glob(os.path.join(base_path, "**", "matches.json"), recursive=True)
        print(f"\n>> {team_key} için {len(match_files)} adet matches.json taranıyor...")

        for file_path in match_files:
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    matches = json.load(f)
                except Exception:
                    continue
            
            if isinstance(matches, list):
                for match in matches:
                    if not isinstance(match, dict):
                        continue
                    
                    # home_team ve away_team alanlarını güvenli şekilde alalım
                    home_raw = match.get("home_team", "")
                    away_raw = match.get("away_team", "")
                    
                    home_name = normalize_name(home_raw)
                    away_name = normalize_name(away_raw)
                    
                    # Hedef takımlardan biri geçiyor mu kontrol edelim
                    if any(target.lower() in home_name.lower() for target in TARGET_TEAMS) or \
                       any(target.lower() in away_name.lower() for target in TARGET_TEAMS):
                        match["source_folder_team"] = team_key
                        all_matches.append(match)

    if not all_matches:
        print("\nHicbir eşleşen maç bulunamadı!")
        return

    df = pd.json_normalize(all_matches)
    
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", "cleaned_matches.csv")
    df.to_csv(out_path, index=False)

    print(f"\nTüm eşleşen maçlar başarıyla kaydedildi: {out_path}")
    print(f"Toplam maç sayısı: {len(df)}")

if __name__ == "__main__":
    main()