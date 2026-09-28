"""
collect_options.py — Ambil data opsi LENGKAP (CALL + PUT) dari yfinance.

TUJUAN: melengkapi dataset lama (yang hanya CALL) dengan PUT nyata, sehingga
Put/Call Ratio & analisis skew dua-sisi dapat dihitung.

Sumber: yfinance (Yahoo Finance) — data opsi publik, gratis.
Output: data/raw/options_full.csv (CALL + PUT)

Jalankan: python src/collect_options.py [n_tickers]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# Ticker (samakan dengan dataset lama + beberapa tambahan)
TICKERS = [
    "AAPL", "AMD", "AMZN", "AVGO", "BAC", "COST", "CRM", "CVX", "DIA", "GLD",
    "GOOGL", "HD", "HYG", "INTC", "IWM", "JPM", "KO", "LLY", "META", "MRK",
    "MSFT", "MU", "NFLX", "NVDA", "ORCL", "PLTR", "PYPL", "QCOM", "QQQ", "RIVN",
    "SLV", "SNAP", "SOFI", "SPY", "TLT", "TSLA", "UBER", "UNH", "V", "WMT", "XOM",
]


def main(n_tickers: int | None = None):
    import yfinance as yf

    tickers = TICKERS[:n_tickers] if n_tickers else TICKERS
    rows = []
    ok = 0
    for tk in tickers:
        try:
            t = yf.Ticker(tk)
            exps = t.options
            if not exps:
                print(f"  {tk}: tidak ada expiry")
                continue
            # ambil expiry terdekat (paling likuid)
            exp = exps[0]
            chain = t.option_chain(exp)
            # harga underlying
            try:
                spot = float(t.fast_info.get("lastPrice") or t.history(period="1d")["Close"].iloc[-1])
            except Exception:
                spot = None

            for kind, df in [("CALL", chain.calls), ("PUT", chain.puts)]:
                for r in df.itertuples(index=False):
                    d = r._asdict() if hasattr(r, "_asdict") else dict(zip(df.columns, r))
                    strike = d.get("strike")
                    rows.append({
                        "contractSymbol": d.get("contractSymbol"),
                        "lastTradeDate": d.get("lastTradeDate"),
                        "strike": strike,
                        "lastPrice": d.get("lastPrice"),
                        "bid": d.get("bid"),
                        "ask": d.get("ask"),
                        "change": d.get("change"),
                        "percentChange": d.get("percentChange"),
                        "volume": d.get("volume"),
                        "openInterest": d.get("openInterest"),
                        "impliedVolatility": d.get("impliedVolatility"),
                        "inTheMoney": d.get("inTheMoney"),
                        "contractSize": d.get("contractSize"),
                        "currency": d.get("currency"),
                        "ticker": tk,
                        "expiry": exp,
                        "option_type": kind,
                        "underlying_price": spot,
                    })
            ok += 1
            print(f"  {tk}: {exp}  calls={len(chain.calls)} puts={len(chain.puts)}")
            time.sleep(0.8)
        except Exception as e:
            print(f"  {tk}: ERR {str(e)[:80]}")

    df = pd.DataFrame(rows)
    if df.empty:
        print("TIDAK ADA DATA")
        return df

    # kolom turunan
    df["mid_price"] = (df["bid"].fillna(0) + df["ask"].fillna(0)) / 2
    df["moneyness"] = df["strike"] / df["underlying_price"]
    df["spread_pct"] = (df["ask"] - df["bid"]) / df["mid_price"].replace(0, pd.NA)
    df["oi_notional"] = df["openInterest"] * df["mid_price"] * 100

    out = RAW / "options_full.csv"
    df.to_csv(out, index=False)
    print(f"\n[OK] {len(df)} kontrak dari {ok} ticker -> {out}")
    print(f"  CALL: {(df['option_type']=='CALL').sum()} | "
          f"PUT: {(df['option_type']=='PUT').sum()}")
    return df


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(n)
