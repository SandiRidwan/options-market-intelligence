<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=40&duration=3000&pause=1000&color=6A4C93&center=true&vCenter=true&width=900&height=70&lines=OPTIONS+MARKET+INTELLIGENCE" alt="Options Market Intelligence" />

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=16&duration=2500&pause=800&color=6A4C93&center=true&vCenter=true&multiline=true&width=940&height=50&lines=IV+Smile+%E2%86%92+Gamma+Exposure+%E2%86%92+OI+Walls+%E2%86%92+Liquidity" alt="Tagline" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-6A4C93?style=for-the-badge&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Domain](https://img.shields.io/badge/Domain-Options_%2F_Derivatives-6A4C93?style=for-the-badge)
![Contracts](https://img.shields.io/badge/Contracts-469_%C3%97_41_tickers-2E6F95?style=for-the-badge)

</div>

---

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██████╗ ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗███████╗               ║
║  ██╔═══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝               ║
║  ██║   ██║██████╔╝   ██║   ██║██║   ██║██╔██╗ ██║███████╗               ║
║  ██║   ██║██╔═══╝    ██║   ██║██║   ██║██║╚██╗██║╚════██║               ║
║  ╚██████╔╝██║        ██║   ██║╚██████╔╝██║ ╚████║███████║               ║
║   ╚═════╝ ╚═╝        ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝               ║
║                                                                          ║
║   MARKET INTELLIGENCE · IV SMILE · GEX · OI WALLS · LIQUIDITY           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 🎬 Demo

<div align="center">
  <img src="reports/figures/dashboard_top.png" width="880" alt="Options Dashboard" />
  <br/>
  <sub><i>Interactive Streamlit dashboard — IV smile, IV skew, GEX, liquidity, contract scores</i></sub>
</div>

<br/>

```bash
streamlit run app/dashboard.py     # → http://localhost:8504
```

---

## 🧠 Overview

**Options Market Intelligence** mengubah **daftar kontrak opsi** menjadi **intelijen
pasar**: apa yang dikatakan permintaan opsi tentang ekspektasi pasar, volatilitas,
dan level kunci. Berbeda dari sebuah *scanner* (yang memilih kontrak), proyek ini
adalah **lapisan analis** — mengukur struktur pasar opsi secara menyeluruh.

<div align="center">

| Metric | Value |
|-------:|:------|
| 📊 Sumber | **yfinance** — 41 ticker · CALL + PUT lengkap |
| 🧾 Kontrak | **4.855 = 2.448 CALL + 2.407 PUT** (lengkap!) |
| 📈 Put/Call Ratio | **0.50** (volume) — sentimen bullish |
| 💧 Median spread | **7,9%** (bid-ask) |
| 🗂️ Total volume | 5,3 juta kontrak |
| 📁 Output | Streamlit app · 10 charts · tabel insight |

</div>

> ✅ **Dataset kini CALL + PUT lengkap** (dikumpulkan via yfinance) — sehingga
> **Put/Call Ratio** dapat dihitung.
>
> ⚠️ **Catatan jujur:** `openInterest` dari Yahoo hampir selalu 0 untuk kuotasi
> realtime, sehingga **PCR berbasis volume** (bukan OI). Bila OI kosong, laporan
> mengatakannya — bukan memaksakan metrik.

---

## ⚡ Analisis Inti

### 1. Implied Volatility Smile / Skew

![IV smile](reports/figures/01_iv_smile.png)

**Temuan:** IV membentuk **pola U** klasik — terendah di **ATM (34%)**, naik ke
**Deep ITM (106%)** dan **Deep OTM (87%)**. Ini adalah *volatility smile*: pasar
memberi premi lebih besar untuk strike ekstrem (deep ITM/OTM).

### 2. IV Skew per Ticker

![IV skew](reports/figures/02_iv_skew.png)

**Skew** = IV OTM − IV ITM. Positif besar = permintaan spekulatif pada strike jauh.

| Ticker | IV skew | Arti |
|--------|--------:|------|
| **MU** | +73 pp | OTM jauh lebih mahal (spekulasi tinggi) |
| **INTC** | +69 pp | |
| **SOFI** | +52 pp | |
| **AMD** | +42 pp | |

Skew negatif (mis. QQQ −9 pp) menunjukkan permintaan lindung nilai/ITM lebih kuat.

### 3. Gamma Exposure (GEX)

![GEX](reports/figures/03_gex.png)

**Gamma exposure** (proxy dari open interest tertimbang kedekatan ATM) menunjukkan
di mana *hedging* dealer terkonsentrasi:

| Ticker | GEX share | Total OI |
|--------|----------:|---------:|
| **SPY** | **14,2%** | 205.240 |
| **NVDA** | **10,1%** | 165.414 |
| **PLTR** | 8,1% | 158.102 |
| **QQQ** | 7,9% | 119.887 |

Level strike paling berpengaruh: **NVDA $220**.

### 4. Open-Interest Walls

![OI walls](reports/figures/04_oi_walls.png)

Strike dengan OI terbesar = **"dinding"** yang sering bertindak sebagai support/resistance
karena konsentrasi posisi di sana.

### 5. Likuiditas

![Liquidity](reports/figures/05_liquidity.png)

Peta likuiditas: ticker di **kiri-bawah** = OI besar & spread sempit (terbaik untuk
eksekusi). Spread sangat lebar (>8%) menandakan kontrak mahal untuk ditransaksikan.

### 7. Put/Call Ratio (analisis baru)

![PCR](reports/figures/09_put_call_ratio.png)

**Put/Call Ratio** (volume-based) mengukur sentimen pasar:

| Ticker | PCR | Arti |
|--------|----:|------|
| **HYG** | 9,89 | Hedging kredit ekstrem (put jauh dominan) |
| QQQ / SPY | ~1,0 | Indeks di-hedge (seimbang) |
| **BAC / CVX / KO** | 0,10–0,16 | Saham individual bullish kuat |
| **Agregat** | **0,50** | Sentimen keseluruhan bullish |

**Pola kunci:** *indeks di-hedge* (PCR ≈ 1), sementara *saham individual bullish*
(PCR < 0,5) — pola klasik "hedge indeks, tapi bullish saham".

### 8. IV Smile Dua-Sisi (CALL vs PUT)

![IV both sides](reports/figures/10_iv_both_sides.png)

**Put wing jauh lebih mahal:** Deep-OTM put **166%** vs call 50%. Ini adalah
*put skew* — pasar membayar premium besar untuk perlindungan penurunan.

### 6. Distribusi Moneyness & Skor

![moneyness](reports/figures/06_moneyness.png)
![scores](reports/figures/07_score_components.png)

Separuh kontrak in-the-money; skor komposit tertinggi berada di sekitar **ATM**.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  data/raw/scored_contracts.csv                                       │
│  469 kontrak × 26 kolom (bid/ask, OI, IV, delta, gamma, skor)        │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  analysis.py — lapisan analis                                        │
│  · iv_by_moneyness / iv_skew_by_ticker   (volatility)                │
│  · gex_by_ticker / oi_walls / top_gex    (gamma & posisi)            │
│  · liquidity / spread_quality            (likuiditas)                │
│  · moneyness_dist / score_decomposition  (distribusi & skor)         │
└───────────────┬───────────────────────────────┬──────────────────────┘
                ▼                               ▼
      reports/figures (8 chart)        app/dashboard.py (Streamlit)
```

---

## 📁 File Structure

```
options-market-intelligence/
├── app/
│   └── dashboard.py                 # ⭐ Interactive Streamlit dashboard
├── src/
│   ├── analysis.py                  # analisis IV/GEX/likuiditas (murni)
│   ├── run_analysis.py              # orkestrator -> tabel + summary.json
│   └── make_charts.py               # 8 visualisasi
├── data/
│   ├── raw/                         # scored_contracts.csv (mentah)
│   └── processed/                   # options_clean.csv
├── reports/
│   ├── figures/                     # 8 chart + dashboard screenshot
│   ├── tables/                      # 12 tabel insight
│   └── summary.json
├── REPORT.md
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt

python src/run_analysis.py     # tabel + summary
python src/make_charts.py      # 8 chart
streamlit run app/dashboard.py # dashboard
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|-------|------------|
| **Data** | pandas · numpy (opsi scan) |
| **Analisis** | IV surface · gamma proxy · OI walls · liquidity metrics |
| **Visualisasi** | matplotlib · Plotly |
| **Dashboard** | Streamlit |

</div>

---

## 📝 Lessons Learned

1. **Kenali datanya sebelum menyusun pertanyaan.** Dataset ini CALL-only → Put/Call
   Ratio mustahil dihitung; jujur soal batasan lebih baik daripada memaksakan metrik.
2. **Proxy yang transparan > model yang rumit.** GEX di sini adalah proxy dari OI
   (bukan gamma Black-Scholes penuh) — diberi label jelas agar tidak menyesatkan.
3. **Lapisan analis ≠ scanner.** Scanner memilih kontrak; analis menjelaskan struktur
   pasar (volatility, positioning, likuiditas).
4. **Normalisasi penting:** IV/ spread dinilai dalam %, moneyness relatif — bukan
   nilai absolut yang tak sebanding antar-ticker.

---

## ⚠️ Disclaimer

Edukasional, **bukan saran investasi**. Data adalah snapshot dari sebuah opsi scan
dan dapat berubah. Options memiliki risiko tinggi.

---



---

## 📖 Cara Membaca Dashboard (Kenapa · Tujuan · Dampak)

Setiap chart & tabel di dashboard ini dilengkapi **kotak penjelasan** yang menjawab
tiga hal — sesuai standar analisis profesional:

| Pertanyaan | Arti |
|-----------|------|
| **🔎 Kenapa** | Mengapa metrik/analisis ini dipilih (masalah & konteks) |
| **🎯 Tujuan** | Pertanyaan bisnis apa yang dijawab |
| **📈 Dampak** | Implikasi / keputusan / tindakan yang timbul |
| **👁️ Cara baca** | Panduan membaca grafik bila tidak intuitif |

Klik kotak **"💡 … — Kenapa · Tujuan · Dampak"** di atas tiap grafik untuk membukanya.
Narasi tersimpan di `src/explanations.py` (terpisah, konsisten, dapat diaudit).

## 👤 Author

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=700&size=20&duration=3000&pause=1000&color=6A4C93&center=true&vCenter=true&width=400&lines=Sandi+Ridwan" />

**Data Analyst · Data Automation Engineer · Python**

📍 Palu, Central Sulawesi, Indonesia

[![Upwork](https://img.shields.io/badge/Upwork-Hire_Me-6A4C93?style=for-the-badge&logo=upwork&logoColor=white)](https://www.upwork.com/freelancers/~011f6d0fbb4a372974)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sandi-ridwan)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SandiRidwan)

</div>

---

## 📄 License

MIT License — Educational and portfolio purposes only.
