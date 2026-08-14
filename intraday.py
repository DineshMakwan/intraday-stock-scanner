import time
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from curl_cffi import requests

# ---------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Grow More | Confluence & Live Option Chain",
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
refresh_btn = st.sidebar.button("🔄 Refresh Live Data", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("""
💡 **PCR Guide:**
* **PCR > 1.2:** Strong Bullish (Support Heavy)
* **PCR 0.8 - 1.2:** Rangebound / Neutral
* **PCR < 0.8:** Strong Bearish (Resistance Heavy)
""")

# ---------------------------------------------------------
# MAIN HEADER BRANDING
# ---------------------------------------------------------
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">🦅 GROW MORE TRADING INSTITUTE</div>
        <div class="brand-subtitle">Intraday Stock Confluence & Live NSE Option Chain Scanner</div>
        <div class="brand-tag">PRO TRADING TOOL 5.0 (ULTRA-FAST TLS ENGINE)</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTOR MAPPING
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
# FAST NSE OPTION CHAIN FETCH ENGINE (CURL-CFFI)
# ---------------------------------------------------------
@st.cache_data(ttl=30)
def fetch_nse_live_option_chain(symbol="BANKNIFTY", strike_step=100, num_strikes=8):
    """
    Fetches real-time Option Chain directly using Chrome TLS Fingerprint Impersonation
    """
    base_url = "https://www.nseindia.com"
    oc_page_url = "https://www.nseindia.com/option-chain"
    api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': oc_page_url,
    }

    try:
        session = requests.Session(impersonate="chrome120")
        session.get(base_url, timeout=5)
        session.get(oc_page_url, timeout=5)
        time.sleep(0.3)

        response = session.get(api_url, headers=headers, timeout=5)

        if response.status_code == 200:
            json_data = response.json()
            records = json_data.get("records", {})

            spot_price = round(float(records.get("underlyingValue", 0)), 2)
            expiries = records.get("expiryDates", [])

            if not expiries or spot_price == 0:
                return None, 0, 0, 0, pd.DataFrame()

            near_expiry = expiries[0]
            atm_strike = round(spot_price / strike_step) * strike_step

            target_strikes = [atm_strike + (i * strike_step) for i in range(-num_strikes, num_strikes + 1)]

            chain_list = []
            raw_data = records.get("data", [])

            for row in raw_data:
                if row.get("expiryDate") == near_expiry and row.get("strikePrice") in target_strikes:
                    strike = row.get("strikePrice")
                    ce_data = row.get("CE", {})
                    pe_data = row.get("PE", {})

                    chain_list.append({
                        "Call OI": ce_data.get("openInterest", 0),
                        "Call LTP": ce_data.get("lastPrice", 0),
                        "Call IV": ce_data.get("impliedVolatility", 0),
                        "Strike Price": strike,
                        "Put LTP": pe_data.get("lastPrice", 0),
                        "Put OI": pe_data.get("openInterest", 0),
                        "Put IV": pe_data.get("impliedVolatility", 0)
                    })

            df_chain = pd.DataFrame(chain_list)
            if not df_chain.empty:
                df_chain = df_chain.sort_values(by="Strike Price").reset_index(drop=True)

                total_call_oi = df_chain["Call OI"].sum()
                total_put_oi = df_chain["Put OI"].sum()
                pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0.0

                return near_expiry, spot_price, atm_strike, pcr, df_chain

    except Exception:
        pass

    return None, 0, 0, 0, pd.DataFrame()

