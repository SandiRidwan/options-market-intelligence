"""
Options Market Intelligence — Interactive Dashboard (Streamlit)
===============================================================
Analisis pasar opsi dari data scan 41 ticker (469 kontrak CALL).

Konsep kunci:
  · Implied Volatility (IV) smile/skew
  · Gamma Exposure (GEX) & open-interest walls
  · Likuiditas & kualitas spread
  · Distribusi moneyness & skor kontrak

Jalankan: streamlit run app/dashboard.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import analysis as A  # noqa: E402
import explanations as X  # noqa: E402

C = {"p": "#1F5C3D", "a": "#E4A11B", "d": "#1B2A33", "g": "#8B9AA6",
     "r": "#C0392B", "b": "#2E6F95", "purple": "#6A4C93"}
SEQ = ["#1F5C3D", "#2E6F95", "#E4A11B", "#C0392B", "#6A4C93"]

st.set_page_config(page_title="Options Market Intelligence", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data(show_spinner="Memuat data opsi...")
def load():
    return A.load()


def style(fig, h=430):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=54, b=10),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#D5DBE1"),
                      title=dict(font=dict(size=16, color="#fff")),
                      legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#2A3038", zeroline=False)
    fig.update_yaxes(gridcolor="#2A3038", zeroline=False)
    return fig


def kpi(col, label, value, sub, color):
    col.markdown(
        f"""<div style="background:#1A1F2B;border-left:4px solid {color};
        padding:14px 16px;border-radius:10px;height:112px;">
        <div style="color:#9AA7B4;font-size:.76rem;text-transform:uppercase;
        letter-spacing:.06em;">{label}</div>
        <div style="color:{color};font-size:1.7rem;font-weight:700;
        margin-top:6px;">{value}</div>
        <div style="color:#6B7885;font-size:.75rem;">{sub}</div></div>""",
        unsafe_allow_html=True)


df = load()
ins = A.key_insights(df)


def exp(key, before=True):
    """Tampilkan kotak 'Kenapa/Tujuan/Dampak' untuk sebuah elemen."""
    X.render(key, st=st)

st.sidebar.markdown("### 🎛️ Filters")
tickers = sorted(df["ticker"].unique())
sel_t = st.sidebar.multiselect("Tickers", tickers, default=tickers[:10])
types = sorted(df["moneyness_bucket"].dropna().unique())
sel_m = st.sidebar.multiselect("Moneyness", types, default=types)
st.sidebar.markdown("---")
st.sidebar.caption("Sumber: yfinance · 41 ticker · CALL + PUT lengkap. "
                   "⚠️ Open interest dari Yahoo sering 0 → PCR berbasis VOLUME.")

st.markdown(
    f"""<div style="background:linear-gradient(100deg,{C['p']},{C['purple']});
    padding:22px 26px;border-radius:14px;margin-bottom:18px;">
    <div style="font-size:1.7rem;font-weight:800;color:white;">
    📈 Options Market Intelligence</div>
    <div style="color:#D7E4DC;font-size:.9rem;margin-top:4px;">
    IV smile · Gamma exposure · OI walls · Liquidity ·
    by <b>Sandi Ridwan</b></div></div>""",
    unsafe_allow_html=True)

d = df.copy()
if sel_t:
    d = d[d["ticker"].isin(sel_t)]
if sel_m:
    d = d[d["moneyness_bucket"].isin(sel_m)]

k1, k2, k3, k4, k5 = st.columns(5)
kpi(k1, "Contracts", f"{len(d):,}", f"{d['ticker'].nunique()} tickers", C["p"])
kpi(k2, "Median IV", f"{d.loc[d['impliedVolatility']>0,'impliedVolatility'].median()*100:.1f}%",
    "implied volatility", C["r"])
kpi(k3, "ITM share", f"{d['inTheMoney'].mean()*100:.0f}%", "in-the-money", C["b"])
kpi(k4, "Median spread", f"{d['spread_pct'].median()*100:.2f}%", "bid-ask", C["a"])
pcr = A.overall_pcr(d)
kpi(k5, "Put/Call Ratio", f"{pcr.get('pcr_volume') or 0:.2f}",
    "volume-based · <1 bullish", C["purple"])
st.write("")

t1, t2, t3, t4, t5 = st.tabs(["📊 Volatility", "⚖️ Put/Call", "⚡ Gamma & OI",
                              "💧 Liquidity", "🎯 Contracts"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        X.render("iv_smile", st=st)
        t = A.iv_by_moneyness(d)
        order = ["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"]
        t = t.reindex([o for o in order if o in t.index])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(t.index), y=t["iv_mean"], mode="lines+markers",
                                 name="mean IV", line=dict(color=C["r"], width=2.5)))
        fig.add_trace(go.Scatter(x=list(t.index), y=t["iv_median"], mode="lines+markers",
                                 name="median IV", line=dict(color=C["b"], width=2, dash="dash")))
        style(fig).update_layout(title="IV Smile / Skew by Moneyness",
                                 yaxis_title="IV (%)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        X.render("iv_skew", st=st)
        t = A.iv_skew_by_ticker(d).head(12).sort_values("iv_skew_pct")
        fig = px.bar(x=t["iv_skew_pct"], y=t.index, orientation="h",
                     color=t["iv_skew_pct"], color_continuous_scale="RdYlGn",
                     labels={"x": "IV skew (OTM−ITM, pp)", "y": ""})
        style(fig, 480).update_layout(coloraxis_showscale=False,
                                      title="IV Skew by Ticker")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Distribusi moneyness & premium")
    X.render("moneyness", st=st)
    md = A.moneyness_dist(d)
    fig = px.bar(md.reset_index(), x="moneyness_bucket", y="avg_premium",
                 color="moneyness_bucket", color_discrete_sequence=SEQ,
                 text="contracts")
    fig.update_traces(texttemplate="n=%{text}", textposition="outside")
    style(fig, 380).update_layout(showlegend=False,
                                  title="Average premium by moneyness",
                                  yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.markdown("#### Put/Call Ratio by ticker")
    st.caption("PCR volume-based: <0.8 bullish · 0.8–1.2 neutral · >1.2 bearish/hedged")
    X.render("pcr", st=st)
    pcrdf = A.put_call_ratio(d).dropna(subset=["pcr_volume"])
    fig = px.bar(pcrdf.sort_values("pcr_volume"), x="pcr_volume", y="ticker",
                 orientation="h", color="pcr_volume",
                 color_continuous_scale="RdYlGn_r", text="pcr_volume")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.add_vline(x=1.0, line_dash="dash", line_color="#9AA7B4")
    style(fig, 620).update_layout(coloraxis_showscale=False,
                                  title="Put/Call Ratio (volume)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pcrdf, use_container_width=True, hide_index=True)

    st.markdown("#### IV Smile — CALL vs PUT")
    X.render("iv_both_sides", st=st)
    t = A.iv_by_moneyness_side(d)
    order = ["Deep ITM", "ITM", "ATM", "OTM", "Deep OTM"]
    t = t.reindex([o for o in order if o in t.index]).reset_index()
    fig = px.bar(t, x="moneyness_bucket", y=["CALL", "PUT"], barmode="group",
                 color_discrete_map={"CALL": C["b"], "PUT": C["r"]},
                 labels={"value": "IV (%)", "moneyness_bucket": "", "variable": ""})
    style(fig, 400).update_layout(title="IV Smile: CALL vs PUT (put wing lebih tinggi = hedging mahal)")
    st.plotly_chart(fig, use_container_width=True)

with t3:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        X.render("gex", st=st)
        t = A.gex_by_ticker(d).head(15).sort_values("gex_share_pct")
        fig = px.bar(x=t["gex_share_pct"], y=t.index, orientation="h",
                     color=t["gex_share_pct"], color_continuous_scale="Purples",
                     labels={"x": "GEX share (%)", "y": ""})
        style(fig, 520).update_layout(coloraxis_showscale=False,
                                      title="Gamma Exposure by Ticker")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("##### Top GEX strikes")
        st.dataframe(A.top_gex_strikes(d, 12), use_container_width=True,
                     hide_index=True)
    st.markdown("#### Open-Interest walls")
    tk = st.selectbox("Ticker", sorted(d["ticker"].unique()),
                      index=0)
    X.render("oi_walls", st=st)
    walls = A.oi_walls(d, tk, 12).reset_index().sort_values("open_interest")
    fig = px.bar(walls, x="open_interest", y=walls["strike"].astype(int).astype(str),
                 orientation="h", color="open_interest",
                 color_continuous_scale="Blues",
                 labels={"open_interest": "Open Interest", "y": "Strike"})
    style(fig, 420).update_layout(coloraxis_showscale=False,
                                  title=f"OI Walls — {tk}")
    st.plotly_chart(fig, use_container_width=True)

with t4:
    c1, c2 = st.columns(2)
    with c1:
        X.render("liquidity", st=st)
        t = A.liquidity_by_ticker(d)
        fig = px.scatter(t.reset_index(), x="median_oi", y="median_spread_pct",
                         size="contracts", color="total_volume",
                         color_continuous_scale="Viridis", hover_name="ticker",
                         labels={"median_oi": "Median OI", "median_spread_pct": "Median spread (%)"},
                         log_x=True)
        style(fig, 480).update_layout(title="Liquidity Map (log OI)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        X.render("spread_quality", st=st)
        sq = A.spread_quality(d).reset_index()
        sq.columns = ["quality", "contracts"]
        fig = px.bar(sq, x="quality", y="contracts", color="quality",
                     color_discrete_sequence=SEQ, text="contracts")
        fig.update_traces(textposition="outside")
        style(fig, 480).update_layout(showlegend=False,
                                      title="Bid-ask spread quality")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Top likuid (spread tersempit)")
    st.dataframe(A.liquidity_by_ticker(d).head(12), use_container_width=True)

with t5:
    X.render("totals", st=st)
    st.dataframe(A.top_contracts(d, 20), use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        X.render("vol_by_moneyness", st=st)
        dd = d.copy()
        dd["volume"] = pd.to_numeric(dd["volume"], errors="coerce").fillna(0)
        g = dd.groupby("moneyness_bucket", observed=True).agg(
            contracts=("volume", "size"), total_volume=("volume", "sum")).reset_index()
        fig = px.bar(g, x="moneyness_bucket", y="total_volume",
                     color="moneyness_bucket", color_discrete_sequence=SEQ,
                     text="contracts")
        fig.update_traces(texttemplate="n=%{text}", textposition="outside")
        style(fig, 400).update_layout(showlegend=False,
                                      title="Total volume by moneyness")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(d, x="moneyness", y="impliedVolatility",
                         color="moneyness_bucket", size="openInterest",
                         color_discrete_sequence=SEQ, opacity=0.6,
                         hover_data=["ticker", "strike"],
                         labels={"moneyness": "Moneyness", "impliedVolatility": "IV"})
        style(fig, 400).update_layout(title="IV vs Moneyness (size=OI)")
        st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"""<hr style="border-color:#2A3038;">
    <div style="color:{C['g']};font-size:.8rem;text-align:center;">
    📈 Options Market Intelligence · data scan yfinance · analisis IV/GEX/likuiditas
    · by <b>Sandi Ridwan</b><br>
    ⚠️ Edukasional, bukan saran investasi. Dataset ini hanya CALL (tanpa PUT).</div>""",
    unsafe_allow_html=True)
