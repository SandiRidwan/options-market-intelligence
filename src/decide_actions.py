"""
decide_actions.py — decision engine untuk strategi opsi (berbasis CSV).

Project ini tidak memakai DuckDB; data dari data/processed/options_clean.csv.
Menghasilkan REKOMENDASI STRATEGI per ticker lewat skor terukur.

Sinyal per ticker:
  · iv_regime     — tingkat IV rata-rata (IV tinggi → beli konveksitas mahal,
                     jual premi menarik)
  · skew_pressure — ketimpangan IV put vs call (hedging mahal = pesimis)
  · rich_premium  — proporsi kontrak deep-ITM/OTM (premi gemuk)
Bobot: 0.4 / 0.35 / 0.25. Tier:
  · beli_konveksitas (>=0.6) · jual_premi (>=0.35) · netral (<0.35)
Output: data/processed/mart_decisions.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from decision import decide, normalize

ROOT = Path(__file__).resolve().parent.parent
SRC_CSV = ROOT / "data" / "processed" / "options_clean.csv"
OUT = ROOT / "data" / "processed" / "mart_decisions.csv"

WEIGHTS = {"iv_regime": 0.40, "skew_pressure": 0.35, "rich_premium": 0.25}
THRESHOLDS = {"beli_konveksitas": 0.60, "jual_premi": 0.35}


def main() -> None:
    if not SRC_CSV.exists():
        raise SystemExit(f"{SRC_CSV} tidak ada — jalankan collect/analysis dulu")
    df = pd.read_csv(SRC_CSV)
    df.columns = [c.strip() for c in df.columns]
    if "impliedVolatility" not in df.columns or "ticker" not in df.columns:
        print("[decision] kolom diperlukan tidak ada. kolom:", list(df.columns))
        return

    # agregasi per ticker
    g = df.groupby("ticker").agg(
        iv_mean=("impliedVolatility", "mean"),
        n=("ticker", "size"),
    ).reset_index()

    # skew: beda IV PUT vs CALL per ticker (jika ada kolom type)
    tcol = next((c for c in df.columns if c.lower() in ("type", "contracttype",
                                                         "option_type")), None)
    if tcol:
        piv = df.pivot_table(index="ticker", columns=tcol,
                             values="impliedVolatility", aggfunc="mean")
        if {"PUT", "CALL"}.issubset(piv.columns):
            piv["put_minus_call"] = piv["PUT"] - piv["CALL"]
            g = g.merge(piv[["put_minus_call"]].reset_index(), on="ticker",
                        how="left")
    if "put_minus_call" not in g.columns:
        g["put_minus_call"] = 0.0
    g["put_minus_call"] = g["put_minus_call"].fillna(0.0)

    iv_lo, iv_hi = g.iv_mean.min(), g.iv_mean.max()
    sk_lo, sk_hi = g.put_minus_call.min(), g.put_minus_call.max()

    payload = []
    for _, r in g.iterrows():
        payload.append({
            "id": r.ticker,
            "signals": {
                "iv_regime": normalize(r.iv_mean, iv_lo, iv_hi),
                "skew_pressure": normalize(r.put_minus_call, sk_lo, sk_hi),
                "rich_premium": normalize(r.iv_mean, iv_lo, iv_hi),  # proksi
            },
            "weights": WEIGHTS, "thresholds": THRESHOLDS,
            "iv_mean": round(float(r.iv_mean), 4),
            "put_minus_call": round(float(r.put_minus_call), 4),
            "n_kontrak": int(r.n),
        })

    dec = decide(payload)
    dec.to_csv(OUT, index=False)
    print(f"[decision] {len(dec)} ticker → rekomendasi strategi:")
    for _, r in dec.head(12).iterrows():
        print(f"   [{r['tier']:18}] skor={r['skor']:.2f}  IV={r['iv_mean']:.3f} "
              f"put-call={r['put_minus_call']:+.3f}  {r['id']}")


if __name__ == "__main__":
    main()
