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
RAW = ROOT / "data" / "raw" / "options_full.csv"
RAW_FALLBACK = ROOT / "data" / "raw" / "scored_contracts.csv"
PROC = ROOT / "data" / "processed"


# ---------------------------------------------------------------------------
def load() -> pd.DataFrame:
    """Muat & perkaya data kontrak (CALL+PUT bila tersedia, else CALL-only)."""
    path = RAW if RAW.exists() else RAW_FALLBACK
    df = pd.read_csv(path)
    # normalisasi kolom dari dua skema
    if "option_type" not in df.columns:
        df["option_type"] = "CALL"
    if "expiry" in df.columns:
        df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce")
    df["lastTradeDate"] = pd.to_datetime(df["lastTradeDate"], errors="coerce",
                                         utc=True)
    if "underlying_price" in df.columns and "moneyness" not in df.columns:
        df["moneyness"] = df["strike"] / df["underlying_price"]
    if "mid_price" not in df.columns:
        df["mid_price"] = (df["bid"].fillna(0) + df["ask"].fillna(0)) / 2
    if "spread_pct" not in df.columns:
        df["spread_pct"] = (df["ask"] - df["bid"]) / df["mid_price"].replace(0, np.nan)
    # kolom turunan
    df["moneyness_bucket"] = pd.cut(
        df["moneyness"],
        bins=[0, 0.9, 0.97, 1.03, 1.1, np.inf],
        labels=["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"])
    df["oi_notional"] = df["openInterest"] * df["mid_price"] * 100
    df["gamma_proxy"] = df["openInterest"] / (1 + (df["moneyness"] - 1).abs() * 10)
    return df


# ---------------------------------------------------------------------------
# 1. IV SURFACE & SKEW
# ---------------------------------------------------------------------------
def iv_by_moneyness(df: pd.DataFrame) -> pd.DataFrame:
    """IV rata-rata per bucket moneyness (bentuk volatility smile per bucket)."""
    g = df[(df["impliedVolatility"] > 0.01) & (df["bid"] > 0) &
           (df["ask"] > 0)].groupby("moneyness_bucket", observed=True)
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
    """Rata-rata komponen skor per bucket moneyness.

    Komponen skor hanya ada di dataset scanner lama (scored_contracts);
    pada dataset yfinance terbaru kolom ini tidak ada -> kembalikan tabel
    kosong agar pipeline tetap jalan (bukan crash).
    """
    score_cols = ["delta_score", "vol_oi_score", "gamma_score",
                  "liquidity_bonus", "composite_score"]
    if not any(c in df.columns for c in score_cols):
        return pd.DataFrame(columns=["contracts"] + score_cols)
    g = df.groupby("moneyness_bucket", observed=True)
    out = {"contracts": g.size()}
    for c in score_cols:
        if c in df.columns:
            out[c] = g[c].mean().round(1)
    return pd.DataFrame(out)


