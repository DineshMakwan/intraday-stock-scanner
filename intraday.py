from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Configuration
st.set_page_config(
    page_title="Grow More Trading Institute - Advanced RRG Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Dark Theme Styling & Institute Branding
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #f3f4f6; }
    
    .brand-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0f172a 100%);
        padding: 18px 24px;
        border-radius: 12px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    .brand-title { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 0.5px; }
    .brand-subtitle { font-size: 0.95rem; color: #9ca3af; margin-top: 4px; }
    
    .live-container {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(15, 23, 42, 0.6);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid #1e293b;
    }
    .live-badge {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        letter-spacing: 1px;
    }
    .live-dot {
        height: 9px;
        width: 9px;
        background-color: #ef4444;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 8px #ef4444;
        animation: pulse 1.2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.3; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1); }
    }
    .clock-text {
        font-size: 0.9rem;
        color: #38bdf8;
        font-weight: 600;
        font-family: monospace;
    }

    /* Badges & Setup Cards */
    .status-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .bg-leading { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .bg-improving { background-color: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid #3b82f6; }
    .bg-weakening { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .bg-lagging { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .bg-near-high { background-color: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid #ec4899; }
    .bg-normal-high { background-color: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid #4b5563; }

    .setup-card-long {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .setup-card-short {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .footer-text {
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #1f2937;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Branding Banner
st.markdown(
    """
    <div class="brand-header">
        <div>
            <div class="brand-title">GROW MORE TRADING INSTITUTE</div>
            <div class="brand-subtitle">Real-Time Sector RRG, Animated Rotations & AI Trade Intelligence</div>
        </div>
        <div class="live-container">
            <div class="live-badge">
                <span class="live-dot"></span>LIVE
            </div>
            <div id="live-clock" class="clock-text">⏰ Loading Clock...</div>
        </div>
    </div>

    <script>
    function updateClock() {
        const now = new Date();
        const options = { 
            timeZone: 'Asia/Kolkata', 
            hour12: true, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            day: '2-digit',
            month: 'short'
        };
        const timeString = now.toLocaleString('en-IN', options);
        const clockElem = document.getElementById('live-clock');
        if(clockElem) {
            clockElem.innerText = '⏰ ' + timeString + ' IST';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
""",
    unsafe_allow_html=True,
)

# FULL EXPANDED 23 SECTORS MAPPING WITH ALL CONSTITUENT STOCKS
SECTOR_MAP = {
    "Nifty REITs & Realty": {
        "index": "^CNXREALTY",
        "stocks": {
            "ABREL": "ABREL.NS",
            "EMBASSY": "EMBASSY.NS",
            "LODHA": "LODHA.NS",
            "NXST": "NXST.NS",
            "SOBHA": "SOBHA.NS",
            "PRESTIGE": "PRESTIGE.NS",
            "OBEROIRLTY": "OBEROIRLTY.NS",
            "MINDSPACE": "MINDSPACE.NS",
            "BIRET": "BIRET.NS",
            "GODREJPROP": "GODREJPROP.NS",
            "DLF": "DLF.NS",
            "PHOENIXLTD": "PHOENIXLTD.NS",
            "ANANTRAJ": "ANANTRAJ.NS",
            "BRIGADE": "BRIGADE.NS",
        },
    },
    "Nifty Cement": {
        "index": "^CNXCMDT",
        "stocks": {
            "STARCEMENT": "STARCEMENT.NS",
            "RAMCOCEM": "RAMCOCEM.NS",
            "JKLAKSHMI": "JKLAKSHMI.NS",
            "NUVOCO": "NUVOCO.NS",
            "AMBUJACEM": "AMBUJACEM.NS",
            "INDIACEM": "INDIACEM.NS",
            "ORIENTCEM": "ORIENTCEM.NS",
            "BIRLACORPN": "BIRLACORPN.NS",
            "ACC": "ACC.NS",
            "JKCEMENT": "JKCEMENT.NS",
            "DALBHARAT": "DALBHARAT.NS",
            "SHREECEM": "SHREECEM.NS",
            "GRASIM": "GRASIM.NS",
            "ULTRACEMCO": "ULTRACEMCO.NS",
        },
    },
    "Nifty Chemicals": {
        "index": "^CNXCMDT",
        "stocks": {
            "FLUOROCHEM": "FLUOROCHEM.NS",
            "SOLARINDS": "SOLARINDS.NS",
            "HSCL": "HSCL.NS",
            "AARTIIND": "AARTIIND.NS",
            "ATUL": "ATUL.NS",
            "NAVINFLUOR": "NAVINFLUOR.NS",
            "PIIND": "PIIND.NS",
            "CHAMBLFERT": "CHAMBLFERT.NS",
            "PCBL": "PCBL.NS",
            "TATACHEM": "TATACHEM.NS",
            "SUMICHEM": "SUMICHEM.NS",
            "COROMANDEL": "COROMANDEL.NS",
            "LINDEINDIA": "LINDEINDIA.NS",
            "DEEPAKNTR": "DEEPAKNTR.NS",
            "DEEPAKFERT": "DEEPAKFERT.NS",
            "PIDILITIND": "PIDILITIND.NS",
            "BAYERCROP": "BAYERCROP.NS",
            "SRF": "SRF.NS",
            "UPL": "UPL.NS",
        },
    },
    "Nifty MidSmall Healthcare": {
        "index": "^CNXPHARMA",
        "stocks": {
            "NATCOPHARM": "NATCOPHARM.NS",
            "IPCALAB": "IPCALAB.NS",
            "AJANTPHARM": "AJANTPHARM.NS",
            "WOCKPHARMA": "WOCKPHARMA.NS",
            "PPLPHARMA": "PPLPHARMA.NS",
            "GLAND": "GLAND.NS",
            "MEDANTA": "MEDANTA.NS",
            "NEULANDLAB": "NEULANDLAB.NS",
            "GLENMARK": "GLENMARK.NS",
            "LALPATHLAB": "LALPATHLAB.NS",
            "ABBOTINDIA": "ABBOTINDIA.NS",
            "NH": "NH.NS",
            "AUROPHARMA": "AUROPHARMA.NS",
            "GLAXO": "GLAXO.NS",
            "ASTERDM": "ASTERDM.NS",
            "FORTIS": "FORTIS.NS",
            "KIMS": "KIMS.NS",
            "PFIZER": "PFIZER.NS",
            "MANKIND": "MANKIND.NS",
            "GRANULES": "GRANULES.NS",
            "ALKEM": "ALKEM.NS",
            "POLYMED": "POLYMED.NS",
            "LUPIN": "LUPIN.NS",
            "LAURUSLABS": "LAURUSLABS.NS",
            "SYNGENE": "SYNGENE.NS",
            "BIOCON": "BIOCON.NS",
        },
    },
    "Nifty Oil & Gas": {
        "index": "^CNXENERGY",
        "stocks": {
            "MGL": "MGL.NS",
            "AEGISLOG": "AEGISLOG.NS",
            "HINDPETRO": "HINDPETRO.NS",
            "IGL": "IGL.NS",
            "OIL": "OIL.NS",
            "CASTROLIND": "CASTROLIND.NS",
            "ONGC": "ONGC.NS",
            "IOC": "IOC.NS",
            "ATGL": "ATGL.NS",
            "RELIANCE": "RELIANCE.NS",
            "GAIL": "GAIL.NS",
            "BPCL": "BPCL.NS",
            "PETRONET": "PETRONET.NS",
            "CHENNPETRO": "CHENNPETRO.NS",
        },
    },
    "Nifty Consumer Durables": {
        "index": "^CNXCONSUM",
        "stocks": {
            "BATAINDIA": "BATAINDIA.NS",
            "KAJARIACER": "KAJARIACER.NS",
            "BLUESTARCO": "BLUESTARCO.NS",
            "AMBER": "AMBER.NS",
            "WHIRLPOOL": "WHIRLPOOL.NS",
            "KALYANKJIL": "KALYANKJIL.NS",
            "HAVELLS": "HAVELLS.NS",
            "VOLTAS": "VOLTAS.NS",
            "CROMPTON": "CROMPTON.NS",
            "DIXON": "DIXON.NS",
            "TITAN": "TITAN.NS",
            "PGEL": "PGEL.NS",
        },
    },
    "Nifty Healthcare": {
        "index": "^CNXPHARMA",
        "stocks": {
            "IPCALAB": "IPCALAB.NS",
            "PPLPHARMA": "PPLPHARMA.NS",
            "APOLLOHOSP": "APOLLOHOSP.NS",
            "GLENMARK": "GLENMARK.NS",
            "MAXHEALTH": "MAXHEALTH.NS",
            "ABBOTINDIA": "ABBOTINDIA.NS",
            "AUROPHARMA": "AUROPHARMA.NS",
            "SUNPHARMA": "SUNPHARMA.NS",
            "DRREDDY": "DRREDDY.NS",
            "CIPLA": "CIPLA.NS",
            "FORTIS": "FORTIS.NS",
            "TORNTPHARM": "TORNTPHARM.NS",
            "MANKIND": "MANKIND.NS",
            "ALKEM": "ALKEM.NS",
            "LUPIN": "LUPIN.NS",
            "LAURUSLABS": "LAURUSLABS.NS",
            "SYNGENE": "SYNGENE.NS",
            "BIOCON": "BIOCON.NS",
            "DIVISLAB": "DIVISLAB.NS",
            "ZYDUSLIFE": "ZYDUSLIFE.NS",
        },
    },
    "Nifty Private Bank": {
        "index": "^NSEBANK",
        "stocks": {
            "IDFCFIRSTB": "IDFCFIRSTB.NS",
            "KOTAKBANK": "KOTAKBANK.NS",
            "BANDHANBNK": "BANDHANBNK.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "YESBANK": "YESBANK.NS",
            "INDUSINDBK": "INDUSINDBK.NS",
            "RBLBANK": "RBLBANK.NS",
            "FEDERALBNK": "FEDERALBNK.NS",
            "AXISBANK": "AXISBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
        },
    },
    "Nifty Realty": {
        "index": "^CNXREALTY",
        "stocks": {
            "ABREL": "ABREL.NS",
            "LODHA": "LODHA.NS",
            "SOBHA": "SOBHA.NS",
            "PRESTIGE": "PRESTIGE.NS",
            "OBEROIRLTY": "OBEROIRLTY.NS",
            "GODREJPROP": "GODREJPROP.NS",
            "DLF": "DLF.NS",
            "PHOENIXLTD": "PHOENIXLTD.NS",
            "ANANTRAJ": "ANANTRAJ.NS",
            "BRIGADE": "BRIGADE.NS",
        },
    },
    "Nifty PSU Bank": {
        "index": "^CNXPSUBANK",
        "stocks": {
            "MAHABANK": "MAHABANK.NS",
            "CENTRALBK": "CENTRALBK.NS",
            "PSB": "PSB.NS",
            "IOB": "IOB.NS",
            "UCOBANK": "UCOBANK.NS",
            "UNIONBANK": "UNIONBANK.NS",
            "SBIN": "SBIN.NS",
            "CANBK": "CANBK.NS",
            "INDIANB": "INDIANB.NS",
            "BANKINDIA": "BANKINDIA.NS",
            "PNB": "PNB.NS",
            "BANKBARODA": "BANKBARODA.NS",
        },
    },
    "Nifty Auto": {
        "index": "^CNXAUTO",
        "stocks": {
            "MARUTI": "MARUTI.NS",
            "M&M": "M&M.NS",
            "TATAMOTORS": "TATAMOTORS.NS",
            "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
            "EICHERMOT": "EICHERMOT.NS",
            "HEROMOTOCO": "HEROMOTOCO.NS",
            "TVSMOTOR": "TVSMOTOR.NS",
            "BHARATFORG": "BHARATFORG.NS",
            "ASHOKLEY": "ASHOKLEY.NS",
            "BALKRISIND": "BALKRISIND.NS",
            "MRF": "MRF.NS",
            "MOTHERSON": "MOTHERSON.NS",
            "TIINDIA": "TIINDIA.NS",
            "BOSCHLTD": "BOSCHLTD.NS",
            "SONACOMS": "SONACOMS.NS",
        },
    },
    "Nifty Bank": {
        "index": "^NSEBANK",
        "stocks": {
            "HDFCBANK": "HDFCBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "AXISBANK": "AXISBANK.NS",
            "KOTAKBANK": "KOTAKBANK.NS",
            "SBIN": "SBIN.NS",
            "INDUSINDBK": "INDUSINDBK.NS",
            "BANKBARODA": "BANKBARODA.NS",
            "PNB": "PNB.NS",
            "AUBANK": "AUBANK.NS",
            "FEDERALBNK": "FEDERALBNK.NS",
            "IDFCFIRSTB": "IDFCFIRSTB.NS",
            "BANDHANBNK": "BANDHANBNK.NS",
        },
    },
    "Nifty Financial Services": {
        "index": "^CNXFIN",
        "stocks": {
            "HDFCBANK": "HDFCBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "AXISBANK": "AXISBANK.NS",
            "KOTAKBANK": "KOTAKBANK.NS",
            "SBIN": "SBIN.NS",
            "BAJFINANCE": "BAJFINANCE.NS",
            "BAJAJFINSV": "BAJAJFINSV.NS",
            "PFC": "PFC.NS",
            "REC": "REC.NS",
            "HDFCLIFE": "HDFCLIFE.NS",
            "SBILIFE": "SBILIFE.NS",
            "ICICIPRULI": "ICICIPRULI.NS",
            "ICICIGI": "ICICIGI.NS",
            "CHOLAFIN": "CHOLAFIN.NS",
            "SHRIRAMFIN": "SHRIRAMFIN.NS",
            "MUTHOOTFIN": "MUTHOOTFIN.NS",
            "JIOFIN": "JIOFIN.NS",
            "HDFCAMC": "HDFCAMC.NS",
        },
    },
    "Nifty FMCG": {
        "index": "^CNXFMCG",
        "stocks": {
            "ITC": "ITC.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "NESTLEIND": "NESTLEIND.NS",
            "BRITANNIA": "BRITANNIA.NS",
            "TATACONSUM": "TATACONSUM.NS",
            "GODREJCP": "GODREJCP.NS",
            "DABUR": "DABUR.NS",
            "MARICO": "MARICO.NS",
            "COLPAL": "COLPAL.NS",
            "VBL": "VBL.NS",
            "MCDOWELL-N": "MCDOWELL-N.NS",
            "UBL": "UBL.NS",
            "BALRAMCHIN": "BALRAMCHIN.NS",
            "PGHH": "PGHH.NS",
            "EMAMILTD": "EMAMILTD.NS",
        },
    },
    "Nifty IT": {
        "index": "^CNXIT",
        "stocks": {
            "TCS": "TCS.NS",
            "INFY": "INFY.NS",
            "HCLTECH": "HCLTECH.NS",
            "WIPRO": "WIPRO.NS",
            "LTIM": "LTIM.NS",
            "TECHM": "TECHM.NS",
            "PERSISTENT": "PERSISTENT.NS",
            "COFORGE": "COFORGE.NS",
            "MPHASIS": "MPHASIS.NS",
            "LTTS": "LTTS.NS",
        },
    },
    "Nifty Media": {
        "index": "^CNXMEDIA",
        "stocks": {
            "SUNTV": "SUNTV.NS",
            "ZEEL": "ZEEL.NS",
            "PVRINOX": "PVRINOX.NS",
            "TV18BRDCST": "TV18BRDCST.NS",
            "NETWORK18": "NETWORK18.NS",
            "NAZARA": "NAZARA.NS",
            "DISHTV": "DISHTV.NS",
            "HATHWAY": "HATHWAY.NS",
            "NAVNETEDUL": "NAVNETEDUL.NS",
            "TIPSMUSIC": "TIPSMUSIC.NS",
        },
    },
    "Nifty Metal": {
        "index": "^CNXMETAL",
        "stocks": {
            "TATASTEEL": "TATASTEEL.NS",
            "JINDALSTEL": "JINDALSTEL.NS",
            "JSWSTEEL": "JSWSTEEL.NS",
            "HINDALCO": "HINDALCO.NS",
            "VEDL": "VEDL.NS",
            "NMDC": "NMDC.NS",
            "SAIL": "SAIL.NS",
            "NATIONALUM": "NATIONALUM.NS",
            "COALINDIA": "COALINDIA.NS",
            "APLAPOLLO": "APLAPOLLO.NS",
            "HINDZINC": "HINDZINC.NS",
            "HINDCOPPER": "HINDCOPPER.NS",
            "WELCORP": "WELCORP.NS",
            "RATNAMANI": "RATNAMANI.NS",
            "MOIL": "MOIL.NS",
        },
    },
    "Nifty Pharma": {
        "index": "^CNXPHARMA",
        "stocks": {
            "SUNPHARMA": "SUNPHARMA.NS",
            "CIPLA": "CIPLA.NS",
            "DRREDDY": "DRREDDY.NS",
            "DIVISLAB": "DIVISLAB.NS",
            "LUPIN": "LUPIN.NS",
            "TORNTPHARM": "TORNTPHARM.NS",
            "AUROPHARMA": "AUROPHARMA.NS",
            "ZYDUSLIFE": "ZYDUSLIFE.NS",
            "ALKEM": "ALKEM.NS",
            "GLENMARK": "GLENMARK.NS",
            "BIOCON": "BIOCON.NS",
            "IPCALAB": "IPCALAB.NS",
            "LAURUSLABS": "LAURUSLABS.NS",
            "GRANULES": "GRANULES.NS",
            "MANKIND": "MANKIND.NS",
            "SYNGENE": "SYNGENE.NS",
            "JBCHEMPH": "JBCHEMPH.NS",
            "NATCOPHARM": "NATCOPHARM.NS",
            "AJANTPHARM": "AJANTPHARM.NS",
            "PPLPHARMA": "PPLPHARMA.NS",
        },
    },
    "Nifty Energy": {
        "index": "^CNXENERGY",
        "stocks": {
            "RELIANCE": "RELIANCE.NS",
            "NTPC": "NTPC.NS",
            "POWERGRID": "POWERGRID.NS",
            "ONGC": "ONGC.NS",
            "BPCL": "BPCL.NS",
            "IOC": "IOC.NS",
            "GAIL": "GAIL.NS",
            "TATAPOWER": "TATAPOWER.NS",
            "ADANIGREEN": "ADANIGREEN.NS",
            "ADANIENERGY": "ADANIENERGY.NS",
        },
    },
    "Nifty Infrastructure": {
        "index": "^CNXINFRA",
        "stocks": {
            "LT": "LT.NS",
            "RELIANCE": "RELIANCE.NS",
            "NTPC": "NTPC.NS",
            "POWERGRID": "POWERGRID.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "ULTRACEMCO": "ULTRACEMCO.NS",
            "GRASIM": "GRASIM.NS",
            "ONGC": "ONGC.NS",
            "ADANIPORTS": "ADANIPORTS.NS",
            "COALINDIA": "COALINDIA.NS",
            "BPCL": "BPCL.NS",
            "IOC": "IOC.NS",
            "GAIL": "GAIL.NS",
            "DLF": "DLF.NS",
            "INDIGO": "INDIGO.NS",
            "TATAPOWER": "TATAPOWER.NS",
            "SIEMENS": "SIEMENS.NS",
            "ABB": "ABB.NS",
            "AMBUJACEM": "AMBUJACEM.NS",
            "HAL": "HAL.NS",
        },
    },
    "Nifty Commodities": {
        "index": "^CNXCMDT",
        "stocks": {
            "RELIANCE": "RELIANCE.NS",
            "TATASTEEL": "TATASTEEL.NS",
            "JINDALSTEL": "JINDALSTEL.NS",
            "JSWSTEEL": "JSWSTEEL.NS",
            "HINDALCO": "HINDALCO.NS",
            "VEDL": "VEDL.NS",
            "ONGC": "ONGC.NS",
            "COALINDIA": "COALINDIA.NS",
            "NTPC": "NTPC.NS",
            "POWERGRID": "POWERGRID.NS",
            "ULTRACEMCO": "ULTRACEMCO.NS",
            "GRASIM": "GRASIM.NS",
            "BPCL": "BPCL.NS",
            "IOC": "IOC.NS",
            "GAIL": "GAIL.NS",
            "AMBUJACEM": "AMBUJACEM.NS",
            "ACC": "ACC.NS",
            "SHREECEM": "SHREECEM.NS",
            "PIDILITIND": "PIDILITIND.NS",
            "UPL": "UPL.NS",
        },
    },
    "Nifty Consumption": {
        "index": "^CNXCONSUM",
        "stocks": {
            "ITC": "ITC.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "MARUTI": "MARUTI.NS",
            "M&M": "M&M.NS",
            "TATAMOTORS": "TATAMOTORS.NS",
            "TITAN": "TITAN.NS",
            "NESTLEIND": "NESTLEIND.NS",
            "BRITANNIA": "BRITANNIA.NS",
            "TATACONSUM": "TATACONSUM.NS",
            "GODREJCP": "GODREJCP.NS",
            "DABUR": "DABUR.NS",
            "MARICO": "MARICO.NS",
            "COLPAL": "COLPAL.NS",
            "VBL": "VBL.NS",
            "APOLLOHOSP": "APOLLOHOSP.NS",
            "TRENT": "TRENT.NS",
            "EICHERMOT": "EICHERMOT.NS",
            "HEROMOTOCO": "HEROMOTOCO.NS",
            "TVSMOTOR": "TVSMOTOR.NS",
        },
    },
    "Nifty PSE": {
        "index": "^CNXPSE",
        "stocks": {
            "NTPC": "NTPC.NS",
            "POWERGRID": "POWERGRID.NS",
            "ONGC": "ONGC.NS",
            "COALINDIA": "COALINDIA.NS",
            "BPCL": "BPCL.NS",
            "IOC": "IOC.NS",
            "GAIL": "GAIL.NS",
            "SBIN": "SBIN.NS",
            "PFC": "PFC.NS",
            "REC": "REC.NS",
            "BEL": "BEL.NS",
            "HAL": "HAL.NS",
            "NHPC": "NHPC.NS",
            "SJVN": "SJVN.NS",
            "OIL": "OIL.NS",
            "NMDC": "NMDC.NS",
            "SAIL": "SAIL.NS",
            "NATIONALUM": "NATIONALUM.NS",
            "CONCOR": "CONCOR.NS",
            "IRCTC": "IRCTC.NS",
        },
    },
}

BENCHMARK_SYMBOL = "^NSEI"  # Nifty 50 Benchmark

# Sidebar Controls
st.sidebar.header("⚙️ RRG Controls")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    options=["1d", "1wk"],
    index=1,
    format_func=lambda x: "Daily Rotation" if x == "1d" else "Weekly Rotation",
)
tail_len = st.sidebar.slider(
    "Tail Length (Periods)", min_value=2, max_value=15, value=5
)

st.sidebar.markdown("---")
st.sidebar.header("🔥 52-Week High Filters")
high_threshold = st.sidebar.slider(
    "Near 52W High Threshold (%)",
    min_value=1.0,
    max_value=15.0,
    value=5.0,
    step=0.5,
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Stock Drill-Down")
selected_sector_for_stocks = st.sidebar.selectbox(
    "Select Sector to Analyze Stocks", options=list(SECTOR_MAP.keys()), index=0
)


# Safe DataFrame extraction helper for yfinance output
def extract_field_df(raw_data, field_name="Close"):
    if raw_data.empty:
        return pd.DataFrame()

    if isinstance(raw_data.columns, pd.MultiIndex):
        if field_name in raw_data.columns.levels[0]:
            return raw_data[field_name].copy()
        else:
            return pd.DataFrame()
    else:
        if field_name in raw_data.columns:
            return raw_data[[field_name]].copy()
        elif len(raw_data.columns) == 1:
            df = raw_data.copy()
            df.columns = [field_name]
            return df
        return raw_data.copy()


# RRG Metric Calculation Engine
def calculate_rrg_metrics(data_df, item_ticker, bench_ticker, period_len=14):
    if item_ticker not in data_df.columns or bench_ticker not in data_df.columns:
        return None

    s_item = data_df[item_ticker].dropna()
    s_bench = data_df[bench_ticker].dropna()

    combined = pd.concat([s_item, s_bench], axis=1, join="inner").dropna()
    if len(combined) < (period_len * 2):
        return None

    item_series = combined.iloc[:, 0]
    bench_series = combined.iloc[:, 1]

    rs = (item_series / bench_series) * 100
    rs_mean = rs.rolling(window=period_len).mean()
    rs_std = rs.rolling(window=period_len).std()
    rs_ratio = 100 + ((rs - rs_mean) / (rs_std + 1e-6)) * 10

    ratio_mean = rs_ratio.rolling(window=period_len).mean()
    ratio_std = rs_ratio.rolling(window=period_len).std()
    rs_momentum = 100 + ((rs_ratio - ratio_mean) / (ratio_std + 1e-6)) * 10

    return pd.DataFrame({"ratio": rs_ratio, "momentum": rs_momentum}).dropna()


@st.cache_data(ttl=300)
def fetch_and_build_rrg(items_dict, benchmark_ticker_sym, interval):
    all_tickers = list(
        set(list(items_dict.values()) + [benchmark_ticker_sym, BENCHMARK_SYMBOL])
    )
    raw_data = yf.download(
        all_tickers, period="2y", interval=interval, progress=False
    )

    if raw_data.empty:
        return {}

    df_close = extract_field_df(raw_data, "Close")
    df_high = extract_field_df(raw_data, "High")

    if not isinstance(df_close.index, pd.DatetimeIndex):
        df_close.index = pd.to_datetime(df_close.index)
    if not isinstance(df_high.index, pd.DatetimeIndex):
        df_high.index = pd.to_datetime(df_high.index)

    if interval == "1wk":
        df_close = df_close.resample("W").last()
        df_high = df_high.resample("W").max()

    active_benchmark = benchmark_ticker_sym
    if (
        active_benchmark not in df_close.columns
        or df_close[active_benchmark].dropna().empty
    ):
        active_benchmark = BENCHMARK_SYMBOL

    rrg_results = {}
    for name, ticker in items_dict.items():
        if ticker not in df_close.columns or df_close[ticker].dropna().empty:
            continue

        metrics = calculate_rrg_metrics(df_close, ticker, active_benchmark)
        if metrics is not None and not metrics.empty:
            cmp = df_close[ticker].dropna().iloc[-1]
            high_52w = (
                df_high[ticker].dropna().max()
                if ticker in df_high.columns
                else cmp
            )
            dist_52w = (
                ((high_52w - cmp) / high_52w) * 100 if high_52w > 0 else 0
            )

            rrg_results[name] = {
                "metrics": metrics,
                "prices": df_close[ticker].dropna(),
                "cmp": round(float(cmp), 2),
                "high_52w": round(float(high_52w), 2),
                "dist_52w": round(float(dist_52w), 2),
                "ticker": ticker,
            }

    return rrg_results


def get_quadrant(ratio, momentum):
    if ratio >= 100 and momentum >= 100:
        return (
            "Leading",
            "🚀 Bullish Momentum & Strong RS",
            "bg-leading",
            "#10B981",
        )
    if ratio >= 100 and momentum < 100:
        return (
            "Weakening",
            "⚠️ RS High but Momentum Slowing",
            "bg-weakening",
            "#F59E0B",
        )
    if ratio < 100 and momentum < 100:
        return (
            "Lagging",
            "🔻 Bearish Momentum & Weak RS",
            "bg-lagging",
            "#EF4444",
        )
    return (
        "Improving",
        "⚡ RS Weak but Momentum Gaining",
        "bg-improving",
        "#3B82F6",
    )


def render_rrg_chart(rrg_data_dict, title_text):
    fig = go.Figure()
    min_x, max_x, min_y, max_y = 98.0, 102.0, 98.0, 102.0
    summary_list = []

    columns_list = [
        "Name",
        "RS-Ratio",
        "RS-Momentum",
        "Quadrant",
        "Status",
        "BadgeClass",
        "Trend",
        "CMP",
        "52W High",
        "Dist 52W High (%)",
        "Near 52W High",
        "NearBadgeClass",
    ]

    colors = [
        "#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899",
        "#14B8A6", "#F97316", "#6366F1", "#06B6D4", "#A855F7", "#EAB308",
        "#84CC16", "#F43F5E", "#D97706", "#059669", "#2563EB", "#7C3AED",
        "#DB2777", "#0284C7", "#16A34A", "#CA8A04", "#DC2626", "#4F46E5"
    ]

    for idx, (name, item_data) in enumerate(rrg_data_dict.items()):
        df = item_data["metrics"]
        cmp = item_data["cmp"]
        high_52w = item_data["high_52w"]
        dist_52w = item_data["dist_52w"]

        history = df.tail(tail_len)
        if history.empty:
            continue

        x_vals = history["ratio"].values
        y_vals = history["momentum"].values
        head_x, head_y = x_vals[-1], y_vals[-1]

        min_x, max_x = min(min_x, min(x_vals)), max(max_x, max(x_vals))
        min_y, max_y = min(min_y, min(y_vals)), max(max_y, max(y_vals))

        quad_name, desc, badge_cls, quad_color = get_quadrant(head_x, head_y)
        color = colors[idx % len(colors)]

        mom_change = head_y - y_vals[-2] if len(y_vals) > 1 else 0
        trend_icon = "⬆️ Up" if mom_change > 0 else "⬇️ Down"

        is_near = dist_52w <= high_threshold
        near_high_status = (
            f"🔥 YES ({dist_52w}%)" if is_near else f"NO ({dist_52w}%)"
        )
        near_badge_cls = "bg-near-high" if is_near else "bg-normal-high"

        summary_list.append({
            "Name": name,
            "RS-Ratio": round(float(head_x), 2),
            "RS-Momentum": round(float(head_y), 2),
            "Quadrant": quad_name,
            "Status": desc,
            "BadgeClass": badge_cls,
            "Trend": trend_icon,
            "CMP": cmp,
            "52W High": high_52w,
            "Dist 52W High (%)": dist_52w,
            "Near 52W High": near_high_status,
            "NearBadgeClass": near_badge_cls,
        })

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                line=dict(color=color, width=2, dash="dot"),
                showlegend=False,
                hoverinfo="none",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[head_x],
                y=[head_y],
                mode="markers+text",
                name=name,
                text=[name],
                textposition="top center",
                textfont=dict(color="#F3F4F6", size=11),
                marker=dict(size=12, color=color),
                hovertemplate=f"<b>{name}</b><br>CMP: ₹{cmp}<br>52W High: ₹{high_52w}<br>Dist High: {dist_52w}%<br>RS-Ratio: {head_x:.2f}<br>RS-Momentum: {head_y:.2f}<br>Quadrant: {quad_name}<extra></extra>",
            )
        )

    padding_x = max(abs(100 - min_x), abs(max_x - 100)) + 1.5
    padding_y = max(abs(100 - min_y), abs(max_y - 100)) + 1.5
    x_range = [100 - padding_x, 100 + padding_x]
    y_range = [100 - padding_y, 100 + padding_y]

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16, color="#38BDF8")),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=580,
        showlegend=False,
        xaxis=dict(
            title="RS-Ratio (Relative Strength)",
            range=x_range,
            gridcolor="#1F2937",
            color="#9CA3AF",
            zeroline=False,
        ),
        yaxis=dict(
            title="RS-Momentum (Rate of Change)",
            range=y_range,
            gridcolor="#1F2937",
            color="#9CA3AF",
            zeroline=False,
        ),
        shapes=[
            dict(
                type="rect",
                x0=100, x1=x_range[1], y0=100, y1=y_range[1],
                fillcolor="rgba(16, 185, 129, 0.08)", line_width=0, layer="below"
            ),
            dict(
                type="rect",
                x0=100, x1=x_range[1], y0=y_range[0], y1=100,
                fillcolor="rgba(245, 158, 11, 0.08)", line_width=0, layer="below"
            ),
            dict(
                type="rect",
                x0=x_range[0], x1=100, y0=y_range[0], y1=100,
                fillcolor="rgba(239, 68, 68, 0.08)", line_width=0, layer="below"
            ),
            dict(
                type="rect",
                x0=x_range[0], x1=100, y0=100, y1=y_range[1],
                fillcolor="rgba(59, 130, 246, 0.08)", line_width=0, layer="below"
            ),
            dict(
                type="line",
                x0=100, x1=100, y0=y_range[0], y1=y_range[1],
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
            dict(
                type="line",
                x0=x_range[0], x1=x_range[1], y0=100, y1=100,
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
        ],
        annotations=[
            dict(
                x=(100 + x_range[1]) / 2, y=(100 + y_range[1]) / 2,
                text="<b>LEADING</b>", showarrow=False, font=dict(color="rgba(16, 185, 129, 0.3)", size=24)
            ),
            dict(
                x=(100 + x_range[1]) / 2, y=(100 + y_range[0]) / 2,
                text="<b>WEAKENING</b>", showarrow=False, font=dict(color="rgba(245, 158, 11, 0.3)", size=24)
            ),
            dict(
                x=(100 + x_range[0]) / 2, y=(100 + y_range[0]) / 2,
                text="<b>LAGGING</b>", showarrow=False, font=dict(color="rgba(239, 68, 68, 0.3)", size=24)
            ),
            dict(
                x=(100 + x_range[0]) / 2, y=(100 + y_range[1]) / 2,
                text="<b>IMPROVING</b>", showarrow=False, font=dict(color="rgba(59, 130, 246, 0.3)", size=24)
            ),
        ],
    )

    summary_df = pd.DataFrame(summary_list, columns=columns_list)
    return fig, summary_df


def render_styled_table(data_frame, col_name="Sector / Stock Name"):
    if data_frame is None or data_frame.empty or "Quadrant" not in data_frame.columns:
        st.info("No items currently available in this category.")
        return

    rows = ""
    for _, row in data_frame.iterrows():
        rows += f"""<tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6; font-size:0.9rem;">
<td style="padding:12px 16px; font-weight:600;">{row['Name']}</td>
<td style="padding:12px 16px;"><span class="status-badge {row['BadgeClass']}">{row['Quadrant']}</span></td>
<td style="padding:12px 16px; font-weight:500;">{row['RS-Ratio']}</td>
<td style="padding:12px 16px; font-weight:500;">{row['RS-Momentum']}</td>
<td style="padding:12px 16px;">{row['Trend']}</td>
<td style="padding:12px 16px; font-weight:600; color:#38bdf8;">₹{row['CMP']}</td>
<td style="padding:12px 16px; font-weight:600; color:#f3f4f6;">₹{row['52W High']}</td>
<td style="padding:12px 16px; font-weight:600;">{row['Dist 52W High (%)']}%</td>
<td style="padding:12px 16px;"><span class="status-badge {row['NearBadgeClass']}">{row['Near 52W High']}</span></td>
</tr>"""

    table_html = f"""<table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; overflow:hidden; margin-top:10px;">
<thead>
<tr style="background-color:#1f2937; text-align:left; color:#9ca3af; font-size:0.9rem;">
<th style="padding:12px 16px;">{col_name}</th>
<th style="padding:12px 16px;">Quadrant</th>
<th style="padding:12px 16px;">RS-Ratio</th>
<th style="padding:12px 16px;">RS-Momentum</th>
<th style="padding:12px 16px;">Trend</th>
<th style="padding:12px 16px;">CMP (₹)</th>
<th style="padding:12px 16px;">52W High (₹)</th>
<th style="padding:12px 16px;">Dist High (%)</th>
<th style="padding:12px 16px;">Near 52W High (&le;{high_threshold}%)</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>"""

    st.markdown(table_html, unsafe_allow_html=True)


# -------------------------------------------------------------------
# FEATURE 1: ANIMATED RRG ROTATION GENERATOR
# -------------------------------------------------------------------
def render_animated_rrg(sector_rrg_dict, lookback_periods=12):
    if not sector_rrg_dict:
        st.warning("No sector data available for animation.")
        return

    all_dates = None
    for item in sector_rrg_dict.values():
        df_m = item["metrics"]
        if all_dates is None:
            all_dates = set(df_m.index)
        else:
            all_dates = all_dates.intersection(set(df_m.index))

    if not all_dates:
        st.warning("Not enough overlapping historical data for animation.")
        return

    sorted_dates = sorted(list(all_dates))[-lookback_periods:]
    if len(sorted_dates) < 3:
        st.warning("Insufficient dates for animation window.")
        return

    colors = [
        "#10B981", "#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899",
        "#14B8A6", "#F97316", "#6366F1", "#06B6D4", "#A855F7", "#EAB308",
        "#84CC16", "#F43F5E", "#D97706", "#059669", "#2563EB", "#7C3AED",
        "#DB2777", "#0284C7", "#16A34A", "#CA8A04", "#DC2626", "#4F46E5"
    ]

    init_date = sorted_dates[0]
    fig = go.Figure()

    for idx, (name, item) in enumerate(sector_rrg_dict.items()):
        df = item["metrics"]
        color = colors[idx % len(colors)]
        if init_date in df.index:
            rx = df.loc[init_date, "ratio"]
            ry = df.loc[init_date, "momentum"]
            fig.add_trace(
                go.Scatter(
                    x=[rx],
                    y=[ry],
                    mode="markers+text",
                    name=name,
                    text=[name],
                    textposition="top center",
                    marker=dict(size=12, color=color),
                )
            )

    frames = []
    for dt in sorted_dates:
        frame_data = []
        date_str = pd.to_datetime(dt).strftime("%d %b %Y")
        for idx, (name, item) in enumerate(sector_rrg_dict.items()):
            df = item["metrics"]
            color = colors[idx % len(colors)]
            if dt in df.index:
                sub_df = df.loc[:dt].tail(4)
                if sub_df.empty:
                    continue
                x_tail = sub_df["ratio"].values
                y_tail = sub_df["momentum"].values
                labels = [""] * (len(x_tail) - 1) + [name] if len(x_tail) > 0 else []
                markers = [6] * (len(x_tail) - 1) + [12] if len(x_tail) > 0 else []
                
                frame_data.append(
                    go.Scatter(
                        x=x_tail,
                        y=y_tail,
                        mode="lines+markers+text",
                        name=name,
                        text=labels,
                        textposition="top center",
                        marker=dict(size=markers, color=color),
                        line=dict(color=color, width=2),
                    )
                )
        frames.append(
            go.Frame(
                data=frame_data,
                name=date_str,
                layout=dict(title=f"🎬 RRG Sector Rotation Date: {date_str}"),
            )
        )

    fig.frames = frames

    fig.update_layout(
        title="🎬 Interactive Sector Rotation Animation (Click Play below)",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=620,
        xaxis=dict(
            title="RS-Ratio",
            range=[94, 106],
            gridcolor="#1F2937",
            zeroline=False,
        ),
        yaxis=dict(
            title="RS-Momentum",
            range=[94, 106],
            gridcolor="#1F2937",
            zeroline=False,
        ),
        shapes=[
            dict(
                type="line",
                x0=100, x1=100, y0=90, y1=110,
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
            dict(
                type="line",
                x0=90, x1=110, y0=100, y1=100,
                line=dict(color="#4B5563", width=1.5, dash="dash"),
            ),
        ],
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=0.0,
                x=0.0,
                xanchor="left",
                yanchor="top",
                pad=dict(t=10, r=10),
                buttons=[
                    dict(
                        label="▶️ Play Rotation",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=600, redraw=True),
                                fromcurrent=True,
                                mode="immediate",
                            ),
                        ],
                    ),
                    dict(
                        label="⏸️ Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                            ),
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [f.name],
                            dict(
                                mode="immediate",
                                frame=dict(duration=300, redraw=True),
                            ),
                        ],
                        label=f.name,
                    )
                    for f in frames
                ],
                transition=dict(duration=0),
                x=0.1,
                y=0,
                currentvalue=dict(
                    font=dict(size=12, color="#38bdf8"),
                    prefix="Date: ",
                    visible=True,
                ),
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# FEATURE 2: SECTOR VS SECTOR PAIR MATRIX
# -------------------------------------------------------------------
def render_pair_comparison(sec1_name, sec2_name, interval):
    t1 = SECTOR_MAP[sec1_name]["index"]
    t2 = SECTOR_MAP[sec2_name]["index"]

    data = yf.download(
        [t1, t2, BENCHMARK_SYMBOL],
        period="1y",
        interval=interval,
        progress=False,
    )
    if data.empty:
        st.error("Pair comparison data unavailable.")
        return

    df_close = extract_field_df(data, "Close")

    if t1 not in df_close.columns or t2 not in df_close.columns:
        st.error("Pair comparison data unavailable for selected tickers.")
        return

    pair_ratio = (df_close[t1] / df_close[t2]).dropna() * 100
    if pair_ratio.empty:
        st.error("Insufficient overlapping data for pair comparison.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Current Value ({sec1_name})", f"₹{df_close[t1].dropna().iloc[-1]:.2f}")
    c2.metric(f"Current Value ({sec2_name})", f"₹{df_close[t2].dropna().iloc[-1]:.2f}")

    curr_pair_ratio = pair_ratio.iloc[-1]
    prev_pair_ratio = (
        pair_ratio.iloc[-5] if len(pair_ratio) > 5 else curr_pair_ratio
    )
    pair_chg = ((curr_pair_ratio - prev_pair_ratio) / (prev_pair_ratio + 1e-6)) * 100
    c3.metric(
        f"Pair Strength ({sec1_name} / {sec2_name})",
        f"{curr_pair_ratio:.2f}",
        delta=f"{pair_chg:.2f}% (5 Periods)",
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pair_ratio.index,
            y=pair_ratio.values,
            mode="lines",
            line=dict(color="#38bdf8", width=2),
            name=f"{sec1_name} / {sec2_name} Ratio",
        )
    )

    ma_pair = pair_ratio.rolling(20).mean()
    fig.add_trace(
        go.Scatter(
            x=ma_pair.index,
            y=ma_pair.values,
            mode="lines",
            line=dict(color="#f59e0b", width=1.5, dash="dash"),
            name="20-Period MA Ratio",
        )
    )

    fig.update_layout(
        title=f"⚖️ Pair Strength Ratio Chart: {sec1_name} vs {sec2_name}",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=400,
        xaxis=dict(gridcolor="#1F2937", color="#9CA3AF"),
        yaxis=dict(
            title="Relative Ratio", gridcolor="#1F2937", color="#9CA3AF"
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------
# FEATURE 3 & 4: AUTOMATED TRADE SETUPS & BACKTESTING
# -------------------------------------------------------------------
def generate_trade_setups(sector_rrg_data):
    long_setups = []
    short_setups = []

    for sec_name, data in sector_rrg_data.items():
        metrics = data["metrics"]
        cmp = data["cmp"]
        high_52w = data["high_52w"]
        dist_52w = data["dist_52w"]

        if metrics.empty:
            continue

        curr_ratio = metrics["ratio"].iloc[-1]
        curr_mom = metrics["momentum"].iloc[-1]
        quad_name, _, _, _ = get_quadrant(curr_ratio, curr_mom)

        if (
            quad_name in ["Leading", "Improving"]
            and dist_52w <= 6.0
            and curr_mom >= 99.5
        ):
            stop_loss = round(cmp * 0.96, 2)
            target_1 = round(cmp * 1.08, 2)
            target_2 = round(cmp * 1.15, 2)
            long_setups.append({
                "Sector": sec_name,
                "Quadrant": quad_name,
                "CMP": cmp,
                "52W High": high_52w,
                "Dist High": f"{dist_52w}%",
                "Stop Loss": f"₹{stop_loss}",
                "Target 1": f"₹{target_1}",
                "Target 2": f"₹{target_2}",
                "Risk Reward": "1 : 2.0",
            })

        if quad_name == "Lagging" and dist_52w >= 12.0 and curr_mom < 99.5:
            stop_loss = round(cmp * 1.04, 2)
            target_1 = round(cmp * 0.92, 2)
            short_setups.append({
                "Sector": sec_name,
                "Quadrant": quad_name,
                "CMP": cmp,
                "52W High": high_52w,
                "Dist High": f"{dist_52w}%",
                "Stop Loss": f"₹{stop_loss}",
                "Target Downside": f"₹{target_1}",
                "Alert": "⚠️ Avoid Long / Consider Hedging",
            })

    return long_setups, short_setups


def run_quadrant_backtest(sector_rrg_data):
    results = []

    for sec_name, data in sector_rrg_data.items():
        metrics = data["metrics"].copy()
        prices = data["prices"]

        if metrics.empty or len(prices) < 50:
            continue

        quadrants = []
        for r, m in zip(metrics["ratio"], metrics["momentum"]):
            q, _, _, _ = get_quadrant(r, m)
            quadrants.append(q)

        # FIXED: Assign via dictionary/assign to avoid SettingWithCopyWarning & performance issues in Pandas 2.0+
        metrics = metrics.assign(
            quadrant=quadrants,
            price=prices.reindex(metrics.index)
        )
        metrics = metrics.assign(
            prev_quadrant=metrics["quadrant"].shift(1)
        )

        transitions = metrics[
            (metrics["prev_quadrant"] == "Improving")
            & (metrics["quadrant"] == "Leading")
        ]

        total_trades = 0
        returns_5d = []
        returns_10d = []

        for idx_date in transitions.index:
            try:
                p_entry = metrics.loc[idx_date, "price"]
                future_prices = metrics.loc[idx_date:, "price"]

                if len(future_prices) > 5:
                    p_5d = future_prices.iloc[5]
                    ret_5d = ((p_5d - p_entry) / p_entry) * 100
                    returns_5d.append(ret_5d)

                if len(future_prices) > 10:
                    p_10d = future_prices.iloc[10]
                    ret_10d = ((p_10d - p_entry) / p_entry) * 100
                    returns_10d.append(ret_10d)

                total_trades += 1
            except Exception:
                continue

        if total_trades > 0:
            avg_5d = np.mean(returns_5d) if returns_5d else 0
            avg_10d = np.mean(returns_10d) if returns_10d else 0
            win_rate = (
                (len([r for r in returns_10d if r > 0]) / len(returns_10d))
                * 100
                if returns_10d
                else 0
            )

            results.append({
                "Sector": sec_name,
                "Signals Count": total_trades,
                "Avg 5-Period Return (%)": round(float(avg_5d), 2),
                "Avg 10-Period Return (%)": round(float(avg_10d), 2),
                "Win Rate (10P) (%)": f"{round(float(win_rate), 1)}%",
            })

    return pd.DataFrame(results)


# -------------------------------------------------------------------
# FEATURE 5: SECTOR MONEY FLOW & ROLLOVER MATRIX MODULE
# -------------------------------------------------------------------
def calculate_sector_money_flow(sector_map):
    """Fetches Price & Volume Dynamics to calculate Sector Capital Inflow vs Outflow"""
    flow_summary = []

    for sec_name, sec_info in sector_map.items():
        stocks = list(sec_info["stocks"].values())
        if not stocks:
            continue

        try:
            raw_data = yf.download(
                stocks, period="5d", interval="1d", progress=False
            )

            if raw_data.empty:
                continue

            close_df = extract_field_df(raw_data, "Close")
            vol_df = extract_field_df(raw_data, "Volume")

            stock_scores = []
            long_buildup_count = 0
            short_buildup_count = 0
            long_unwinding_count = 0
            short_covering_count = 0

            for tk in stocks:
                if tk in close_df.columns and tk in vol_df.columns:
                    p_series = close_df[tk].dropna()
                    v_series = vol_df[tk].dropna()

                    if len(p_series) >= 2 and len(v_series) >= 2:
                        p_curr, p_prev = p_series.iloc[-1], p_series.iloc[-2]
                        v_curr, v_prev = v_series.iloc[-1], v_series.iloc[-2]

                        p_chg = ((p_curr - p_prev) / (p_prev + 1e-6)) * 100
                        v_chg = (
                            ((v_curr - v_prev) / (v_prev + 1e-6)) * 100
                            if v_prev > 0
                            else 0
                        )

                        # Buildup Logic (Price + Volume Expansion)
                        if p_chg > 0 and v_chg > 0:
                            long_buildup_count += 1
                        elif p_chg < 0 and v_chg > 0:
                            short_buildup_count += 1
                        elif p_chg < 0 and v_chg <= 0:
                            long_unwinding_count += 1
                        else:
                            short_covering_count += 1

                        score = p_chg * (1 + (v_chg / 100))
                        stock_scores.append(score)

            if stock_scores:
                avg_flow_score = round(float(np.mean(stock_scores)), 2)
                total_stocks = len(stock_scores)

                counts = {
                    "Long Buildup 🟢": long_buildup_count,
                    "Short Buildup 🔴": short_buildup_count,
                    "Long Unwinding 🟡": long_unwinding_count,
                    "Short Covering 🔵": short_covering_count,
                }
                dominant_state = max(counts, key=counts.get)

                flow_summary.append({
                    "Sector": sec_name,
                    "Money Flow Score": avg_flow_score,
                    "Dominant Buildup": dominant_state,
                    "Long Buildup Stocks": f"{long_buildup_count}/{total_stocks}",
                    "Short Buildup Stocks": f"{short_buildup_count}/{total_stocks}",
                    "Long Unwinding Stocks": f"{long_unwinding_count}/{total_stocks}",
                    "Short Covering Stocks": f"{short_covering_count}/{total_stocks}",
                })
        except Exception:
            continue

    df_res = pd.DataFrame(flow_summary)
    if not df_res.empty:
        df_res = df_res.sort_values(
            by="Money Flow Score", ascending=False
        ).reset_index(drop=True)
    return df_res


def render_money_flow_tab(sector_map):
    st.markdown("### 💸 Sector Capital Inflow vs Outflow Tracker")
    st.caption(
        "Price Change aur Volume/OI Expansion ko combine karke bataayein ki kis sector mein **Naya Capital Aa Raha Hai** aur kahan se **Liquidation Ho Raha Hai**."
    )

    with st.spinner("Calculating Live Sector Money Flow & F&O Dynamics..."):
        df_flow = calculate_sector_money_flow(sector_map)

    if df_flow.empty:
        st.warning("Data fetch karne me dikkat aayi. Please refresh karein.")
        return

    top_inflow = df_flow.iloc[0]
    top_outflow = df_flow.iloc[-1]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; padding: 15px; border-radius: 10px;">
                <h4 style="color: #10b981; margin:0;">🚀 Highest Capital Inflow Sector</h4>
                <h2 style="color: #ffffff; margin: 5px 0;">{top_inflow['Sector']}</h2>
                <p style="margin:0; color: #9ca3af;">Money Flow Score: <b style="color:#10b981;">+{top_inflow['Money Flow Score']}</b> | Status: <b>{top_inflow['Dominant Buildup']}</b></p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 15px; border-radius: 10px;">
                <h4 style="color: #ef4444; margin:0;">🔻 Highest Capital Outflow / Shorting</h4>
                <h2 style="color: #ffffff; margin: 5px 0;">{top_outflow['Sector']}</h2>
                <p style="margin:0; color: #9ca3af;">Money Flow Score: <b style="color:#ef4444;">{top_outflow['Money Flow Score']}</b> | Status: <b>{top_outflow['Dominant Buildup']}</b></p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Bar Chart for Money Flow Scores
    fig = go.Figure()
    colors = [
        "#10b981" if val >= 0 else "#ef4444"
        for val in df_flow["Money Flow Score"]
    ]

    fig.add_trace(
        go.Bar(
            x=df_flow["Sector"],
            y=df_flow["Money Flow Score"],
            marker_color=colors,
            text=df_flow["Money Flow Score"],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="📊 Sector Wise Net Money Flow Score (+Inflow / -Outflow)",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        height=420,
        xaxis=dict(gridcolor="#1F2937", color="#9CA3AF", tickangle=-45),
        yaxis=dict(
            title="Money Flow Score", gridcolor="#1F2937", color="#9CA3AF"
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Sector Open Interest & Buildup Breakdown Table")
    rows = ""
    for _, row in df_flow.iterrows():
        b_class = "bg-leading" if row["Money Flow Score"] >= 0 else "bg-lagging"
        rows += f"""<tr style="border-bottom: 1px solid #1f2937; color:#f3f4f6; font-size:0.9rem;">
<td style="padding:12px 16px; font-weight:600;">{row['Sector']}</td>
<td style="padding:12px 16px; font-weight:700;"><span class="status-badge {b_class}">{row['Money Flow Score']}</span></td>
<td style="padding:12px 16px; font-weight:600;">{row['Dominant Buildup']}</td>
<td style="padding:12px 16px; color:#10b981;">{row['Long Buildup Stocks']}</td>
<td style="padding:12px 16px; color:#ef4444;">{row['Short Buildup Stocks']}</td>
<td style="padding:12px 16px; color:#f59e0b;">{row['Long Unwinding Stocks']}</td>
<td style="padding:12px 16px; color:#3b82f6;">{row['Short Covering Stocks']}</td>
</tr>"""

    table_html = f"""<table style="width:100%; border-collapse:collapse; background-color:#111827; border-radius:8px; overflow:hidden; margin-top:10px;">
<thead>
<tr style="background-color:#1f2937; text-align:left; color:#9ca3af; font-size:0.9rem;">
<th style="padding:12px 16px;">Sector Name</th>
<th style="padding:12px 16px;">Flow Score</th>
<th style="padding:12px 16px;">Dominant Buildup</th>
<th style="padding:12px 16px;">Long Buildup 🟢</th>
<th style="padding:12px 16px;">Short Buildup 🔴</th>
<th style="padding:12px 16px;">Long Unwinding 🟡</th>
<th style="padding:12px 16px;">Short Covering 🔵</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>"""

    st.markdown(table_html, unsafe_allow_html=True)


# -------------------------------------------------------------------
# MAIN DASHBOARD NAVIGATION (5 INTEGRATED TABS)
# -------------------------------------------------------------------

main_tab1, main_tab2, main_tab3, main_tab4, main_tab5 = st.tabs([
    "🌐 All NSE Sectors",
    "🎯 Heavyweight Stock Drill-Down",
    "🎬 Animated RRG & Pair Matrix",
    "🤖 AI Trade Setups & Backtesting",
    "💸 Sector Money Flow & Rollover Matrix",
])

# Fetch Sector Data
sector_ticker_dict = {sec: SECTOR_MAP[sec]["index"] for sec in SECTOR_MAP}

# FIXED: Replaced broad-scope spinner with focused data-loading spinner
with st.spinner("Fetching Live Sector Market Data..."):
    sector_rrg_data = fetch_and_build_rrg(
        sector_ticker_dict, BENCHMARK_SYMBOL, timeframe
    )

# TAB 1: SECTORS RRG
with main_tab1:
    st.markdown("### 📊 All NSE Sector Rotations vs Nifty 50")
    fig_sec, df_sec_summary = render_rrg_chart(
        sector_rrg_data, "All NSE Sectors Relative Rotation Graph"
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    st.subheader("📋 Sector Rotation Matrix")
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "All Sectors",
        "🔥 Near 52W High",
        "🚀 Leading",
        "⚡ Improving",
        "⚠️ Weakening",
        "🔻 Lagging",
    ])

    with t1:
        render_styled_table(df_sec_summary, "Sector Name")
    with t2:
        render_styled_table(
            df_sec_summary[
                df_sec_summary["Dist 52W High (%)"] <= high_threshold
            ],
            "Sector Name",
        )
    with t3:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Leading"],
            "Sector Name",
        )
    with t4:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Improving"],
            "Sector Name",
        )
    with t5:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Weakening"],
            "Sector Name",
        )
    with t6:
        render_styled_table(
            df_sec_summary[df_sec_summary["Quadrant"] == "Lagging"],
            "Sector Name",
        )


# TAB 2: STOCK DRILL-DOWN RRG
with main_tab2:
    st.markdown(
        f"### 🎯 Stock Drill-Down Analysis: <span style='color:#38bdf8;'>{selected_sector_for_stocks}</span>",
        unsafe_allow_html=True,
    )

    selected_sector_info = SECTOR_MAP[selected_sector_for_stocks]
    stock_dict = selected_sector_info["stocks"]
    sector_bench_symbol = selected_sector_info["index"]

    with st.spinner(
        f"Fetching Live Stock Data for {selected_sector_for_stocks}..."
    ):
        stock_rrg_data = fetch_and_build_rrg(
            stock_dict, sector_bench_symbol, timeframe
        )

    fig_stock, df_stock_summary = render_rrg_chart(
        stock_rrg_data,
        f"{selected_sector_for_stocks} Top Stocks vs Sector Index/Benchmark",
    )
    st.plotly_chart(fig_stock, use_container_width=True)

    st.subheader(f"📋 {selected_sector_for_stocks} Stock Matrix")
    st1, st2, st3, st4, st5, st6 = st.tabs([
        "All Sector Stocks",
        "🔥 Near 52W High",
        "🚀 Leading",
        "⚡ Improving",
        "⚠️ Weakening",
        "🔻 Lagging",
    ])

    with st1:
        render_styled_table(df_stock_summary, "Stock Name")
    with st2:
        render_styled_table(
            df_stock_summary[
                df_stock_summary["Dist 52W High (%)"] <= high_threshold
            ],
            "Stock Name",
        )
    with st3:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Leading"],
            "Stock Name",
        )
    with st4:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Improving"],
            "Stock Name",
        )
    with st5:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Weakening"],
            "Stock Name",
        )
    with st6:
        render_styled_table(
            df_stock_summary[df_stock_summary["Quadrant"] == "Lagging"],
            "Stock Name",
        )


# TAB 3: ANIMATED RRG & SECTOR PAIR MATRIX
with main_tab3:
    st.markdown("### 🎬 Historical RRG Rotation Player")
    st.caption(
        "Niche **Play** button par click karke dekhein ki pichle 12 periods mein sectors ne quadrants kaise rotate kiye."
    )
    render_animated_rrg(sector_rrg_data, lookback_periods=12)

    st.markdown("---")
    st.markdown("### ⚔️ Sector vs Sector Pair Strength Ratio")
    st.caption(
        "Select any 2 sectors to compare their relative strength ratio directly (Pair Trading Analysis)."
    )

    col1, col2 = st.columns(2)
    s1 = col1.selectbox(
        "Base Sector (Numerator)", options=list(SECTOR_MAP.keys()), index=0
    )
    s2 = col2.selectbox(
        "Benchmark Sector (Denominator)",
        options=list(SECTOR_MAP.keys()),
        index=1,
    )

    if s1 == s2:
        st.warning("Please select two different sectors to compare.")
    else:
        render_pair_comparison(s1, s2, timeframe)


# TAB 4: AI TRADE SETUPS & BACKTESTING
with main_tab4:
    st.markdown("### 🤖 Automated AI Trade Setups")
    st.caption(
        "High-conviction setups generated automatically based on RRG Quadrants & 52-Week High Proximity."
    )

    long_ideas, short_ideas = generate_trade_setups(sector_rrg_data)

    c_long, c_short = st.columns(2)

    with c_long:
        st.markdown(
            "#### 🚀 Bullish High-Conviction Setups (Leading / Early Improving)"
        )
        if not long_ideas:
            st.info("No high-conviction bullish setups at this moment.")
        else:
            for item in long_ideas:
                st.markdown(
                    f"""
                <div class="setup-card-long">
                    <h4 style="color:#10b981; margin:0;">{item['Sector']} <span style="font-size:0.8rem; color:#9ca3af;">({item['Quadrant']})</span></h4>
                    <p style="margin:5px 0; color:#f3f4f6;"><b>CMP:</b> ₹{item['CMP']} | <b>52W High:</b> ₹{item['52W High']} (Dist: {item['Dist High']})</p>
                    <p style="margin:5px 0; color:#38bdf8;">🎯 <b>Target 1:</b> {item['Target 1']} | 🎯 <b>Target 2:</b> {item['Target 2']}</p>
                    <p style="margin:5px 0; color:#ef4444;">🛑 <b>Stop Loss:</b> {item['Stop Loss']} (RR {item['Risk Reward']})</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    with c_short:
        st.markdown("#### 🔻 Bearish / Exit Warning Setups (Lagging Quadrant)")
        if not short_ideas:
            st.info("No high-risk short/exit setups detected.")
        else:
            for item in short_ideas:
                st.markdown(
                    f"""
                <div class="setup-card-short">
                    <h4 style="color:#ef4444; margin:0;">{item['Sector']} <span style="font-size:0.8rem; color:#9ca3af;">({item['Quadrant']})</span></h4>
                    <p style="margin:5px 0; color:#f3f4f6;"><b>CMP:</b> ₹{item['CMP']} | <b>52W High:</b> ₹{item['52W High']} (Dist: {item['Dist High']})</p>
                    <p style="margin:5px 0; color:#f59e0b;"><b>Downside Target:</b> {item['Target Downside']}</p>
                    <p style="margin:5px 0; color:#ef4444;">⚠️ <b>{item['Alert']}</b></p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("### 📈 Historical Quadrant Shift Backtest Engine")
    st.caption(
        "Proof of Performance: Jab koi sector **Improving se Leading Quadrant** mein enter hota hai, uske baad ke historical returns:"
    )

    backtest_df = run_quadrant_backtest(sector_rrg_data)
    if backtest_df.empty:
        st.info("Calculating backtest metrics...")
    else:
        st.dataframe(backtest_df, use_container_width=True, hide_index=True)


# TAB 5: SECTOR MONEY FLOW & ROLLOVER MATRIX
with main_tab5:
    render_money_flow_tab(SECTOR_MAP)


# Footer Branding
st.markdown(
    """
    <div class="footer-text">
        © 2026 <b>Grow More Trading Institute</b> | Institutional RRG & AI Trade Intelligence Dashboard
    </div>
""",
    unsafe_allow_html=True,
)
