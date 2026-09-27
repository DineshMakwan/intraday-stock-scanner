from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# Page Configuration - StockMojo Light Theme & Wide Layout
# ---------------------------------------------------------
st.set_page_config(
    page_title="StockMojo Style - Relative Rotation Graph",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# StockMojo Inspired CSS Styling
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    
    /* Navbar Styling */
    .mojo-navbar {
        background-color: #ffffff;
        padding: 14px 24px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .mojo-brand { font-size: 1.6rem; font-weight: 800; color: #1e40af; letter-spacing: -0.5px; }
    .mojo-tag { font-size: 0.9rem; color: #64748b; font-weight: 500; margin-left: 10px; }
    
    /* Quadrant Status Badges */
    .status-badge {
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }
    .bg-leading { background-color: #d1fae5; color: #065f46; border: 1px solid #10b981; }
    .bg-improving { background-color: #dbeafe; color: #1e40af; border: 1px solid #3b82f6; }
    .bg-weakening { background-color: #fef3c7; color: #92400e; border: 1px solid #f59e0b; }
    .bg-lagging { background-color: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }

    /* Customizing Streamlit Controls */
    .stMultiSelect, .stSelectbox { background-color: #ffffff; border-radius: 6px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Banner
st.markdown(
    """
    <div class="mojo-navbar">
        <div>
            <span class="mojo-brand">StockMojo</span>
            <span class="mojo-tag">| Relative Rotation Graph (RRG) Analytics</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NSE Sector Mapping Dictionary
# ---------------------------------------------------------
SECTOR_MAP = {
    "BANKNIFTY": {"index": "^NSEBANK", "fallback": "HDFCBANK.NS"},
    "SENSEX": {"index": "^BSESN", "fallback": "^BSESN"},
    "FINNIFTY": {"index": "NIFTY_FIN_SERVICE.NS", "fallback": "^CNXFIN"},
    "MIDCAP": {"index": "NIFTY_MIDSELECT.NS", "fallback": "^NSEMDCP50"},
    "AUTO": {"index": "^CNXAUTO", "fallback": "TATAMOTORS.NS"},
    "CAPITAL MRKT": {"index": "^CNXINFRA", "fallback": "LT.NS"},
    "CHEMICALS": {"index": "^CNXCMDT", "fallback": "PIDILITIND.NS"},
    "COMMODITIES": {"index": "^CNXCMDT", "fallback": "COALINDIA.NS"},
    "CONSR DURBL": {"index": "^CNXCONSUM", "fallback": "TITAN.NS"},
    "CONSUMPTION": {"index": "^CNXCONSUM", "fallback": "HINDUNILVR.NS"},
    "DEFENCE": {"index": "^CNXPSE", "fallback": "BEL.NS"},
    "ENERGY": {"index": "^CNXENERGY", "fallback": "RELIANCE.NS"},
    "FMCG": {"index": "^CNXFMCG", "fallback": "ITC.NS"},
    "HEALTHCARE": {"index": "^CNXPHARMA", "fallback": "SUNPHARMA.NS"},
    "INFRA": {"index": "^CNXINFRA", "fallback": "LT.NS"},
    "IT": {"index": "^CNXIT", "fallback": "TCS.NS"},
    "MEDIA": {"index": "^CNXMEDIA", "fallback": "SUNTV.NS"},
    "METAL": {"index": "^CNXMETAL", "fallback": "TATASTEEL.NS"},
    "OIL & GAS": {"index": "^CNXENERGY", "fallback": "ONGC.NS"},
    "PHARMA": {"index": "^CNXPHARMA", "fallback": "CIPLA.NS"},
    "PSU BANK": {"index": "^CNXPSUBANK", "fallback": "SBIN.NS"},
    "PVT BANK": {"index": "^NSEBANK", "fallback": "ICICIBANK.NS"},
    "REALTY": {"index": "^CNXREALTY", "fallback": "DLF.NS"},
    "SERVICES": {"index": "^CNXSERVICE", "fallback": "BHARTIARTL.NS"},
}

BENCHMARK_SYMBOL = "^NSEI"  # Nifty 50 Benchmark

# ---------------------------------------------------------
# Sidebar Settings - StockMojo Style
# ---------------------------------------------------------
st.sidebar.header("⚙️ RRG Settings")

benchmark_choice = st.sidebar.selectbox("Benchmark", options=["Nifty 50"], index=0)

timeframe_option = st.sidebar.radio(
    "Timeframe",
    options=["Daily", "Weekly"],
    index=1,
    horizontal=True,
)
interval_code = "1d" if timeframe_option == "Daily" else "1wk"

tail_len = st.sidebar.slider("Tail Length (Periods)", min_value=2, max_value=12, value=5)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Sectors Selection")

all_sector_names = list(SECTOR_MAP.keys())
col_btn1, col_btn2 = st.sidebar.columns(2)

selected_sectors = st.sidebar.multiselect(
    "Select Sectors to Show:",
    options=all_sector_names,
    default=all_sector_names,
)

# ---------------------------------------------------------
# Fast Concurrent Data Fetcher
# ---------------------------------------------------------
def fetch_single_ticker(ticker, interval):
    try:
        t_obj = yf.Ticker(ticker)
        df = t_obj.history(period="2y", interval=interval)
        if df is not None and not df.empty and len(df) > 10:
            return ticker, df[["Close"]]
    except Exception:
        pass
    return ticker, None

@st.cache_data(ttl=300)
def load_all_market_data(tickers, interval):
    data_store = {}
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(fetch_single_ticker, tickers, [interval] * len(tickers))
        for t, df in results:
            if df is not None:
                data_store[t] = df
    return data_store

# RRG Calculation Engine
def calculate_rrg_metrics(item_df, bench_df, period=14):
    combined = pd.concat([item_df["Close"], bench_df["Close"]], axis=1, join="inner").dropna()
    if len(combined) < (period * 2):
        return None

    item_prices = combined.iloc[:, 0]
    bench_prices = combined.iloc[:, 1]

    # Relative Strength Ratio
    rs = (item_prices / bench_prices) * 100
    rs_mean = rs.rolling(window=period).mean()
    rs_std = rs.rolling(window=period).std()
    rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-6)) * 10

    # Relative Momentum Ratio
    ratio_mean = rs_ratio.rolling(window=period).mean()
    ratio_std = rs_ratio.rolling(window=period).std()
    rs_momentum = 100 + ((rs_ratio - ratio_mean) / (ratio_std + 1e-6)) * 10

    return pd.DataFrame({"ratio": rs_ratio, "momentum": rs_momentum}).dropna()

# ---------------------------------------------------------
# Fetch Data & Build RRG Data
# ---------------------------------------------------------
needed_tickers = set([BENCHMARK_SYMBOL])
for sec in selected_sectors:
    needed_tickers.add(SECTOR_MAP[sec]["index"])
    needed_tickers.add(SECTOR_MAP[sec]["fallback"])

with st.spinner("Fetching Live Market Rotation Data..."):
    market_db = load_all_market_data(list(needed_tickers), interval_code)

bench_df = market_db.get(BENCHMARK_SYMBOL)

rrg_results = {}
if bench_df is not None:
    for sec_name in selected_sectors:
        info = SECTOR_MAP[sec_name]
        target_t = info["index"] if info["index"] in market_db else info["fallback"]
        if target_t in market_db:
            res_df = calculate_rrg_metrics(market_db[target_t], bench_df)
            if res_df is not None:
                rrg_results[sec_name] = res_df

# ---------------------------------------------------------
# StockMojo RRG Plotting Function
# ---------------------------------------------------------
def render_stockmojo_rrg(rrg_data, tail):
    fig = go.Figure()

    colors = [
        "#1e40af", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899",
        "#14b8a6", "#f97316", "#06b6d4", "#84cc16", "#0284c7", "#d97706",
        "#6366f1", "#a855f7", "#ec4899", "#ca8a04", "#059669", "#2563eb"
    ]

    min_x, max_x, min_y, max_y = 98.0, 102.0, 98.0, 102.0
    summary_rows = []

    for idx, (name, df) in enumerate(rrg_data.items()):
        hist = df.tail(tail)
        if hist.empty:
            continue

        x_vals = hist["ratio"].values
        y_vals = hist["momentum"].values
        head_x, head_y = x_vals[-1], y_vals[-1]

        min_x, max_x = min(min_x, min(x_vals)), max(max_x, max(x_vals))
        min_y, max_y = min(min_y, min(y_vals)), max(max_y, max(y_vals))

        color = colors[idx % len(colors)]

        # Quadrant Determination
        if head_x >= 100 and head_y >= 100:
            quad = "Leading"
            badge = "bg-leading"
        elif head_x >= 100 and head_y < 100:
            quad = "Weakening"
            badge = "bg-weakening"
        elif head_x < 100 and head_y < 100:
            quad = "Lagging"
            badge = "bg-lagging"
        else:
            quad = "Improving"
            badge = "bg-improving"

        summary_rows.append({
            "Sector": name,
            "RS-Ratio": round(head_x, 2),
            "RS-Momentum": round(head_y, 2),
            "Quadrant": quad,
            "BadgeClass": badge,
        })

        # Tail Rotation Line
        fig.add_trace(
            go.Scatter(
                x=x_vals, y=y_vals, mode="lines",
                line=dict(color=color, width=1.8),
                showlegend=False, hoverinfo="none",
            )
        )

        # Head Marker
        fig.add_trace(
            go.Scatter(
                x=[head_x], y=[head_y], mode="markers+text",
                name=name, text=[name], textposition="bottom center",
                textfont=dict(color=color, size=11, family="sans-serif"),
                marker=dict(size=8, color=color),
                hovertemplate=f"<b>{name}</b><br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad}<extra></extra>",
            )
        )

    pad_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.2
    pad_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.2
    x_range = [100 - pad_x, 100 + pad_x]
    y_range = [100 - pad_y, 100 + pad_y]

    # Layout Customization matching StockMojo
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=620,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            title="RS-Ratio",
            range=x_range,
            gridcolor="#f1f5f9",
            zeroline=False,
            color="#64748b"
        ),
        yaxis=dict(
            title="RS-Momentum",
            range=y_range,
            gridcolor="#f1f5f9",
            zeroline=False,
            color="#64748b"
        ),
        shapes=[
            # Center Axis Lines
            dict(type="line", x0=100, x1=100, y0=y_range[0], y1=y_range[1], line=dict(color="#cbd5e1", width=1.5)),
            dict(type="line", x0=x_range[0], x1=x_range[1], y0=100, y1=100, line=dict(color="#cbd5e1", width=1.5)),
        ],
        annotations=[
            dict(x=x_range[0] + 0.8, y=y_range[1] - 0.8, text="<b>Improving</b>", showarrow=False, font=dict(color="#2563eb", size=15)),
            dict(x=x_range[1] - 0.8, y=y_range[1] - 0.8, text="<b>Leading</b>", showarrow=False, font=dict(color="#16a34a", size=15)),
            dict(x=x_range[0] + 0.8, y=y_range[0] + 0.8, text="<b>Lagging</b>", showarrow=False, font=dict(color="#dc2626", size=15)),
            dict(x=x_range[1] - 0.8, y=y_range[0] + 0.8, text="<b>Weakening</b>", showarrow=False, font=dict(color="#ca8a04", size=15)),
        ],
    )

    return fig, pd.DataFrame(summary_rows)

# ---------------------------------------------------------
# Dashboard Rendering
# ---------------------------------------------------------
if rrg_results:
    fig, summary_df = render_stockmojo_rrg(rrg_results, tail_len)
    
    st.markdown("### Relative Rotation Graph (RRG)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Sector Quadrant Summary Table")

    if not summary_df.empty:
        table_rows = ""
        for _, row in summary_df.iterrows():
            table_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0; font-size: 0.9rem;">
                <td style="padding: 10px 14px; font-weight: 600; color:#0f172a;">{row['Sector']}</td>
                <td style="padding: 10px 14px;"><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
                <td style="padding: 10px 14px; font-weight: 500;">{row['RS-Ratio']}</td>
                <td style="padding: 10px 14px; font-weight: 500;">{row['RS-Momentum']}</td>
            </tr>
            """

        table_html = f"""
        <table style="width:100%; border-collapse:collapse; background-color:#ffffff; border-radius:8px; overflow:hidden; border: 1px solid #e2e8f0;">
            <thead>
                <tr style="background-color:#f1f5f9; text-align:left; color:#475569; font-size:0.85rem;">
                    <th style="padding:10px 14px;">Sector Name</th>
                    <th style="padding:10px 14px;">Quadrant</th>
                    <th style="padding:10px 14px;">RS-Ratio</th>
                    <th style="padding:10px 14px;">RS-Momentum</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """
        st.markdown(table_html, unsafe_allow_html=True)
else:
    st.warning("Data load karne mein dikkat aayi hai. Kripya page refresh karein.")
