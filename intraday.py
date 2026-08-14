import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

# Streamlit Page Configuration
st.set_page_config(
    page_title="High Precision Intraday Scanner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    .header-box {
        background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #6366f1;
        margin-bottom: 20px;
    }
    .badge {
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .badge-success { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .badge-danger { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .badge-neutral { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid #4b5563; }
    .badge-warning { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-box">
        <h2 style="margin:0; color:#ffffff;">🎯 High-Accuracy Multi-Factor Intraday Scanner</h2>
        <p style="margin:4px 0 0 0; color:#9ca3af;">VWAP + Volume Spike + Relative Strength vs Nifty + ORB 15m + Confluence Scoring</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTOR & STOCK MAPPING
# ---------------------------------------------------------
SECTOR_MAP = {
    "Nifty Bank": {
        "index": "^NSEBANK",
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS"]
    },
    "Nifty IT": {
        "index": "^CNXIT",
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "LTIM.NS", "TECHM.NS", "PERSISTENT.NS", "COFORGE.NS"]
    },
    "Nifty Auto": {
        "index": "^CNXAUTO",
        "stocks": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS"]
    },
    "Nifty Metal": {
        "index": "^CNXMETAL",
        "stocks": ["TATASTEEL.NS", "JINDALSTEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NMDC.NS", "SAIL.NS", "COALINDIA.NS"]
    },
    "Nifty Pharma": {
        "index": "^CNXPHARMA",
        "stocks": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS", "TORNTPHARM.NS", "AUROPHARMA.NS"]
    },
    "Nifty FMCG": {
        "index": "^CNXFMCG",
        "stocks": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "GODREJCP.NS", "DABUR.NS"]
    },
    "Nifty Energy": {
        "index": "^CNXENERGY",
        "stocks": ["RELIANCE.NS", "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "GAIL.NS", "TATAPOWER.NS"]
    }
}

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def fetch_data(tickers, interval="5m"):
    try:
        df = yf.download(tickers, period="1d", interval=interval, progress=False)
        return df
    except Exception:
        return pd.DataFrame()

# Calculate Intraday VWAP
def calculate_vwap(df_single):
    tp = (df_single["High"] + df_single["Low"] + df_single["Close"]) / 3
    vwap = (tp * df_single["Volume"]).cumsum() / df_single["Volume"].cumsum()
    return vwap

# Fetch Benchmark Nifty 50 Change
@st.cache_data(ttl=60)
def get_nifty_change():
    try:
        nifty = yf.download("^NSEI", period="1d", interval="5m", progress=False)
        if not nifty.empty:
            open_p = float(nifty["Open"].iloc[0])
            cmp_p = float(nifty["Close"].iloc[-1])
            return round(((cmp_p - open_p) / open_p) * 100, 2)
    except Exception:
        pass
    return 0.0

# ---------------------------------------------------------
# STEP 1: SECTOR ANALYSIS
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_sector_momentum():
    sector_results = []
    sector_indices = [info["index"] for info in SECTOR_MAP.values()]
    data = fetch_data(sector_indices, interval="5m")

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
                open_p = s_open.iloc[0]
                cmp_p = s_close.iloc[-1]
                pct_chg = ((cmp_p - open_p) / open_p) * 100

                sector_results.append({
                    "Sector": sec_name,
                    "CMP": round(float(cmp_p), 2),
                    "Change (%)": round(float(pct_chg), 2)
                })

    df_sec = pd.DataFrame(sector_results)
    if not df_sec.empty:
        df_sec = df_sec.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    return df_sec

# ---------------------------------------------------------
# STEP 2: HIGH-ACCURACY STOCK SCANNER
# ---------------------------------------------------------
def scan_stocks_advanced(stock_list, nifty_chg):
    results = []
    
    data_5m = fetch_data(stock_list, interval="5m")
    data_15m = fetch_data(stock_list, interval="15m")

    if data_5m.empty or data_15m.empty:
        return pd.DataFrame()

    for ticker in stock_list:
        try:
            # Extract 5m data frame for single stock
            df_5m_single = pd.DataFrame({
                "Open": data_5m["Open"][ticker].dropna(),
                "High": data_5m["High"][ticker].dropna(),
                "Low": data_5m["Low"][ticker].dropna(),
                "Close": data_5m["Close"][ticker].dropna(),
                "Volume": data_5m["Volume"][ticker].dropna()
            })

            # Extract 15m data frame for single stock
            df_15m_single = pd.DataFrame({
                "High": data_15m["High"][ticker].dropna(),
                "Low": data_15m["Low"][ticker].dropna(),
                "Close": data_15m["Close"][ticker].dropna()
            })

            if df_5m_single.empty or df_15m_single.empty:
                continue

            cmp = round(float(df_5m_single["Close"].iloc[-1]), 2)
            day_open = round(float(df_5m_single["Open"].iloc[0]), 2)
            day_chg = round(((cmp - day_open) / day_open) * 100, 2)

            # 1. VWAP Calculation
            vwap_series = calculate_vwap(df_5m_single)
            current_vwap = round(float(vwap_series.iloc[-1]), 2)
            vwap_status = " Above VWAP (Bullish)" if cmp > current_vwap else " Below VWAP (Bearish)"

            # 2. Volume Spike (RVOL check)
            latest_vol = float(df_5m_single["Volume"].iloc[-1])
            avg_vol_20 = float(df_5m_single["Volume"].tail(20).mean())
            vol_ratio = round(latest_vol / avg_vol_20, 2) if avg_vol_20 > 0 else 1.0
            vol_status = f"🔥 High ({vol_ratio}x)" if vol_ratio >= 1.8 else (f"⚡ Normal ({vol_ratio}x)" if vol_ratio >= 1.0 else " Low")

            # 3. Relative Strength vs Nifty
            rs_diff = round(day_chg - nifty_chg, 2)
            rs_status = f" Outperforming (+{rs_diff}%)" if rs_diff > 0.3 else (f" Underperforming ({rs_diff}%)" if rs_diff < -0.3 else " Neutral")

            # 4. 15-Min ORB Status
            h15_first = round(float(df_15m_single["High"].iloc[0]), 2)
            l15_first = round(float(df_15m_single["Low"].iloc[0]), 2)

            orb_status = "Inside Range ➖"
            if cmp > h15_first:
                orb_status = "🚀 15M High Breakout"
            elif cmp < l15_first:
                orb_status = "🔻 15M Low Breakdown"

            # 5. CONFLUENCE SCORE CALCULATION (0 to 5 Points)
            score = 0
            # Bullish Criteria Score
            if day_chg > 0:
                if cmp > current_vwap: score += 1
                if "15M High" in orb_status: score += 1.5
                if vol_ratio >= 1.5: score += 1.25
                if rs_diff > 0.3: score += 1.25
            # Bearish Criteria Score
            else:
                if cmp < current_vwap: score += 1
                if "15M Low" in orb_status: score += 1.5
                if vol_ratio >= 1.5: score += 1.25
                if rs_diff < -0.3: score += 1.25

            final_score = min(round(score, 1), 5.0)

            results.append({
                "Stock": ticker.replace(".NS", ""),
                "CMP (₹)": cmp,
                "VWAP (₹)": current_vwap,
                "Day Chg (%)": day_chg,
                "Confluence Score": final_score,
                "VWAP Signal": vwap_status,
                "15m ORB Status": orb_status,
                "Volume Spike": vol_status,
                "RS vs Nifty": rs_status,
                "15m High": h15_first,
                "15m Low": l15_first
            })

        except Exception:
            continue

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Confluence Score", ascending=False).reset_index(drop=True)
    return df_res


# ---------------------------------------------------------
# UI CONTROLS & DASHBOARD
# ---------------------------------------------------------
nifty_chg = get_nifty_change()

col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.markdown(f"**Nifty 50 Intraday Trend:** `{'+' if nifty_chg>=0 else ''}{nifty_chg}%`")
with col_top2:
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()

st.markdown("---")

# Sector Leaderboard
st.markdown("### 📊 Sector Momentum Leaderboard")
df_sectors = get_sector_momentum()

if not df_sectors.empty:
    col_sec1, col_sec2 = st.columns(2)
    top_bull_sec = df_sectors.iloc[0]["Sector"]
    top_bear_sec = df_sectors.iloc[-1]["Sector"]

    with col_sec1:
        st.success(f"🔥 **Top Bullish Sector:** {top_bull_sec} (+{df_sectors.iloc[0]['Change (%)']}%)")
    with col_sec2:
        st.error(f"🔻 **Top Bearish Sector:** {top_bear_sec} ({df_sectors.iloc[-1]['Change (%)']}%)")

st.markdown("---")

# Stock Scanner Section
st.markdown("### 🎯 Multi-Parameter Stock Scanner")

selected_sector = st.selectbox("Select Sector to Scan Stocks:", options=list(SECTOR_MAP.keys()), index=0)
stocks_to_scan = SECTOR_MAP[selected_sector]["stocks"]

with st.spinner(f"Scanning Stocks in {selected_sector} with VWAP, Volume & RS Filters..."):
    df_stocks = scan_stocks_advanced(stocks_to_scan, nifty_chg)

if not df_stocks.empty:
    # Filter Tabs
    tab_all, tab_high_conf, tab_bull, tab_bear = st.tabs([
        "All Stocks", 
        "⭐ High Confluence Trades (Score 3.5+)", 
        "🚀 Bullish Setup", 
        "🔻 Bearish Setup"
    ])

    def render_custom_table(df_to_show):
        if df_to_show.empty:
            st.info("Iss category mein koi stock fit nahi baith raha hai abhi.")
            return

        rows = ""
        for _, r in df_to_show.iterrows():
            # Badges styling
            vwap_badge = "badge-success" if "Above" in r["VWAP Signal"] else "badge-danger"
            orb_badge = "badge-success" if "High" in r["15m ORB Status"] else ("badge-danger" if "Low" in r["15m ORB Status"] else "badge-neutral")
            vol_badge = "badge-warning" if "High" in r["Volume Spike"] else "badge-neutral"
            rs_badge = "badge-success" if "Outperforming" in r["RS vs Nifty"] else ("badge-danger" if "Underperforming" in r["RS vs Nifty"] else "badge-neutral")
            
            score_color = "#10b981" if r["Confluence Score"] >= 3.5 else ("#f59e0b" if r["Confluence Score"] >= 2.0 else "#9ca3af")

            rows += f"""
            <tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6;">
                <td style="padding:10px; font-weight:bold;">{r['Stock']}</td>
                <td style="padding:10px; font-weight:bold; color:{score_color};">⭐ {r['Confluence Score']} / 5.0</td>
                <td style="padding:10px; color:#38bdf8;">₹{r['CMP (₹)']}</td>
                <td style="padding:10px;">₹{r['VWAP (₹)']}</td>
                <td style="padding:10px;"><span class="badge {vwap_badge}">{r['VWAP Signal']}</span></td>
                <td style="padding:10px;"><span class="badge {orb_badge}">{r['15m ORB Status']}</span></td>
                <td style="padding:10px;"><span class="badge {vol_badge}">{r['Volume Spike']}</span></td>
                <td style="padding:10px;"><span class="badge {rs_badge}">{r['RS vs Nifty']}</span></td>
            </tr>
            """

        html_table = f"""
        <table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; font-size:0.88rem;">
            <thead>
                <tr style="background-color:#1f2937; color:#9ca3af; text-align:left;">
                    <th style="padding:10px;">Stock</th>
                    <th style="padding:10px;">Confluence Score</th>
                    <th style="padding:10px;">CMP</th>
                    <th style="padding:10px;">VWAP</th>
                    <th style="padding:10px;">VWAP Status</th>
                    <th style="padding:10px;">15m ORB</th>
                    <th style="padding:10px;">Volume Spike</th>
                    <th style="padding:10px;">RS vs Nifty</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)

    with tab_all:
        render_custom_table(df_stocks)

    with tab_high_conf:
        render_custom_table(df_stocks[df_stocks["Confluence Score"] >= 3.5])

    with tab_bull:
        render_custom_table(df_stocks[df_stocks["Day Chg (%)"] > 0])

    with tab_bear:
        render_custom_table(df_stocks[df_stocks["Day Chg (%)"] < 0])

else:
    st.error("Market data load nahi ho paya. Please refresh karein.")
