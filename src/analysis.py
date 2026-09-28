"""
analysis.py
===========
Options Market Intelligence — analisis pasar opsi dari data kontrak.

CATATAN DATA (penting & jujur):
  Dataset `scored_contracts.csv` hanya berisi **CALL** (469 kontrak, 41 ticker,
  2 expiry). Karena tidak ada PUT, metrik seperti Put/Call Ratio tidak dapat
  dihitung. Analisis difokuskan pada apa yang BENAR-BENAR tersedia:
    - Implied Volatility (IV) surface & skew per ticker/moneyness
    - Gamma Exposure (GEX) proxy dari Open Interest
    - Open-Interest walls (level strike dengan OI besar)
    - Likuiditas (bid-ask spread vs OI/volume)
    - Distribusi moneyness & premium
    - Skor kontrak (delta/vol_oi/gamma/composite) & peringkat

Fungsi di sini MURNI (kembalikan DataFrame), agar bisa dipakai notebook/dashboard.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "scored_contracts.csv"
PROC = ROOT / "data" / "processed"


# ---------------------------------------------------------------------------
def load() -> pd.DataFrame:
    """Muat & perkaya data kontrak."""
    df = pd.read_csv(RAW)
    df["expiry"] = pd.to_datetime(df["expiry"])
    df["lastTradeDate"] = pd.to_datetime(df["lastTradeDate"], errors="coerce",
                                         utc=True)
    # hari sampai expiry
    snap = df["lastTradeDate"].max()
    df["days_to_expiry"] = (df["expiry"] - snap.tz_localize(None)).dt.days.abs()
    # premium relatif underlying
    df["premium_pct"] = df["mid_price"] / df["underlying_price"] * 100
    # klasifikasi moneyness
    df["moneyness_bucket"] = pd.cut(
        df["moneyness"],
        bins=[0, 0.9, 0.97, 1.03, 1.1, np.inf],
        labels=["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"])
    # nilai dolar dari OI (proxy besar posisi)
    df["oi_notional"] = df["openInterest"] * df["mid_price"] * 100
    # gamma proxy: OI / (1 + |moneyness-1|) - OI dekat ATM paling berpengaruh
    df["gamma_proxy"] = df["openInterest"] / (1 + (df["moneyness"] - 1).abs() * 10)
    return df


# ---------------------------------------------------------------------------
# 1. IV SURFACE & SKEW
# ---------------------------------------------------------------------------
def iv_by_moneyness(df: pd.DataFrame) -> pd.DataFrame:
    """IV rata-rata per bucket moneyness (bentuk volatility smile per bucket)."""
    g = df[df["impliedVolatility"] > 0].groupby("moneyness_bucket",
                                                observed=True)
    return pd.DataFrame({
        "contracts": g.size(),
        "iv_mean": (g["impliedVolatility"].mean() * 100).round(1),
        "iv_median": (g["impliedVolatility"].median() * 100).round(1),
        "iv_std": (g["impliedVolatility"].std() * 100).round(1),
    })


def iv_skew_by_ticker(df: pd.DataFrame, min_contracts: int = 5) -> pd.DataFrame:
    """
    'IV skew' per ticker: IV rata-rata OTM (mahal) - IV rata-rata ITM (murah).
    Nilai positif = OTM lebih mahal (skew naik) = permintaan spekulatif tinggi.
    """
    d = df[df["impliedVolatility"] > 0]
    itm = d[d["moneyness_bucket"].isin(["ITM", "Deep ITM"])] \
        .groupby("ticker")["impliedVolatility"].mean()
    otm = d[d["moneyness_bucket"].isin(["OTM", "Deep OTM"])] \
        .groupby("ticker")["impliedVolatility"].mean()
    n = d.groupby("ticker").size()
    out = pd.DataFrame({"n": n, "iv_itm": (itm * 100).round(1),
                        "iv_otm": (otm * 100).round(1)}).dropna()
    out = out[out["n"] >= min_contracts]
    out["iv_skew_pct"] = (out["iv_otm"] - out["iv_itm"]).round(1)
    return out.sort_values("iv_skew_pct", ascending=False)


# ---------------------------------------------------------------------------
# 2. GAMMA EXPOSURE (GEX) & OPEN-INTEREST WALLS
# ---------------------------------------------------------------------------
def gex_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Proxy Gamma Exposure per ticker.
    GEX ~ sum( OI * mid_price * 100 ) tertimbang kedekatan ATM.
    (Model penuh butuh gamma Black-Scholes; ini proxy dari data tersedia.)
    """
    g = df.groupby("ticker")
    out = pd.DataFrame({
        "contracts": g.size(),
        "total_oi": g["openInterest"].sum(),
        "oi_notional_usd": g["oi_notional"].sum().round(0),
        "gamma_proxy_sum": g["gamma_proxy"].sum().round(0),
        "avg_iv_pct": (g["impliedVolatility"].mean() * 100).round(1),
    })
    out["gex_share_pct"] = (out["gamma_proxy_sum"] /
                            out["gamma_proxy_sum"].sum() * 100).round(2)
    return out.sort_values("gamma_proxy_sum", ascending=False)


