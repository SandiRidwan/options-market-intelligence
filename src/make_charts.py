"""make_charts.py — visualisasi Options Market Intelligence."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analysis as A

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

C = {"p": "#1F5C3D", "a": "#E4A11B", "d": "#1B2A33", "g": "#8B9AA6",
     "r": "#C0392B", "b": "#2E6F95", "purple": "#6A4C93"}

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#CCCCCC", "axes.grid": True, "grid.color": "#EEEEEE",
    "figure.facecolor": "white",
})


def _save(fig, name):
    fp = FIG / f"{name}.png"
    fig.tight_layout(); fig.savefig(fp, bbox_inches="tight"); plt.close(fig)
    print(f"  [fig] {fp.name}")


def chart_iv_smile(df):
    t = A.iv_by_moneyness(df)
    t = t[t.index.isin(["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"])]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(t))
    ax.plot(x, t["iv_mean"], "o-", color=C["r"], lw=2.5, ms=9,
            label="mean IV")
    ax.plot(x, t["iv_median"], "s--", color=C["b"], lw=1.8, ms=7,
            label="median IV")
    ax.fill_between(x, t["iv_mean"] - t["iv_std"]/2, t["iv_mean"] + t["iv_std"]/2,
                    color=C["r"], alpha=0.12)
    for i, (m, n) in enumerate(zip(t["iv_mean"], t["contracts"])):
        ax.text(i, m + 3, f"{m:.0f}%\n(n={n})", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(t.index)
    ax.set_xlabel("Moneyness"); ax.set_ylabel("Implied Volatility (%)")
    ax.set_title("Implied Volatility Smile / Skew\n(IV terendah di ATM, naik ke kedua sayap)")
    ax.legend(frameon=False)
    _save(fig, "01_iv_smile")


def chart_iv_skew_tickers(df):
    t = A.iv_skew_by_ticker(df).head(12).sort_values("iv_skew_pct")
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [C["r"] if v > 0 else C["p"] for v in t["iv_skew_pct"]]
    bars = ax.barh(t.index, t["iv_skew_pct"], color=colors, zorder=3)
    for b, v in zip(bars, t["iv_skew_pct"]):
        ax.text(v + (0.6 if v > 0 else -0.6), b.get_y() + b.get_height()/2,
                f"{v:+.0f}pp", va="center", ha="left" if v > 0 else "right",
                fontsize=8, color=C["d"])
    ax.axvline(0, color=C["d"], lw=1)
    ax.set_xlabel("IV skew (OTM − ITM), percentage points")
    ax.set_title("IV Skew by Ticker\n(positif = OTM lebih mahal / spekulasi tinggi)")
    ax.grid(axis="y", visible=False)
    _save(fig, "02_iv_skew")


def chart_gex(df):
    t = A.gex_by_ticker(df).head(15).sort_values("gamma_proxy_sum")
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(t.index, t["gex_share_pct"], color=C["purple"], zorder=3)
    for b, v, oi in zip(bars, t["gex_share_pct"], t["total_oi"]):
        ax.text(v + 0.08, b.get_y() + b.get_height()/2,
                f"{v:.1f}%  (OI {oi:,})", va="center", fontsize=7.5,
                color=C["d"])
    ax.set_xlabel("Share of total gamma exposure (%)")
    ax.set_title("Gamma Exposure (GEX) by Ticker\ntop-15 by gamma proxy from open interest")
    ax.set_xlim(0, t["gex_share_pct"].max() * 1.35)
    ax.grid(axis="y", visible=False)
    _save(fig, "03_gex")


def chart_oi_walls(df, ticker="SPY"):
    t = A.oi_walls(df, ticker, 12).sort_values("open_interest")
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh([f"${s:,.0f}" for s in t.index], t["open_interest"],
                   color=C["b"], zorder=3)
    for b, v, m in zip(bars, t["open_interest"], t["avg_moneyness"]):
        ax.text(v + t["open_interest"].max()*0.01,
                b.get_y() + b.get_height()/2,
                f"{v:,}  (m={m:.2f})", va="center", fontsize=7.5, color=C["d"])
    ax.set_xlabel("Open Interest (contracts)")
    ax.set_title(f"Open-Interest Walls — {ticker}\n(strikes with largest OI)")
    ax.set_xlim(0, t["open_interest"].max()*1.3)
    ax.grid(axis="y", visible=False)
    _save(fig, "04_oi_walls")


def chart_liquidity(df):
    t = A.liquidity_by_ticker(df)
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(t["median_oi"].clip(lower=1), t["median_spread_pct"],
                    s=t["contracts"]*6, c=t["total_volume"],
                    cmap="viridis", alpha=0.75, edgecolor="white")
    fig.colorbar(sc, ax=ax, label="total volume")
    for tk, r in t.iterrows():
        ax.annotate(tk, (max(r["median_oi"], 1), r["median_spread_pct"]),
                    fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("Median Open Interest (log)")
    ax.set_ylabel("Median bid-ask spread (%)")
    ax.set_title("Liquidity Map\n(bawah-kiri = likuid & murah; ukuran = jumlah kontrak)")
    _save(fig, "05_liquidity")


def chart_moneyness_dist(df):
    t = A.moneyness_dist(df)
    order = ["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"]
    t = t.reindex([o for o in order if o in t.index])
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].pie(t["contracts"], labels=t.index, autopct="%1.1f%%",
                colors=[C["p"], C["b"], C["a"], C["r"], C["purple"]],
                startangle=90, textprops={"fontsize": 8},
                wedgeprops={"edgecolor": "white"})
    axes[0].set_title("Contracts by Moneyness")
    axes[1].bar(t.index, t["avg_premium"], color=C["p"], zorder=3)
    for i, v in enumerate(t["avg_premium"]):
        axes[1].text(i, v + 0.5, f"${v:.2f}", ha="center", fontsize=8)
    axes[1].set_ylabel("Avg premium ($)")
    axes[1].set_title("Average Premium by Moneyness")
    axes[1].tick_params(axis="x", labelrotation=20)
    axes[1].grid(axis="x", visible=False)
    fig.suptitle("Moneyness Distribution", fontsize=13, fontweight="bold")
    _save(fig, "06_moneyness")


def chart_score_components(df):
    t = A.score_decomposition(df)
    order = ["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"]
    t = t.reindex([o for o in order if o in t.index])
    fig, ax = plt.subplots(figsize=(9, 5.5))
    comps = ["delta_score", "vol_oi_score", "gamma_score", "liquidity_bonus"]
    x = np.arange(len(t)); w = 0.2
    for i, c in enumerate(comps):
        ax.bar(x + i*w - 1.5*w, t[c], width=w, label=c.replace("_", " "), zorder=3)
    ax.plot(x, t["composite"], "o-", color=C["d"], lw=2, ms=8,
            label="composite", zorder=4)
    ax.set_xticks(x); ax.set_xticklabels(t.index)
    ax.set_ylabel("Average score")
    ax.set_title("Score Decomposition by Moneyness\n(apa yang dinilai sistem per bucket)")
    ax.legend(frameon=False, fontsize=8, ncols=2)
    ax.grid(axis="x", visible=False)
    _save(fig, "07_score_components")


def chart_top_contracts(df):
    t = A.top_contracts(df, 15).sort_values("composite_score")
    fig, ax = plt.subplots(figsize=(9.5, 7))
    labels = [f"{r.ticker} ${r.strike:,.0f}  (IV {r.impliedVolatility:.0f}%)"
              for r in t.itertuples()]
    bars = ax.barh(labels, t["composite_score"], color=C["a"], zorder=3)
    for b, v in zip(bars, t["composite_score"]):
        ax.text(v + 0.4, b.get_y() + b.get_height()/2, f"{v:.1f}",
                va="center", fontsize=8, color=C["d"])
    ax.set_xlabel("Composite score (0–110)")
    ax.set_xlim(0, 115)
    ax.set_title("Top 15 Contracts by Composite Score")
    ax.grid(axis="y", visible=False)
    _save(fig, "08_top_contracts")


def build_all():
    df = A.load()
    print("Membuat visualisasi...")
    chart_iv_smile(df)
    chart_iv_skew_tickers(df)
    chart_gex(df)
    top_oi = df.groupby("ticker")["openInterest"].sum().idxmax()
    chart_oi_walls(df, top_oi)
    chart_liquidity(df)
    chart_moneyness_dist(df)
    chart_score_components(df)
    chart_top_contracts(df)
    print(f"[OK] {FIG}")


if __name__ == "__main__":
    build_all()