# ---------------------------------------------------------
# HELPER FUNCTIONS - STOCK SCANNER
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

            vwap_series = calculate_vwap(df_5m_single)
            current_vwap = round(float(vwap_series.iloc[-1]), 2)
            vwap_status = "🟢 Above VWAP" if cmp > current_vwap else "🔴 Below VWAP"

            latest_vol = float(df_5m_single["Volume"].iloc[-1])
            avg_vol_20 = float(df_5m_single["Volume"].tail(20).mean())
            vol_ratio = round(latest_vol / avg_vol_20, 2) if avg_vol_20 > 0 else 1.0
            vol_status = f"🔥 High ({vol_ratio}x)" if vol_ratio >= 1.8 else (f"⚡ Normal ({vol_ratio}x)" if vol_ratio >= 1.0 else "⚪ Low")

            rs_diff = round(day_chg - nifty_chg, 2)
            rs_status = f"🟢 Outperform (+{rs_diff}%)" if rs_diff > 0.3 else (f"🔴 Underperform ({rs_diff}%)" if rs_diff < -0.3 else "⚪ Neutral")

            h15_first = round(float(df_15m_single["High"].iloc[0]), 2)
            l15_first = round(float(df_15m_single["Low"].iloc[0]), 2)

            orb_status = "⚪ Inside Range"
            if cmp > h15_first:
                orb_status = "🚀 15M High Breakout"
            elif cmp < l15_first:
                orb_status = "🔻 15M Low Breakdown"

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
# MAIN NAVIGATION TABS
# ---------------------------------------------------------
if refresh_btn:
    st.cache_data.clear()

nifty_chg = get_nifty_change()

main_tab1, main_tab2, main_tab3 = st.tabs([
    "📈 Stock Confluence Scanner", 
    "🎯 NIFTY 50 Option Chain", 
    "🏦 BANK NIFTY Option Chain"
])

