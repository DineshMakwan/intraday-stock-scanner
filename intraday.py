"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     GROW MORE TRADING INSTITUTE — ADVANCED SECTOR RRG ANALYTICS v2.0        ║
║     Real-Time NSE Sector Rotation | Animated RRG | Smart Trade Intelligence  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Requirements (requirements.txt):
    streamlit>=1.32.0
    yfinance>=0.2.36
    plotly>=5.20.0
    pandas>=2.0.0
    numpy>=1.26.0

Run:
    streamlit run app.py
"""

from datetime import datetime, time as dtime, timezone, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grow More — Sector RRG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
BENCHMARK_SYMBOL = "^NSEI"
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

# Single source of truth for chart colors — no more copy-paste across functions
CHART_COLORS = [
    "#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899",
    "#14B8A6", "#F97316", "#6366F1", "#06B6D4", "#A855F7", "#EAB308",
    "#84CC16", "#F43F5E", "#D97706", "#059669", "#2563EB", "#7C3AED",
    "#DB2777", "#0284C7", "#16A34A", "#CA8A04", "#DC2626", "#4F46E5",
]

QUADRANT_CFG = {
    "Leading":   {"color": "#10B981", "badge": "bg-leading",   "icon": "🚀", "desc": "Strong RS & Rising Momentum"},
    "Weakening": {"color": "#F59E0B", "badge": "bg-weakening", "icon": "⚠️", "desc": "Strong RS but Momentum Slowing"},
    "Lagging":   {"color": "#EF4444", "badge": "bg-lagging",   "icon": "🔻", "desc": "Weak RS & Falling Momentum"},
    "Improving": {"color": "#3B82F6", "badge": "bg-improving", "icon": "⚡", "desc": "Weak RS but Momentum Gaining"},
}

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM DARK THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── BASE ─────────────────────────────────────────────────────────────────── */
.stApp { background: #060b18; color: #e2e8f0; }
[data-testid="stSidebar"] {
    background: #080f1f;
    border-right: 1px solid rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #94a3b8; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a1220; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
.stTabs [data-baseweb="tab-list"] { background: rgba(15,23,42,0.6); border-radius: 10px; padding: 4px; gap: 2px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #64748b; border-radius: 7px; font-weight: 500; font-size: 0.88rem; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background: rgba(59,130,246,0.15); color: #93c5fd; border-bottom: none; }

/* ── BRAND HEADER ─────────────────────────────────────────────────────────── */
.brand-header {
    background: linear-gradient(135deg, #0c1e3e 0%, #080f1f 60%, #0f172a 100%);
    padding: 22px 30px;
    border-radius: 16px;
    border: 1px solid rgba(59,130,246,0.18);
    border-left: 5px solid #3b82f6;
    margin-bottom: 24px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.5), 0 0 60px rgba(59,130,246,0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.brand-title {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: 0.3px;
    background: linear-gradient(90deg, #fff 0%, #93c5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.brand-subtitle { font-size: 0.88rem; color: #475569; margin-top: 5px; font-weight: 400; }
.live-container {
    display: flex; align-items: center; gap: 14px;
    background: rgba(6,11,24,0.8);
    padding: 10px 20px; border-radius: 40px;
    border: 1px solid rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
}
.live-badge {
    display: flex; align-items: center; gap: 7px;
    padding: 5px 13px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px;
}
.market-open  { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
.market-closed{ background: rgba(100,116,139,0.12); color: #94a3b8; border: 1px solid rgba(100,116,139,0.3); }
.live-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-active  { background: #ef4444; box-shadow: 0 0 8px #ef4444; animation: blink 1.4s ease-in-out infinite; }
.dot-inactive{ background: #475569; }
.clock-text  { font-size: 0.84rem; color: #38bdf8; font-weight: 600; font-family: 'Courier New', monospace; }
@keyframes blink { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.35;transform:scale(0.8);} }

/* ── KPI CARDS ────────────────────────────────────────────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin: 20px 0 28px; }
.kpi-card {
    background: rgba(12,20,40,0.8);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 13px; padding: 18px 20px;
    backdrop-filter: blur(8px);
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}
.kpi-card:hover { border-color: rgba(59,130,246,0.3); box-shadow: 0 0 24px rgba(59,130,246,0.08); transform: translateY(-2px); }
.kpi-label { font-size: 0.72rem; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.9px; margin-bottom: 8px; }
.kpi-value { font-size: 2rem; font-weight: 800; line-height: 1; }
.kpi-sub   { font-size: 0.78rem; margin-top: 5px; color: #475569; }
.c-green { color: #10b981; } .c-blue { color: #3b82f6; }
.c-amber { color: #f59e0b; } .c-red  { color: #ef4444; }
.c-white { color: #f1f5f9; } .c-pink { color: #ec4899; }

/* ── STATUS BADGES ────────────────────────────────────────────────────────── */
.status-badge { padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.76rem; display: inline-block; letter-spacing: 0.3px; }
.bg-leading   { background:rgba(16,185,129,0.13); color:#10b981; border:1px solid rgba(16,185,129,0.28); }
.bg-improving { background:rgba(59,130,246,0.13); color:#3b82f6; border:1px solid rgba(59,130,246,0.28); }
.bg-weakening { background:rgba(245,158,11,0.13); color:#f59e0b; border:1px solid rgba(245,158,11,0.28); }
.bg-lagging   { background:rgba(239,68,68,0.13);  color:#ef4444; border:1px solid rgba(239,68,68,0.28);  }
.bg-near-high { background:rgba(236,72,153,0.13); color:#ec4899; border:1px solid rgba(236,72,153,0.28); }
.bg-normal    { background:rgba(71,85,105,0.18);  color:#94a3b8; border:1px solid rgba(71,85,105,0.35);  }

/* ── DATA TABLE ───────────────────────────────────────────────────────────── */
.rrg-table { width:100%; border-collapse:collapse; border-radius:12px; overflow:hidden; margin-top:14px; }
.rrg-table thead tr  { background:#0a1628; }
.rrg-table th {
    padding:13px 16px; text-align:left;
    color:#475569; font-size:0.73rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.7px;
    border-bottom:1px solid rgba(255,255,255,0.05);
    white-space:nowrap;
}
.rrg-table tbody tr { border-bottom:1px solid rgba(255,255,255,0.04); transition:background 0.15s; }
.rrg-table tbody tr:hover { background:rgba(59,130,246,0.06); }
.rrg-table td { padding:12px 16px; font-size:0.87rem; color:#cbd5e1; vertical-align:middle; }
.td-name { font-weight:700; color:#f1f5f9; }
.td-cmp  { font-weight:700; color:#38bdf8; }
.td-high { font-weight:600; color:#94a3b8; }

/* ── SETUP CARDS ──────────────────────────────────────────────────────────── */
.setup-card { border-radius:13px; padding:18px 20px; margin-bottom:14px; border:1px solid; transition:transform 0.15s, box-shadow 0.15s; }
.setup-card:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(0,0,0,0.35); }
.card-long  { background:rgba(16,185,129,0.06); border-color:rgba(16,185,129,0.25); }
.card-short { background:rgba(239,68,68,0.06);  border-color:rgba(239,68,68,0.25); }
.card-title-long  { color:#10b981; font-size:1rem; font-weight:700; margin:0 0 10px; }
.card-title-short { color:#ef4444; font-size:1rem; font-weight:700; margin:0 0 10px; }
.card-row { font-size:0.87rem; color:#94a3b8; margin:5px 0; }
.card-row b { color:#e2e8f0; }
.card-target { color:#38bdf8; }
.card-sl     { color:#ef4444; }
.card-rr     { color:#f59e0b; font-weight:700; }

/* ── MONEY FLOW HIGHLIGHT CARDS ───────────────────────────────────────────── */
.flow-card { border-radius:13px; padding:20px 24px; border:1px solid; }
.flow-in  { background:rgba(16,185,129,0.07); border-color:rgba(16,185,129,0.22); }
.flow-out { background:rgba(239,68,68,0.07);  border-color:rgba(239,68,68,0.22);  }
.flow-title { font-size:0.82rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; margin:0 0 6px; }
.flow-sector{ font-size:1.4rem; font-weight:800; color:#f1f5f9; margin:2px 0 6px; }
.flow-meta  { font-size:0.84rem; color:#64748b; margin:0; }

/* ── SECTION HEADERS ──────────────────────────────────────────────────────── */
.section-header { font-size:1.05rem; font-weight:700; color:#f1f5f9; margin:0 0 4px; }
.section-sub    { font-size:0.84rem; color:#475569; margin-bottom:20px; }

/* ── FOOTER ───────────────────────────────────────────────────────────────── */
.footer {
    text-align:center; color:#1e3a5f; font-size:0.8rem;
    margin-top:52px; padding:20px;
    border-top:1px solid rgba(255,255,255,0.04);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MARKET HOURS HELPER
# ─────────────────────────────────────────────────────────────────────────────
def is_market_open() -> bool:
    now = datetime.now(IST_OFFSET)
    if now.weekday() >= 5:          # Saturday / Sunday
        return False
    market_start = dtime(9, 15)
    market_end   = dtime(15, 30)
    return market_start <= now.time() <= market_end


# ─────────────────────────────────────────────────────────────────────────────
# SECTOR MAP  — 23 NSE Sectors with correct benchmarks
# ─────────────────────────────────────────────────────────────────────────────
SECTOR_MAP = {
    "Nifty Bank": {
        "index": "^NSEBANK",
        "stocks": {
            "HDFCBANK":   "HDFCBANK.NS",   "ICICIBANK":  "ICICIBANK.NS",
            "AXISBANK":   "AXISBANK.NS",    "KOTAKBANK":  "KOTAKBANK.NS",
            "SBIN":       "SBIN.NS",        "INDUSINDBK": "INDUSINDBK.NS",
            "BANKBARODA": "BANKBARODA.NS",  "PNB":        "PNB.NS",
            "AUBANK":     "AUBANK.NS",      "FEDERALBNK": "FEDERALBNK.NS",
            "IDFCFIRSTB": "IDFCFIRSTB.NS", "BANDHANBNK": "BANDHANBNK.NS",
        },
    },
    "Nifty Private Bank": {
        "index": "^NSEBANK",
        "stocks": {
            "HDFCBANK":   "HDFCBANK.NS",   "ICICIBANK":  "ICICIBANK.NS",
            "AXISBANK":   "AXISBANK.NS",    "KOTAKBANK":  "KOTAKBANK.NS",
            "INDUSINDBK": "INDUSINDBK.NS", "FEDERALBNK": "FEDERALBNK.NS",
            "IDFCFIRSTB": "IDFCFIRSTB.NS", "BANDHANBNK": "BANDHANBNK.NS",
            "YESBANK":    "YESBANK.NS",     "RBLBANK":    "RBLBANK.NS",
        },
    },
    "Nifty PSU Bank": {
        "index": "^CNXPSUBANK",
        "stocks": {
            "SBIN":       "SBIN.NS",       "BANKBARODA": "BANKBARODA.NS",
            "PNB":        "PNB.NS",        "CANBK":      "CANBK.NS",
            "UNIONBANK":  "UNIONBANK.NS",  "INDIANB":    "INDIANB.NS",
            "BANKINDIA":  "BANKINDIA.NS",  "MAHABANK":   "MAHABANK.NS",
            "IOB":        "IOB.NS",        "UCOBANK":    "UCOBANK.NS",
            "CENTRALBK":  "CENTRALBK.NS",  "PSB":        "PSB.NS",
        },
    },
    "Nifty Financial Services": {
        "index": "^CNXFIN",
        "stocks": {
            "HDFCBANK":   "HDFCBANK.NS",   "ICICIBANK":  "ICICIBANK.NS",
            "BAJFINANCE": "BAJFINANCE.NS",  "BAJAJFINSV": "BAJAJFINSV.NS",
            "SBIN":       "SBIN.NS",        "PFC":        "PFC.NS",
            "REC":        "REC.NS",         "HDFCLIFE":   "HDFCLIFE.NS",
            "SBILIFE":    "SBILIFE.NS",     "ICICIPRULI": "ICICIPRULI.NS",
            "ICICIGI":    "ICICIGI.NS",     "CHOLAFIN":   "CHOLAFIN.NS",
            "SHRIRAMFIN": "SHRIRAMFIN.NS", "MUTHOOTFIN": "MUTHOOTFIN.NS",
            "HDFCAMC":    "HDFCAMC.NS",    "JIOFIN":     "JIOFIN.NS",
        },
    },
    "Nifty IT": {
        "index": "^CNXIT",
        "stocks": {
            "TCS":        "TCS.NS",        "INFY":       "INFY.NS",
            "HCLTECH":    "HCLTECH.NS",    "WIPRO":      "WIPRO.NS",
            "LTIM":       "LTIM.NS",       "TECHM":      "TECHM.NS",
            "PERSISTENT": "PERSISTENT.NS", "COFORGE":    "COFORGE.NS",
            "MPHASIS":    "MPHASIS.NS",    "LTTS":       "LTTS.NS",
        },
    },
    "Nifty Pharma": {
        "index": "^CNXPHARMA",
        "stocks": {
            "SUNPHARMA":  "SUNPHARMA.NS",  "CIPLA":      "CIPLA.NS",
            "DRREDDY":    "DRREDDY.NS",    "DIVISLAB":   "DIVISLAB.NS",
            "LUPIN":      "LUPIN.NS",      "TORNTPHARM": "TORNTPHARM.NS",
            "AUROPHARMA": "AUROPHARMA.NS", "ZYDUSLIFE":  "ZYDUSLIFE.NS",
            "ALKEM":      "ALKEM.NS",      "GLENMARK":   "GLENMARK.NS",
            "BIOCON":     "BIOCON.NS",     "IPCALAB":    "IPCALAB.NS",
            "LAURUSLABS": "LAURUSLABS.NS", "GRANULES":   "GRANULES.NS",
            "MANKIND":    "MANKIND.NS",    "SYNGENE":    "SYNGENE.NS",
            "NATCOPHARM": "NATCOPHARM.NS", "AJANTPHARM": "AJANTPHARM.NS",
        },
    },
    "Nifty Healthcare": {
        "index": "^CNXPHARMA",
        "stocks": {
            "APOLLOHOSP": "APOLLOHOSP.NS", "MAXHEALTH":  "MAXHEALTH.NS",
            "FORTIS":     "FORTIS.NS",     "MEDANTA":    "MEDANTA.NS",
            "NH":         "NH.NS",         "KIMS":       "KIMS.NS",
            "ASTERDM":    "ASTERDM.NS",    "LALPATHLAB": "LALPATHLAB.NS",
            "SUNPHARMA":  "SUNPHARMA.NS",  "CIPLA":      "CIPLA.NS",
            "DRREDDY":    "DRREDDY.NS",    "DIVISLAB":   "DIVISLAB.NS",
            "ABBOTINDIA": "ABBOTINDIA.NS", "PFIZER":     "PFIZER.NS",
            "GLAXO":      "GLAXO.NS",
        },
    },
    "Nifty Auto": {
        "index": "^CNXAUTO",
        "stocks": {
            "MARUTI":     "MARUTI.NS",     "M&M":        "M&M.NS",
            "TATAMOTORS": "TATAMOTORS.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
            "EICHERMOT":  "EICHERMOT.NS",  "HEROMOTOCO": "HEROMOTOCO.NS",
            "TVSMOTOR":   "TVSMOTOR.NS",   "BHARATFORG": "BHARATFORG.NS",
            "ASHOKLEY":   "ASHOKLEY.NS",   "BALKRISIND": "BALKRISIND.NS",
            "MRF":        "MRF.NS",        "MOTHERSON":  "MOTHERSON.NS",
            "TIINDIA":    "TIINDIA.NS",    "BOSCHLTD":   "BOSCHLTD.NS",
            "SONACOMS":   "SONACOMS.NS",
        },
    },
    "Nifty FMCG": {
        "index": "^CNXFMCG",
        "stocks": {
            "ITC":        "ITC.NS",        "HINDUNILVR": "HINDUNILVR.NS",
            "NESTLEIND":  "NESTLEIND.NS",  "BRITANNIA":  "BRITANNIA.NS",
            "TATACONSUM": "TATACONSUM.NS", "GODREJCP":   "GODREJCP.NS",
            "DABUR":      "DABUR.NS",      "MARICO":     "MARICO.NS",
            "COLPAL":     "COLPAL.NS",     "VBL":        "VBL.NS",
            "EMAMILTD":   "EMAMILTD.NS",   "PGHH":       "PGHH.NS",
        },
    },
    "Nifty Metal": {
        "index": "^CNXMETAL",
        "stocks": {
            "TATASTEEL":  "TATASTEEL.NS",  "JSWSTEEL":   "JSWSTEEL.NS",
            "JINDALSTEL": "JINDALSTEL.NS", "HINDALCO":   "HINDALCO.NS",
            "VEDL":       "VEDL.NS",       "NMDC":       "NMDC.NS",
            "SAIL":       "SAIL.NS",       "NATIONALUM": "NATIONALUM.NS",
            "COALINDIA":  "COALINDIA.NS",  "APLAPOLLO":  "APLAPOLLO.NS",
            "HINDZINC":   "HINDZINC.NS",   "HINDCOPPER": "HINDCOPPER.NS",
            "WELCORP":    "WELCORP.NS",    "RATNAMANI":  "RATNAMANI.NS",
            "MOIL":       "MOIL.NS",
        },
    },
    "Nifty Realty": {
        "index": "^CNXREALTY",
        "stocks": {
            "DLF":        "DLF.NS",        "GODREJPROP": "GODREJPROP.NS",
            "LODHA":      "LODHA.NS",      "PRESTIGE":   "PRESTIGE.NS",
            "OBEROIRLTY": "OBEROIRLTY.NS", "PHOENIXLTD": "PHOENIXLTD.NS",
            "ANANTRAJ":   "ANANTRAJ.NS",   "BRIGADE":    "BRIGADE.NS",
            "SOBHA":      "SOBHA.NS",      "ABREL":      "ABREL.NS",
            "EMBASSY":    "EMBASSY.NS",    "MINDSPACE":  "MINDSPACE.NS",
        },
    },
    "Nifty Energy": {
        "index": "^CNXENERGY",
        "stocks": {
            "RELIANCE":   "RELIANCE.NS",   "NTPC":       "NTPC.NS",
            "POWERGRID":  "POWERGRID.NS",  "ONGC":       "ONGC.NS",
            "BPCL":       "BPCL.NS",       "IOC":        "IOC.NS",
            "GAIL":       "GAIL.NS",       "TATAPOWER":  "TATAPOWER.NS",
            "ADANIGREEN": "ADANIGREEN.NS", "COALINDIA":  "COALINDIA.NS",
        },
    },
    "Nifty Oil & Gas": {
        "index": "^CNXENERGY",
        "stocks": {
            "RELIANCE":   "RELIANCE.NS",   "ONGC":       "ONGC.NS",
            "BPCL":       "BPCL.NS",       "IOC":        "IOC.NS",
            "GAIL":       "GAIL.NS",       "OIL":        "OIL.NS",
            "PETRONET":   "PETRONET.NS",   "MGL":        "MGL.NS",
            "IGL":        "IGL.NS",        "ATGL":       "ATGL.NS",
            "HINDPETRO":  "HINDPETRO.NS",  "CASTROLIND": "CASTROLIND.NS",
        },
    },
    "Nifty Cement": {
        "index": "^CNXINFRA",          # Infrastructure index — best proxy for cement on yfinance
        "stocks": {
            "ULTRACEMCO": "ULTRACEMCO.NS", "SHREECEM":   "SHREECEM.NS",
            "GRASIM":     "GRASIM.NS",     "AMBUJACEM":  "AMBUJACEM.NS",
            "ACC":        "ACC.NS",        "DALBHARAT":  "DALBHARAT.NS",
            "JKCEMENT":   "JKCEMENT.NS",   "RAMCOCEM":   "RAMCOCEM.NS",
            "BIRLACORPN": "BIRLACORPN.NS", "JKLAKSHMI":  "JKLAKSHMI.NS",
            "STARCEMENT": "STARCEMENT.NS", "NUVOCO":     "NUVOCO.NS",
            "ORIENTCEM":  "ORIENTCEM.NS",  "INDIACEM":   "INDIACEM.NS",
        },
    },
    "Nifty Chemicals": {
        "index": "^NSEI",              # No direct NSE Chemicals index on yfinance; use Nifty 50
        "stocks": {
            "PIDILITIND": "PIDILITIND.NS", "SRF":        "SRF.NS",
            "DEEPAKNTR":  "DEEPAKNTR.NS",  "AARTIIND":   "AARTIIND.NS",
            "TATACHEM":   "TATACHEM.NS",   "UPL":        "UPL.NS",
            "PIIND":      "PIIND.NS",      "NAVINFLUOR": "NAVINFLUOR.NS",
            "FLUOROCHEM": "FLUOROCHEM.NS", "ATUL":       "ATUL.NS",
            "PCBL":       "PCBL.NS",       "SUMICHEM":   "SUMICHEM.NS",
            "COROMANDEL": "COROMANDEL.NS", "BAYERCROP":  "BAYERCROP.NS",
            "DEEPAKFERT": "DEEPAKFERT.NS", "CHAMBLFERT": "CHAMBLFERT.NS",
        },
    },
    "Nifty Infrastructure": {
        "index": "^CNXINFRA",
        "stocks": {
            "LT":         "LT.NS",         "SIEMENS":    "SIEMENS.NS",
            "ABB":        "ABB.NS",        "HAL":        "HAL.NS",
            "BEL":        "BEL.NS",        "BHEL":       "BHEL.NS",
            "ADANIPORTS": "ADANIPORTS.NS", "IRCTC":      "IRCTC.NS",
            "CONCOR":     "CONCOR.NS",     "NTPC":       "NTPC.NS",
            "POWERGRID":  "POWERGRID.NS",  "TATAPOWER":  "TATAPOWER.NS",
            "INDIGO":     "INDIGO.NS",     "ULTRACEMCO": "ULTRACEMCO.NS",
        },
    },
    "Nifty Media": {
        "index": "^CNXMEDIA",
        "stocks": {
            "SUNTV":      "SUNTV.NS",      "ZEEL":       "ZEEL.NS",
            "PVRINOX":    "PVRINOX.NS",    "TV18BRDCST": "TV18BRDCST.NS",
            "NETWORK18":  "NETWORK18.NS",  "NAZARA":     "NAZARA.NS",
            "DISHTV":     "DISHTV.NS",     "HATHWAY":    "HATHWAY.NS",
            "TIPSMUSIC":  "TIPSMUSIC.NS",
        },
    },
    "Nifty Consumer Durables": {
        "index": "^CNXCONSUM",
        "stocks": {
            "TITAN":      "TITAN.NS",      "DIXON":      "DIXON.NS",
            "HAVELLS":    "HAVELLS.NS",    "VOLTAS":     "VOLTAS.NS",
            "CROMPTON":   "CROMPTON.NS",   "AMBER":      "AMBER.NS",
            "BLUESTARCO": "BLUESTARCO.NS", "KALYANKJIL": "KALYANKJIL.NS",
            "BATAINDIA":  "BATAINDIA.NS",  "KAJARIACER": "KAJARIACER.NS",
            "WHIRLPOOL":  "WHIRLPOOL.NS",  "PGEL":       "PGEL.NS",
        },
    },
    "Nifty Commodities": {
        "index": "^CNXCMDT",
        "stocks": {
            "RELIANCE":   "RELIANCE.NS",   "TATASTEEL":  "TATASTEEL.NS",
            "HINDALCO":   "HINDALCO.NS",   "VEDL":       "VEDL.NS",
            "ONGC":       "ONGC.NS",       "COALINDIA":  "COALINDIA.NS",
            "PIDILITIND": "PIDILITIND.NS", "UPL":        "UPL.NS",
            "SHREECEM":   "SHREECEM.NS",   "ULTRACEMCO": "ULTRACEMCO.NS",
            "GRASIM":     "GRASIM.NS",     "NMDC":       "NMDC.NS",
        },
    },
    "Nifty Consumption": {
        "index": "^CNXCONSUM",
        "stocks": {
            "ITC":        "ITC.NS",        "HINDUNILVR": "HINDUNILVR.NS",
            "MARUTI":     "MARUTI.NS",     "TITAN":      "TITAN.NS",
            "NESTLEIND":  "NESTLEIND.NS",  "BRITANNIA":  "BRITANNIA.NS",
            "TATACONSUM": "TATACONSUM.NS", "GODREJCP":   "GODREJCP.NS",
            "DABUR":      "DABUR.NS",      "MARICO":     "MARICO.NS",
            "VBL":        "VBL.NS",        "COLPAL":     "COLPAL.NS",
            "TRENT":      "TRENT.NS",      "EICHERMOT":  "EICHERMOT.NS",
        },
    },
    "Nifty PSE": {
        "index": "^CNXPSE",
        "stocks": {
            "NTPC":       "NTPC.NS",       "POWERGRID":  "POWERGRID.NS",
            "ONGC":       "ONGC.NS",       "COALINDIA":  "COALINDIA.NS",
            "BPCL":       "BPCL.NS",       "IOC":        "IOC.NS",
            "GAIL":       "GAIL.NS",       "SBIN":       "SBIN.NS",
            "PFC":        "PFC.NS",        "REC":        "REC.NS",
            "BEL":        "BEL.NS",        "HAL":        "HAL.NS",
            "NHPC":       "NHPC.NS",       "SJVN":       "SJVN.NS",
            "NMDC":       "NMDC.NS",       "SAIL":       "SAIL.NS",
            "CONCOR":     "CONCOR.NS",     "IRCTC":      "IRCTC.NS",
        },
    },
    "Nifty MidSmall Healthcare": {
        "index": "^CNXPHARMA",
        "stocks": {
            "NATCOPHARM": "NATCOPHARM.NS", "IPCALAB":    "IPCALAB.NS",
            "AJANTPHARM": "AJANTPHARM.NS", "WOCKPHARMA": "WOCKPHARMA.NS",
            "PPLPHARMA":  "PPLPHARMA.NS",  "GLAND":      "GLAND.NS",
            "MEDANTA":    "MEDANTA.NS",    "NEULANDLAB": "NEULANDLAB.NS",
            "GLENMARK":   "GLENMARK.NS",   "LALPATHLAB": "LALPATHLAB.NS",
            "AUROPHARMA": "AUROPHARMA.NS", "GRANULES":   "GRANULES.NS",
            "ALKEM":      "ALKEM.NS",      "LAURUSLABS": "LAURUSLABS.NS",
            "SYNGENE":    "SYNGENE.NS",    "BIOCON":     "BIOCON.NS",
        },
    },
    "Nifty REITs": {
        "index": "^CNXREALTY",
        "stocks": {
            "EMBASSY":    "EMBASSY.NS",    "MINDSPACE":  "MINDSPACE.NS",
            "BIRET":      "BIRET.NS",      "NXST":       "NXST.NS",
            "LODHA":      "LODHA.NS",      "DLF":        "DLF.NS",
            "PRESTIGE":   "PRESTIGE.NS",   "BRIGADE":    "BRIGADE.NS",
            "PHOENIXLTD": "PHOENIXLTD.NS", "OBEROIRLTY": "OBEROIRLTY.NS",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ RRG Controls")

    timeframe = st.selectbox(
        "Timeframe",
        options=["1d", "1wk"],
        index=1,
        format_func=lambda x: "📅 Daily Rotation" if x == "1d" else "📆 Weekly Rotation",
    )

    tail_len = st.slider("Trail Length (periods)", min_value=2, max_value=15, value=5,
                         help="Number of historical data points shown as tail on RRG chart")

    rrg_period = st.slider("RS Smoothing Period", min_value=5, max_value=26, value=14,
                           help="Look-back window for RS-Ratio and RS-Momentum calculation")

    st.markdown("---")
    st.markdown("### 🔍 Stock Drill-Down")
    selected_sector_for_stocks = st.selectbox(
        "Select Sector", options=list(SECTOR_MAP.keys()), index=0
    )

    st.markdown("---")
    st.markdown("### 🔥 52-Week High Filter")
    high_threshold = st.slider(
        "Near 52W High Threshold (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.5,
        help="Sectors/stocks within this % of their 52-week high are flagged"
    )

    st.markdown("---")
    if st.button("🔄 Refresh Market Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        "<div style='font-size:0.75rem; color:#334155; margin-top:12px;'>"
        "Data cached for 5 min. Click Refresh for live update.</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def extract_field_df(raw_data: pd.DataFrame, field: str = "Close") -> pd.DataFrame:
    """Safely extract a price field from single or multi-ticker yfinance download."""
    if raw_data.empty:
        return pd.DataFrame()
    if isinstance(raw_data.columns, pd.MultiIndex):
        if field in raw_data.columns.get_level_values(0):
            return raw_data[field].copy()
        return pd.DataFrame()
    if field in raw_data.columns:
        return raw_data[[field]].copy()
    if len(raw_data.columns) == 1:
        df = raw_data.copy()
        df.columns = [field]
        return df
    return raw_data.copy()


def get_quadrant(ratio: float, momentum: float) -> tuple:
    """Return (name, description, badge_class, hex_color) for given RS coordinates."""
    if ratio >= 100 and momentum >= 100:
        q = "Leading"
    elif ratio >= 100 and momentum < 100:
        q = "Weakening"
    elif ratio < 100 and momentum < 100:
        q = "Lagging"
    else:
        q = "Improving"
    cfg = QUADRANT_CFG[q]
    return q, f"{cfg['icon']} {cfg['desc']}", cfg["badge"], cfg["color"]


def calculate_rrg_metrics(
    data_df: pd.DataFrame,
    item_ticker: str,
    bench_ticker: str,
    period: int = 14,
) -> pd.DataFrame | None:
    """
    Compute RS-Ratio and RS-Momentum (JdK RS methodology).
    Returns DataFrame with columns ['ratio', 'momentum'] or None on insufficient data.
    """
    if item_ticker not in data_df.columns or bench_ticker not in data_df.columns:
        return None

    combined = pd.concat(
        [data_df[item_ticker], data_df[bench_ticker]], axis=1, join="inner"
    ).dropna()
    combined.columns = ["item", "bench"]

    if len(combined) < period * 3:
        return None

    rs = (combined["item"] / combined["bench"]) * 100
    rs_mean = rs.rolling(period).mean()
    rs_std  = rs.rolling(period).std()
    rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-9)) * 10

    rm_mean = rs_ratio.rolling(period).mean()
    rm_std  = rs_ratio.rolling(period).std()
    rs_momentum = 100 + ((rs_ratio - rm_mean) / (rm_std + 1e-9)) * 10

    return pd.DataFrame({"ratio": rs_ratio, "momentum": rs_momentum}).dropna()


def compute_volatility_sl(prices: pd.Series, lookback: int = 20) -> float:
    """Return stop-loss % based on recent price volatility (capped 3%-8%)."""
    if len(prices) < lookback:
        return 4.0
    daily_vol = prices.pct_change().dropna().tail(lookback).std() * 100
    return float(np.clip(daily_vol * 1.5, 3.0, 8.0))


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH — CACHED
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_and_build_rrg(
    items_dict: dict,
    benchmark_ticker: str,
    interval: str,
    period: int = 14,
) -> dict:
    """
    Download 2-year OHLCV data for all tickers in one batch call,
    then compute RRG metrics for each item vs the benchmark.
    Returns dict: { display_name: {metrics, prices, cmp, high_52w, dist_52w, ticker} }
    """
    all_tickers = list(set(list(items_dict.values()) + [benchmark_ticker, BENCHMARK_SYMBOL]))

    try:
        raw = yf.download(all_tickers, period="2y", interval=interval,
                          progress=False, auto_adjust=True)
    except Exception:
        return {}

    if raw.empty:
        return {}

    df_close = extract_field_df(raw, "Close")
    df_high  = extract_field_df(raw, "High")

    if not isinstance(df_close.index, pd.DatetimeIndex):
        df_close.index = pd.to_datetime(df_close.index)
    if not isinstance(df_high.index, pd.DatetimeIndex):
        df_high.index = pd.to_datetime(df_high.index)

    # Resample to weekly end-of-week if needed
    if interval == "1wk":
        df_close = df_close.resample("W").last()
        df_high  = df_high.resample("W").max()

    # Choose best available benchmark
    active_bench = benchmark_ticker
    if active_bench not in df_close.columns or df_close[active_bench].dropna().empty:
        active_bench = BENCHMARK_SYMBOL

    results = {}
    for name, ticker in items_dict.items():
        if ticker not in df_close.columns or df_close[ticker].dropna().empty:
            continue

        metrics = calculate_rrg_metrics(df_close, ticker, active_bench, period)
        if metrics is None or metrics.empty:
            continue

        cmp     = float(df_close[ticker].dropna().iloc[-1])
        high_52w = float(df_high[ticker].dropna().max()) if ticker in df_high.columns else cmp
        dist_52w = round(((high_52w - cmp) / high_52w) * 100, 2) if high_52w > 0 else 0.0

        results[name] = {
            "metrics":  metrics,
            "prices":   df_close[ticker].dropna(),
            "cmp":      round(cmp, 2),
            "high_52w": round(high_52w, 2),
            "dist_52w": dist_52w,
            "ticker":   ticker,
        }

    return results


@st.cache_data(ttl=300, show_spinner=False)
def fetch_pair_data(t1: str, t2: str, interval: str) -> pd.DataFrame:
    """Cached pair data download."""
    try:
        raw = yf.download([t1, t2, BENCHMARK_SYMBOL], period="1y",
                          interval=interval, progress=False, auto_adjust=True)
        return raw
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def calculate_sector_money_flow(_sector_map: dict) -> pd.DataFrame:
    """
    SINGLE batched yfinance download for ALL sector stocks,
    then compute Price×Volume money flow score per sector.
    """
    ticker_list: list[str] = []
    sector_tickers: dict[str, list[str]] = {}

    for sec_name, sec_info in _sector_map.items():
        tickers = list(sec_info["stocks"].values())
        sector_tickers[sec_name] = tickers
        ticker_list.extend(tickers)

    unique_tickers = list(set(ticker_list))

    try:
        raw = yf.download(unique_tickers, period="5d", interval="1d",
                          progress=False, auto_adjust=True)
    except Exception:
        return pd.DataFrame()

    if raw.empty:
        return pd.DataFrame()

    close_df = extract_field_df(raw, "Close")
    vol_df   = extract_field_df(raw, "Volume")

    summary = []
    for sec_name, tickers in sector_tickers.items():
        scores, lb, sb, lu, sc = [], 0, 0, 0, 0

        for tk in tickers:
            if tk not in close_df.columns or tk not in vol_df.columns:
                continue
            p = close_df[tk].dropna()
            v = vol_df[tk].dropna()
            if len(p) < 2 or len(v) < 2:
                continue

            p_chg = ((p.iloc[-1] - p.iloc[-2]) / (abs(p.iloc[-2]) + 1e-9)) * 100
            v_prev = v.iloc[-2]
            v_chg  = ((v.iloc[-1] - v_prev) / (abs(v_prev) + 1e-9)) * 100 if v_prev > 0 else 0.0

            if   p_chg > 0 and v_chg > 0:  lb += 1
            elif p_chg < 0 and v_chg > 0:  sb += 1
            elif p_chg < 0 and v_chg <= 0: lu += 1
            else:                            sc += 1

            scores.append(p_chg * (1 + v_chg / 100))

        if not scores:
            continue

        n = len(scores)
        dominant = max(
            {"Long Buildup 🟢": lb, "Short Buildup 🔴": sb,
             "Long Unwinding 🟡": lu, "Short Covering 🔵": sc},
            key=lambda k: {"Long Buildup 🟢": lb, "Short Buildup 🔴": sb,
                           "Long Unwinding 🟡": lu, "Short Covering 🔵": sc}[k],
        )
        summary.append({
            "Sector":          sec_name,
            "Flow Score":      round(float(np.mean(scores)), 2),
            "Dominant Signal": dominant,
            "Long Buildup 🟢": f"{lb}/{n}",
            "Short Buildup 🔴": f"{sb}/{n}",
            "Long Unwinding 🟡": f"{lu}/{n}",
            "Short Covering 🔵": f"{sc}/{n}",
        })

    df = pd.DataFrame(summary)
    if not df.empty:
        df = df.sort_values("Flow Score", ascending=False).reset_index(drop=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# RRG CHART RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_rrg_chart(
    rrg_data: dict,
    title: str,
    tail: int = 5,
    thresh: float = 5.0,
) -> tuple[go.Figure, pd.DataFrame]:
    """Render the Relative Rotation Graph and return (figure, summary_df)."""
    fig = go.Figure()
    summary = []

    all_x, all_y = [], []

    for idx, (name, item) in enumerate(rrg_data.items()):
        df      = item["metrics"]
        cmp     = item["cmp"]
        high_52w = item["high_52w"]
        dist_52w = item["dist_52w"]

        history = df.tail(tail)
        if history.empty:
            continue

        x_vals = history["ratio"].values
        y_vals = history["momentum"].values
        hx, hy = x_vals[-1], y_vals[-1]

        all_x.extend(x_vals)
        all_y.extend(y_vals)

        quad_name, desc, badge_cls, quad_color = get_quadrant(hx, hy)
        color = CHART_COLORS[idx % len(CHART_COLORS)]

        mom_change  = hy - y_vals[-2] if len(y_vals) > 1 else 0
        trend_arrow = "▲" if mom_change > 0 else "▼"
        trend_color = "#10b981" if mom_change > 0 else "#ef4444"

        is_near      = dist_52w <= thresh
        near_status  = f"🔥 {dist_52w:.1f}%" if is_near else f"{dist_52w:.1f}%"
        near_badge   = "bg-near-high" if is_near else "bg-normal"

        # Trail line (dashed, fading)
        if len(x_vals) > 1:
            fig.add_trace(go.Scatter(
                x=x_vals[:-1], y=y_vals[:-1],
                mode="lines",
                line=dict(color=color, width=1.5, dash="dot"),
                opacity=0.45, showlegend=False, hoverinfo="none",
            ))

        # Head marker with label
        fig.add_trace(go.Scatter(
            x=[hx], y=[hy],
            mode="markers+text",
            name=name,
            text=[name],
            textposition="top center",
            textfont=dict(color="#e2e8f0", size=10, family="Inter, sans-serif"),
            marker=dict(
                size=13, color=color,
                line=dict(width=2, color="rgba(255,255,255,0.25)"),
                symbol="circle",
            ),
            hovertemplate=(
                f"<b>{name}</b><br>"
                f"CMP: ₹{cmp:,.2f}  |  52W High: ₹{high_52w:,.2f}<br>"
                f"Dist from High: {dist_52w:.1f}%<br>"
                f"RS-Ratio: {hx:.2f}  |  RS-Mom: {hy:.2f}<br>"
                f"Quadrant: <b>{quad_name}</b><br>"
                f"Momentum Trend: {trend_arrow}<extra></extra>"
            ),
        ))

        summary.append({
            "Name":           name,
            "RS-Ratio":       round(float(hx), 2),
            "RS-Momentum":    round(float(hy), 2),
            "Quadrant":       quad_name,
            "Status":         desc,
            "BadgeClass":     badge_cls,
            "Trend":          f'<span style="color:{trend_color};">{trend_arrow} {"Up" if mom_change > 0 else "Down"}</span>',
            "CMP":            cmp,
            "52W High":       high_52w,
            "Dist 52W High (%)": dist_52w,
            "Near 52W High":  near_status,
            "NearBadgeClass": near_badge,
        })

    # Dynamic axis padding
    if all_x and all_y:
        pad_x = max(abs(100 - min(all_x)), abs(max(all_x) - 100)) + 2.0
        pad_y = max(abs(100 - min(all_y)), abs(max(all_y) - 100)) + 2.0
    else:
        pad_x = pad_y = 3.0

    xr = [100 - pad_x, 100 + pad_x]
    yr = [100 - pad_y, 100 + pad_y]

    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#93c5fd", family="Inter, sans-serif")),
        paper_bgcolor="#07101f",
        plot_bgcolor="#07101f",
        height=580,
        showlegend=False,
        margin=dict(l=50, r=30, t=50, b=50),
        xaxis=dict(title="RS-Ratio  →  Relative Strength", range=xr,
                   gridcolor="#0f1e35", color="#475569", zeroline=False,
                   tickfont=dict(size=11, color="#475569")),
        yaxis=dict(title="RS-Momentum  →  Rate of Change", range=yr,
                   gridcolor="#0f1e35", color="#475569", zeroline=False,
                   tickfont=dict(size=11, color="#475569")),
        shapes=[
            # Quadrant fills
            dict(type="rect", x0=100, x1=xr[1], y0=100, y1=yr[1],
                 fillcolor="rgba(16,185,129,0.06)", line_width=0, layer="below"),
            dict(type="rect", x0=100, x1=xr[1], y0=yr[0], y1=100,
                 fillcolor="rgba(245,158,11,0.06)", line_width=0, layer="below"),
            dict(type="rect", x0=xr[0], x1=100, y0=yr[0], y1=100,
                 fillcolor="rgba(239,68,68,0.06)",  line_width=0, layer="below"),
            dict(type="rect", x0=xr[0], x1=100, y0=100, y1=yr[1],
                 fillcolor="rgba(59,130,246,0.06)", line_width=0, layer="below"),
            # Crosshair lines
            dict(type="line", x0=100, x1=100, y0=yr[0], y1=yr[1],
                 line=dict(color="#1e3a5f", width=1.5, dash="dash")),
            dict(type="line", x0=xr[0], x1=xr[1], y0=100, y1=100,
                 line=dict(color="#1e3a5f", width=1.5, dash="dash")),
        ],
        annotations=[
            dict(x=(100 + xr[1]) / 2, y=(100 + yr[1]) / 2,
                 text="<b>LEADING</b>",  showarrow=False,
                 font=dict(color="rgba(16,185,129,0.25)", size=22, family="Inter")),
            dict(x=(100 + xr[1]) / 2, y=(100 + yr[0]) / 2,
                 text="<b>WEAKENING</b>", showarrow=False,
                 font=dict(color="rgba(245,158,11,0.25)", size=22, family="Inter")),
            dict(x=(100 + xr[0]) / 2, y=(100 + yr[0]) / 2,
                 text="<b>LAGGING</b>",  showarrow=False,
                 font=dict(color="rgba(239,68,68,0.25)",  size=22, family="Inter")),
            dict(x=(100 + xr[0]) / 2, y=(100 + yr[1]) / 2,
                 text="<b>IMPROVING</b>", showarrow=False,
                 font=dict(color="rgba(59,130,246,0.25)", size=22, family="Inter")),
        ],
    )

    summary_df = pd.DataFrame(summary, columns=[
        "Name", "RS-Ratio", "RS-Momentum", "Quadrant", "Status",
        "BadgeClass", "Trend", "CMP", "52W High", "Dist 52W High (%)",
        "Near 52W High", "NearBadgeClass",
    ])
    return fig, summary_df


# ─────────────────────────────────────────────────────────────────────────────
# STYLED TABLE RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_styled_table(df: pd.DataFrame, col_name: str = "Name", sort_key: str = "") -> None:
    """Render a premium HTML data table with optional sort."""
    if df is None or df.empty:
        st.info("No items in this category right now.")
        return

    # Sort control
    sort_options = ["RS-Ratio", "RS-Momentum", "Dist 52W High (%)", "CMP", "Quadrant"]
    col_s, _ = st.columns([2, 6])
    sort_by = col_s.selectbox(
        "Sort by", sort_options, index=0, key=f"sort_{col_name}_{sort_key}"
    )
    ascending = sort_by in ["Dist 52W High (%)", "Quadrant"]
    df = df.sort_values(sort_by, ascending=ascending)

    rows_html = ""
    for _, row in df.iterrows():
        rows_html += f"""
        <tr>
          <td class="td-name">{row['Name']}</td>
          <td><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
          <td style="font-weight:600; color:#e2e8f0;">{row['RS-Ratio']:.2f}</td>
          <td style="font-weight:600; color:#e2e8f0;">{row['RS-Momentum']:.2f}</td>
          <td>{row['Trend']}</td>
          <td class="td-cmp">₹{row['CMP']:,.2f}</td>
          <td class="td-high">₹{row['52W High']:,.2f}</td>
          <td style="color:{'#10b981' if row['Dist 52W High (%)'] <= 5 else '#94a3b8'}; font-weight:600;">
              {row['Dist 52W High (%)']:.1f}%
          </td>
          <td><span class="status-badge {row['NearBadgeClass']}">{row['Near 52W High']}</span></td>
        </tr>"""

    table = f"""
    <div style="overflow-x:auto;">
    <table class="rrg-table">
      <thead>
        <tr>
          <th>{col_name}</th>
          <th>Quadrant</th>
          <th>RS-Ratio</th>
          <th>RS-Momentum</th>
          <th>Trend</th>
          <th>CMP (₹)</th>
          <th>52W High</th>
          <th>Dist High</th>
          <th>Near 52W High (&le;{high_threshold}%)</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>"""

    st.markdown(table, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPI SUMMARY CARDS
# ─────────────────────────────────────────────────────────────────────────────
def render_kpi_summary(rrg_data: dict, thresh: float) -> None:
    counts = {"Leading": 0, "Improving": 0, "Weakening": 0, "Lagging": 0}
    near_high = 0
    total = 0

    for item in rrg_data.values():
        df = item["metrics"]
        if df.empty:
            continue
        q, *_ = get_quadrant(df["ratio"].iloc[-1], df["momentum"].iloc[-1])
        counts[q] += 1
        if item["dist_52w"] <= thresh:
            near_high += 1
        total += 1

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Tracked</div>
        <div class="kpi-value c-white">{total}</div>
        <div class="kpi-sub">NSE Sectors / Stocks</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🚀 Leading</div>
        <div class="kpi-value c-green">{counts['Leading']}</div>
        <div class="kpi-sub">Bullish momentum & RS</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">⚡ Improving</div>
        <div class="kpi-value c-blue">{counts['Improving']}</div>
        <div class="kpi-sub">Rising momentum</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">⚠️ Weakening</div>
        <div class="kpi-value c-amber">{counts['Weakening']}</div>
        <div class="kpi-sub">Momentum slowing</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🔻 Lagging</div>
        <div class="kpi-value c-red">{counts['Lagging']}</div>
        <div class="kpi-sub">Weak RS & momentum</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">🔥 Near 52W High</div>
        <div class="kpi-value c-pink">{near_high}</div>
        <div class="kpi-sub">Within {thresh:.0f}% of highs</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANIMATED RRG
# ─────────────────────────────────────────────────────────────────────────────
def render_animated_rrg(rrg_data: dict, lookback: int = 12) -> None:
    if not rrg_data:
        st.warning("No data available for animation.")
        return

    # Find intersection of all dates
    common_dates = None
    for item in rrg_data.values():
        dates = set(item["metrics"].index)
        common_dates = dates if common_dates is None else common_dates & dates

    if not common_dates:
        st.warning("Not enough overlapping data for animation.")
        return

    sorted_dates = sorted(common_dates)[-lookback:]
    if len(sorted_dates) < 3:
        st.warning("Insufficient date range for animation.")
        return

    # Compute dynamic axis range from ALL animation data
    all_ratios, all_moms = [], []
    for item in rrg_data.values():
        df = item["metrics"]
        for dt in sorted_dates:
            if dt in df.index:
                all_ratios.append(df.loc[dt, "ratio"])
                all_moms.append(df.loc[dt, "momentum"])

    pad_x = max(abs(100 - min(all_ratios)), abs(max(all_ratios) - 100)) + 2.0 if all_ratios else 4.0
    pad_y = max(abs(100 - min(all_moms)),   abs(max(all_moms)   - 100)) + 2.0 if all_moms   else 4.0
    xr = [100 - pad_x, 100 + pad_x]
    yr = [100 - pad_y, 100 + pad_y]

    init_date = sorted_dates[0]
    fig = go.Figure()

    for idx, (name, item) in enumerate(rrg_data.items()):
        df    = item["metrics"]
        color = CHART_COLORS[idx % len(CHART_COLORS)]
        if init_date in df.index:
            fig.add_trace(go.Scatter(
                x=[df.loc[init_date, "ratio"]],
                y=[df.loc[init_date, "momentum"]],
                mode="markers+text", name=name,
                text=[name], textposition="top center",
                textfont=dict(size=10, color="#e2e8f0"),
                marker=dict(size=12, color=color,
                            line=dict(width=1.5, color="rgba(255,255,255,0.2)")),
            ))

    frames = []
    for dt in sorted_dates:
        frame_data = []
        date_str = pd.to_datetime(dt).strftime("%d %b %Y")
        for idx, (name, item) in enumerate(rrg_data.items()):
            df    = item["metrics"]
            color = CHART_COLORS[idx % len(CHART_COLORS)]
            if dt not in df.index:
                continue
            sub = df.loc[:dt].tail(4)
            if sub.empty:
                continue
            xs = sub["ratio"].values
            ys = sub["momentum"].values
            n  = len(xs)
            labels  = [""] * (n - 1) + [name]
            sizes   = [6]  * (n - 1) + [13]
            frame_data.append(go.Scatter(
                x=xs, y=ys,
                mode="lines+markers+text",
                name=name,
                text=labels,
                textposition="top center",
                textfont=dict(size=10, color="#e2e8f0"),
                marker=dict(size=sizes, color=color,
                            line=dict(width=1, color="rgba(255,255,255,0.15)")),
                line=dict(color=color, width=2),
            ))
        frames.append(go.Frame(
            data=frame_data, name=date_str,
            layout=dict(title=dict(text=f"🎬 Sector Rotation — {date_str}",
                                   font=dict(color="#93c5fd", size=15))),
        ))

    fig.frames = frames
    fig.update_layout(
        title=dict(text="🎬 Interactive Sector Rotation — Press ▶ to Play",
                   font=dict(color="#93c5fd", size=15, family="Inter")),
        paper_bgcolor="#07101f", plot_bgcolor="#07101f",
        height=620, margin=dict(l=50, r=30, t=55, b=80),
        xaxis=dict(title="RS-Ratio", range=xr, gridcolor="#0f1e35",
                   color="#475569", zeroline=False),
        yaxis=dict(title="RS-Momentum", range=yr, gridcolor="#0f1e35",
                   color="#475569", zeroline=False),
        shapes=[
            dict(type="rect", x0=100, x1=xr[1], y0=100, y1=yr[1],
                 fillcolor="rgba(16,185,129,0.05)", line_width=0, layer="below"),
            dict(type="rect", x0=100, x1=xr[1], y0=yr[0], y1=100,
                 fillcolor="rgba(245,158,11,0.05)", line_width=0, layer="below"),
            dict(type="rect", x0=xr[0], x1=100, y0=yr[0], y1=100,
                 fillcolor="rgba(239,68,68,0.05)", line_width=0, layer="below"),
            dict(type="rect", x0=xr[0], x1=100, y0=100, y1=yr[1],
                 fillcolor="rgba(59,130,246,0.05)", line_width=0, layer="below"),
            dict(type="line", x0=100, x1=100, y0=yr[0], y1=yr[1],
                 line=dict(color="#1e3a5f", width=1.5, dash="dash")),
            dict(type="line", x0=xr[0], x1=xr[1], y0=100, y1=100,
                 line=dict(color="#1e3a5f", width=1.5, dash="dash")),
        ],
        annotations=[
            dict(x=(100+xr[1])/2, y=(100+yr[1])/2, text="<b>LEADING</b>",   showarrow=False, font=dict(color="rgba(16,185,129,0.2)", size=20)),
            dict(x=(100+xr[1])/2, y=(100+yr[0])/2, text="<b>WEAKENING</b>", showarrow=False, font=dict(color="rgba(245,158,11,0.2)", size=20)),
            dict(x=(100+xr[0])/2, y=(100+yr[0])/2, text="<b>LAGGING</b>",   showarrow=False, font=dict(color="rgba(239,68,68,0.2)",  size=20)),
            dict(x=(100+xr[0])/2, y=(100+yr[1])/2, text="<b>IMPROVING</b>", showarrow=False, font=dict(color="rgba(59,130,246,0.2)", size=20)),
        ],
        updatemenus=[dict(
            type="buttons", showactive=False,
            y=0.02, x=0.02, xanchor="left", yanchor="bottom",
            buttons=[
                dict(label="▶  Play", method="animate",
                     args=[None, dict(frame=dict(duration=650, redraw=True),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="⏸  Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate")]),
            ],
            bgcolor="#0f1e35", bordercolor="#1e3a5f",
            font=dict(color="#93c5fd", size=13),
        )],
        sliders=[dict(
            steps=[dict(method="animate",
                        args=[[f.name], dict(mode="immediate",
                                             frame=dict(duration=300, redraw=True))],
                        label=f.name) for f in frames],
            transition=dict(duration=0),
            x=0.0, y=0.0, len=1.0,
            currentvalue=dict(font=dict(size=12, color="#38bdf8"),
                              prefix="Period: ", visible=True,
                              xanchor="center"),
            tickcolor="#1e3a5f", bgcolor="#0a1628",
            bordercolor="#1e3a5f",
        )],
    )

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTOR PAIR COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
def render_pair_comparison(sec1: str, sec2: str, interval: str) -> None:
    t1 = SECTOR_MAP[sec1]["index"]
    t2 = SECTOR_MAP[sec2]["index"]

    raw = fetch_pair_data(t1, t2, interval)
    if raw.empty:
        st.error("Could not fetch pair data. Please try again.")
        return

    df_close = extract_field_df(raw, "Close")
    if t1 not in df_close.columns or t2 not in df_close.columns:
        st.error("Insufficient pair data for selected sectors.")
        return

    s1 = df_close[t1].dropna()
    s2 = df_close[t2].dropna()
    pair_ratio = (s1 / s2 * 100).dropna()
    if pair_ratio.empty:
        st.error("Could not compute pair ratio.")
        return

    curr_val = pair_ratio.iloc[-1]
    prev_val = pair_ratio.iloc[-5] if len(pair_ratio) > 5 else pair_ratio.iloc[0]
    delta    = ((curr_val - prev_val) / (abs(prev_val) + 1e-9)) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{sec1}", f"₹{s1.iloc[-1]:,.2f}",
              delta=f"{((s1.iloc[-1]-s1.iloc[-2])/s1.iloc[-2]*100):+.2f}%" if len(s1) > 1 else "")
    c2.metric(f"{sec2}", f"₹{s2.iloc[-1]:,.2f}",
              delta=f"{((s2.iloc[-1]-s2.iloc[-2])/s2.iloc[-2]*100):+.2f}%" if len(s2) > 1 else "")
    c3.metric(f"Pair Ratio ({sec1} / {sec2})", f"{curr_val:.2f}",
              delta=f"{delta:+.2f}% (5 Periods)")

    ma20 = pair_ratio.rolling(20).mean()
    upper = ma20 + pair_ratio.rolling(20).std() * 1.5
    lower = ma20 - pair_ratio.rolling(20).std() * 1.5

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=upper.index, y=upper.values, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="none",
    ))
    fig.add_trace(go.Scatter(
        x=lower.index, y=lower.values, mode="lines",
        fill="tonexty", fillcolor="rgba(59,130,246,0.08)",
        line=dict(width=0), name="±1.5σ Band", hoverinfo="none",
    ))
    fig.add_trace(go.Scatter(
        x=pair_ratio.index, y=pair_ratio.values, mode="lines",
        line=dict(color="#38bdf8", width=2),
        name=f"{sec1} / {sec2} Ratio",
    ))
    fig.add_trace(go.Scatter(
        x=ma20.index, y=ma20.values, mode="lines",
        line=dict(color="#f59e0b", width=1.5, dash="dash"),
        name="20-Period MA",
    ))

    fig.update_layout(
        title=f"⚖️ Pair Strength: {sec1}  vs  {sec2}",
        paper_bgcolor="#07101f", plot_bgcolor="#07101f",
        height=420, legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        xaxis=dict(gridcolor="#0f1e35", color="#475569"),
        yaxis=dict(title="Relative Ratio", gridcolor="#0f1e35", color="#475569"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SMART TRADE SETUP GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_trade_setups(rrg_data: dict, thresh: float = 6.0) -> tuple[list, list]:
    """
    Rule-based high-conviction setup generator.
    Stop-loss is volatility-adjusted (not hardcoded).
    Risk-Reward is computed dynamically.
    """
    long_setups, short_setups = [], []

    for name, data in rrg_data.items():
        metrics  = data["metrics"]
        cmp      = data["cmp"]
        high_52w = data["high_52w"]
        dist_52w = data["dist_52w"]
        prices   = data["prices"]

        if metrics.empty or cmp <= 0:
            continue

        curr_ratio = metrics["ratio"].iloc[-1]
        curr_mom   = metrics["momentum"].iloc[-1]
        quad, *_   = get_quadrant(curr_ratio, curr_mom)

        # Volatility-based stop (3%–8%)
        sl_pct = compute_volatility_sl(prices)

        # ── LONG SETUP: Leading or Improving + near 52W High + rising momentum
        if quad in ("Leading", "Improving") and dist_52w <= thresh and curr_mom >= 99.5:
            sl     = round(cmp * (1 - sl_pct / 100), 2)
            t1_pct = sl_pct * 2.0
            t2_pct = sl_pct * 3.0
            t1     = round(cmp * (1 + t1_pct / 100), 2)
            t2     = round(cmp * (1 + t2_pct / 100), 2)
            rr     = round(t1_pct / sl_pct, 1)
            long_setups.append({
                "Sector": name, "Quadrant": quad,
                "CMP": cmp, "52W High": high_52w, "Dist High": f"{dist_52w:.1f}%",
                "Stop Loss": sl, "SL %": f"{sl_pct:.1f}%",
                "Target 1": t1, "Target 2": t2,
                "Risk Reward": f"1 : {rr}",
            })

        # ── SHORT / EXIT SETUP: Lagging + far from 52W High + falling momentum
        if quad == "Lagging" and dist_52w >= 12.0 and curr_mom < 99.5:
            sl      = round(cmp * (1 + sl_pct / 100), 2)
            t_down  = round(cmp * (1 - sl_pct * 2 / 100), 2)
            short_setups.append({
                "Sector": name, "Quadrant": quad,
                "CMP": cmp, "52W High": high_52w, "Dist High": f"{dist_52w:.1f}%",
                "Cover SL": sl, "Target Downside": t_down,
                "Alert": "⚠️ Avoid Long / Consider Hedging",
            })

    return long_setups, short_setups


# ─────────────────────────────────────────────────────────────────────────────
# QUADRANT BACKTEST ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def run_quadrant_backtest(rrg_data: dict, interval: str = "1d") -> pd.DataFrame:
    """
    Backtest: Improving → Leading quadrant transition signal.
    Returns forward returns (5-period & 10-period) and win rate.
    Period label adjusts for weekly vs daily timeframe.
    """
    p_label = "5W" if interval == "1wk" else "5D"
    t_label = "10W" if interval == "1wk" else "10D"

    results = []
    for name, data in rrg_data.items():
        metrics = data["metrics"].copy()
        prices  = data["prices"]

        if metrics.empty or len(prices) < 30:
            continue

        quadrants = [get_quadrant(r, m)[0] for r, m in
                     zip(metrics["ratio"], metrics["momentum"])]
        metrics["quad"]      = quadrants
        metrics["prev_quad"] = metrics["quad"].shift(1)
        metrics["price"]     = prices.reindex(metrics.index).ffill()

        transitions = metrics[
            (metrics["prev_quad"] == "Improving") &
            (metrics["quad"] == "Leading")
        ]

        ret5, ret10 = [], []
        for dt in transitions.index:
            future = metrics.loc[dt:, "price"]
            if len(future) > 5:
                r5 = (future.iloc[5] - future.iloc[0]) / (future.iloc[0] + 1e-9) * 100
                ret5.append(r5)
            if len(future) > 10:
                r10 = (future.iloc[10] - future.iloc[0]) / (future.iloc[0] + 1e-9) * 100
                ret10.append(r10)

        if not ret5 and not ret10:
            continue

        win_rate = (sum(1 for r in ret10 if r > 0) / len(ret10) * 100) if ret10 else 0.0

        results.append({
            "Sector":              name,
            "Signals":             len(transitions),
            f"Avg Fwd Return ({p_label}) %": round(float(np.mean(ret5)),  2) if ret5  else "—",
            f"Avg Fwd Return ({t_label}) %": round(float(np.mean(ret10)), 2) if ret10 else "—",
            f"Win Rate ({t_label}) %":       f"{win_rate:.1f}%",
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────────────────────────
# MONEY FLOW TAB RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_money_flow_tab(sector_map: dict) -> None:
    st.markdown('<p class="section-header">💸 Sector Capital Inflow vs Outflow Tracker</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Price change × Volume expansion — identifies sectors with fresh capital vs liquidation pressure.</p>',
        unsafe_allow_html=True,
    )

    with st.spinner("Fetching sector-wide money flow data (batched download)..."):
        df = calculate_sector_money_flow(sector_map)

    if df.empty:
        st.warning("Data temporarily unavailable. Click **Refresh Market Data** in the sidebar.")
        return

    top_in  = df.iloc[0]
    top_out = df.iloc[-1]

    ca, cb = st.columns(2)
    ca.markdown(f"""
    <div class="flow-card flow-in">
      <div class="flow-title" style="color:#10b981;">🚀 Highest Capital Inflow</div>
      <div class="flow-sector">{top_in['Sector']}</div>
      <div class="flow-meta">Flow Score: <b style="color:#10b981;">+{top_in['Flow Score']}</b> &nbsp;|&nbsp; {top_in['Dominant Signal']}</div>
    </div>""", unsafe_allow_html=True)

    cb.markdown(f"""
    <div class="flow-card flow-out">
      <div class="flow-title" style="color:#ef4444;">🔻 Highest Capital Outflow</div>
      <div class="flow-sector">{top_out['Sector']}</div>
      <div class="flow-meta">Flow Score: <b style="color:#ef4444;">{top_out['Flow Score']}</b> &nbsp;|&nbsp; {top_out['Dominant Signal']}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Horizontal bar chart (much better with many sectors)
    colors = ["#10b981" if v >= 0 else "#ef4444" for v in df["Flow Score"]]
    fig = go.Figure(go.Bar(
        y=df["Sector"],
        x=df["Flow Score"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:+.2f}" for v in df["Flow Score"]],
        textposition="outside",
        textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Flow Score: %{x:+.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#1e3a5f", width=1.5, dash="dash"))
    fig.update_layout(
        title=dict(text="📊 Net Sector Money Flow Score  (+ve = Inflow  /  -ve = Outflow)",
                   font=dict(color="#93c5fd", size=14)),
        paper_bgcolor="#07101f", plot_bgcolor="#07101f",
        height=max(500, len(df) * 26),
        margin=dict(l=10, r=80, t=50, b=20),
        yaxis=dict(autorange="reversed", gridcolor="#0a1628",
                   color="#94a3b8", tickfont=dict(size=11)),
        xaxis=dict(gridcolor="#0f1e35", color="#475569", zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Buildup breakdown table
    st.markdown("---")
    st.markdown('<p class="section-header">📋 Sector Buildup Breakdown</p>', unsafe_allow_html=True)

    rows_html = ""
    for _, row in df.iterrows():
        badge = "bg-leading" if row["Flow Score"] >= 0 else "bg-lagging"
        score_sign = "+" if row["Flow Score"] >= 0 else ""
        rows_html += f"""
        <tr>
          <td class="td-name">{row['Sector']}</td>
          <td><span class="status-badge {badge}">{score_sign}{row['Flow Score']}</span></td>
          <td style="font-weight:600; color:#94a3b8;">{row['Dominant Signal']}</td>
          <td style="color:#10b981;">{row['Long Buildup 🟢']}</td>
          <td style="color:#ef4444;">{row['Short Buildup 🔴']}</td>
          <td style="color:#f59e0b;">{row['Long Unwinding 🟡']}</td>
          <td style="color:#3b82f6;">{row['Short Covering 🔵']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="rrg-table">
      <thead>
        <tr>
          <th>Sector</th><th>Flow Score</th><th>Dominant Signal</th>
          <th>Long Buildup 🟢</th><th>Short Buildup 🔴</th>
          <th>Long Unwinding 🟡</th><th>Short Covering 🔵</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER — Market Hours Aware
# ─────────────────────────────────────────────────────────────────────────────
now_ist     = datetime.now(IST_OFFSET)
market_open = is_market_open()
badge_cls   = "market-open"  if market_open else "market-closed"
dot_cls     = "dot-active"   if market_open else "dot-inactive"
badge_text  = "● LIVE"       if market_open else "● CLOSED"

st.markdown(f"""
<div class="brand-header">
  <div>
    <div class="brand-title">GROW MORE TRADING INSTITUTE</div>
    <div class="brand-subtitle">
      Real-Time NSE Sector RRG &nbsp;·&nbsp; Animated Rotation Player &nbsp;·&nbsp;
      Smart Trade Intelligence &nbsp;·&nbsp; Capital Flow Tracker
    </div>
  </div>
  <div class="live-container">
    <div class="live-badge {badge_cls}">
      <span class="live-dot {dot_cls}"></span>
      {badge_text}
    </div>
    <div id="live-clock" class="clock-text">⏰ Loading…</div>
  </div>
</div>

<script>
(function() {{
  function updateClock() {{
    const now = new Date();
    const opts = {{
      timeZone: 'Asia/Kolkata', hour12: true,
      day: '2-digit', month: 'short',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    }};
    const el = document.getElementById('live-clock');
    if (el) el.innerText = '⏰ ' + now.toLocaleString('en-IN', opts) + ' IST';
  }}
  setInterval(updateClock, 1000);
  updateClock();
}})();
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOAD — Sector RRG (with session_state caching to avoid repeat loads)
# ─────────────────────────────────────────────────────────────────────────────
sector_ticker_dict = {s: SECTOR_MAP[s]["index"] for s in SECTOR_MAP}

with st.spinner("⏳ Loading live sector data from NSE…"):
    sector_rrg_data = fetch_and_build_rrg(
        sector_ticker_dict, BENCHMARK_SYMBOL, timeframe, rrg_period
    )

if not sector_rrg_data:
    st.error("❌ Could not fetch market data. Check your internet connection and try refreshing.")
    st.stop()

# KPI Summary Row
render_kpi_summary(sector_rrg_data, high_threshold)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN TAB NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐  All NSE Sectors",
    "🎯  Stock Drill-Down",
    "🎬  Animated RRG",
    "📊  Trade Setups & Backtest",
    "💸  Money Flow & Rollover",
])


# ── TAB 1 : ALL SECTOR RRG ───────────────────────────────────────────────────
with tab1:
    st.markdown('<p class="section-header">📊 All NSE Sectors — Relative Rotation vs Nifty 50</p>',
                unsafe_allow_html=True)

    fig_sec, df_sec = render_rrg_chart(
        sector_rrg_data,
        "NSE Sector Relative Rotation Graph (RRG)",
        tail=tail_len,
        thresh=high_threshold,
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-header">📋 Sector Rotation Matrix</p>', unsafe_allow_html=True)

    f1, f2, f3, f4, f5, f6 = st.tabs([
        "All Sectors", "🔥 Near 52W High", "🚀 Leading", "⚡ Improving", "⚠️ Weakening", "🔻 Lagging"
    ])
    with f1: render_styled_table(df_sec, "Sector Name", sort_key="all")
    with f2: render_styled_table(df_sec[df_sec["Dist 52W High (%)"] <= high_threshold], "Sector Name", sort_key="near")
    with f3: render_styled_table(df_sec[df_sec["Quadrant"] == "Leading"],   "Sector Name", sort_key="lead")
    with f4: render_styled_table(df_sec[df_sec["Quadrant"] == "Improving"], "Sector Name", sort_key="impr")
    with f5: render_styled_table(df_sec[df_sec["Quadrant"] == "Weakening"], "Sector Name", sort_key="weak")
    with f6: render_styled_table(df_sec[df_sec["Quadrant"] == "Lagging"],   "Sector Name", sort_key="lagg")


# ── TAB 2 : STOCK DRILL-DOWN ─────────────────────────────────────────────────
with tab2:
    st.markdown(
        f'<p class="section-header">🎯 Stock Drill-Down — '
        f'<span style="color:#38bdf8;">{selected_sector_for_stocks}</span></p>',
        unsafe_allow_html=True,
    )

    sec_info        = SECTOR_MAP[selected_sector_for_stocks]
    stock_dict      = sec_info["stocks"]
    sector_bench    = sec_info["index"]

    with st.spinner(f"Loading {selected_sector_for_stocks} stocks…"):
        stock_rrg_data = fetch_and_build_rrg(
            stock_dict, sector_bench, timeframe, rrg_period
        )

    if not stock_rrg_data:
        st.warning("Could not fetch stock data for this sector. Try a different sector or refresh.")
    else:
        # KPI for stocks
        render_kpi_summary(stock_rrg_data, high_threshold)

        fig_stk, df_stk = render_rrg_chart(
            stock_rrg_data,
            f"{selected_sector_for_stocks} — Stocks vs Sector Index",
            tail=tail_len,
            thresh=high_threshold,
        )
        st.plotly_chart(fig_stk, use_container_width=True)

        st.markdown("---")
        st.markdown(f'<p class="section-header">📋 {selected_sector_for_stocks} — Stock Matrix</p>',
                    unsafe_allow_html=True)

        s1, s2, s3, s4, s5, s6 = st.tabs([
            "All Stocks", "🔥 Near 52W High", "🚀 Leading", "⚡ Improving", "⚠️ Weakening", "🔻 Lagging"
        ])
        with s1: render_styled_table(df_stk, "Stock Name", sort_key="stk_all")
        with s2: render_styled_table(df_stk[df_stk["Dist 52W High (%)"] <= high_threshold], "Stock Name", sort_key="stk_near")
        with s3: render_styled_table(df_stk[df_stk["Quadrant"] == "Leading"],   "Stock Name", sort_key="stk_lead")
        with s4: render_styled_table(df_stk[df_stk["Quadrant"] == "Improving"], "Stock Name", sort_key="stk_impr")
        with s5: render_styled_table(df_stk[df_stk["Quadrant"] == "Weakening"], "Stock Name", sort_key="stk_weak")
        with s6: render_styled_table(df_stk[df_stk["Quadrant"] == "Lagging"],   "Stock Name", sort_key="stk_lagg")


# ── TAB 3 : ANIMATED RRG & PAIR MATRIX ──────────────────────────────────────
with tab3:
    st.markdown('<p class="section-header">🎬 Historical RRG Rotation Player</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Press ▶ Play to watch how sectors rotated across quadrants over the last 12 periods.</p>',
        unsafe_allow_html=True,
    )

    lookback_col, _ = st.columns([2, 6])
    lookback = lookback_col.slider("Lookback Periods", min_value=6, max_value=26, value=12,
                                    key="anim_lookback")
    render_animated_rrg(sector_rrg_data, lookback=lookback)

    st.markdown("---")
    st.markdown('<p class="section-header">⚖️ Sector vs Sector — Pair Strength Ratio</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">Compare any 2 sectors head-to-head. The ratio shows relative dominance and mean-reversion opportunities.</p>',
        unsafe_allow_html=True,
    )

    p_col1, p_col2 = st.columns(2)
    s1_sel = p_col1.selectbox("Base Sector (Numerator)",      list(SECTOR_MAP.keys()), index=0, key="pair_s1")
    s2_sel = p_col2.selectbox("Compare Sector (Denominator)", list(SECTOR_MAP.keys()), index=1, key="pair_s2")

    if s1_sel == s2_sel:
        st.warning("Please select two different sectors.")
    else:
        render_pair_comparison(s1_sel, s2_sel, timeframe)


# ── TAB 4 : SMART TRADE SETUPS & BACKTEST ───────────────────────────────────
with tab4:
    st.markdown('<p class="section-header">📊 Smart Trade Setups — Rule-Based High Conviction Signals</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">'
        'Setups generated from RRG Quadrant position, 52-Week High proximity, and volatility-calibrated stop-loss.'
        '</p>',
        unsafe_allow_html=True,
    )

    thresh_col, _ = st.columns([2, 6])
    setup_thresh = thresh_col.slider("Long Setup — Max Dist from 52W High (%)",
                                     min_value=2.0, max_value=15.0, value=6.0, step=0.5,
                                     key="setup_thresh")

    long_ideas, short_ideas = generate_trade_setups(sector_rrg_data, thresh=setup_thresh)

    c_long, c_short = st.columns(2)

    with c_long:
        st.markdown("#### 🚀 Bullish Setups  (Leading / Improving + Near High)")
        if not long_ideas:
            st.info("No high-conviction bullish setups at this moment. Try widening the 52W High threshold.")
        for item in long_ideas:
            st.markdown(f"""
            <div class="setup-card card-long">
              <div class="card-title-long">
                {item['Sector']}
                <span style="font-size:0.78rem;color:#475569;font-weight:400;">
                  ({item['Quadrant']}) · Dist: {item['Dist High']}
                </span>
              </div>
              <div class="card-row">CMP: <b>₹{item['CMP']:,.2f}</b> &nbsp;·&nbsp; 52W High: <b>₹{item['52W High']:,.2f}</b></div>
              <div class="card-row card-target">
                🎯 Target 1: <b>₹{item['Target 1']:,.2f}</b> &nbsp;|&nbsp;
                   Target 2: <b>₹{item['Target 2']:,.2f}</b>
              </div>
              <div class="card-row card-sl">
                🛑 Stop Loss: <b>₹{item['Stop Loss']:,.2f}</b> ({item['SL %']})
              </div>
              <div class="card-row card-rr">Risk : Reward = {item['Risk Reward']}</div>
            </div>""", unsafe_allow_html=True)

    with c_short:
        st.markdown("#### 🔻 Exit / Hedge Signals  (Lagging Quadrant)")
        if not short_ideas:
            st.info("No high-risk exit signals detected. Market momentum looks broadly constructive.")
        for item in short_ideas:
            st.markdown(f"""
            <div class="setup-card card-short">
              <div class="card-title-short">
                {item['Sector']}
                <span style="font-size:0.78rem;color:#475569;font-weight:400;">
                  ({item['Quadrant']}) · Dist: {item['Dist High']}
                </span>
              </div>
              <div class="card-row">CMP: <b>₹{item['CMP']:,.2f}</b> &nbsp;·&nbsp; 52W High: <b>₹{item['52W High']:,.2f}</b></div>
              <div class="card-row" style="color:#f59e0b;">
                📉 Downside Target: <b>₹{item['Target Downside']:,.2f}</b>
              </div>
              <div class="card-row card-sl">Cover SL: <b>₹{item['Cover SL']:,.2f}</b></div>
              <div class="card-row" style="color:#ef4444; font-weight:700;">{item['Alert']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="section-header">📈 Quadrant Transition Backtest  (Improving → Leading)</p>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="section-sub">'
        'Historical forward returns after each sector crossed from Improving into Leading quadrant.'
        '</p>',
        unsafe_allow_html=True,
    )

    with st.spinner("Running backtest…"):
        bt_df = run_quadrant_backtest(sector_rrg_data, interval=timeframe)

    if bt_df.empty:
        st.info("Insufficient historical data for backtest. Try switching to Weekly timeframe.")
    else:
        # Colour-code the dataframe
        st.dataframe(
            bt_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sector": st.column_config.TextColumn("Sector", width="medium"),
                "Signals": st.column_config.NumberColumn("Signals", format="%d"),
            },
        )


# ── TAB 5 : MONEY FLOW & ROLLOVER ───────────────────────────────────────────
with tab5:
    render_money_flow_tab(SECTOR_MAP)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  © 2026 &nbsp;<b>Grow More Trading Institute</b>&nbsp; · &nbsp;
  Institutional RRG Analytics &amp; Smart Trade Intelligence Dashboard &nbsp;·&nbsp;
  Data via Yahoo Finance &nbsp;·&nbsp;
  <span style="color:#1e3a5f;">Not SEBI registered. For educational purposes only.</span>
</div>
""", unsafe_allow_html=True)
