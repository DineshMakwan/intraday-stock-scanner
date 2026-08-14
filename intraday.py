import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Grow More | Confluence Scanner",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM BRANDING & DARK THEME CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { 
        background-color: #0b0f19; 
        color: #f3f4f6; 
    }
    
    /* Branding Header Box */
    .brand-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        padding: 22px 28px;
        border-radius: 16px;
        border-left: 8px solid #6366f1;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    .brand-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #ffffff;
        margin: 0;
    }
    .brand-subtitle {
        color: #a5b4fc;
        font-size: 0.95rem;
        margin-top: 6px;
        font-weight: 500;
    }
    .brand-tag {
        background-color: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #6366f1;
        display: inline-block;
        margin-top: 10px;
    }

    /* Custom Cards */
    .metric-card-bull {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 16px;
        border-radius: 12px;
    }
    .metric-card-bear {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 16px;
        border-radius: 12px;
    }

    /* Sidebar Branding */
    .sidebar-brand {
        text-align: center;
        padding: 10px 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR BRANDING & CONTROLS
# ---------------------------------------------------------
st.sidebar.markdown("""
    <div class="sidebar-brand">
        <h2 style="color: #6366f1; margin: 0; font-size: 1.4rem; font-weight: 800;">GROW MORE</h2>
        <p style="color: #9ca3af; margin: 2px 0 0 0; font-size: 0.75rem;">TRADING INSTITUTE</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Scanner Controls")
refresh_btn = st.sidebar.button("🔄 Refresh Market Data", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Pro Tip:** Focus on stocks with **Score >= 3.5** where Sector Alignment + Volume Spike + VWAP confirm together.")

# ---------------------------------------------------------
# MAIN HEADER BRANDING
# ---------------------------------------------------------
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">🦅 GROW MORE TRADING INSTITUTE</div>
        <div class="brand-subtitle">High-Precision Intraday Confluence Scanner (Multi-Factor Analysis)</div>
        <div class="brand-tag">PRO TRADING TOOL 2.0</div>
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

def calculate_vwap(df_single):
    tp = (df_single["High"] + df_single["Low"] + df_single["Close"]) / 3
    vwap = (tp * df_single["Volume"]).cumsum() / df_single["Volume"].cumsum()
    return vwap

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

def scan_stocks_advanced(stock_list, nifty_chg):
    results = []
    
    data_5m = fetch_data(stock_list, interval="5m")
    data_15m = fetch_data(stock_list, interval="15m")

    if data_5m.empty or data_15m.empty:
        return pd.DataFrame()

    for ticker in stock_list:
        try:
            df_5m_single = pd.DataFrame({
                "Open": data_5m["Open"][ticker].dropna(),
                "High": data_5m["High"][ticker].dropna(),
                "Low": data_5m["Low"][ticker].dropna(),
                "Close": data_5m["Close"][ticker].dropna(),
                "Volume": data_5m["Volume"][ticker].dropna()
            })

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

            # 1. VWAP
            vwap_series = calculate_vwap(df_5m_single)
            current_vwap = round(float(vwap_series.iloc[-1]), 2)
            vwap_status = "🟢 Above VWAP" if cmp > current_vwap else "🔴 Below VWAP"

            # 2. Volume Spike
            latest_vol = float(df_5m_single["Volume"].iloc[-1])
            avg_vol_20 = float(df_5m_single["Volume"].tail(20).mean())
            vol_ratio = round(latest_vol / avg_vol_20, 2) if avg_vol_20 > 0 else 1.0
            vol_status = f"🔥 High ({vol_ratio}x)" if vol_ratio >= 1.8 else (f"⚡ Normal ({vol_ratio}x)" if vol_ratio >= 1.0 else "⚪ Low")

            # 3. RS vs Nifty
            rs_diff = round(day_chg - nifty_chg, 2)
            rs_status = f"🟢 Outperform (+{rs_diff}%)" if rs_diff > 0.3 else (f"🔴 Underperform ({rs_diff}%)" if rs_diff < -0.3 else "⚪ Neutral")

            # 4. 15-Min ORB Status
            h15_first = round(float(df_15m_single["High"].iloc[0]), 2)
            l15_first = round(float(df_15m_single["Low"].iloc[0]), 2)

            orb_status = "⚪ Inside Range"
            if cmp > h15_first:
                orb_status = "🚀 15M High Breakout"
            elif cmp < l15_first:
                orb_status = "🔻 15M Low Breakdown"

            # 5. Score Calculation
            score = 0
            if day_chg > 0:
                if cmp > current_vwap: score += 1
                if "15M High" in orb_status: score += 1.5
                if vol_ratio >= 1.5: score += 1.25
                if rs_diff > 0.3: score += 1.25
            else:
                if cmp < current_vwap: score += 1
                if "15M Low" in orb_status: score += 1.5
                if vol_ratio >= 1.5: score += 1.25
                if rs_diff < -0.3: score += 1.25

            final_score = min(round(score, 1), 5.0)

            results.append({
                "Stock": ticker.replace(".NS", ""),
                "Confluence Score": final_score,
                "CMP (₹)": cmp,
                "VWAP (₹)": current_vwap,
                "Day Chg (%)": day_chg,
                "VWAP Status": vwap_status,
                "15m ORB Status": orb_status,
                "Volume Spike": vol_status,
                "RS vs Nifty": rs_status
            })

        except Exception:
            continue

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Confluence Score", ascending=False).reset_index(drop=True)
    return df_res

# ---------------------------------------------------------
# DASHBOARD BODY
# ---------------------------------------------------------
if refresh_btn:
    st.cache_data.clear()

nifty_chg = get_nifty_change()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"**Nifty 50 Benchmark Trend:** `{'+' if nifty_chg>=0 else ''}{nifty_chg}%`")

st.markdown("---")

# Sector Leaderboard
st.markdown("### 📊 Sector Momentum Leaderboard")
df_sectors = get_sector_momentum()

if not df_sectors.empty:
    top_bull_sec = df_sectors.iloc[0]["Sector"]
    top_bear_sec = df_sectors.iloc[-1]["Sector"]

    col_sec1, col_sec2 = st.columns(2)

    with col_sec1:
        st.markdown(f"""
            <div class="metric-card-bull">
                <small style="color:#10b981; font-weight:bold;">🔥 TOP BULLISH SECTOR</small>
                <h3 style="margin:4px 0 0 0; color:#ffffff;">{top_bull_sec} (+{df_sectors.iloc[0]['Change (%)']}%)</h3>
            </div>
        """, unsafe_allow_html=True)

    with col_sec2:
        st.markdown(f"""
            <div class="metric-card-bear">
                <small style="color:#ef4444; font-weight:bold;">🔻 TOP BEARISH SECTOR</small>
                <h3 style="margin:4px 0 0 0; color:#ffffff;">{top_bear_sec} ({df_sectors.iloc[-1]['Change (%)']}%)</h3>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Stock Scanner Section
st.markdown("### 🎯 Confluence Stock Scanner")

selected_sector = st.selectbox("Select Sector to Scan:", options=list(SECTOR_MAP.keys()), index=0)
stocks_to_scan = SECTOR_MAP[selected_sector]["stocks"]

with st.spinner(f"Grow More Engine Scanning {selected_sector}..."):
    df_stocks = scan_stocks_advanced(stocks_to_scan, nifty_chg)

if not df_stocks.empty:
    tab_all, tab_high, tab_bull, tab_bear = st.tabs([
        "📋 All Stocks", 
        "⭐ High Confluence (Score 3.5+)", 
        "🚀 Bullish Setups", 
        "🔻 Bearish Setups"
    ])

    # DISPLAY FUNCTION USING CLEAN STREAMLIT DATAFRAME FORMATTING
    def display_clean_table(df_show):
        if df_show.empty:
            st.info("Iss category mein abhi koi stock fit nahi ho raha hai.")
            return

        # Formatting Score column with Stars
        df_display = df_show.copy()
        df_display["Confluence Score"] = df_display["Confluence Score"].apply(lambda s: f"⭐ {s} / 5.0")

        # Configured Streamlit Dataframe display
        st.dataframe(
            df_display,
            column_config={
                "Stock": st.column_config.TextColumn("Stock", help="Stock Ticker Symbol"),
                "Confluence Score": st.column_config.TextColumn("Grow More Score", help="0 to 5 Confluence Rating"),
                "CMP (₹)": st.column_config.NumberColumn("CMP (₹)", format="₹%.2f"),
                "VWAP (₹)": st.column_config.NumberColumn("VWAP (₹)", format="₹%.2f"),
                "Day Chg (%)": st.column_config.NumberColumn("Day Chg %", format="%.2f%%"),
                "VWAP Status": st.column_config.TextColumn("VWAP Signal"),
                "15m ORB Status": st.column_config.TextColumn("15m ORB Breakout"),
                "Volume Spike": st.column_config.TextColumn("Volume Status"),
                "RS vs Nifty": st.column_config.TextColumn("Relative Strength")
            },
            hide_index=True,
            use_container_width=True
        )

    with tab_all:
        display_clean_table(df_stocks)

    with tab_high:
        display_clean_table(df_stocks[df_stocks["Confluence Score"] >= 3.5])

    with tab_bull:
        display_clean_table(df_stocks[df_stocks["Day Chg (%)"] > 0])

    with tab_bear:
        display_clean_table(df_stocks[df_stocks["Day Chg (%)"] < 0])

else:
    st.error("Market Data fetch nahi ho paya. Please Refresh button dabayein.")

# Footer Branding
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.8rem; padding: 10px;'>"
    "© Grow More Trading Institute | Built for Professional Intraday Traders"
    "</div>",
    unsafe_allow_html=True
)
