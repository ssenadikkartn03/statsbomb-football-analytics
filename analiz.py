import json
import glob
import os

# Klasör yolların
TEAM_PATHS = {
    "Grimsby Town": r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Grimsby_StatsBomb_Data",
    "Bromley":     r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Bromley_StatsBomb_Data",
    "Crawley Town": r"C:\Users\asena\OneDrive\Desktop\statsbomb-analiz\Crawley_Town_StatsBomb_Data",
}

for team_name, folder_path in TEAM_PATHS.items():
    print(f"\n================ {team_name} KONTROLÜ ================")
    if not os.path.exists(folder_path):
        print(f"Klasör bulunamadı: {folder_path}")
        continue
        
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    print(f"Toplam dosya sayısı: {len(json_files)}")
    
    if json_files:
        # İlk dosyayı açıp içine bakalım
        with open(json_files[0], "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"İlk dosya tipi: {type(data)}")
                if isinstance(data, list) and len(data) > 0:
                    print(f"İlk elemanın anahtarları: {list(data[0].keys())[:8]}")
                    # İçinde 'team' veya 'name' geçen herhangi bir anahtar var mı arayalım
                    keys_str = str(data[0].keys()).lower()
                    print(f"İçerik anahtar özeti: {keys_str[:150]}...")
            except Exception as e:
                print(f"Dosya okunurken hata oluştu: {e}")