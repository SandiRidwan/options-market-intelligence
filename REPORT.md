# 📊 Options Market Intelligence — Laporan

Analisis struktur pasar opsi dari 469 kontrak CALL (41 ticker).

## 1. Ringkasan
| Metrik | Nilai |
|--------|-------|
| Kontrak | 469 CALL (100%) |
| Ticker | 41 |
| Expiry | 2 (5 & 7 Agu 2026) |
| Median IV | 43% |
| ITM | 47.5% |
| Median spread | 7.9% |
| Total OI | 1.696.080 |
| Total volume | 881.983 |

## 2. Temuan
1. **IV smile** terbentuk: ATM terendah (34%), sayap Deep ITM (106%) & Deep OTM (87%) lebih mahal.
2. **Skew spekulatif** tinggi pada MU (+73pp), INTC (+69pp), SOFI (+52pp).
3. **GEX terkonsentrasi** di SPY (14.2%), NVDA (10.1%), PLTR (8.1%).
4. **Level kunci**: strike NVDA $220 = gamma proxy tertinggi.
5. **Likuiditas bervariasi** — sebagian kontrak spread >8% (mahal ditransaksikan).

## 3. Rekomendasi analitis
- Pantau OI walls sebagai kandidat support/resistance.
- Waspadai kontrak spread lebar (biaya eksekusi tinggi).
- Skew tinggi = ekspektasi pergerakan tajam pada ticker tsb.

## 4. Keterbatasan (jujur)
- Data hanya CALL → Put/Call Ratio tidak tersedia.
- GEX = proxy dari OI (bukan gamma Black-Scholes penuh).
- Snapshot tunggal; bukan time-series.
- Bukan saran investasi.
