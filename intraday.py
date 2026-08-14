import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Streamlit Page Setup
st.set_page_config(
    page_title="Intraday Sector & Breakout Scanner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme & Styling
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .header-box {
        background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-bull { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .badge-bear { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .badge-neutral { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid #4b5563; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-box">
        <h2 style="margin:0; color:#ffffff;">⚡ LIVE Intraday Sector & Breakout Scanner</h2>
        <p style="margin:4px 0 0 0; color:#9ca3af;">Real-Time Top Bullish/Bearish Sectors & 5m / 15m High-Low Breakout Intelligence</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTOR & STOCK MAP DEFINITION
# ---------------------------------------------------------
SECTOR_MAP = {
    "Nifty Bank": {
        "index": "^NSEBANK",
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS"]
    },
    "Nifty IT": {
        "index": "^CNXIT",
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS", "TECHM.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS"]
    },
    "Nifty Auto": {
        "index": "^CNXAUTO",
        "stocks": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS", "BHARATFORG.NS", "ASHOKLEY.NS"]
    },
    "Nifty Metal": {
        "index": "^CNXMETAL",
        "stocks": ["TATASTEEL.NS", "JINDALSTEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NMDC.NS", "SAIL.NS", "COALINDIA.NS", "NATIONALUM.NS"]
    },
    "Nifty Pharma": {
        "index": "^CNXPHARMA",
        "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS", "TORNTPHARM.NS", "AUROPHARMA.NS", "ZYDUSLIFE.NS"]
    },
    "Nifty FMCG": {
        "index": "^CNXFMCG",
        "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS"]
    },
    "Nifty Energy": {
        "index": "^CNXENERGY",
        "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "GAIL.NS", "TATAPOWER.NS", "ADANIGREEN.NS"]
    },
    "Nifty Realty": {
        "index": "^CNXREALTY",
        "stocks": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "LODHA.NS", "PHOENIXLTD.NS", "BRIGADE.NS"]
    },
    "Nifty PSU Bank": {
        "index": "^CNXPSUBANK",
        "stocks": ["SBIN.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS", "INDIANB.NS", "IOB.NS", "UCOBANK.NS"]
    }
}

# Sidebar Controls
st.sidebar.header("⚙️ Scanner Settings")
auto_refresh = st.sidebar.button("🔄 Refresh Data Now")
selected_timeframe = st.sidebar.radio("Primary Breakout Timeframe", options=["5m", "15m"], index=0)

# Helper function to extract price data safely
def fetch_intraday_data(tickers, interval="5m"):
    try:
        df = yf.download(tickers, period="1d", interval=interval, progress=False)
        return df
    except Exception as e:
        return pd.DataFrame()

# ---------------------------------------------------------
# STEP 1: SCAN LIVE SECTOR MOMENTUM
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_sector_momentum():
    sector_results = []
    sector_indices = [info["index"] for info in SECTOR_MAP.values()]
    
    data = fetch_intraday_data(sector_indices, interval="5m")
    if data.empty:
        return pd.DataFrame()

    close_data = data["Close"] if "Close" in data else pd.DataFrame()
    open_data = data["Open"] if "Open" in data else pd.DataFrame()

    for sec_name, sec_info in SECTOR_MAP.items():
        idx_symbol = sec_info["index"]
        if idx_symbol in close_data.columns:
            s_close = close_data[idx_symbol].dropna()
            s_open = open_data[idx_symbol].dropna()

            if not s_close.empty and not s_open.empty:
                open_price = s_open.iloc[0] # Day Open
                cmp = s_close.iloc[-1]       # Current Price
                pct_chg = ((cmp - open_price) / open_price) * 100

                sector_results.append({
                    "Sector": sec_name,
                    "CMP": round(float(cmp), 2),
                    "Change (%)": round(float(pct_chg), 2),
                    "Status": "🚀 Bullish" if pct_chg > 0.2 else ("🔻 Bearish" if pct_chg < -0.2 else "⚡ Neutral")
                })

    df_sec = pd.DataFrame(sector_results)
    if not df_sec.empty:
        df_sec = df_sec.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    return df_sec

# ---------------------------------------------------------
# STEP 2: SCAN STOCKS IN TOP SECTORS FOR BREAKOUTS
# ---------------------------------------------------------
def scan_stock_breakouts(stock_list):
    results = []
    
    # Download 5m and 15m data
    data_5m = fetch_intraday_data(stock_list, interval="5m")
    data_15m = fetch_intraday_data(stock_list, interval="15m")

    if data_5m.empty or data_15m.empty:
        return pd.DataFrame()

    for ticker in stock_list:
        try:
            # 5-Min calculations
            c5 = data_5m["Close"][ticker].dropna()
            h5 = data_5m["High"][ticker].dropna()
            l5 = data_5m["Low"][ticker].dropna()

            # 15-Min calculations
            c15 = data_15m["Close"][ticker].dropna()
            h15 = data_15m["High"][ticker].dropna()
            l15 = data_15m["Low"][ticker].dropna()

            if c5.empty or c15.empty:
                continue

            cmp = round(float(c5.iloc[-1]), 2)
            day_open = round(float(data_5m["Open"][ticker].dropna().iloc[0]), 2)
            day_change = round(((cmp - day_open) / day_open) * 100, 2)

            # First 5-min High / Low
            high_5m_first = round(float(h5.iloc[0]), 2)
            low_5m_first = round(float(l5.iloc[0]), 2)

            # First 15-min High / Low
            high_15m_first = round(float(h15.iloc[0]), 2)
            low_15m_first = round(float(l15.iloc[0]), 2)

            # Check 5M Breakout / Breakdown
            status_5m = "Inside Range ➖"
            if cmp > high_5m_first:
                status_5m = "🚀 5M High Broken (Bullish)"
            elif cmp < low_5m_first:
                status_5m = "🔻 5M Low Broken (Bearish)"

            # Check 15M Breakout / Breakdown
            status_15m = "Inside Range ➖"
            if cmp > high_15m_first:
                status_15m = "🚀 15M High Broken (Bullish)"
            elif cmp < low_15m_first:
                status_15m = "🔻 15M Low Broken (Bearish)"

            results.append({
                "Stock": ticker.replace(".NS", ""),
                "CMP (₹)": cmp,
                "Day Change (%)": day_change,
                "1st 5m High": high_5m_first,
                "1st 5m Low": low_5m_first,
                "5m Status": status_5m,
                "1st 15m High": high_15m_first,
                "1st 15m Low": low_15m_first,
                "15m Status": status_15m
            })
        except Exception:
            continue

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Day Change (%)", ascending=False).reset_index(drop=True)
    return df_res


# ---------------------------------------------------------
# UI DISPLAY LOGIC
# ---------------------------------------------------------
st.markdown("### 📊 Step 1: Real-Time Sector Momentum Leaderboard")

with st.spinner("Fetching Sector Intraday Data..."):
    df_sectors = get_sector_momentum()

if not df_sectors.empty:
    top_bullish_sec = df_sectors.iloc[0]["Sector"]
    top_bearish_sec = df_sectors.iloc[-1]["Sector"]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; padding: 16px; border-radius: 10px;">
                <h4 style="color:#10b981; margin:0;">🔥 Most Bullish Sector Right Now</h4>
                <h2 style="color:#ffffff; margin:6px 0;">{top_bullish_sec} (+{df_sectors.iloc[0]['Change (%)']}%)</h2>
            </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 16px; border-radius: 10px;">
                <h4 style="color:#ef4444; margin:0;">🔻 Most Bearish Sector Right Now</h4>
                <h2 style="color:#ffffff; margin:6px 0;">{top_bearish_sec} ({df_sectors.iloc[-1]['Change (%)']}%)</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sector Bar Chart
    fig_sec = go.Figure()
    colors = ["#10b981" if val >= 0 else "#ef4444" for val in df_sectors["Change (%)"]]
    fig_sec.add_trace(go.Bar(
        x=df_sectors["Sector"],
        y=df_sectors["Change (%)"],
        marker_color=colors,
        text=df_sectors["Change (%)"],
        textposition="auto"
    ))
    fig_sec.update_layout(
        title="Intraday Sector Performance (% Change from Open)",
        paper_bgcolor="#111827", plot_bgcolor="#111827", height=320,
        xaxis=dict(gridcolor="#1f2937", color="#9ca3af"),
        yaxis=dict(gridcolor="#1f2937", color="#9ca3af")
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🎯 Step 2: Stock Breakout Scanner (5m & 15m Range)")

    # Sector Selection for Stock Scan
    selected_sector = st.selectbox(
        "Scan Stocks from Sector:",
        options=list(SECTOR_MAP.keys()),
        index=0
    )

    stocks_to_scan = SECTOR_MAP[selected_sector]["stocks"]

    with st.spinner(f"Scanning Stocks in {selected_sector}..."):
        df_stocks = scan_stock_breakouts(stocks_to_scan)

    if not df_stocks.empty:
        # Filter Tabs
        t_all, t_bull, t_bear = st.tabs(["All Stocks", "🚀 High Breakout Stocks", "🔻 Low Breakdown Stocks"])

        def display_table(df):
            rows = ""
            for _, r in df.iterrows():
                b5_class = "badge-bull" if "High" in r['5m Status'] else ("badge-bear" if "Low" in r['5m Status'] else "badge-neutral")
                b15_class = "badge-bull" if "High" in r['15m Status'] else ("badge-bear" if "Low" in r['15m Status'] else "badge-neutral")
                
                rows += f"""<tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6; font-size:0.9rem;">
                    <td style="padding:10px; font-weight:bold;">{r['Stock']}</td>
                    <td style="padding:10px; color:#38bdf8;">₹{r['CMP (₹)']}</td>
                    <td style="padding:10px; font-weight:bold; color:{'#10b981' if r['Day Change (%)']>=0 else '#ef4444'};">{r['Day Change (%)']}%</td>
                    <td style="padding:10px;">₹{r['1st 5m High']} / ₹{r['1st 5m Low']}</td>
                    <td style="padding:10px;"><span class="status-badge {b5_class}">{r['5m Status']}</span></td>
                    <td style="padding:10px;">₹{r['1st 15m High']} / ₹{r['1st 15m Low']}</td>
                    <td style="padding:10px;"><span class="status-badge {b15_class}">{r['15m Status']}</span></td>
                </tr>"""

            html = f"""<table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; margin-top:10px;">
                <thead>
                    <tr style="background-color:#1f2937; text-align:left; color:#9ca3af;">
                        <th style="padding:10px;">Stock</th>
                        <th style="padding:10px;">CMP</th>
                        <th style="padding:10px;">Day Chg (%)</th>
                        <th style="padding:10px;">5m High / Low</th>
                        <th style="padding:10px;">5m Status</th>
                        <th style="padding:10px;">15m High / Low</th>
                        <th style="padding:10px;">15m Status</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>"""
            st.markdown(html, unsafe_allow_html=True)

        with t_all:
            display_table(df_stocks)

        with t_bull:
            df_bull = df_stocks[(df_stocks["5m Status"].str.contains("High")) | (df_stocks["15m Status"].str.contains("High"))]
            if not df_bull.empty:
                display_table(df_bull)
            else:
                st.info("Iss sector mein abhi kisi stock ne 5m/15m High break nahi kiya hai.")

        with t_bear:
            df_bear = df_stocks[(df_stocks["5m Status"].str.contains("Low")) | (df_stocks["15m Status"].str.contains("Low"))]
            if not df_bear.empty:
                display_table(df_bear)
            else:
                st.info("Iss sector mein abhi kisi stock ne 5m/15m Low break nahi kiya hai.")

else:
    st.error("Market data fetch karne mein dikkat aayi. Please refresh karein.")