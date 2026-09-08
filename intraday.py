"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GROW MORE TRADING INSTITUTE — ADVANCED ALL-IN-ONE MARKET DASHBOARD      ║
║   Nifty Trend | Running Sector Tickers | News & Block Deals | 2026 Holidays  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Requirements (requirements.txt):
    streamlit>=1.32.0
    yfinance>=0.2.36
    plotly>=5.20.0
    pandas>=2.0.0
    numpy>=1.26.0
    requests

Run:
    streamlit run app.py
"""

from datetime import datetime, time as dtime, timezone, timedelta
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grow More — All-in-One Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CONSTANTS & MAPS
# ─────────────────────────────────────────────────────────────────────────────
BENCHMARK_SYMBOL = "^NSEI"
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

CHART_COLORS = [
    "#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899",
    "#14B8A6", "#F97316", "#6366F1", "#06B6D4", "#A855F7", "#EAB308",
    "#84CC16", "#F43F5E", "#D97706", "#059669", "#2563EB", "#7C3AED",
]

QUADRANT_CFG = {
    "Leading":   {"color": "#10B981", "badge": "bg-leading",   "icon": "🚀", "desc": "Strong RS & Rising Momentum"},
    "Weakening": {"color": "#F59E0B", "badge": "bg-weakening", "icon": "⚠️", "desc": "Strong RS but Momentum Slowing"},
    "Lagging":   {"color": "#EF4444", "badge": "bg-lagging",   "icon": "🔻", "desc": "Weak RS & Falling Momentum"},
    "Improving": {"color": "#3B82F6", "badge": "bg-improving", "icon": "⚡", "desc": "Weak RS but Momentum Gaining"},
}

SECTOR_MAP = {
    "Nifty Bank": {"index": "^NSEBANK", "stocks": {"HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "SBIN": "SBIN.NS", "AXISBANK": "AXISBANK.NS", "KOTAKBANK": "KOTAKBANK.NS"}},
    "Nifty IT": {"index": "^CNXIT", "stocks": {"TCS": "TCS.NS", "INFY": "INFY.NS", "HCLTECH": "HCLTECH.NS", "WIPRO": "WIPRO.NS", "TECHM": "TECHM.NS"}},
    "Nifty Auto": {"index": "^CNXAUTO", "stocks": {"MARUTI": "MARUTI.NS", "TATAMOTORS": "TATAMOTORS.NS", "M&M": "M&M.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS"}},
    "Nifty Pharma": {"index": "^CNXPHARMA", "stocks": {"SUNPHARMA": "SUNPHARMA.NS", "CIPLA": "CIPLA.NS", "DRREDDY": "DRREDDY.NS", "DIVISLAB": "DIVISLAB.NS"}},
    "Nifty FMCG": {"index": "^CNXFMCG", "stocks": {"ITC": "ITC.NS", "HINDUNILVR": "HINDUNILVR.NS", "NESTLEIND": "NESTLEIND.NS", "BRITANNIA": "BRITANNIA.NS"}},
    "Nifty Metal": {"index": "^CNXMETAL", "stocks": {"TATASTEEL": "TATASTEEL.NS", "JSWSTEEL": "JSWSTEEL.NS", "HINDALCO": "HINDALCO.NS", "VEDL": "VEDL.NS"}},
    "Nifty Energy": {"index": "^CNXENERGY", "stocks": {"RELIANCE": "RELIANCE.NS", "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS", "ONGC": "ONGC.NS"}},
    "Nifty Realty": {"index": "^CNXREALTY", "stocks": {"DLF": "DLF.NS", "GODREJPROP": "GODREJPROP.NS", "LODHA": "LODHA.NS", "OBEROIRLTY": "OBEROIRLTY.NS"}},
}

NSE_HOLIDAYS_2026 = [
    {"Date": "2026-01-26", "Day": "Monday", "Holiday": "Republic Day"},
    {"Date": "2026-03-03", "Day": "Tuesday", "Holiday": "Holi"},
    {"Date": "2026-03-26", "Day": "Thursday", "Holiday": "Shri Ram Navami"},
    {"Date": "2026-03-31", "Day": "Tuesday", "Holiday": "Shri Mahavir Jayanti"},
    {"Date": "2026-04-03", "Day": "Friday", "Holiday": "Good Friday"},
    {"Date": "2026-04-14", "Day": "Tuesday", "Holiday": "Dr. Baba Saheb Ambedkar Jayanti"},
    {"Date": "2026-05-01", "Day": "Friday", "Holiday": "Maharashtra Day"},
    {"Date": "2026-05-28", "Day": "Thursday", "Holiday": "Bakri Id"},
    {"Date": "2026-06-26", "Day": "Friday", "Holiday": "Muharram"},
    {"Date": "2026-09-14", "Day": "Monday", "Holiday": "Ganesh Chaturthi"},
    {"Date": "2026-10-02", "Day": "Friday", "Holiday": "Mahatma Gandhi Jayanti"},
    {"Date": "2026-10-20", "Day": "Tuesday", "Holiday": "Dussehra"},
    {"Date": "2026-11-08", "Day": "Sunday", "Holiday": "Diwali Laxmi Pujan (Muhurat Trading)"},
    {"Date": "2026-11-10", "Day": "Tuesday", "Holiday": "Diwali-Balipratipada"},
    {"Date": "2026-11-24", "Day": "Tuesday", "Holiday": "Prakash Gurpurb Sri Guru Nanak Dev"},
    {"Date": "2026-12-25", "Day": "Friday", "Holiday": "Christmas"},
]

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS STYLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #060b18; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #080f1f; border-right: 1px solid rgba(255,255,255,0.05); }

/* Ticker Bar */
.ticker-wrapper {
    background: #0d172a; border: 1px solid rgba(59,130,246,0.2);
    border-radius: 8px; padding: 8px 15px; margin-bottom: 20px;
    display: flex; overflow-x: auto; gap: 20px; white-space: nowrap;
}
.ticker-item { font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
.t-green { color: #10b981; } .t-red { color: #ef4444; }

/* News Cards */
.news-card {
    background: #0f172a; border-left: 4px solid #3b82f6; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 12px; border-top: 1px solid rgba(255,255,255,0.05);
}
.news-title { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; text-decoration: none; }
.news-title:hover { color: #38bdf8; }
.news-meta { font-size: 0.75rem; color: #64748b; margin-top: 4px; }

/* Status Badges */
.status-badge { padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.76rem; display: inline-block; }
.bg-leading   { background:rgba(16,185,129,0.13); color:#10b981; border:1px solid rgba(16,185,129,0.28); }
.bg-improving { background:rgba(59,130,246,0.13); color:#3b82f6; border:1px solid rgba(59,130,246,0.28); }
.bg-weakening { background:rgba(245,158,11,0.13); color:#f59e0b; border:1px solid rgba(245,158,11,0.28); }
.bg-lagging   { background:rgba(239,68,68,0.13);  color:#ef4444; border:1px solid rgba(239,68,68,0.28);  }

/* Headers */
.brand-title {
    font-size: 1.8rem; font-weight: 800;
    background: linear-gradient(90deg, #fff 0%, #93c5fd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.rrg-table { width:100%; border-collapse:collapse; border-radius:12px; overflow:hidden; margin-top:14px; }
.rrg-table th { padding:10px; background:#0a1628; color:#64748b; font-size:0.75rem; text-align:left; }
.rrg-table td { padding:10px; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS & DATA FETCHERS
# ─────────────────────────────────────────────────────────────────────────────
def is_market_open() -> bool:
    now = datetime.now(IST_OFFSET)
    if now.weekday() >= 5:
        return False
    return dtime(9, 15) <= now.time() <= dtime(15, 30)

@st.cache_data(ttl=300)
def fetch_rss_news(query_term: str, max_items: int = 8) -> list:
    """Fetch live news from Google News RSS feed."""
    url = f"https://news.google.com/rss/search?q={query_term}&hl=en-IN&gl=IN&ceid=IN:en"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:max_items]:
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else "#"
                pubDate = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source = item.find("source").text if item.find("source") is not None else "News"
                items.append({"title": title, "link": link, "date": pubDate[:16], "source": source})
    except Exception:
        pass
    return items

@st.cache_data(ttl=120)
def fetch_running_sector_tickers() -> list:
    """Fetch live tickers for Nifty & major sectors."""
    tickers = {
        "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY IT": "^CNXIT",
        "NIFTY AUTO": "^CNXAUTO", "NIFTY PHARMA": "^CNXPHARMA", "NIFTY METAL": "^CNXMETAL"
    }
    raw = yf.download(list(tickers.values()), period="5d", interval="1d", progress=False)
    if raw.empty or "Close" not in raw.columns:
        return []
    
    close_df = raw["Close"]
    res = []
    for name, sym in tickers.items():
        if sym in close_df.columns:
            s = close_df[sym].dropna()
            if len(s) >= 2:
                cmp = float(s.iloc[-1])
                chg = ((cmp - float(s.iloc[-2])) / float(s.iloc[-2])) * 100
                res.append({"name": name, "cmp": round(cmp, 2), "chg": round(chg, 2)})
    return res

@st.cache_data(ttl=300)
def calculate_nifty_trend() -> dict:
    """Calculate Nifty trend status using EMA & RSI."""
    df = yf.download("^NSEI", period="1y", interval="1d", progress=False)
    if df.empty:
        return {}
    
    close = df["Close"].iloc[:, 0] if isinstance(df["Close"], pd.DataFrame) else df["Close"]
    cmp = float(close.iloc[-1])
    ema20 = float(close.ewm(span=20).mean().iloc[-1])
    ema50 = float(close.ewm(span=50).mean().iloc[-1])
    sma200 = float(close.rolling(200).mean().iloc[-1])
    
    # RSI Calculation
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    rsi = float(100 - (100 / (1 + rs)).iloc[-1])
    
    # Trend Analysis
    if cmp > ema20 > ema50 > sma200:
        status, color = "Strong Bullish 🚀", "#10b981"
    elif cmp < ema20 < ema50:
        status, color = "Bearish Trend 🔻", "#ef4444"
    else:
        status, color = "Sideways / Neutral ⚖️", "#f59e0b"
        
    return {
        "cmp": round(cmp, 2), "ema20": round(ema20, 2), "ema50": round(ema50, 2),
        "sma200": round(sma200, 2), "rsi": round(rsi, 2), "status": status, "color": color
    }

@st.cache_data(ttl=300)
def fetch_and_build_rrg(items_dict: dict, benchmark_ticker: str, interval: str = "1wk", period: int = 14) -> dict:
    all_tickers = list(set(list(items_dict.values()) + [benchmark_ticker]))
    raw = yf.download(all_tickers, period="2y", interval=interval, progress=False)
    if raw.empty or "Close" not in raw.columns:
        return {}
    
    df_close = raw["Close"]
    results = {}
    
    for name, ticker in items_dict.items():
        if ticker not in df_close.columns or ticker == benchmark_ticker:
            continue
        comb = pd.concat([df_close[ticker], df_close[benchmark_ticker]], axis=1).dropna()
        comb.columns = ["item", "bench"]
        if len(comb) < period * 2:
            continue
        
        rs = (comb["item"] / comb["bench"]) * 100
        rs_ratio = 100 + ((rs - rs.rolling(period).mean()) / (rs.rolling(period).std() + 1e-9)) * 10
        rs_mom = 100 + ((rs_ratio - rs_ratio.rolling(period).mean()) / (rs_ratio.rolling(period).std() + 1e-9)) * 10
        
        metrics = pd.DataFrame({"ratio": rs_ratio, "momentum": rs_mom}).dropna()
        if metrics.empty:
            continue
        
        cmp = float(df_close[ticker].dropna().iloc[-1])
        results[name] = {"metrics": metrics, "cmp": round(cmp, 2)}
        
    return results

# ─────────────────────────────────────────────────────────────────────────────
# TOP RUNNING TICKER BANNER
# ─────────────────────────────────────────────────────────────────────────────
running_tickers = fetch_running_sector_tickers()
if running_tickers:
    ticker_html = '<div class="ticker-wrapper">'
    for t in running_tickers:
        cls = "t-green" if t["chg"] >= 0 else "t-red"
        arrow = "▲" if t["chg"] >= 0 else "▼"
        ticker_html += f'<div class="ticker-item">{t["name"]}: <b>₹{t["cmp"]:,.2f}</b> <span class="{cls}">{arrow} {t["chg"]:+.2f}%</span></div>'
    ticker_html += '</div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="brand-title">GROW MORE TRADING INSTITUTE</div>', unsafe_allow_html=True)
st.caption("Live Market Intelligence • Nifty Trend • Sector RRG • Block Deals • Indian & World News")

with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    timeframe = st.selectbox("RRG Timeframe", ["1d", "1wk"], index=1, format_func=lambda x: "Daily" if x == "1d" else "Weekly")
    selected_sector_for_stocks = st.selectbox("Select Sector for Stocks", list(SECTOR_MAP.keys()))
    if st.button("🔄 Refresh All Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN TAB NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Nifty Trend & Summary",
    "🌐  Sector RRG Analytics",
    "🎯  Stock Drill-Down",
    "📰  Market News & Block Deals",
    "📅  Upcoming Holidays (2026)",
])

# ── TAB 1: NIFTY TREND & MARKET SUMMARY ──────────────────────────────────────
with tab1:
    nifty = calculate_nifty_trend()
    if nifty:
        st.markdown("### 🎯 Nifty 50 Trend Analyzer")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Nifty CMP", f"₹{nifty['cmp']:,.2f}")
        c2.metric("20 EMA", f"₹{nifty['ema20']:,.2f}")
        c3.metric("50 EMA", f"₹{nifty['ema50']:,.2f}")
        c4.metric("200 SMA", f"₹{nifty['sma200']:,.2f}")
        c5.metric("RSI (14)", f"{nifty['rsi']}")
        
        st.markdown(f"#### Market Trend Status: <span style='color:{nifty['color']}; font-weight:bold;'>{nifty['status']}</span>", unsafe_allow_html=True)
    else:
        st.warning("Could not compute Nifty Trend.")

# ── TAB 2: SECTOR RRG ANALYTICS ──────────────────────────────────────────────
with tab2:
    st.markdown("### 🌐 NSE Sector Relative Rotation Graph")
    sec_dict = {s: SECTOR_MAP[s]["index"] for s in SECTOR_MAP}
    rrg_data = fetch_and_build_rrg(sec_dict, BENCHMARK_SYMBOL, interval=timeframe)
    
    if rrg_data:
        fig = go.Figure()
        for idx, (name, data) in enumerate(rrg_data.items()):
            df = data["metrics"].tail(5)
            x_val, y_val = df["ratio"].iloc[-1], df["momentum"].iloc[-1]
            color = CHART_COLORS[idx % len(CHART_COLORS)]
            
            fig.add_trace(go.Scatter(
                x=[x_val], y=[y_val], mode="markers+text", name=name, text=[name],
                textposition="top center", marker=dict(size=12, color=color)
            ))
            
        fig.update_layout(
            title="NSE Sector Rotation (RS-Ratio vs RS-Momentum)",
            paper_bgcolor="#07101f", plot_bgcolor="#07101f", height=520,
            xaxis=dict(title="RS-Ratio", gridcolor="#0f1e35"),
            yaxis=dict(title="RS-Momentum", gridcolor="#0f1e35")
        )
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: STOCK DRILL DOWN ──────────────────────────────────────────────────
with tab3:
    st.markdown(f"### 🎯 Stocks in {selected_sector_for_stocks}")
    stk_map = SECTOR_MAP[selected_sector_for_stocks]["stocks"]
    bench_idx = SECTOR_MAP[selected_sector_for_stocks]["index"]
    stk_rrg = fetch_and_build_rrg(stk_map, bench_idx, interval=timeframe)
    
    if stk_rrg:
        stk_list = [{"Stock": k, "CMP": v["CMP"] if "CMP" in v else v["cmp"], "RS-Ratio": round(v["metrics"]["ratio"].iloc[-1], 2), "RS-Momentum": round(v["metrics"]["momentum"].iloc[-1], 2)} for k, v in stk_rrg.items()]
        st.dataframe(pd.DataFrame(stk_list), use_container_width=True)

# ── TAB 4: MARKET NEWS & BLOCK DEALS ─────────────────────────────────────────
with tab4:
    st.markdown("### 📰 Real-Time News & Intelligence Feed")
    n_col1, n_col2 = st.columns(2)
    
    with n_col1:
        st.markdown("#### 🇮🇳 Big Indian Market News")
        ind_news = fetch_rss_news("Indian+Stock+Market+Economy", max_items=6)
        for item in ind_news:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">📅 {item['date']} | 🏢 {item['source']}</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("#### 💥 Block Deals & Bulk Deals")
        block_news = fetch_rss_news("Block+Deal+NSE+BSE+India", max_items=5)
        for item in block_news:
            st.markdown(f"""
            <div class="news-card" style="border-left-color:#f59e0b;">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">📅 {item['date']} | 🏢 {item['source']}</div>
            </div>""", unsafe_allow_html=True)

    with n_col2:
        st.markdown("#### 🌍 Global / Worldwide Market News")
        world_news = fetch_rss_news("Global+Stock+Market+Fed+Inflation", max_items=6)
        for item in world_news:
            st.markdown(f"""
            <div class="news-card" style="border-left-color:#10b981;">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">📅 {item['date']} | 🏢 {item['source']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 📌 Upcoming Stock News & Earnings")
        stock_news = fetch_rss_news("NSE+Stock+Corporate+Action+Earnings", max_items=5)
        for item in stock_news:
            st.markdown(f"""
            <div class="news-card" style="border-left-color:#ec4899;">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">📅 {item['date']} | 🏢 {item['source']}</div>
            </div>""", unsafe_allow_html=True)

# ── TAB 5: UPCOMING HOLIDAYS ──────────────────────────────────────────────────
with tab5:
    st.markdown("### 📅 Upcoming NSE Trading Holidays Calendar (2026)")
    today_str = datetime.now(IST_OFFSET).strftime("%Y-%m-%d")
    
    holiday_df = pd.DataFrame(NSE_HOLIDAYS_2026)
    holiday_df["Status"] = holiday_df["Date"].apply(lambda x: "Passed" if x < today_str else "Upcoming ⏳")
    
    st.dataframe(holiday_df, use_container_width=True, height=450)
