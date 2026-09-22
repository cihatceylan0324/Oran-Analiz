import time
import random
import requests
import pandas as pd

# API-Football Pro Anahtarın
API_KEY = "6872ad88365b79a00040ce0ce9c7ab6a"
BASE_URL = "https://v3.football.api-sports.io/fixtures"

headers = {
    'x-apisports-key': API_KEY
}

# Türkiye Süper Lig ID'si: 203
LEAGUE_ID = 203
sezonlar = [2021, 2022, 2023, 2024, 2025, 2026]
dosya_adi = "oran_analiz.csv"

print("⚽ API-Football Pro Veri Toplama Botu Başlatıldı...")
tum_maclar = []

for sezon in sezonlar:
    print(f"📥 {sezon} sezonu maçları çekiliyor...")
    
    params = {
        "league": LEAGUE_ID,
        "season": sezon
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            veri = response.json()
            fixtures = veri.get("response", [])
            
            if fixtures:
                for match in fixtures:
                    mac_detay = {
                        'Sezon': f"{sezon}-{sezon+1}",
                        'Tarih': match.get('fixture', {}).get('date'),
                        'Ev Sahibi': match.get('teams', {}).get('home', {}).get('name'),
                        'Deplasman': match.get('teams', {}).get('away', {}).get('name'),
                        'IY_Ev': match.get('score', {}).get('halftime', {}).get('home'),
                        'IY_Dep': match.get('score', {}).get('halftime', {}).get('away'),
                        'MS_Ev': match.get('score', {}).get('fulltime', {}).get('home'),
                        'MS_Dep': match.get('score', {}).get('fulltime', {}).get('away'),
                    }
                    tum_maclar.append(mac_detay)
                print(f"✅ {sezon} sezonundan {len(fixtures)} maç başarıyla alındı.")
            else:
                print(f"⚠️ {sezon} sezonunda veri bulunamadı.")
        else:
            print(f"❌ API Hatası: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"⚠️ Bağlantı hatası: {e}")
    
    time.sleep(2)

# Verileri CSV'ye dökme
if tum_maclar:
    final_df = pd.DataFrame(tum_maclar)
    
    final_df['İY/MS'] = final_df.apply(lambda r: f"{'1' if r['IY_Ev'] > r['IY_Dep'] else ('2' if r['IY_Ev'] < r['IY_Dep'] else '0')}/"
                                                f"{'1' if r['MS_Ev'] > r['MS_Dep'] else ('2' if r['MS_Ev'] < r['MS_Dep'] else '0')}" 
                                                if pd.notnull(r['IY_Ev']) and pd.notnull(r['MS_Ev']) else "-", axis=1)
    
    final_df.to_csv(dosya_adi, index=False, encoding='utf-8')
    print(f"\n🎉 İşlem tamam! Toplam {len(final_df)} maç '{dosya_adi}' dosyasına kaydedildi.")
    print("Artık bu dosyayı GitHub depona yükleyebilirsin.")
else:
    print("❌ Hiç veri çekilemedi.")
