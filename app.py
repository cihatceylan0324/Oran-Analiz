import time
import random
import pandas as pd
import requests

# Örnek olarak sezon bazlı liste (İstediğin kaynak veya siteye göre uyarlanabilir)
sezonlar = ["2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026"]
dosya_adi = "oran_analiz.csv"

print("🚀 Güvenli veri toplama süreci başlatıldı (Anti-ban mod aktif)...")

tum_veriler = []

for sezon in sezonlar:
    print(f"📥 {sezon} sezonu verileri çekiliyor...")
    
    try:
        # BURAYA Veriyi çekeceğin kaynak API veya URL gelecek
        # Örnek simülasyon (Gerçek çekim kodunu buraya entegre edeceğiz)
        # url = f"https://ornek-kaynak.com/api?season={sezon}"
        # response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        
        # Dikkat çekmemek için her istek arasında rastgele bekleme (3 ile 7 saniye arası)
        bekleme_suresi = random.uniform(3.0, 7.0)
        print(f"⏳ Güvenlik için {bekleme_suresi:.1f} saniye bekleniyor...")
        time.sleep(bekleme_suresi)
        
        # Simüle edilmiş parça veri (Burada gerçek çektiğin veriyi işleyeceksin)
        parca_df = pd.DataFrame({
            'Sezon': [sezon] * 10,
            'Ev Sahibi': [f"Takim_A_{i}" for i in range(10)],
            'Deplasman': [f"Takim_B_{i}" for i in range(10)],
            'MS_1': [round(random.uniform(1.40, 3.50), 2) for _ in range(10)],
            'MS_0': [round(random.uniform(3.10, 3.60), 2) for _ in range(10)],
            'MS_2': [round(random.uniform(1.80, 4.50), 2) for _ in range(10)]
        })
        
        # Parçayı ana listeye ekle
        tum_veriler.append(parca_df)
        print(f"✅ {sezon} sezonu başarıyla eklendi.")
        
    except Exception as e:
        print(f"⚠️ Hata oluştu ({sezon}): {e}")
        continue

# Hepsini tek bir CSV'de birleştir ve kaydet
if tum_veriler:
    final_df = pd.concat(tum_veriler, ignore_index=True)
    final_df.to_csv(dosya_adi, index=False, encoding='utf-8')
    print(f"\n🎉 İşlem tamam! Toplam {len(final_df)} maç '{dosya_adi' dosyasına kaydedildi.")
else:
    print("❌ Hiç veri alınamadı.")
