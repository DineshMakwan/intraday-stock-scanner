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
    .setup-card-long { background: rgba(16, 185, 129, 0.08); border: 1px solid #10b981; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
    .setup-card-short { background: rgba(239, 68, 68, 0.08); border: 1px solid #ef4444; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
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

# 23 SECTORS MAPPING
SECTOR_MAP = {
    "Nifty Realty": {"index": "^CNXREALTY", "stocks": {"DLF": "DLF.NS", "GODREJPROP": "GODREJPROP.NS", "OBEROIRLTY": "OBEROIRLTY.NS", "PHOENIXLTD": "PHOENIXLTD.NS", "PRESTIGE": "PRESTIGE.NS"}},
    "Nifty Cement": {"index": "^CNXCMDT", "stocks": {"ULTRACEMCO": "ULTRACEMCO.NS", "GRASIM": "GRASIM.NS", "AMBUJACEM": "AMBUJACEM.NS", "ACC": "ACC.NS", "DALBHARAT": "DALBHARAT.NS"}},
    "Nifty Chemicals": {"index": "^CNXCMDT", "stocks": {"PIDILITIND": "PIDILITIND.NS", "SRF": "SRF.NS", "LINDEINDIA": "LINDEINDIA.NS", "SOLARINDS": "SOLARINDS.NS", "AARTIIND": "AARTIIND.NS"}},
    "Nifty Healthcare": {"index": "^CNXPHARMA", "stocks": {"SUNPHARMA": "SUNPHARMA.NS", "CIPLA": "CIPLA.NS", "DRREDDY": "DRREDDY.NS", "DIVISLAB": "DIVISLAB.NS", "APOLLOHOSP": "APOLLOHOSP.NS"}},
    "Nifty Oil & Gas": {"index": "^CNXENERGY", "stocks": {"RELIANCE": "RELIANCE.NS", "ONGC": "ONGC.NS", "IOC": "IOC.NS", "BPCL": "BPCL.NS", "GAIL": "GAIL.NS"}},
    "Nifty Consumer Durables": {"index": "^CNXCONSUM", "stocks": {"TITAN": "TITAN.NS", "HAVELLS": "HAVELLS.NS", "DIXON": "DIXON.NS", "VOLTAS": "VOLTAS.NS", "CROMPTON": "CROMPTON.NS"}},
    "Nifty Private Bank": {"index": "^NSEBANK", "stocks": {"HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "AXISBANK": "AXISBANK.NS", "KOTAKBANK": "KOTAKBANK.NS", "INDUSINDBK": "INDUSINDBK.NS"}},
    "Nifty PSU Bank": {"index": "^CNXPSUBANK", "stocks": {"SBIN": "SBIN.NS", "BANKBARODA": "BANKBARODA.NS", "PNB": "PNB.NS", "CANBK": "CANBK.NS", "UNIONBANK": "UNIONBANK.NS"}},
    "Nifty Auto": {"index": "^CNXAUTO", "stocks": {"M&M": "M&M.NS", "MARUTI": "MARUTI.NS", "TATAMOTORS": "TATAMOTORS.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS", "EICHERMOT": "EICHERMOT.NS"}},
    "Nifty Bank": {"index": "^NSEBANK", "stocks": {"HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "AXISBANK": "AXISBANK.NS", "SBIN": "SBIN.NS", "KOTAKBANK": "KOTAKBANK.NS"}},
    "Nifty Financial Services": {"index": "^CNXFIN", "stocks": {"HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "BAJFINANCE": "BAJFINANCE.NS", "BAJAJFINSV": "BAJAJFINSV.NS", "PFC": "PFC.NS"}},
    "Nifty FMCG": {"index": "^CNXFMCG", "stocks": {"ITC": "ITC.NS", "HINDUNILVR": "HINDUNILVR.NS", "NESTLEIND": "NESTLEIND.NS", "BRITANNIA": "BRITANNIA.NS", "VBL": "VBL.NS"}},
    "Nifty IT": {"index": "^CNXIT", "stocks": {"TCS": "TCS.NS", "INFY": "INFY.NS", "HCLTECH": "HCLTECH.NS", "WIPRO": "WIPRO.NS", "LTIM": "LTIM.NS"}},
    "Nifty Media": {"index": "^CNXMEDIA", "stocks": {"SUNTV": "SUNTV.NS", "ZEEL": "ZEEL.NS", "PVRINOX": "PVRINOX.NS", "NAZARA": "NAZARA.NS", "TV18BRDCST": "TV18BRDCST.NS"}},
    "Nifty Metal": {"index": "^CNXMETAL", "stocks": {"TATASTEEL": "TATASTEEL.NS", "JINDALSTEL": "JINDALSTEL.NS", "JSWSTEEL": "JSWSTEEL.NS", "HINDALCO": "HINDALCO.NS", "VEDL": "VEDL.NS"}},
    "Nifty Pharma": {"index": "^CNXPHARMA", "stocks": {"SUNPHARMA": "SUNPHARMA.NS", "CIPLA": "CIPLA.NS", "DRREDDY": "DRREDDY.NS", "TORNTPHARM": "TORNTPHARM.NS", "LUPIN": "LUPIN.NS"}},
    "Nifty Energy": {"index": "^CNXENERGY", "stocks": {"RELIANCE": "RELIANCE.NS", "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS", "ONGC": "ONGC.NS", "TATAPOWER": "TATAPOWER.NS"}},
    "Nifty Infra": {"index": "^CNXINFRA", "stocks": {"LT": "LT.NS", "BHARTIARTL": "BHARTIARTL.NS", "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS", "ULTRACEMCO": "ULTRACEMCO.NS"}},
    "Nifty Commodities": {"index": "^CNXCMDT", "stocks": {"RELIANCE": "RELIANCE.NS", "TATASTEEL": "TATASTEEL.NS", "NTPC": "NTPC.NS", "COALINDIA": "COALINDIA.NS", "JINDALSTEL": "JINDALSTEL.NS"}},
    "Nifty Consumption": {"index": "^CNXCONSUM", "stocks": {"ITC": "ITC.NS", "BHARTIARTL": "BHARTIARTL.NS", "MARUTI": "MARUTI.NS", "TITAN": "TITAN.NS", "TRENT": "TRENT.NS"}},
    "Nifty PSE": {"index": "^CNXPSE", "stocks": {"NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS", "ONGC": "ONGC.NS", "COALINDIA": "COALINDIA.NS", "HAL": "HAL.NS"}},
    "Nifty MidSmall Healthcare": {"index": "^CNXPHARMA", "stocks": {"GLENMARK": "GLENMARK.NS", "IPCALAB": "IPCALAB.NS", "AJANTPHARM": "AJANTPHARM.NS", "LAURUSLABS": "LAURUSLABS.NS", "FORTIS": "FORTIS.NS"}},
    "Nifty REITs & Realty": {"index": "^CNXREALTY", "stocks": {"DLF": "DLF.NS", "LODHA": "LODHA.NS", "EMBASSY": "EMBASSY.NS", "MINDSPACE": "MINDSPACE.NS", "BIRET": "BIRET.NS"}},
}

BENCHMARK_SYMBOL = "^NSEI"

# Controls
st.sidebar.header("⚙️ RRG Settings")
timeframe = st.sidebar.selectbox("Timeframe", options=["1d", "1wk"], index=1, format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation")
tail_len = st.sidebar.slider("Tail Length", min_value=2, max_value=15, value=5)
high_threshold = st.sidebar.slider("Near 52W High Limit (%)", min_value=1.0, max_value=15.0, value=5.0)

# Single Ticker Fetcher Helper
def fetch_ticker_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="2y", interval=timeframe)
        if not df.empty:
            return ticker, df[["Close", "High", "Volume"]]
    except Exception:
        pass
    return ticker, None

# Parallel Fast Fetching Engine
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
    if ratio >= 100 and momentum >= 100: return ("Leading", "bg-leading", "#10B981")
    if ratio >= 100 and momentum < 100: return ("Weakening", "bg-weakening", "#F59E0B")
    if ratio < 100 and momentum < 100: return ("Lagging", "bg-lagging", "#EF4444")
    return ("Improving", "bg-improving", "#3B82F6")

# Build all unique tickers list
all_needed_tickers = set([BENCHMARK_SYMBOL])
for s_info in SECTOR_MAP.values():
    all_needed_tickers.add(s_info["index"])
    all_needed_tickers.update(s_info["stocks"].values())

with st.spinner("⚡ Fetching All 23 Sectors & Underlying Stocks Data in Parallel..."):
    market_db = load_all_market_data(list(all_needed_tickers))

bench_df = market_db.get(BENCHMARK_SYMBOL)

# Build Sector RRG
sector_rrg_results = {}
if bench_df is not None:
    for sec_name, sec_info in SECTOR_MAP.items():
        s_ticker = sec_info["index"]
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

# Main Interface Rendering
if not sector_rrg_results:
    st.error("Market data load nahi ho paaya. Please Internet/Rate-limit check karke Refresh karein.")
else:
    st.success(f"✅ Success! Loaded Data for {len(sector_rrg_results)} Sectors.")

    fig = go.Figure()
    summary_list = []
    colors = ["#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#F97316"]

    for idx, (name, s_data) in enumerate(sector_rrg_results.items()):
        df = s_data["metrics"].tail(tail_len)
        x_vals, y_vals = df["ratio"].values, df["momentum"].values
        head_x, head_y = x_vals[-1], y_vals[-1]
        
        quad_name, badge_cls, color = get_quadrant(head_x, head_y)
        trend = "⬆️ Up" if len(y_vals) > 1 and head_y > y_vals[-2] else "⬇️ Down"
        is_near = s_data["dist_52w"] <= high_threshold

        summary_list.append({
            "Name": name, "Quadrant": quad_name, "RS-Ratio": round(head_x, 2), "RS-Momentum": round(head_y, 2),
            "Trend": trend, "CMP": s_data["cmp"], "52W High": s_data["high_52w"], "Dist High (%)": s_data["dist_52w"],
            "BadgeClass": badge_cls, "Near High": "🔥 YES" if is_near else "NO", "NearBadge": "bg-near-high" if is_near else "bg-normal-high"
        })

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines", line=dict(color=colors[idx % len(colors)], dash="dot"), showlegend=False))
        fig.add_trace(go.Scatter(x=[head_x], y=[head_y], mode="markers+text", name=name, text=[name], textposition="top center", marker=dict(size=10, color=colors[idx % len(colors)])))

    fig.update_layout(
        title="📊 All 23 Sectors RRG Relative Rotation Chart", paper_bgcolor="#111827", plot_bgcolor="#111827", height=600,
        xaxis=dict(title="RS-Ratio", gridcolor="#1F2937", zeroline=False), yaxis=dict(title="RS-Momentum", gridcolor="#1F2937", zeroline=False),
        shapes=[
            dict(type="line", x0=100, x1=100, y0=90, y1=110, line=dict(color="#4B5563", dash="dash")),
            dict(type="line", x0=90, x1=110, y0=100, y1=100, line=dict(color="#4B5563", dash="dash"))
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # All Sectors Matrix Table
    st.subheader("📋 Sector Breakdown Matrix (All Sectors)")
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