# =========================================================
# TAB 1: STOCK CONFLUENCE SCANNER
# =========================================================
with main_tab1:
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
    st.markdown("### 🎯 Confluence Stock Scanner")

    selected_sector = st.selectbox("Select Sector to Scan:", options=list(SECTOR_MAP.keys()), index=0)
    stocks_to_scan = SECTOR_MAP[selected_sector]["stocks"]

    with st.spinner(f"Scanning Stocks in {selected_sector}..."):
        df_stocks = scan_stocks_advanced(stocks_to_scan, nifty_chg)

    if not df_stocks.empty:
        tab_all, tab_high, tab_bull, tab_bear = st.tabs([
            "📋 All Stocks", 
            "⭐ High Confluence (Score 3.5+)", 
            "🚀 Bullish Setups", 
            "🔻 Bearish Setups"
        ])

        def display_clean_table(df_show):
            if df_show.empty:
                st.info("Iss category mein abhi koi stock fit nahi ho raha hai.")
                return

            df_display = df_show.copy()
            df_display["Confluence Score"] = df_display["Confluence Score"].apply(lambda s: f"⭐ {s} / 5.0")

            st.dataframe(
                df_display,
                column_config={
                    "Stock": st.column_config.TextColumn("Stock"),
                    "Confluence Score": st.column_config.TextColumn("Grow More Score"),
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

        with tab_all: display_clean_table(df_stocks)
        with tab_high: display_clean_table(df_stocks[df_stocks["Confluence Score"] >= 3.5])
        with tab_bull: display_clean_table(df_stocks[df_stocks["Day Chg (%)"] > 0])
        with tab_bear: display_clean_table(df_stocks[df_stocks["Day Chg (%)"] < 0])

# =========================================================
# TAB 2: NIFTY 50 OPTION CHAIN
# =========================================================
with main_tab2:
    st.markdown("### 🎯 Nifty 50 Real-Time NSE Option Chain & OI Intelligence")
    
    with st.spinner("Connecting to NSE Engine for Nifty Data..."):
        expiry, spot, atm, pcr, df_chain = fetch_nse_live_option_chain(symbol="NIFTY", strike_step=50, num_strikes=8)

    if not df_chain.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Nifty Spot Price", f"₹{spot}")
        c2.metric("ATM Strike", f"₹{atm}")
        c3.metric("Put-Call Ratio (PCR)", f"{pcr}")

        if pcr >= 1.2:
            c4.success("🚀 BULLISH (Support Heavy)")
        elif pcr <= 0.8:
            c4.error("🔻 BEARISH (Resistance Heavy)")
        else:
            c4.warning("⚡ NEUTRAL / RANGEBOUND")

        st.markdown(f"**Expiry Date:** `{expiry}`")
        st.markdown("---")

        st.markdown("#### 📊 Open Interest Distribution (Resistance vs Support)")
        fig_nifty = go.Figure()
        fig_nifty.add_trace(go.Bar(x=df_chain["Strike Price"], y=df_chain["Call OI"], name="Call OI (Resistance)", marker_color="#ef4444"))
        fig_nifty.add_trace(go.Bar(x=df_chain["Strike Price"], y=df_chain["Put OI"], name="Put OI (Support)", marker_color="#10b981"))
        fig_nifty.update_layout(
            barmode="group",
            height=360,
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="#f3f4f6"),
            xaxis=dict(gridcolor="#1f2937", title="Strike Price"),
            yaxis=dict(gridcolor="#1f2937", title="Open Interest")
        )
        st.plotly_chart(fig_nifty, use_container_width=True)

        st.markdown("#### 📋 Live NSE Option Chain Table")
        st.dataframe(df_chain, hide_index=True, use_container_width=True)
    else:
        st.warning("⚠️ Data fetch nahi ho paya. Local terminal par `streamlit run app_growmore_pro_v5.py` se run karke test karein.")

# =========================================================
# TAB 3: BANK NIFTY OPTION CHAIN
# =========================================================
with main_tab3:
    st.markdown("### 🏦 Bank Nifty Real-Time NSE Option Chain & OI Intelligence")
    
    with st.spinner("Connecting to NSE Engine for Bank Nifty Data..."):
        expiry, spot, atm, pcr, df_chain = fetch_nse_live_option_chain(symbol="BANKNIFTY", strike_step=100, num_strikes=8)

    if not df_chain.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Bank Nifty Spot Price", f"₹{spot}")
        c2.metric("ATM Strike", f"₹{atm}")
        c3.metric("Put-Call Ratio (PCR)", f"{pcr}")

        if pcr >= 1.2:
            c4.success("🚀 BULLISH (Support Heavy)")
        elif pcr <= 0.8:
            c4.error("🔻 BEARISH (Resistance Heavy)")
        else:
            c4.warning("⚡ NEUTRAL / RANGEBOUND")

        st.markdown(f"**Expiry Date:** `{expiry}`")
        st.markdown("---")

        st.markdown("#### 📊 Open Interest Distribution (Resistance vs Support)")
        fig_bn = go.Figure()
        fig_bn.add_trace(go.Bar(x=df_chain["Strike Price"], y=df_chain["Call OI"], name="Call OI (Resistance)", marker_color="#ef4444"))
        fig_bn.add_trace(go.Bar(x=df_chain["Strike Price"], y=df_chain["Put OI"], name="Put OI (Support)", marker_color="#10b981"))
        fig_bn.update_layout(
            barmode="group",
            height=360,
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font=dict(color="#f3f4f6"),
            xaxis=dict(gridcolor="#1f2937", title="Strike Price"),
            yaxis=dict(gridcolor="#1f2937", title="Open Interest")
        )
        st.plotly_chart(fig_bn, use_container_width=True)

        st.markdown("#### 📋 Live NSE Option Chain Table")
        st.dataframe(df_chain, hide_index=True, use_container_width=True)
    else:
        st.warning("⚠️ Data fetch nahi ho paya. Local terminal par `streamlit run app_growmore_pro_v5.py` se run karke test karein.")

# ---------------------------------------------------------
# FOOTER BRANDING
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.8rem; padding: 10px;'>"
    "© Grow More Trading Institute | Pro Intraday & Options Intelligence Dashboard"
    "</div>",
    unsafe_allow_html=True
)
