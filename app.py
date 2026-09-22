<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tahmin Paneli</title>
<style>
  :root{
    --bg:#0d1117;
    --panel:#151b23;
    --panel2:#1c2530;
    --line:#2a3542;
    --text:#e6edf3;
    --muted:#8b98a5;
    --accent:#3fb950;
    --accent2:#58a6ff;
    --warn:#e3b341;
    --danger:#f85149;
  }
  *{box-sizing:border-box;}
  body{
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    padding:24px;
  }
  h1{font-size:22px;font-weight:700;margin:0 0 4px;}
  .sub{color:var(--muted);font-size:13px;margin-bottom:20px;}
  .note{
    background:#2d2410;border:1px solid #4a3a12;color:var(--warn);
    padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:20px;
  }
  .controls{
    display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-bottom:20px;
    background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;
  }
  .field label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px;}
  select,button,input{
    background:var(--panel2);color:var(--text);border:1px solid var(--line);
    border-radius:6px;padding:8px 10px;font-size:14px;
  }
  button{
    cursor:pointer;background:var(--accent2);color:#04121f;font-weight:600;border:none;
  }
  button:hover{filter:brightness(1.1);}
  button:disabled{opacity:.5;cursor:not-allowed;}
  button.secondary{background:var(--panel2);color:var(--text);border:1px solid var(--line);}
  #status{font-size:13px;color:var(--muted);margin-bottom:16px;min-height:18px;}
  .layout{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap;}
  #fixtureList{
    flex:1;min-width:320px;max-height:640px;overflow-y:auto;
    background:var(--panel);border:1px solid var(--line);border-radius:10px;
  }
  .fixture-row{
    padding:12px 14px;border-bottom:1px solid var(--line);cursor:pointer;
    display:flex;justify-content:space-between;font-size:14px;
  }
  .fixture-row:hover{background:var(--panel2);}
  .fixture-row.active{background:#12283f;}
  .fixture-date{color:var(--muted);font-size:12px;}
  #detail{
    flex:1.3;min-width:360px;background:var(--panel);border:1px solid var(--line);
    border-radius:10px;padding:18px;
  }
  .placeholder{color:var(--muted);font-size:14px;text-align:center;padding:60px 20px;}
  .match-title{font-size:17px;font-weight:700;margin-bottom:2px;}
  .match-meta{color:var(--muted);font-size:12px;margin-bottom:16px;}
  .section-title{
    font-size:12px;text-transform:none;color:var(--accent2);
    margin:18px 0 8px;font-weight:700;border-top:1px solid var(--line);padding-top:14px;
  }
  .section-title:first-of-type{border-top:none;padding-top:0;}
  .prob-grid{display:flex;gap:10px;}
  .prob-box{
    flex:1;background:var(--panel2);border-radius:8px;padding:10px;text-align:center;
  }
  .prob-box .lbl{font-size:11px;color:var(--muted);}
  .prob-box .val{font-size:20px;font-weight:700;margin-top:2px;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  td,th{padding:6px 4px;border-bottom:1px solid var(--line);text-align:left;}
  th{color:var(--muted);font-weight:600;}
  .row-flex{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-bottom:1px dashed var(--line);}
  .odds-diff-pos{color:var(--accent);}
  .odds-diff-neg{color:var(--danger);}
  #similarBtn{margin-top:6px;}
  .small{font-size:12px;color:var(--muted);}
</style>
</head>
<body>

<h1>Tahmin Paneli</h1>
<div class="sub">Poisson modeli · H2H · Bet365 oran karşılaştırması · benzer oranlı geçmiş maçlar</div>

<div class="note">
  API-Football ücretsiz/pro plan kısıtlamaları nedeniyle oran verileri en verimli güncel sezonda (2024–2025/2026) çekilebilmektedir. Oranlı aramalarda bu detay baz alınır.
</div>

<div class="controls">
  <div class="field">
    <label>Lig</label>
    <select id="leagueSelect">
      <option value="203">Süper Lig (Türkiye)</option>
      <option value="39">Premier League</option>
      <option value="140">La Liga</option>
      <option value="135">Serie A</option>
      <option value="78">Bundesliga</option>
      <option value="61">Ligue 1</option>
    </select>
  </div>
  <div class="field">
    <label>Sezon</label>
    <select id="seasonSelect">
      <option value="2024" selected>2024</option>
      <option value="2023">2023</option>
      <option value="2022">2022</option>
    </select>
  </div>
  <div class="field">
    <button id="loadBtn" onclick="maclariYukle()">Maçları Yükle</button>
  </div>
  <div class="field">
    <button class="secondary" id="apiKeyBtn" onclick="keyDurumGoster()">Key durumu</button>
  </div>
</div>

<div class="controls" style="flex-direction:column;align-items:stretch;">
  <div style="font-size:13px;color:var(--accent2);font-weight:700;">Tam/Yakın Oranlı Maç Arama</div>
  <div class="small">
    MS1, MS0 veya MS2 değerlerinden dilediğini (veya hepsini) doldurarak tarama yapabilirsin. Boş bıraktığın oranlar eşleşmede dikkate alınmaz.
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-top:8px;">
    <div class="field"><label>MS1 (Ev) - İsteğe bağlı</label><input type="number" step="0.01" id="oddHomeInput" placeholder="Örn: 1.69" style="width:100px;"></div>
    <div class="field"><label>MS0 (Beraberlik) - İsteğe bağlı</label><input type="number" step="0.01" id="oddDrawInput" placeholder="Örn: 3.50" style="width:100px;"></div>
    <div class="field"><label>MS2 (Deplasman) - İsteğe bağlı</label><input type="number" step="0.01" id="oddAwayInput" placeholder="Örn: 3.20" style="width:100px;"></div>
    <div class="field"><label>Tolerans (±)</label>
      <select id="toleranceSelect" style="width:90px;">
        <option value="0.05">±0.05</option>
        <option value="0.1" selected>±0.10</option>
        <option value="0.25">±0.25</option>
        <option value="0.5">±0.50</option>
      </select>
    </div>
    <div class="field"><label>Taranacak maç sınırı</label>
      <select id="scanLimitSelect" style="width:90px;">
        <option value="20" selected>20</option>
        <option value="50">50</option>
      </select>
    </div>
    <div class="field"><button onclick="tekVeyaCokluOranTara()">Orana Göre Ara</button></div>
  </div>
  <div id="fullScanStatus" class="small" style="margin-top:6px;"></div>
  <div id="fullScanResults"></div>
</div>

<div id="status"></div>

<div class="layout">
  <div id="fixtureList">
    <div class="placeholder">Bir lig/sezon seçip "Maçları Yükle"ye bas.</div>
  </div>
  <div id="detail">
    <div class="placeholder">Soldan bir maç seç, detaylar burada görünecek.</div>
  </div>
</div>

<script>
const API_KEYS = [
  "3b90f0de19091dbf6593732af60ccb25",
  "8782d0553955500b2d68552bfa5fe531c"
];
const BASE_URL = "https://v3.football.api-sports.io";
const BET365_ID = 8;

let aktifKeyIndex = 0;
let sonFixtures = [];
let sonLeagueId = null;
let sonSeason = null;
let takimIstatistikCache = {};

function setStatus(msg, isError){
  const el = document.getElementById("status");
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function keyDurumGoster(){
  setStatus(`${API_KEYS.length} key tanımlı. Şu an key #${aktifKeyIndex + 1} kullanılıyor.`);
}

async function apiGet(endpoint, params){
  const url = new URL(BASE_URL + endpoint);
  Object.entries(params || {}).forEach(([k,v]) => url.searchParams.set(k, v));

  while(aktifKeyIndex < API_KEYS.length){
    try{
      const res = await fetch(url.toString(), {
        headers: { "x-apisports-key": API_KEYS[aktifKeyIndex] }
      });
      const data = await res.json();
      const errors = data.errors;
      const errorText = errors ? JSON.stringify(errors).toLowerCase() : "";
      if(errors && Object.keys(errors).length > 0 &&
         (errorText.includes("limit") || errorText.includes("quota") ||
          errorText.includes("rate") || errorText.includes("suspend"))){
        aktifKeyIndex++;
        setStatus(`Key ${aktifKeyIndex} limiti doldu, sıradaki deneniyor...`);
        continue;
      }
      return data;
    }catch(e){
      setStatus("Ağ hatası: " + e.message, true);
      return null;
    }
  }
  setStatus("Tüm key'ler limitine ulaştı.", true);
  return null;
}

async function maclariYukle(){
  const leagueId = document.getElementById("leagueSelect").value;
  const season = document.getElementById("seasonSelect").value;
  sonLeagueId = leagueId;
  sonSeason = season;

  document.getElementById("loadBtn").disabled = true;
  setStatus("Maçlar yükleniyor...");
  document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Yükleniyor...</div>';
  document.getElementById("detail").innerHTML = '<div class="placeholder">Soldan bir maç seç, detaylar burada görünecek.</div>';

  const data = await apiGet("/fixtures", { league: leagueId, season: season });
  document.getElementById("loadBtn").disabled = false;

  if(!data || !data.response){
    document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Maç bulunamadı.</div>';
    return;
  }

  sonFixtures = data.response
    .filter(f => f.fixture.status.short === "FT")
    .sort((a,b) => new Date(b.fixture.date) - new Date(a.fixture.date));

  if(sonFixtures.length === 0){
    document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Tamamlanmış maç bulunamadı.</div>';
    setStatus("0 maç bulundu.");
    return;
  }

  setStatus(`${sonFixtures.length} maç yüklendi.`);
  renderFixtureList();
}

function renderFixtureList(){
  const container = document.getElementById("fixtureList");
  container.innerHTML = "";
  sonFixtures.forEach((f, idx) => {
    const row = document.createElement("div");
    row.className = "fixture-row";
    row.id = "fx-" + idx;
    const tarih = new Date(f.fixture.date).toLocaleDateString("tr-TR");
    row.innerHTML = `
      <div>
        <div>${f.teams.home.name} ${f.goals.home ?? "-"} - ${f.goals.away ?? "-"} ${f.teams.away.name}</div>
        <div class="fixture-date">${tarih}</div>
      </div>`;
    row.onclick = () => macSec(idx);
    container.appendChild(row);
  });
}

async function macSec(idx){
  document.querySelectorAll(".fixture-row").forEach(r => r.classList.remove("active"));
  document.getElementById("fx-" + idx).classList.add("active");

  const fixture = sonFixtures[idx];
  const detail = document.getElementById("detail");
  detail.innerHTML = '<div class="placeholder">Yükleniyor...</div>';
  setStatus("İstatistikler ve oranlar çekiliyor...");

  const homeId = fixture.teams.home.id;
  const awayId = fixture.teams.away.id;

  const [homeStats, awayStats, h2h, odds] = await Promise.all([
    takimIstatistikGetir(homeId, sonLeagueId, sonSeason),
    takimIstatistikGetir(awayId, sonLeagueId, sonSeason),
    apiGet("/fixtures/headtohead", { h2h: `${homeId}-${awayId}`, last: 5 }),
    apiGet("/odds", { fixture: fixture.fixture.id, bookmaker: BET365_ID })
  ]);

  setStatus("Hazır.");
  renderDetail(fixture, homeStats, awayStats, h2h, odds, idx);
}

async function takimIstatistikGetir(teamId, leagueId, season){
  const key = `${teamId}_${leagueId}_${season}`;
  if(takimIstatistikCache[key]) return takimIstatistikCache[key];
  const data = await apiGet("/teams/statistics", { team: teamId, league: leagueId, season: season });
  const result = data && data.response ? data.response : null;
  takimIstatistikCache[key] = result;
  return result;
}

function faktoriyel(n){
  let r = 1;
  for(let i = 2; i <= n; i++) r *= i;
  return r;
}
function poissonOlasilik(lambda, k){
  return Math.exp(-lambda) * Math.pow(lambda, k) / faktoriyel(k);
}

function beklenenGolHesapla(homeStats, awayStats){
  const homeAtkHome = parseFloat(homeStats?.goals?.for?.average?.home) || 1.3;
  const awayDefAway = parseFloat(awayStats?.goals?.against?.average?.away) || 1.3;
  const awayAtkAway = parseFloat(awayStats?.goals?.for?.average?.away) || 1.1;
  const homeDefHome = parseFloat(homeStats?.goals?.against?.average?.home) || 1.1;

  const homeExpected = (homeAtkHome + awayDefAway) / 2;
  const awayExpected = (awayAtkAway + homeDefHome) / 2;
  return { homeExpected, awayExpected };
}

function modelTahminHesapla(homeExpected, awayExpected){
  const MAKS_GOL = 6;
  let pHome = 0, pDraw = 0, pAway = 0, pOver25 = 0, pBTTS = 0;
  for(let h = 0; h <= MAKS_GOL; h++){
    for(let a = 0; a <= MAKS_GOL; a++){
      const p = poissonOlasilik(homeExpected, h) * poissonOlasilik(awayExpected, a);
      if(h > a) pHome += p;
      else if(h === a) pDraw += p;
      else pAway += p;
      if(h + a > 2.5) pOver25 += p;
      if(h > 0 && a > 0) pBTTS += p;
    }
  }
  return { homeWin: pHome, draw: pDraw, awayWin: pAway, over25: pOver25, btts: pBTTS };
}

function impliedProb(odd){
  if(!odd || isNaN(odd)) return null;
  return 1 / parseFloat(odd);
}

function renderDetail(fixture, homeStats, awayStats, h2h, oddsData, fixtureIdx){
  const detail = document.getElementById("detail");
  const home = fixture.teams.home.name;
  const away = fixture.teams.away.name;
  const tarih = new Date(fixture.fixture.date).toLocaleDateString("tr-TR");

  let html = `
    <div class="match-title">${home} vs ${away}</div>
    <div class="match-meta">${tarih} · Gerçek sonuç: ${fixture.goals.home} - ${fixture.goals.away}</div>
  `;

  if(!homeStats || !awayStats){
    html += `<div class="placeholder">Bu takımlar için istatistik verisi bulunamadı.</div>`;
    detail.innerHTML = html;
    return;
  }

  const { homeExpected, awayExpected } = beklenenGolHesapla(homeStats, awayStats);
  const model = modelTahminHesapla(homeExpected, awayExpected);

  html += `<div class="section-title">Model Tahmini (Poisson)</div>`;
  html += `
    <div class="prob-grid">
      <div class="prob-box"><div class="lbl">${home}</div><div class="val">${(model.homeWin*100).toFixed(0)}%</div></div>
      <div class="prob-box"><div class="lbl">Beraberlik</div><div class="val">${(model.draw*100).toFixed(0)}%</div></div>
      <div class="prob-box"><div class="lbl">${away}</div><div class="val">${(model.awayWin*100).toFixed(0)}%</div></div>
    </div>
  `;

  const bet365 = oddsData?.response?.[0]?.bookmakers?.find(b => b.id === BET365_ID);
  const matchWinnerBet = bet365?.bets?.find(b => b.name === "Match Winner");
  
  html += `<div class="section-title">Bet365 Oranları</div>`;
  if(matchWinnerBet){
    const homeOdd = matchWinnerBet.values.find(v => v.value === "Home")?.odd;
    const drawOdd = matchWinnerBet.values.find(v => v.value === "Draw")?.odd;
    const awayOdd = matchWinnerBet.values.find(v => v.value === "Away")?.odd;
    html += renderOddsRow("Ev sahibi kazanır", model.homeWin, homeOdd);
    html += renderOddsRow("Beraberlik", model.draw, drawOdd);
    html += renderOddsRow("Deplasman kazanır", model.awayWin, awayOdd);
  } else {
    html += `<div class="small">Bet365 oranı bulunamadı.</div>`;
  }

  detail.innerHTML = html;
}

function renderOddsRow(label, modelProb, odd){
  const implied = impliedProb(odd);
  let diffHtml = "";
  if(implied !== null){
    const fark = (modelProb - implied) * 100;
    const cls = fark >= 0 ? "odds-diff-pos" : "odds-diff-neg";
    diffHtml = `<span class="${cls}">${fark >= 0 ? "+" : ""}${fark.toFixed(1)} puan</span>`;
  }
  return `
    <div class="row-flex">
      <span>${label}</span>
      <span>Model: ${(modelProb*100).toFixed(0)}% · Bet365: ${odd ? (implied*100).toFixed(0) + "% (" + odd + ")" : "yok"} ${diffHtml}</span>
    </div>`;
}

// ** Esnek Tek veya Çoklu Oran Arama Fonksiyonu **
async function tekVeyaCokluOranTara(){
  const leagueId = document.getElementById("leagueSelect").value;
  const season = document.getElementById("seasonSelect").value;
  const hHedef = document.getElementById("oddHomeInput").value ? parseFloat(document.getElementById("oddHomeInput").value) : null;
  const dHedef = document.getElementById("oddDrawInput").value ? parseFloat(document.getElementById("oddDrawInput").value) : null;
  const aHedef = document.getElementById("oddAwayInput").value ? parseFloat(document.getElementById("oddAwayInput").value) : null;
  const tol = parseFloat(document.getElementById("toleranceSelect").value);
  const ustSinir = parseInt(document.getElementById("scanLimitSelect").value);

  const statusEl = document.getElementById("fullScanStatus");
  const resultsEl = document.getElementById("fullScanResults");
  resultsEl.innerHTML = "";

  if(hHedef === null && dHedef === null && aHedef === null){
    statusEl.textContent = "Lütfen en az bir oran alanı (MS1, MS0 veya MS2) doldurun.";
    statusEl.style.color = "var(--danger)";
    return;
  }

  statusEl.style.color = "var(--muted)";
  statusEl.textContent = "Sezon maçları çekiliyor...";

  const data = await apiGet("/fixtures", { league: leagueId, season: season });
  if(!data || !data.response){
    statusEl.textContent = "Maçlar alınamadı.";
    return;
  }

  const ftMatches = data.response
    .filter(f => f.fixture.status.short === "FT")
    .slice(0, ustSinir);

  statusEl.textContent = `${ftMatches.length} maç taranıyor, oranlar kontrol ediliyor...`;

  let bulunanlar = [];
  for(let i = 0; i < ftMatches.length; i++){
    const f = ftMatches[i];
    statusEl.textContent = `Taranıyor: ${i+1}/${ftMatches.length} (${bulunanlar.length} eşleşme bulundu)`;
    
    const oddsData = await apiGet("/odds", { fixture: f.fixture.id, bookmaker: BET365_ID });
    const bet365 = oddsData?.response?.[0]?.bookmakers?.find(b => b.id === BET365_ID);
    const mw = bet365?.bets?.find(b => b.name === "Match Winner");
    if(!mw) continue;

    const h = parseFloat(mw.values.find(v => v.value === "Home")?.odd);
    const d = parseFloat(mw.values.find(v => v.value === "Draw")?.odd);
    const a = parseFloat(mw.values.find(v => v.value === "Away")?.odd);
    if(isNaN(h) || isNaN(d) || isNaN(a)) continue;

    // Esnek filtreleme: Sadece doldurulan alanlar tolerans dahilinde karşılaştırılır
    let matchH = hHedef === null || Math.abs(h - hHedef) <= tol;
    let matchD = dHedef === null || Math.abs(d - dHedef) <= tol;
    let matchA = aHedef === null || Math.abs(a - aHedef) <= tol;

    if(matchH && matchD && matchA){
      bulunanlar.push({ f, h, d, a });
    }
  }

  statusEl.textContent = `Tarama tamamlandı. ${bulunanlar.length} maç eşleşti.`;

  if(bulunanlar.length === 0){
    resultsEl.innerHTML = `<div class="placeholder" style="padding:15px;">Bu kriterlere uygun maç bulunamadı. Tolerans aralığını genişletebilirsin.</div>`;
    return;
  }

  let html = `<table><tr><th>Tarih</th><th>Maç</th><th>Oranlar (1-X-2)</th><th>Skor</th></tr>`;
  bulunanlar.forEach(b => {
    const tarih = new Date(b.f.fixture.date).toLocaleDateString("tr-TR");
    html += `<tr>
      <td>${tarih}</td>
      <td>${b.f.teams.home.name} - ${b.f.teams.away.name}</td>
      <td>${b.h} / ${b.d} / ${b.a}</td>
      <td><strong>${b.f.goals.home}-${b.f.goals.away}</strong></td>
    </tr>`;
  });
  html += `</table>`;
  resultsEl.innerHTML = html;
}
</script>
</body>
</html><!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tahmin Paneli</title>
<style>
  :root{
    --bg:#0d1117;
    --panel:#151b23;
    --panel2:#1c2530;
    --line:#2a3542;
    --text:#e6edf3;
    --muted:#8b98a5;
    --accent:#3fb950;
    --accent2:#58a6ff;
    --warn:#e3b341;
    --danger:#f85149;
  }
  *{box-sizing:border-box;}
  body{
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    padding:24px;
  }
  h1{font-size:22px;font-weight:700;margin:0 0 4px;}
  .sub{color:var(--muted);font-size:13px;margin-bottom:20px;}
  .note{
    background:#2d2410;border:1px solid #4a3a12;color:var(--warn);
    padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:20px;
  }
  .controls{
    display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-bottom:20px;
    background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;
  }
  .field label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px;}
  select,button,input{
    background:var(--panel2);color:var(--text);border:1px solid var(--line);
    border-radius:6px;padding:8px 10px;font-size:14px;
  }
  button{
    cursor:pointer;background:var(--accent2);color:#04121f;font-weight:600;border:none;
  }
  button:hover{filter:brightness(1.1);}
  button:disabled{opacity:.5;cursor:not-allowed;}
  button.secondary{background:var(--panel2);color:var(--text);border:1px solid var(--line);}
  #status{font-size:13px;color:var(--muted);margin-bottom:16px;min-height:18px;}
  .layout{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap;}
  #fixtureList{
    flex:1;min-width:320px;max-height:640px;overflow-y:auto;
    background:var(--panel);border:1px solid var(--line);border-radius:10px;
  }
  .fixture-row{
    padding:12px 14px;border-bottom:1px solid var(--line);cursor:pointer;
    display:flex;justify-content:space-between;font-size:14px;
  }
  .fixture-row:hover{background:var(--panel2);}
  .fixture-row.active{background:#12283f;}
  .fixture-date{color:var(--muted);font-size:12px;}
  #detail{
    flex:1.3;min-width:360px;background:var(--panel);border:1px solid var(--line);
    border-radius:10px;padding:18px;
  }
  .placeholder{color:var(--muted);font-size:14px;text-align:center;padding:60px 20px;}
  .match-title{font-size:17px;font-weight:700;margin-bottom:2px;}
  .match-meta{color:var(--muted);font-size:12px;margin-bottom:16px;}
  .section-title{
    font-size:12px;text-transform:none;color:var(--accent2);
    margin:18px 0 8px;font-weight:700;border-top:1px solid var(--line);padding-top:14px;
  }
  .section-title:first-of-type{border-top:none;padding-top:0;}
  .prob-grid{display:flex;gap:10px;}
  .prob-box{
    flex:1;background:var(--panel2);border-radius:8px;padding:10px;text-align:center;
  }
  .prob-box .lbl{font-size:11px;color:var(--muted);}
  .prob-box .val{font-size:20px;font-weight:700;margin-top:2px;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  td,th{padding:6px 4px;border-bottom:1px solid var(--line);text-align:left;}
  th{color:var(--muted);font-weight:600;}
  .row-flex{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-bottom:1px dashed var(--line);}
  .odds-diff-pos{color:var(--accent);}
  .odds-diff-neg{color:var(--danger);}
  #similarBtn{margin-top:6px;}
  .small{font-size:12px;color:var(--muted);}
</style>
</head>
<body>

<h1>Tahmin Paneli</h1>
<div class="sub">Poisson modeli · H2H · Bet365 oran karşılaştırması · benzer oranlı geçmiş maçlar</div>

<div class="note">
  API-Football ücretsiz/pro plan kısıtlamaları nedeniyle oran verileri en verimli güncel sezonda (2024–2025/2026) çekilebilmektedir. Oranlı aramalarda bu detay baz alınır.
</div>

<div class="controls">
  <div class="field">
    <label>Lig</label>
    <select id="leagueSelect">
      <option value="203">Süper Lig (Türkiye)</option>
      <option value="39">Premier League</option>
      <option value="140">La Liga</option>
      <option value="135">Serie A</option>
      <option value="78">Bundesliga</option>
      <option value="61">Ligue 1</option>
    </select>
  </div>
  <div class="field">
    <label>Sezon</label>
    <select id="seasonSelect">
      <option value="2024" selected>2024</option>
      <option value="2023">2023</option>
      <option value="2022">2022</option>
    </select>
  </div>
  <div class="field">
    <button id="loadBtn" onclick="maclariYukle()">Maçları Yükle</button>
  </div>
  <div class="field">
    <button class="secondary" id="apiKeyBtn" onclick="keyDurumGoster()">Key durumu</button>
  </div>
</div>

<div class="controls" style="flex-direction:column;align-items:stretch;">
  <div style="font-size:13px;color:var(--accent2);font-weight:700;">Tam/Yakın Oranlı Maç Arama</div>
  <div class="small">
    MS1, MS0 veya MS2 değerlerinden dilediğini (veya hepsini) doldurarak tarama yapabilirsin. Boş bıraktığın oranlar eşleşmede dikkate alınmaz.
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-top:8px;">
    <div class="field"><label>MS1 (Ev) - İsteğe bağlı</label><input type="number" step="0.01" id="oddHomeInput" placeholder="Örn: 1.69" style="width:100px;"></div>
    <div class="field"><label>MS0 (Beraberlik) - İsteğe bağlı</label><input type="number" step="0.01" id="oddDrawInput" placeholder="Örn: 3.50" style="width:100px;"></div>
    <div class="field"><label>MS2 (Deplasman) - İsteğe bağlı</label><input type="number" step="0.01" id="oddAwayInput" placeholder="Örn: 3.20" style="width:100px;"></div>
    <div class="field"><label>Tolerans (±)</label>
      <select id="toleranceSelect" style="width:90px;">
        <option value="0.05">±0.05</option>
        <option value="0.1" selected>±0.10</option>
        <option value="0.25">±0.25</option>
        <option value="0.5">±0.50</option>
      </select>
    </div>
    <div class="field"><label>Taranacak maç sınırı</label>
      <select id="scanLimitSelect" style="width:90px;">
        <option value="20" selected>20</option>
        <option value="50">50</option>
      </select>
    </div>
    <div class="field"><button onclick="tekVeyaCokluOranTara()">Orana Göre Ara</button></div>
  </div>
  <div id="fullScanStatus" class="small" style="margin-top:6px;"></div>
  <div id="fullScanResults"></div>
</div>

<div id="status"></div>

<div class="layout">
  <div id="fixtureList">
    <div class="placeholder">Bir lig/sezon seçip "Maçları Yükle"ye bas.</div>
  </div>
  <div id="detail">
    <div class="placeholder">Soldan bir maç seç, detaylar burada görünecek.</div>
  </div>
</div>

<script>
const API_KEYS = [
  "3b90f0de19091dbf6593732af60ccb25",
  "8782d0553955500b2d68552bfa5fe531c"
];
const BASE_URL = "https://v3.football.api-sports.io";
const BET365_ID = 8;

let aktifKeyIndex = 0;
let sonFixtures = [];
let sonLeagueId = null;
let sonSeason = null;
let takimIstatistikCache = {};

function setStatus(msg, isError){
  const el = document.getElementById("status");
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function keyDurumGoster(){
  setStatus(`${API_KEYS.length} key tanımlı. Şu an key #${aktifKeyIndex + 1} kullanılıyor.`);
}

async function apiGet(endpoint, params){
  const url = new URL(BASE_URL + endpoint);
  Object.entries(params || {}).forEach(([k,v]) => url.searchParams.set(k, v));

  while(aktifKeyIndex < API_KEYS.length){
    try{
      const res = await fetch(url.toString(), {
        headers: { "x-apisports-key": API_KEYS[aktifKeyIndex] }
      });
      const data = await res.json();
      const errors = data.errors;
      const errorText = errors ? JSON.stringify(errors).toLowerCase() : "";
      if(errors && Object.keys(errors).length > 0 &&
         (errorText.includes("limit") || errorText.includes("quota") ||
          errorText.includes("rate") || errorText.includes("suspend"))){
        aktifKeyIndex++;
        setStatus(`Key ${aktifKeyIndex} limiti doldu, sıradaki deneniyor...`);
        continue;
      }
      return data;
    }catch(e){
      setStatus("Ağ hatası: " + e.message, true);
      return null;
    }
  }
  setStatus("Tüm key'ler limitine ulaştı.", true);
  return null;
}

async function maclariYukle(){
  const leagueId = document.getElementById("leagueSelect").value;
  const season = document.getElementById("seasonSelect").value;
  sonLeagueId = leagueId;
  sonSeason = season;

  document.getElementById("loadBtn").disabled = true;
  setStatus("Maçlar yükleniyor...");
  document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Yükleniyor...</div>';
  document.getElementById("detail").innerHTML = '<div class="placeholder">Soldan bir maç seç, detaylar burada görünecek.</div>';

  const data = await apiGet("/fixtures", { league: leagueId, season: season });
  document.getElementById("loadBtn").disabled = false;

  if(!data || !data.response){
    document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Maç bulunamadı.</div>';
    return;
  }

  sonFixtures = data.response
    .filter(f => f.fixture.status.short === "FT")
    .sort((a,b) => new Date(b.fixture.date) - new Date(a.fixture.date));

  if(sonFixtures.length === 0){
    document.getElementById("fixtureList").innerHTML = '<div class="placeholder">Tamamlanmış maç bulunamadı.</div>';
    setStatus("0 maç bulundu.");
    return;
  }

  setStatus(`${sonFixtures.length} maç yüklendi.`);
  renderFixtureList();
}

function renderFixtureList(){
  const container = document.getElementById("fixtureList");
  container.innerHTML = "";
  sonFixtures.forEach((f, idx) => {
    const row = document.createElement("div");
    row.className = "fixture-row";
    row.id = "fx-" + idx;
    const tarih = new Date(f.fixture.date).toLocaleDateString("tr-TR");
    row.innerHTML = `
      <div>
        <div>${f.teams.home.name} ${f.goals.home ?? "-"} - ${f.goals.away ?? "-"} ${f.teams.away.name}</div>
        <div class="fixture-date">${tarih}</div>
      </div>`;
    row.onclick = () => macSec(idx);
    container.appendChild(row);
  });
}

async function macSec(idx){
  document.querySelectorAll(".fixture-row").forEach(r => r.classList.remove("active"));
  document.getElementById("fx-" + idx).classList.add("active");

  const fixture = sonFixtures[idx];
  const detail = document.getElementById("detail");
  detail.innerHTML = '<div class="placeholder">Yükleniyor...</div>';
  setStatus("İstatistikler ve oranlar çekiliyor...");

  const homeId = fixture.teams.home.id;
  const awayId = fixture.teams.away.id;

  const [homeStats, awayStats, h2h, odds] = await Promise.all([
    takimIstatistikGetir(homeId, sonLeagueId, sonSeason),
    takimIstatistikGetir(awayId, sonLeagueId, sonSeason),
    apiGet("/fixtures/headtohead", { h2h: `${homeId}-${awayId}`, last: 5 }),
    apiGet("/odds", { fixture: fixture.fixture.id, bookmaker: BET365_ID })
  ]);

  setStatus("Hazır.");
  renderDetail(fixture, homeStats, awayStats, h2h, odds, idx);
}

async function takimIstatistikGetir(teamId, leagueId, season){
  const key = `${teamId}_${leagueId}_${season}`;
  if(takimIstatistikCache[key]) return takimIstatistikCache[key];
  const data = await apiGet("/teams/statistics", { team: teamId, league: leagueId, season: season });
  const result = data && data.response ? data.response : null;
  takimIstatistikCache[key] = result;
  return result;
}

function faktoriyel(n){
  let r = 1;
  for(let i = 2; i <= n; i++) r *= i;
  return r;
}
function poissonOlasilik(lambda, k){
  return Math.exp(-lambda) * Math.pow(lambda, k) / faktoriyel(k);
}

function beklenenGolHesapla(homeStats, awayStats){
  const homeAtkHome = parseFloat(homeStats?.goals?.for?.average?.home) || 1.3;
  const awayDefAway = parseFloat(awayStats?.goals?.against?.average?.away) || 1.3;
  const awayAtkAway = parseFloat(awayStats?.goals?.for?.average?.away) || 1.1;
  const homeDefHome = parseFloat(homeStats?.goals?.against?.average?.home) || 1.1;

  const homeExpected = (homeAtkHome + awayDefAway) / 2;
  const awayExpected = (awayAtkAway + homeDefHome) / 2;
  return { homeExpected, awayExpected };
}

function modelTahminHesapla(homeExpected, awayExpected){
  const MAKS_GOL = 6;
  let pHome = 0, pDraw = 0, pAway = 0, pOver25 = 0, pBTTS = 0;
  for(let h = 0; h <= MAKS_GOL; h++){
    for(let a = 0; a <= MAKS_GOL; a++){
      const p = poissonOlasilik(homeExpected, h) * poissonOlasilik(awayExpected, a);
      if(h > a) pHome += p;
      else if(h === a) pDraw += p;
      else pAway += p;
      if(h + a > 2.5) pOver25 += p;
      if(h > 0 && a > 0) pBTTS += p;
    }
  }
  return { homeWin: pHome, draw: pDraw, awayWin: pAway, over25: pOver25, btts: pBTTS };
}

function impliedProb(odd){
  if(!odd || isNaN(odd)) return null;
  return 1 / parseFloat(odd);
}

function renderDetail(fixture, homeStats, awayStats, h2h, oddsData, fixtureIdx){
  const detail = document.getElementById("detail");
  const home = fixture.teams.home.name;
  const away = fixture.teams.away.name;
  const tarih = new Date(fixture.fixture.date).toLocaleDateString("tr-TR");

  let html = `
    <div class="match-title">${home} vs ${away}</div>
    <div class="match-meta">${tarih} · Gerçek sonuç: ${fixture.goals.home} - ${fixture.goals.away}</div>
  `;

  if(!homeStats || !awayStats){
    html += `<div class="placeholder">Bu takımlar için istatistik verisi bulunamadı.</div>`;
    detail.innerHTML = html;
    return;
  }

  const { homeExpected, awayExpected } = beklenenGolHesapla(homeStats, awayStats);
  const model = modelTahminHesapla(homeExpected, awayExpected);

  html += `<div class="section-title">Model Tahmini (Poisson)</div>`;
  html += `
    <div class="prob-grid">
      <div class="prob-box"><div class="lbl">${home}</div><div class="val">${(model.homeWin*100).toFixed(0)}%</div></div>
      <div class="prob-box"><div class="lbl">Beraberlik</div><div class="val">${(model.draw*100).toFixed(0)}%</div></div>
      <div class="prob-box"><div class="lbl">${away}</div><div class="val">${(model.awayWin*100).toFixed(0)}%</div></div>
    </div>
  `;

  const bet365 = oddsData?.response?.[0]?.bookmakers?.find(b => b.id === BET365_ID);
  const matchWinnerBet = bet365?.bets?.find(b => b.name === "Match Winner");
  
  html += `<div class="section-title">Bet365 Oranları</div>`;
  if(matchWinnerBet){
    const homeOdd = matchWinnerBet.values.find(v => v.value === "Home")?.odd;
    const drawOdd = matchWinnerBet.values.find(v => v.value === "Draw")?.odd;
    const awayOdd = matchWinnerBet.values.find(v => v.value === "Away")?.odd;
    html += renderOddsRow("Ev sahibi kazanır", model.homeWin, homeOdd);
    html += renderOddsRow("Beraberlik", model.draw, drawOdd);
    html += renderOddsRow("Deplasman kazanır", model.awayWin, awayOdd);
  } else {
    html += `<div class="small">Bet365 oranı bulunamadı.</div>`;
  }

  detail.innerHTML = html;
}

function renderOddsRow(label, modelProb, odd){
  const implied = impliedProb(odd);
  let diffHtml = "";
  if(implied !== null){
    const fark = (modelProb - implied) * 100;
    const cls = fark >= 0 ? "odds-diff-pos" : "odds-diff-neg";
    diffHtml = `<span class="${cls}">${fark >= 0 ? "+" : ""}${fark.toFixed(1)} puan</span>`;
  }
  return `
    <div class="row-flex">
      <span>${label}</span>
      <span>Model: ${(modelProb*100).toFixed(0)}% · Bet365: ${odd ? (implied*100).toFixed(0) + "% (" + odd + ")" : "yok"} ${diffHtml}</span>
    </div>`;
}

// ** Esnek Tek veya Çoklu Oran Arama Fonksiyonu **
async function tekVeyaCokluOranTara(){
  const leagueId = document.getElementById("leagueSelect").value;
  const season = document.getElementById("seasonSelect").value;
  const hHedef = document.getElementById("oddHomeInput").value ? parseFloat(document.getElementById("oddHomeInput").value) : null;
  const dHedef = document.getElementById("oddDrawInput").value ? parseFloat(document.getElementById("oddDrawInput").value) : null;
  const aHedef = document.getElementById("oddAwayInput").value ? parseFloat(document.getElementById("oddAwayInput").value) : null;
  const tol = parseFloat(document.getElementById("toleranceSelect").value);
  const ustSinir = parseInt(document.getElementById("scanLimitSelect").value);

  const statusEl = document.getElementById("fullScanStatus");
  const resultsEl = document.getElementById("fullScanResults");
  resultsEl.innerHTML = "";

  if(hHedef === null && dHedef === null && aHedef === null){
    statusEl.textContent = "Lütfen en az bir oran alanı (MS1, MS0 veya MS2) doldurun.";
    statusEl.style.color = "var(--danger)";
    return;
  }

  statusEl.style.color = "var(--muted)";
  statusEl.textContent = "Sezon maçları çekiliyor...";

  const data = await apiGet("/fixtures", { league: leagueId, season: season });
  if(!data || !data.response){
    statusEl.textContent = "Maçlar alınamadı.";
    return;
  }

  const ftMatches = data.response
    .filter(f => f.fixture.status.short === "FT")
    .slice(0, ustSinir);

  statusEl.textContent = `${ftMatches.length} maç taranıyor, oranlar kontrol ediliyor...`;

  let bulunanlar = [];
  for(let i = 0; i < ftMatches.length; i++){
    const f = ftMatches[i];
    statusEl.textContent = `Taranıyor: ${i+1}/${ftMatches.length} (${bulunanlar.length} eşleşme bulundu)`;
    
    const oddsData = await apiGet("/odds", { fixture: f.fixture.id, bookmaker: BET365_ID });
    const bet365 = oddsData?.response?.[0]?.bookmakers?.find(b => b.id === BET365_ID);
    const mw = bet365?.bets?.find(b => b.name === "Match Winner");
    if(!mw) continue;

    const h = parseFloat(mw.values.find(v => v.value === "Home")?.odd);
    const d = parseFloat(mw.values.find(v => v.value === "Draw")?.odd);
    const a = parseFloat(mw.values.find(v => v.value === "Away")?.odd);
    if(isNaN(h) || isNaN(d) || isNaN(a)) continue;

    // Esnek filtreleme: Sadece doldurulan alanlar tolerans dahilinde karşılaştırılır
    let matchH = hHedef === null || Math.abs(h - hHedef) <= tol;
    let matchD = dHedef === null || Math.abs(d - dHedef) <= tol;
    let matchA = aHedef === null || Math.abs(a - aHedef) <= tol;

    if(matchH && matchD && matchA){
      bulunanlar.push({ f, h, d, a });
    }
  }

  statusEl.textContent = `Tarama tamamlandı. ${bulunanlar.length} maç eşleşti.`;

  if(bulunanlar.length === 0){
    resultsEl.innerHTML = `<div class="placeholder" style="padding:15px;">Bu kriterlere uygun maç bulunamadı. Tolerans aralığını genişletebilirsin.</div>`;
    return;
  }

  let html = `<table><tr><th>Tarih</th><th>Maç</th><th>Oranlar (1-X-2)</th><th>Skor</th></tr>`;
  bulunanlar.forEach(b => {
    const tarih = new Date(b.f.fixture.date).toLocaleDateString("tr-TR");
    html += `<tr>
      <td>${tarih}</td>
      <td>${b.f.teams.home.name} - ${b.f.teams.away.name}</td>
      <td>${b.h} / ${b.d} / ${b.a}</td>
      <td><strong>${b.f.goals.home}-${b.f.goals.away}</strong></td>
    </tr>`;
  });
  html += `</table>`;
  resultsEl.innerHTML = html;
}
</script>
</body>
</html>
