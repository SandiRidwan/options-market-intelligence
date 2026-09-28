"""run_analysis.py — orkestrator: jalankan semua analisis & simpan tabel+summary."""
from __future__ import annotations

import json
from pathlib import Path

import analysis as A

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "reports" / "tables"
PROC = ROOT / "data" / "processed"
TABLES.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)


def main():
    df = A.load()
    df.to_csv(PROC / "options_clean.csv", index=False)

    tables = {
        "iv_by_moneyness": A.iv_by_moneyness(df),
        "iv_skew_by_ticker": A.iv_skew_by_ticker(df),
        "gex_by_ticker": A.gex_by_ticker(df),
        "top_gex_strikes": A.top_gex_strikes(df),
        "liquidity_by_ticker": A.liquidity_by_ticker(df),
        "moneyness_dist": A.moneyness_dist(df),
        "score_decomposition": A.score_decomposition(df),
        "top_contracts": A.top_contracts(df),
    }
    for name, t in tables.items():
        t.to_csv(TABLES / f"{name}.csv")
        print(f"  [table] {name:24} ({len(t)} rows)")

    # spread quality
    A.spread_quality(df).to_frame("contracts").to_csv(
        TABLES / "spread_quality.csv")

    # OI walls untuk ticker teratas
    top_oi = df.groupby("ticker")["openInterest"].sum().nlargest(5).index
    for tk in top_oi:
        A.oi_walls(df, tk).to_csv(TABLES / f"oi_walls_{tk}.csv")
    print(f"  [table] oi_walls_* ({len(top_oi)} tickers)")

    summary = A.key_insights(df)
    (ROOT / "reports" / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print("  [json] summary.json")
    print("\n=== INSIGHT ===")
    for k, v in summary.items():
        print(f"  {k:20}: {v}")


if __name__ == "__main__":
    main()
