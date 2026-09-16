from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More Trading Institute - RRG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .brand-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%);
        padding: 18px 24px; border-radius: 12px; border-left: 6px solid #3b82f6;
        margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;
    }
    .brand-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; }
    .status-badge { padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; display: inline-block; }
    .bg-leading { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .bg-improving { background-color: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
    .bg-weakening { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .bg-lagging { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .bg-near-high { background-color: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid #ec4899; }
    .bg-normal-high { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid #4b5563; }
    </style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="brand-header">
        <div>
            <div class="brand-title">GROW MORE TRADING INSTITUTE</div>
            <div style="color: #9ca3af;">All 23 Sector RRG & Live Money Flow Matrix</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 23 SECTORS MAPPING WITH RELIABLE ETFs / LEADING STOCKS AS REPRESENTATIVE
SECTOR_MAP = {
    "Nifty Realty": "DLF.NS",
    "Nifty Cement": "ULTRACEMCO.NS",
    "Nifty Chemicals": "PIDILITIND.NS",
    "Nifty Healthcare": "SUNPHARMA.NS",
    "Nifty Oil & Gas": "RELIANCE.NS",
    "Nifty Consumer Durables": "TITAN.NS",
    "Nifty Private Bank": "HDFCBANK.NS",
    "Nifty PSU Bank": "SBIN.NS",
    "Nifty Auto": "M&M.NS",
    "Nifty Bank": "BANKBEES.NS",
    "Nifty Financial Services": "BAJFINANCE.NS",
    "Nifty FMCG": "ITC.NS",
    "Nifty IT": "TCS.NS",
    "Nifty Media": "SUNTV.NS",
    "Nifty Metal": "TATASTEEL.NS",
    "Nifty Pharma": "CIPLA.NS",
    "Nifty Energy": "NTPC.NS",
    "Nifty Infra": "LT.NS",
    "Nifty Commodities": "COALINDIA.NS",
    "Nifty Consumption": "HINDUNILVR.NS",
    "Nifty PSE": "POWERGRID.NS",
    "Nifty MidSmall Healthcare": "GLENMARK.NS",
    "Nifty REITs & Realty": "GODREJPROP.NS",
}

BENCHMARK_SYMBOL = "^NSEI"

# Controls
st.sidebar.header("⚙️ RRG Settings")
timeframe = st.sidebar.selectbox("Timeframe", options=["1d", "1wk"], index=1, format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation")
tail_len = st.sidebar.slider("Tail Length", min_value=2, max_value=15, value=5)
high_threshold = st.sidebar.slider("Near 52W High Limit (%)", min_value=1.0, max_value=15.0, value=5.0)

# Fetcher Function
def fetch_ticker_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="2y", interval=timeframe)
        if not df.empty:
            return ticker, df[["Close", "High"]]
    except Exception:
        pass
    return ticker, None

@st.cache_data(ttl=300)
def load_all_market_data(all_tickers):
    data_store = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(fetch_ticker_data, all_tickers)
        for ticker, df in results:
            if df is not None and not df.empty:
                data_store[ticker] = df
    return data_store

def calculate_rrg(item_df, bench_df, period_len=14):
    combined = pd.concat([item_df["Close"], bench_df["Close"]], axis=1, join="inner").dropna()
    if len(combined) < (period_len * 2):
        return None
    rs = (combined.iloc[:, 0] / combined.iloc[:, 1]) * 100
    rs_ratio = 100 + ((rs - rs.rolling(period_len).mean()) / (rs.rolling(period_len).std() + 1e-6)) * 10
    rs_mom = 100 + ((rs_ratio - rs_ratio.rolling(period_len).mean()) / (rs_ratio.rolling(period_len).std() + 1e-6)) * 10
    return pd.DataFrame({"ratio": rs_ratio, "momentum": rs_mom}).dropna()

def get_quadrant(ratio, momentum):
    if ratio >= 100 and momentum >= 100: return ("Leading", "bg-leading")
    if ratio >= 100 and momentum < 100: return ("Weakening", "bg-weakening")
    if ratio < 100 and momentum < 100: return ("Lagging", "bg-lagging")
    return ("Improving", "bg-improving")

# Fetch Data
all_tickers = [BENCHMARK_SYMBOL] + list(SECTOR_MAP.values())
with st.spinner("⚡ Fetching All 23 Sectors Data..."):
    market_db = load_all_market_data(all_tickers)

bench_df = market_db.get(BENCHMARK_SYMBOL)

sector_rrg_results = {}
if bench_df is not None:
    for sec_name, s_ticker in SECTOR_MAP.items():
        if s_ticker in market_db:
            s_df = market_db[s_ticker]
            m_df = calculate_rrg(s_df, bench_df)
            if m_df is not None and not m_df.empty:
                cmp = float(s_df["Close"].iloc[-1])
                high_52 = float(s_df["High"].max())
                dist_high = round(((high_52 - cmp) / high_52) * 100, 2)
                sector_rrg_results[sec_name] = {
                    "metrics": m_df, "cmp": round(cmp, 2), "high_52w": round(high_52, 2), "dist_52w": dist_high
                }

if not sector_rrg_results:
    st.error("Market data fetch nahi hua. Please Refresh karein.")
else:
    st.success(f"✅ Success! Loaded Data for {len(sector_rrg_results)} Sectors.")

    fig = go.Figure()
    summary_list = []
    colors = [
        "#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316",
        "#06B6D4", "#A855F7", "#6366F1", "#84CC16", "#EAB308", "#F43F5E", "#D946EF", "#64748B",
        "#22C55E", "#0284C7", "#E11D48", "#7C3AED", "#059669", "#D97706", "#4F46E5"
    ]

    for idx, (name, s_data) in enumerate(sector_rrg_results.items()):
        df = s_data["metrics"].tail(tail_len)
        x_vals, y_vals = df["ratio"].values, df["momentum"].values
        head_x, head_y = x_vals[-1], y_vals[-1]
        
        quad_name, badge_cls = get_quadrant(head_x, head_y)
        trend = "⬆️ Up" if len(y_vals) > 1 and head_y > y_vals[-2] else "⬇️ Down"
        is_near = s_data["dist_52w"] <= high_threshold

        summary_list.append({
            "Name": name, "Quadrant": quad_name, "RS-Ratio": round(head_x, 2), "RS-Momentum": round(head_y, 2),
            "Trend": trend, "CMP": s_data["cmp"], "52W High": s_data["high_52w"], "Dist High (%)": s_data["dist_52w"],
            "BadgeClass": badge_cls, "Near High": "🔥 YES" if is_near else "NO", "NearBadge": "bg-near-high" if is_near else "bg-normal-high"
        })

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines", line=dict(color=colors[idx % len(colors)], dash="dot"), showlegend=False))
        fig.add_trace(go.Scatter(x=[head_x], y=[head_y], mode="markers+text", name=name, text=[name], textposition="top center", marker=dict(size=9, color=colors[idx % len(colors)])))

    fig.update_layout(
        title="📊 All 23 Sectors RRG Relative Rotation Chart", paper_bgcolor="#111827", plot_bgcolor="#111827", height=650,
        xaxis=dict(title="RS-Ratio", gridcolor="#1F2937", zeroline=False), yaxis=dict(title="RS-Momentum", gridcolor="#1F2937", zeroline=False),
        shapes=[
            dict(type="line", x0=100, x1=100, y0=85, y1=115, line=dict(color="#4B5563", dash="dash")),
            dict(type="line", x0=85, x1=115, y0=100, y1=100, line=dict(color="#4B5563", dash="dash"))
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Matrix Table
    st.subheader("📋 Sector Breakdown Matrix (All 23 Sectors)")
    df_summary = pd.DataFrame(summary_list)
    
    rows = ""
    for _, row in df_summary.iterrows():
        rows += f"""<tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6;">
            <td style="padding:10px;"><b>{row['Name']}</b></td>
            <td style="padding:10px;"><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
            <td style="padding:10px;">{row['RS-Ratio']}</td>
            <td style="padding:10px;">{row['RS-Momentum']}</td>
            <td style="padding:10px;">{row['Trend']}</td>
            <td style="padding:10px; color:#38bdf8;">₹{row['CMP']}</td>
            <td style="padding:10px;">₹{row['52W High']}</td>
            <td style="padding:10px;">{row['Dist High (%)']}%</td>
            <td style="padding:10px;"><span class="status-badge {row['NearBadge']}">{row['Near High']}</span></td>
        </tr>"""

    table_html = f"""<table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px;">
        <thead><tr style="background-color:#1f2937; color:#9ca3af; text-align:left;">
            <th style="padding:10px;">Sector</th><th style="padding:10px;">Quadrant</th><th style="padding:10px;">RS-Ratio</th><th style="padding:10px;">RS-Momentum</th><th style="padding:10px;">Trend</th><th style="padding:10px;">CMP</th><th style="padding:10px;">52W High</th><th style="padding:10px;">Dist High</th><th style="padding:10px;">Near High</th>
        </tr></thead><tbody>{rows}</tbody></table>"""
    
    st.markdown(table_html, unsafe_allow_html=True)
