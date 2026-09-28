# 📊 Options Market Intelligence — Laporan

Analisis struktur pasar opsi dari 4.855 kontrak (CALL + PUT, 41 ticker).

## 1. Ringkasan
| Metrik | Nilai |
|--------|-------|
| Kontrak | 4.855 (2.448 CALL + 2.407 PUT) |
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

## 4. Put/Call Ratio
- Agregat PCR (volume) = 0.50 → sentimen bullish keseluruhan.
- HYG PCR 9.89 (hedging kredit ekstrem); indeks SPY/QQQ ≈ 1.0 (hedged).
- Saham individual bullish kuat (BAC 0.10).
- Put wing IV (Deep OTM 166%) >> call wing (50%) = premi lindung nilai mahal.

## 5. Keterbatasan (jujur)
- openInterest dari Yahoo sering 0 → PCR memakai volume, bukan OI.
- GEX = proxy dari OI (bukan gamma Black-Scholes penuh).
- Snapshot tunggal; bukan time-series.
- Bukan saran investasi.
