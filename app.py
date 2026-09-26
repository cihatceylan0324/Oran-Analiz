# preprocess.py
import csv, json, re, sys, unicodedata
from collections import defaultdict

# --- Ayarlar ---
CSV_RESULTS = "results.csv"        # Tarih, Sezon, Lig, Ev, Dep, MS, İY, Sonuc, TopGol, KG
TSV_ODDS    = "odds.tsv"           # Tarih, Ülke, Lig, Sezon, Ev, Dep, MS1, MS0, MS2, ...
JSON_API    = "api_football.json"  # API-Football ham JSON (opsiyonel)

# --- Normalizasyon ---
TR = str.maketrans("ıİşŞğĞüÜöÖçÇ", "iissgguuoocc")
ALIAS = {
    "cephanelik": "arsenal",
    "karagumruk": "fatih karagumruk",
    "karagümrük": "fatih karagumruk",
}
def norm(s):
    if not s: return ""
    s = s.translate(TR).lower()
    s = re.sub(r"\b(fc|fk|sk|as|spor|kulubu|kulübü|club|city|united|utd)\b", "", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()
def canon(s):
    n = norm(s)
    return ALIAS.get(n, n)

# --- Oran kolon eşleme (esnek) ---
ODDS_MAP = {
    "ms1": ["ms1","1","home","ev","odd_1"],
    "ms0": ["ms0","x","draw","beraberlik","odd_x"],
    "ms2": ["ms2","2","away","dep","odd_2"],
    "over25": ["over25","ust25","o25","over_2_5"],
    "under25": ["under25","alt25","u25","under_2_5"],
    "kg": ["kg","btts","kgvar","gg"],
    "iyOver15": ["iyover15","iy_ust15","ht_over_1_5"],
}
def find_col(headers, keys):
    for h in headers:
        hn = norm(h).replace(" ", "")
        for k in keys:
            if k.replace("_","") in hn:
                return h
    return None

def parse_float(v):
    if v is None: return None
    v = str(v).strip().replace(",", ".")
    if v in ("", "-", "NA", "null"): return None
    try: return float(v)
    except: return None

# --- 1) Sonuç CSV ---
def load_results(path):
    out = []
    with open(path, encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        for row in r:
            ms1 = int(float(row.get("MS Skor","0").split("-")[0] or 0)) if row.get("MS Skor") else None
            # MS skor "2-1" formatında olabilir
            ms = row.get("MS Skor") or row.get("MS") or ""
            iy = row.get("İY Skor") or row.get("IY") or ""
            def split_score(s):
                m = re.findall(r"\d+", s)
                return (int(m[0]), int(m[1])) if len(m) >= 2 else (None, None)
            ms1, ms0 = split_score(ms)
            ht1, ht0 = split_score(iy)
            out.append({
                "date": row.get("Tarih") or row.get("Date"),
                "season": row.get("Sezon") or row.get("Season"),
                "league": row.get("Lig") or row.get("League"),
                "country": row.get("Ülke") or row.get("Country") or "",
                "home": row.get("Ev Sahibi") or row.get("Home"),
                "away": row.get("Deplasman") or row.get("Away"),
                "ms1": ms1, "ms0": ms0, "ht1": ht1, "ht0": ht0,
                "result": row.get("MS Sonucu") or row.get("Sonuc"),
                "totalGoals": None, "kg": None,
                "odds": {}, "source": "csv"
            })
    return out

# --- 2) Oran TSV ---
def load_odds(path):
    out = []
    with open(path, encoding="utf-8-sig") as f:
        r = csv.DictReader(f, delimiter="\t")
        headers = r.fieldnames or []
        col = {k: find_col(headers, v) for k, v in ODDS_MAP.items()}
        for row in r:
            odds = {}
            for k, c in col.items():
                if c: odds[k] = parse_float(row.get(c))
            out.append({
                "date": row.get("Tarih") or row.get("Date"),
                "season": row.get("Sezon") or row.get("Season"),
                "league": row.get("Lig") or row.get("League"),
                "country": row.get("Ülke") or row.get("Country") or "",
                "home": row.get("Ev Sahibi") or row.get("Home") or row.get("Ev"),
                "away": row.get("Deplasman") or row.get("Away") or row.get("Dep"),
                "odds": odds, "source": "odds",
                "ms1": None, "ms0": None, "ht1": None, "ht0": None,
                "result": None, "totalGoals": None, "kg": None
            })
    return out

# --- 3) API-Football JSON ---
def load_api(path):
    if not path: return []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return []
    out = []
    fixtures = data.get("response", data if isinstance(data, list) else [])
    for fx in fixtures:
        try:
            f = fx.get("fixture", fx)
            teams = fx.get("teams", {})
            goals = fx.get("goals", {})
            score = fx.get("score", {})
            ht = score.get("halftime", {})
            odds = {}
            # API-Football odds yapısı (varsa)
            for b in fx.get("odds", []) or []:
                for v in b.get("values", []) or []:
                    val = parse_float(v.get("odd"))
                    label = (v.get("value") or "").lower()
                    if label in ("home","1"): odds["ms1"] = val
                    elif label in ("draw","x"): odds["ms0"] = val
                    elif label in ("away","2"): odds["ms2"] = val
                    elif "over 2.5" in label: odds["over25"] = val
                    elif "under 2.5" in label: odds["under25"] = val
                    elif "yes" in label and "both" in label: odds["kg"] = val
            out.append({
                "date": (f.get("date") or "")[:10],
                "season": str(fx.get("league",{}).get("season","")),
                "league": fx.get("league",{}).get("name",""),
                "country": fx.get("league",{}).get("country",""),
                "home": teams.get("home",{}).get("name",""),
                "away": teams.get("away",{}).get("name",""),
                "ms1": goals.get("home"), "ms0": goals.get("away"),
                "ht1": ht.get("home"), "ht0": ht.get("away"),
                "result": None, "totalGoals": None, "kg": None,
                "odds": odds, "source": "api"
            })
        except Exception as e:
            print("API kayıt atlandı:", e)
    return out

# --- Birleştirme ---
def merge(all_rows):
    merged = {}
    for m in all_rows:
        key = (m["date"], canon(m["home"]), canon(m["away"]))
        if key in merged:
            ex = merged[key]
            for f in ("ms1","ms0","ht1","ht0","result","league","season","country"):
                if not ex.get(f) and m.get(f): ex[f] = m[f]
            ex["odds"] = {**m.get("odds",{}), **ex.get("odds",{})}
            if ex.get("source") != "api": ex["source"] = m.get("source", ex.get("source"))
        else:
            merged[key] = dict(m)
    # Türetilen alanlar
    out = []
    for m in merged.values():
        if m["ms1"] is not None and m["ms0"] is not None:
            m["totalGoals"] = m["ms1"] + m["ms0"]
            m["kg"] = m["ms1"] > 0 and m["ms0"] > 0
            m["result"] = "1" if m["ms1"]>m["ms0"] else ("2" if m["ms1"]<m["ms0"] else "0")
        out.append(m)
    return out

# --- Lig çakışması ayırma (union-find) ---
class UF:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        if self.p[x] != x: self.p[x] = self.find(self.p[x])
        return self.p[x]
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb

def split_leagues(rows):
    by_league = defaultdict(list)
    for m in rows: by_league[m["league"]].append(m)
    out = []
    for lg, ms in by_league.items():
        uf = UF()
        for m in ms:
            uf.union(canon(m["home"]), canon(m["away"]))
        comps = defaultdict(list)
        for m in ms:
            comps[uf.find(canon(m["home"]))].append(m)
        if len(comps) == 1:
            out.extend(ms)
        else:
            for i, (root, cms) in enumerate(comps.items()):
                countries = defaultdict(int)
                for m in cms: countries[m.get("country") or "?"] += 1
                main_c = max(countries, key=countries.get)
                label = f"{lg} ({main_c})" if main_c != "?" else f"{lg} #{i+1}"
                for m in cms:
                    m = dict(m); m["league"] = label; out.append(m)
    return out

def main():
    rows = []
    rows += load_results(CSV_RESULTS) if CSV_RESULTS else []
    rows += load_odds(TSV_ODDS)       if TSV_ODDS    else []
    rows += load_api(JSON_API)        if JSON_API    else []
    print(f"Ham kayıt: {len(rows)}")
    merged = merge(rows)
    print(f"Birleşik: {len(merged)}")
    merged = split_leagues(merged)
    print(f"Lig ayrımı sonrası: {len(merged)}")
    with open("embedded_data.js", "w", encoding="utf-8") as f:
        f.write("const EMBEDDED_DATA = " + json.dumps(merged, ensure_ascii=False, indent=1) + ";\n")
    print("Yazıldı: embedded_data.js")
    print("Bu dosyanın içeriğini HTML'deki EMBEDDED_DATA bloğuyla değiştirin.")

if __name__ == "__main__":
    main()
