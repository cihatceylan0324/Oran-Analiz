!pip install requests pandas

import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "BURAYA_YENI_ANAHTARINI_YAZ"
BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# Son 14 gün
bugun = datetime.today()
baslangic = bugun - timedelta(days=14)

params = {
    "from": baslangic.strftime("%Y-%m-%d"),
    "to": bugun.strftime("%Y-%m-%d"),
}

r = requests.get(f"{BASE}/fixtures", headers=HEADERS, params=params)
data = r.json().get("response", [])

rows = []
for m in data:
    rows.append({
        "Tarih": m["fixture"]["date"],
        "Lig": m["league"]["name"],
        "Ülke": m["league"]["country"],
        "Ev": m["teams"]["home"]["name"],
        "Deplasman": m["teams"]["away"]["name"],
        "IY_Ev": m["score"]["halftime"]["home"],
        "IY_Dep": m["score"]["halftime"]["away"],
        "MS_Ev": m["score"]["fulltime"]["home"],
        "MS_Dep": m["score"]["fulltime"]["away"],
        "Fixture_ID": m["fixture"]["id"],
    })

df = pd.DataFrame(rows)
df.to_csv("son_14_gun.csv", index=False)
print(f"✅ {len(df)} maç çekildi.")
print(df.head())
