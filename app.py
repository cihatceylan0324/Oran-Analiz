import time
import random
import requests
import pandas as pd

# API Bilgileri (Kullandığın API'nin endpoint ve key bilgilerini buraya yazacaksın)
API_KEY = "BURAYA_API_KEY_GIRIN"
BASE_URL = "https://api.ornek-futbol-api.com/v1/matches" # Kendi API adresin

# Türkiye Süper Lig Sezon ID'leri veya Yılları
sezonlar = [2021, 2022, 2023, 2024, 2025]
dosya_adi = "oran_analiz.csv"

print("🛡️ Anti-Ban korumalı güvenli veri toplama botu başlatıldı...")

tum_veriler = []

for sezon in sezonlar:
    print(f"📥 {sezon} - {sezon+1} sezonu verileri çekiliyor...")
    
    params = {
        "league": "turkey-super-lig",
        "season": sezon,
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code == 200:
            veri = response.json()
            df_parca = pd.DataFrame(veri.get("response", []))
            
            if not df_parca.empty:
                tum_veriler.append(df_parca)
                print(f"✅ {sezon} sezonundan {len(df_parca)} maç başarıyla alındı.")
            else:
                print(f"⚠️ {sezon} sezonunda veri bulunamadı.")
        else:
            print(f"❌ API Hatası (Kod: {response.status_code})")
            
    except Exception as e:
        print(f"⚠️ Bağlantı hatası: {e}")
        
    bekleme = random.uniform(4.0, 9.0)
    print(f"⏳ Güvenlik uyarısı: {bekleme:.1f} saniye bekleniyor...\n")
    time.sleep(bekleme)

# Toplanan tüm verileri tek dosyada birleştir
if tum_veriler:
    final_df = pd.concat(tum_veriler, ignore_index=True)
    final_df.to_csv(dosya_adi, index=False, encoding='utf-8')
    print(f"\n🎉 İşlem tamam! Toplam {len(final_df)} maç '{dosya_adi}' dosyasına kaydedildi.")
    print("Artık bu dosyayı GitHub deposuna yükleyebilirsin.")
else:
    print("❌ Hiçbir veri kaydedilemedi.")