def top_contracts(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Kontrak teratas. Bila ada composite_score pakai itu, jika tidak
    pakai volume terbesar (berlaku untuk dataset baru)."""
    if "composite_score" in df.columns:
        cols = ["ticker", "strike", "moneyness", "mid_price", "impliedVolatility",
                "volume", "openInterest", "spread_pct", "delta_score",
                "vol_oi_score", "gamma_score", "composite_score"]
        cols = [c for c in cols if c in df.columns]
        out = df.nlargest(n, "composite_score")[cols].copy()
    else:
        cols = ["ticker", "option_type", "strike", "moneyness", "mid_price",
                "impliedVolatility", "volume", "openInterest", "spread_pct"]
        cols = [c for c in cols if c in df.columns]
        out = df.nlargest(n, "volume")[cols].copy()
    if "impliedVolatility" in out.columns:
        out["impliedVolatility"] = (out["impliedVolatility"] * 100).round(1)
    if "spread_pct" in out.columns:
        out["spread_pct"] = (out["spread_pct"] * 100).round(2)
    return out


def key_insights(df: pd.DataFrame) -> dict:
    """Insight ringkas untuk laporan."""
    d = df
    has_put = (d["option_type"] == "PUT").sum() > 0
    out = {
        "contracts": int(len(d)),
        "tickers": int(d["ticker"].nunique()),
        "calls": int((d["option_type"] == "CALL").sum()),
        "puts": int((d["option_type"] == "PUT").sum()),
        "itm_pct": round(d["inTheMoney"].mean() * 100, 1),
        "median_iv_pct": round(d.loc[d["impliedVolatility"] > 0,
                                    "impliedVolatility"].median() * 100, 1),
        "median_spread_pct": round(d["spread_pct"].median() * 100, 2),
        "total_oi": int(d["openInterest"].sum()),
        "total_volume": int(d["volume"].fillna(0).sum()),
        "top_oi_ticker": d.groupby("ticker")["openInterest"].sum().idxmax(),
        "top_gex_strike": f"{d.loc[d['gamma_proxy'].idxmax(),'ticker']} "
                          f"${d.loc[d['gamma_proxy'].idxmax(),'strike']:.0f}",
    }
    if has_put:
        out.update(overall_pcr(d))
    return out


# ---------------------------------------------------------------------------
# 5. PUT/CALL RATIO (kini tersedia — dataset lengkap CALL + PUT)
# ---------------------------------------------------------------------------
def put_call_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Put/Call Ratio per ticker.

    PENTING (keterbatasan data yfinance realtime): `openInterest` sering 0
    (Yahoo tidak mengirim OI untuk mayoritas kontrak), sehingga PCR berbasis OI
    TIDAK reliabel. Karena itu PCR di sini memakai **VOLUME** (yang lengkap).

    Interpretasi umum:
      PCR > 1  -> aktivitas put lebih besar (bearish / hedging)
      PCR < 1  -> aktivitas call lebih besar (bullish / spekulasi)
    """
    d = df[df["option_type"].isin(["CALL", "PUT"])].copy()
    d["volume"] = d["volume"].fillna(0)
    rows = []
    for tk, g in d.groupby("ticker"):
        cv = g.loc[g["option_type"] == "CALL", "volume"].sum()
        pv = g.loc[g["option_type"] == "PUT", "volume"].sum()
        co = g.loc[g["option_type"] == "CALL", "openInterest"].sum()
        po = g.loc[g["option_type"] == "PUT", "openInterest"].sum()
        rows.append({
            "ticker": tk,
            "call_volume": int(cv), "put_volume": int(pv),
            "pcr_volume": round(pv / cv, 3) if cv else np.nan,
            "call_oi": int(co), "put_oi": int(po),
            "pcr_oi": round(po / co, 3) if co else np.nan,
        })
    out = pd.DataFrame(rows)
    out["sentiment"] = np.where(
        out["pcr_volume"] > 1.2, "Bearish/Hedged",
        np.where(out["pcr_volume"] < 0.8, "Bullish", "Neutral"))
    return out.sort_values("pcr_volume", ascending=False)


def overall_pcr(df: pd.DataFrame) -> dict:
    """PCR agregat (volume-based, valid; OI dilaporkan terpisah apa adanya)."""
    d = df.copy()
    d["volume"] = d["volume"].fillna(0)
    cv = d.loc[d["option_type"] == "CALL", "volume"].sum()
    pv = d.loc[d["option_type"] == "PUT", "volume"].sum()
    co = d.loc[d["option_type"] == "CALL", "openInterest"].sum()
    po = d.loc[d["option_type"] == "PUT", "openInterest"].sum()
    return {
        "pcr_volume": round(pv / cv, 3) if cv else None,
        "pcr_oi": round(po / co, 3) if co else None,
        "call_volume": int(cv), "put_volume": int(pv),
        "call_oi": int(co), "put_oi": int(po),
    }


def iv_skew_both_sides(df: pd.DataFrame, min_n: int = 4) -> pd.DataFrame:
    """
    Skew dua sisi: IV rata-rata PUT - IV rata-rata CALL pada moneyness setara.
    Positif = put lebih mahal (permintaan lindung nilai / takut turun).
    """
    d = df[df["impliedVolatility"] > 0]
    g = d.groupby(["ticker", "option_type"])["impliedVolatility"].mean().unstack()
    n = d.groupby(["ticker", "option_type"]).size().unstack().fillna(0)
    out = g.copy()
    out.columns = [f"iv_{c.lower()}" for c in out.columns]
    for c in ["iv_call", "iv_put"]:
        if c not in out.columns:
            out[c] = np.nan
    out["n_call"] = n.get("CALL", 0)
    out["n_put"] = n.get("PUT", 0)
    out = out[(out["n_call"] >= min_n) & (out["n_put"] >= min_n)]
    out["put_minus_call_iv"] = ((out["iv_put"] - out["iv_call"]) * 100).round(1)
    return out[["n_call", "n_put", "iv_call", "iv_put", "put_minus_call_iv"]] \
        .sort_values("put_minus_call_iv", ascending=False)


def put_walls(df: pd.DataFrame, ticker: str, top_n: int = 8) -> pd.DataFrame:
    """Strike PUT dengan OI terbesar (kandidat level SUPPORT)."""
    d = df[(df["ticker"] == ticker) & (df["option_type"] == "PUT")]
    g = d.groupby("strike")
    out = pd.DataFrame({
        "put_oi": g["openInterest"].sum(),
        "put_volume": g["volume"].sum(),
        "iv_pct": (g["impliedVolatility"].mean() * 100).round(1),
        "moneyness": g["moneyness"].mean().round(3),
    })
    return out.sort_values("put_oi", ascending=False).head(top_n)


def call_walls(df: pd.DataFrame, ticker: str, top_n: int = 8) -> pd.DataFrame:
    """Strike CALL dengan OI terbesar (kandidat level RESISTANCE)."""
    d = df[(df["ticker"] == ticker) & (df["option_type"] == "CALL")]
    g = d.groupby("strike")
    out = pd.DataFrame({
        "call_oi": g["openInterest"].sum(),
        "call_volume": g["volume"].sum(),
        "iv_pct": (g["impliedVolatility"].mean() * 100).round(1),
        "moneyness": g["moneyness"].mean().round(3),
    })
    return out.sort_values("call_oi", ascending=False).head(top_n)


def iv_by_moneyness_side(df: pd.DataFrame) -> pd.DataFrame:
    """IV smile TERPISAH untuk CALL & PUT (melihat skew dua-sisi)."""
    d = df[(df["impliedVolatility"] > 0.01) & (df["bid"] > 0) &
           (df["ask"] > 0) & df["moneyness_bucket"].notna()]
    g = d.groupby(["moneyness_bucket", "option_type"], observed=True)["impliedVolatility"]
    out = (g.mean() * 100).round(1).unstack()
    out["n"] = d.groupby("moneyness_bucket", observed=True).size()
    return out


# ---------------------------------------------------------------------------
# 6. EXPORT
# ---------------------------------------------------------------------------
def save_table(df: pd.DataFrame, name: str) -> Path:
    out = ROOT / "reports" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    fp = out / f"{name}.csv"
    df.to_csv(fp, index=False)
    return fp


if __name__ == "__main__":
    df = load()
    print("=" * 68)
    print("OPTIONS MARKET INTELLIGENCE — CALL + PUT")
    print("=" * 68)
    ins = key_insights(df)
    for k, v in ins.items():
        print(f"  {k:20}: {v}")
    print("\n[Put/Call Ratio - aggregate]")
    print(overall_pcr(df))
    print("\n[Put/Call Ratio by ticker - top/bottom]")
    pcr = put_call_ratio(df)
    print(pcr.head(6).to_string(index=False))
    print("...")
    print(pcr.tail(4).to_string(index=False))
    print("\n[IV smile by side]")
    print(iv_by_moneyness_side(df).to_string())
