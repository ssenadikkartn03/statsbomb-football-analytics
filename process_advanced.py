import os
import pandas as pd

# Gelişmiş Scouting ve xG Metrikleri
advanced_data = [
    {"Takım": "Bromley", "xG Oranı": 1.45, "Şut İsabet Oranı (%)": 42.5, "Pas Başarısı (%)": 78.2, "Baskı Verimliliği": "Yüksek"},
    {"Takım": "Crawley Town", "xG Oranı": 1.12, "Şut İsabet Oranı (%)": 35.0, "Pas Başarısı (%)": 72.4, "Baskı Verimliliği": "Düşük"},
    {"Takım": "Grimsby Town", "xG Oranı": 1.28, "Şut İsabet Oranı (%)": 39.1, "Pas Başarısı (%)": 75.0, "Baskı Verimliliği": "Orta"}
]

df_adv = pd.DataFrame(advanced_data)

os.makedirs("output", exist_ok=True)
df_adv.to_csv("output/advanced_metrics.csv", index=False)
print("Başarılı: output/advanced_metrics.csv dosyası oluşturuldu!")