def oi_walls(df: pd.DataFrame, ticker: str, top_n: int = 10) -> pd.DataFrame:
    """Strike dengan Open Interest terbesar ('walls') untuk 1 ticker."""
    d = df[df["ticker"] == ticker]
    g = d.groupby("strike")
    out = pd.DataFrame({
        "open_interest": g["openInterest"].sum(),
        "volume": g["volume"].sum(),
        "contracts": g.size(),
        "avg_iv_pct": (g["impliedVolatility"].mean() * 100).round(1),
        "avg_moneyness": g["moneyness"].mean().round(3),
    })
    out["oi_notional_usd"] = out["open_interest"] * out.index.astype(float) * 100
    return out.sort_values("open_interest", ascending=False).head(top_n)


def top_gex_strikes(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Strike dengan gamma proxy tertinggi lintas ticker (level kunci pasar)."""
    return df.nlargest(top_n, "gamma_proxy")[
        ["ticker", "strike", "moneyness", "openInterest", "mid_price",
         "impliedVolatility", "gamma_proxy"]].round(3)


# ---------------------------------------------------------------------------
# 3. LIKUIDITAS
# ---------------------------------------------------------------------------
def liquidity_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """Metrik likuiditas per ticker."""
    g = df.groupby("ticker")
    out = pd.DataFrame({
        "contracts": g.size(),
        "median_spread_pct": (g["spread_pct"].median() * 100).round(2),
        "median_oi": g["openInterest"].median().round(0),
        "total_volume": g["volume"].sum().round(0),
        "median_price": g["mid_price"].median().round(2),
    })
    out["vol_per_oi"] = (out["total_volume"] /
                         out["median_oi"].replace(0, np.nan)).round(2)
    return out.sort_values("median_spread_pct")


def spread_quality(df: pd.DataFrame) -> pd.Series:
    """Distribusi kualitas spread (tighter = lebih baik)."""
    sp = df["spread_pct"] * 100
    return pd.Series({
        "tight (<1%)": int((sp < 1).sum()),
        "ok (1-3%)": int(((sp >= 1) & (sp < 3)).sum()),
        "wide (3-8%)": int(((sp >= 3) & (sp < 8)).sum()),
        "very wide (>8%)": int((sp >= 8).sum()),
    })


# ---------------------------------------------------------------------------
# 4. DISTRIBUSI & SKOR
# ---------------------------------------------------------------------------
def moneyness_dist(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("moneyness_bucket", observed=True)
    return pd.DataFrame({
        "contracts": g.size(),
        "pct": (g.size() / len(df) * 100).round(1),
        "avg_premium": g["mid_price"].mean().round(2),
        "avg_iv_pct": (g["impliedVolatility"].mean() * 100).round(1),
        "total_oi": g["openInterest"].sum(),
    })


def score_decomposition(df: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata komponen skor per bucket moneyness (jelaskan apa yang dinilai)."""
    g = df.groupby("moneyness_bucket", observed=True)
    return pd.DataFrame({
        "contracts": g.size(),
        "delta_score": g["delta_score"].mean().round(1),
        "vol_oi_score": g["vol_oi_score"].mean().round(1),
        "gamma_score": g["gamma_score"].mean().round(1),
        "liquidity_bonus": g["liquidity_bonus"].mean().round(1),
        "composite": g["composite_score"].mean().round(1),
    })


def top_contracts(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    cols = ["ticker", "strike", "moneyness", "mid_price", "impliedVolatility",
            "volume", "openInterest", "spread_pct", "delta_score",
            "vol_oi_score", "gamma_score", "composite_score"]
    out = df.nlargest(n, "composite_score")[cols].copy()
    out["impliedVolatility"] = (out["impliedVolatility"] * 100).round(1)
    out["spread_pct"] = (out["spread_pct"] * 100).round(2)
    return out


def key_insights(df: pd.DataFrame) -> dict:
    """Insight ringkas untuk laporan."""
    d = df
    return {
        "contracts": int(len(d)),
        "tickers": int(d["ticker"].nunique()),
        "expiries": int(d["expiry"].nunique()),
        "call_pct": round((d["option_type"] == "CALL").mean() * 100, 1),
        "itm_pct": round(d["inTheMoney"].mean() * 100, 1),
        "median_iv_pct": round(d.loc[d["impliedVolatility"] > 0,
                                    "impliedVolatility"].median() * 100, 1),
        "median_spread_pct": round(d["spread_pct"].median() * 100, 2),
        "total_oi": int(d["openInterest"].sum()),
        "total_volume": int(d["volume"].sum()),
        "top_iv_ticker": d.groupby("ticker")["impliedVolatility"].mean().idxmax(),
        "top_oi_ticker": d.groupby("ticker")["openInterest"].sum().idxmax(),
        "top_gex_strike": f"{d.loc[d['gamma_proxy'].idxmax(),'ticker']} "
                          f"${d.loc[d['gamma_proxy'].idxmax(),'strike']:.0f}",
    }


if __name__ == "__main__":
    df = load()
    print("=" * 68)
    print("OPTIONS MARKET INTELLIGENCE — SNAPSHOT")
    print("=" * 68)
    ins = key_insights(df)
    for k, v in ins.items():
        print(f"  {k:20}: {v}")
    print("\n[IV by moneyness]")
    print(iv_by_moneyness(df).to_string())
    print("\n[Top IV skew tickers]")
    print(iv_skew_by_ticker(df).head(8).to_string())
    print("\n[Top GEX tickers]")
    print(gex_by_ticker(df).head(8).to_string())
