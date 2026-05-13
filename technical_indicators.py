import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
import warnings
import traceback
import logging
import sys
import json
import hashlib
from functools import wraps
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings('ignore')

# ==================== ADVANCED CONFIGURATION ====================
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v21", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 30 seconds for near real-time
st_autorefresh(interval=30 * 1000, key="realtime_refresh")

# ==================== PROFESSIONAL DARK THEME CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', 'Cairo', sans-serif !important; letter-spacing: -0.01em; }
    .main { background: linear-gradient(180deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%); color: #e2e8f0; }
    .pro-panel { background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98)); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.4); margin-bottom: 12px; transition: all 0.2s ease; }
    .pro-panel:hover { border-color: rgba(99,102,241,0.15); box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
    .pro-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .pro-panel-title { font-size: 13px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .pro-panel-value { font-size: 24px; font-weight: 700; color: #f1f5f9; margin: 4px 0; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
    .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
    .status-up { color: #10b981; } .status-down { color: #ef4444; } .status-neutral { color: #94a3b8; } .status-warning { color: #f59e0b; }
    .badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-green { background: rgba(16,185,129,0.15); color: #10b981; } .badge-red { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; } .badge-blue { background: rgba(99,102,241,0.15); color: #818cf8; }
    .badge-purple { background: rgba(139,92,246,0.15); color: #a78bfa; }
    .live-pulse { display: inline-block; width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse-live 2s infinite; margin-left: 6px; }
    @keyframes pulse-live { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } }
    .stock-card { background: linear-gradient(145deg, rgba(25,25,35,0.9), rgba(20,20,30,0.95)); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; text-align: center; cursor: pointer; transition: all 0.2s ease; position: relative; overflow: hidden; }
    .stock-card:hover { border-color: rgba(99,102,241,0.3); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.15); }
    .stock-card-symbol { font-size: 14px; font-weight: 700; color: #fbbf24; margin-bottom: 4px; }
    .stock-card-price { font-size: 20px; font-weight: 700; color: #f1f5f9; margin: 4px 0; }
    .stock-card-change { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 12px; display: inline-block; }
    .stock-card-change.up { background: rgba(16,185,129,0.15); color: #10b981; }
    .stock-card-change.down { background: rgba(239,68,68,0.15); color: #ef4444; }
    .signal-box { border-radius: 8px; padding: 16px; text-align: center; border: 1px solid; }
    .signal-buy { background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.02)); border-color: rgba(16,185,129,0.3); }
    .signal-sell { background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.02)); border-color: rgba(239,68,68,0.3); }
    .signal-hold { background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.02)); border-color: rgba(245,158,11,0.3); }
    .risk-metric { padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }
    .risk-low { border-color: rgba(16,185,129,0.3); } .risk-medium { border-color: rgba(245,158,11,0.3); } .risk-high { border-color: rgba(239,68,68,0.3); }
    .corporate-card { padding: 16px; background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05)); border: 1px solid rgba(99,102,241,0.15); border-radius: 12px; margin-bottom: 12px; }
    .task-item { padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid; transition: all 0.2s; }
    .task-item:hover { background: rgba(255,255,255,0.04); }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(255,255,255,0.02); padding: 4px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 6px; padding: 10px 20px; border: none; color: #64748b; font-size: 13px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: rgba(99,102,241,0.15) !important; color: #818cf8 !important; font-weight: 600; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
    div[data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 700 !important; color: #f1f5f9 !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f0f16 0%, #1a1a2e 100%); border-right: 1px solid rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE MANAGEMENT ====================
def init_session_state():
    """Initialize all session state variables with safe defaults"""
    defaults = {
        'selected_stock': None,
        'show_analysis': False,
        'analysis_symbol': None,
        'debug_mode': False,
        'market_data_cache': {},
        'tasks': [
            {"id": 1, "title": "مراجعة أداء سهم CIB", "priority": "high", "category": "work", "due": "2026-05-15", "completed": False, "created": "2026-05-10"},
            {"id": 2, "title": "تحليل تقرير البورصة الأسبوعي", "priority": "medium", "category": "work", "due": "2026-05-16", "completed": True, "created": "2026-05-09"},
            {"id": 3, "title": "قراءة كتاب الاستثمار الذكي", "priority": "low", "category": "learning", "due": "2026-05-20", "completed": False, "created": "2026-05-08"},
            {"id": 4, "title": "متابعة اجتماع عمومية البنك التجاري", "priority": "high", "category": "urgent", "due": "2026-05-14", "completed": False, "created": "2026-05-12"},
            {"id": 5, "title": "تحديث بيانات المحفظة الاستثمارية", "priority": "medium", "category": "personal", "due": "2026-05-13", "completed": False, "created": "2026-05-11"},
        ],
        'alerts_cache': None,
        'alerts_timestamp': None,
        'last_analysis': None,
        'risk_settings': {'max_risk_pct': 2.0, 'max_portfolio_heat': 25.0, 'min_rr': 1.5},
        'corporate_cache': None,
        'active_tab': 0,
        'price_history_sim': {},
        'realtime_prices': {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== HYBRID DATA ENGINE (REAL + FALLBACK) ====================
class EGXDataEngine:
    """Advanced data engine with real-time fallback simulation"""

    EGYPTIAN_STOCKS = [
        {"symbol": "COMI", "name": "CIB", "sector": "بنوك", "base_price": 140.01, "volatility": 0.015, "market_cap": 420000000000},
        {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "base_price": 58.14, "volatility": 0.012, "market_cap": 180000000000},
        {"symbol": "ADIB", "name": "أبوظبي الإسلامي", "sector": "بنوك", "base_price": 47.49, "volatility": 0.018, "market_cap": 95000000000},
        {"symbol": "HDBK", "name": "بنك الإسكان", "sector": "بنوك", "base_price": 147.26, "volatility": 0.014, "market_cap": 220000000000},
        {"symbol": "CANA", "name": "قناة السويس", "sector": "بنوك", "base_price": 33.88, "volatility": 0.022, "market_cap": 45000000000},
        {"symbol": "CIEB", "name": "كريدي أجريكول", "sector": "بنوك", "base_price": 23.73, "volatility": 0.016, "market_cap": 32000000000},
        {"symbol": "FAIT", "name": "فيصل الإسلامي", "sector": "بنوك", "base_price": 34.11, "volatility": 0.015, "market_cap": 48000000000},
        {"symbol": "SAUD", "name": "البركة", "sector": "بنوك", "base_price": 24.70, "volatility": 0.017, "market_cap": 28000000000},
        {"symbol": "UBEE", "name": "المصرف المتحد", "sector": "بنوك", "base_price": 13.98, "volatility": 0.025, "market_cap": 15000000000},
        {"symbol": "EXPA", "name": "التنمية الصادرات", "sector": "بنوك", "base_price": 18.68, "volatility": 0.019, "market_cap": 22000000000},
        {"symbol": "EFIH", "name": "e-Finance", "sector": "تكنولوجيا مالية", "base_price": 22.32, "volatility": 0.028, "market_cap": 65000000000},
        {"symbol": "FWRY", "name": "فوري", "sector": "تكنولوجيا مالية", "base_price": 20.88, "volatility": 0.026, "market_cap": 52000000000},
        {"symbol": "SCTS", "name": "مقاصة قناة السويس", "sector": "تكنولوجيا مالية", "base_price": 652.11, "volatility": 0.012, "market_cap": 130000000000},
        {"symbol": "VALU", "name": "U للتمويل", "sector": "تكنولوجيا مالية", "base_price": 12.60, "volatility": 0.032, "market_cap": 18000000000},
        {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "base_price": 98.25, "volatility": 0.016, "market_cap": 280000000000},
        {"symbol": "EMFD", "name": "إعمار مصر", "sector": "عقارات", "base_price": 11.10, "volatility": 0.024, "market_cap": 55000000000},
        {"symbol": "PHDC", "name": "بالم هيلز", "sector": "عقارات", "base_price": 14.00, "volatility": 0.021, "market_cap": 42000000000},
        {"symbol": "ORHD", "name": "أوراسكوم للتنمية", "sector": "عقارات", "base_price": 33.35, "volatility": 0.018, "market_cap": 78000000000},
        {"symbol": "OCDI", "name": "سوديك", "sector": "عقارات", "base_price": 22.98, "volatility": 0.017, "market_cap": 65000000000},
        {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "base_price": 89.51, "volatility": 0.015, "market_cap": 180000000000},
        {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "base_price": 317.00, "volatility": 0.020, "market_cap": 95000000000},
        {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "base_price": 87.19, "volatility": 0.014, "market_cap": 72000000000},
        {"symbol": "MFPC", "name": "موبكو", "sector": "صناعة", "base_price": 45.15, "volatility": 0.019, "market_cap": 48000000000},
        {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "base_price": 58.00, "volatility": 0.016, "market_cap": 35000000000},
        {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "base_price": 98.49, "volatility": 0.013, "market_cap": 200000000000},
        {"symbol": "EGSA", "name": "النايل سات", "sector": "اتصالات", "base_price": 9.09, "volatility": 0.018, "market_cap": 18000000000},
        {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "base_price": 40.31, "volatility": 0.012, "market_cap": 85000000000},
        {"symbol": "EFID", "name": "إيديتا", "sector": "سلع استهلاكية", "base_price": 28.60, "volatility": 0.015, "market_cap": 62000000000},
        {"symbol": "JUFO", "name": "جهينة", "sector": "سلع استهلاكية", "base_price": 28.90, "volatility": 0.014, "market_cap": 58000000000},
        {"symbol": "DOMT", "name": "دومتي", "sector": "سلع استهلاكية", "base_price": 26.00, "volatility": 0.022, "market_cap": 22000000000},
        {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "base_price": 48.81, "volatility": 0.013, "market_cap": 38000000000},
        {"symbol": "POUL", "name": "القاهرة للدواجن", "sector": "سلع استهلاكية", "base_price": 34.80, "volatility": 0.016, "market_cap": 28000000000},
        {"symbol": "GBCO", "name": "GB Corp", "sector": "سلع استهلاكية", "base_price": 29.30, "volatility": 0.020, "market_cap": 45000000000},
        {"symbol": "ORWE", "name": "النساجون الشرقيون", "sector": "سلع استهلاكية", "base_price": 23.56, "volatility": 0.015, "market_cap": 32000000000},
        {"symbol": "CLHO", "name": "كليوباترا", "sector": "صحة", "base_price": 14.94, "volatility": 0.021, "market_cap": 18000000000},
        {"symbol": "PHAR", "name": "أمون", "sector": "صحة", "base_price": 89.49, "volatility": 0.014, "market_cap": 42000000000},
        {"symbol": "ISPH", "name": "ابن سينا", "sector": "صحة", "base_price": 11.96, "volatility": 0.019, "market_cap": 35000000000},
        {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "base_price": 687.72, "volatility": 0.011, "market_cap": 85000000000},
        {"symbol": "NIPH", "name": "النيل للأدوية", "sector": "صحة", "base_price": 173.20, "volatility": 0.013, "market_cap": 22000000000},
        {"symbol": "ADCI", "name": "العربية للأدوية", "sector": "صحة", "base_price": 216.63, "volatility": 0.012, "market_cap": 28000000000},
        {"symbol": "AXPH", "name": "الإسكندرية للأدوية", "sector": "صحة", "base_price": 1166.22, "volatility": 0.010, "market_cap": 65000000000},
        {"symbol": "HRHO", "name": "EFG هيرمس", "sector": "استثمار", "base_price": 29.50, "volatility": 0.023, "market_cap": 75000000000},
        {"symbol": "BTFH", "name": "بلتون", "sector": "استثمار", "base_price": 3.20, "volatility": 0.035, "market_cap": 8000000000},
        {"symbol": "CCAP", "name": "قلعة", "sector": "استثمار", "base_price": 4.70, "volatility": 0.028, "market_cap": 12000000000},
        {"symbol": "CICH", "name": "سي آي كابيتال", "sector": "استثمار", "base_price": 12.90, "volatility": 0.030, "market_cap": 15000000000},
        {"symbol": "RAYA", "name": "راية", "sector": "استثمار", "base_price": 7.10, "volatility": 0.032, "market_cap": 22000000000},
        {"symbol": "RACC", "name": "راية لخدمة العملاء", "sector": "استثمار", "base_price": 10.25, "volatility": 0.022, "market_cap": 18000000000},
        {"symbol": "BINV", "name": "B للاستثمارات", "sector": "استثمار", "base_price": 42.00, "volatility": 0.018, "market_cap": 28000000000},
        {"symbol": "AMOC", "name": "Alexandria Mineral Oils", "sector": "طاقة", "base_price": 8.59, "volatility": 0.024, "market_cap": 25000000000},
        {"symbol": "EGAS", "name": "مصر للغاز", "sector": "طاقة", "base_price": 49.12, "volatility": 0.016, "market_cap": 35000000000},
        {"symbol": "MTIE", "name": "MM Group", "sector": "تعليم", "base_price": 9.42, "volatility": 0.026, "market_cap": 18000000000},
        {"symbol": "MPRC", "name": "مدينة الإنتاج", "sector": "إعلام", "base_price": 31.75, "volatility": 0.017, "market_cap": 12000000000},
        {"symbol": "ETRS", "name": "النقل والخدمات", "sector": "نقل", "base_price": 7.78, "volatility": 0.021, "market_cap": 15000000000},
        {"symbol": "EEII", "name": "العربية للصناعات الهندسية", "sector": "تكنولوجيا", "base_price": 2.35, "volatility": 0.040, "market_cap": 8000000000},
    ]

    def __init__(self):
        self.cache = st.session_state.market_data_cache
        self.price_history = st.session_state.price_history_sim

    def _generate_realistic_price(self, stock_info: dict) -> dict:
        """Generate realistic simulated price with random walk"""
        symbol = stock_info['symbol']
        base = stock_info['base_price']
        vol = stock_info['volatility']

        # Use stored simulated price if exists, else base
        if symbol in self.price_history:
            last_price = self.price_history[symbol]
        else:
            last_price = base

        # Random walk with mean reversion to base
        drift = (base - last_price) * 0.01  # Mean reversion factor
        shock = np.random.normal(drift, vol * last_price)
        new_price = max(last_price + shock, base * 0.5)  # Floor at 50% of base

        # Calculate change from base
        change = new_price - base
        change_pct = (change / base) * 100

        # Volume simulation (correlated with volatility)
        base_volume = stock_info.get('market_cap', 1e9) / (new_price * 100)
        volume_shock = np.random.lognormal(0, 0.5)
        volume = int(base_volume * volume_shock)

        # High/Low simulation
        high = new_price * (1 + abs(np.random.normal(0, vol/2)))
        low = new_price * (1 - abs(np.random.normal(0, vol/2)))

        self.price_history[symbol] = new_price

        return {
            "symbol": symbol,
            "name": stock_info['name'],
            "sector": stock_info['sector'],
            "price": round(new_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "high": round(high, 2),
            "low": round(low, 2),
            "market_cap": stock_info['market_cap'],
            "open": round(new_price - np.random.normal(0, vol * new_price * 0.3), 2),
            "volatility": vol,
            "base_price": base
        }

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_yfinance_data(_self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """Fetch from yfinance with Cairo suffix"""
        try:
            ticker = yf.Ticker(f"{symbol}.CA")
            df = ticker.history(period=period)
            if df.empty or len(df) < 5:
                return None
            return df
        except Exception:
            return None

    def get_live_prices(self) -> List[dict]:
        """Get live prices - try yfinance first, fallback to simulation"""
        results = []
        for stock in self.EGYPTIAN_STOCKS:
            # Try real data first (but don't block on failure)
            real_df = self.fetch_yfinance_data(stock['symbol'], "1d")
            if real_df is not None and not real_df.empty:
                last = real_df.iloc[-1]
                results.append({
                    "symbol": stock['symbol'],
                    "name": stock['name'],
                    "sector": stock['sector'],
                    "price": round(last['Close'], 2),
                    "change": round(last['Close'] - last['Open'], 2),
                    "change_pct": round((last['Close'] - last['Open']) / last['Open'] * 100, 2) if last['Open'] > 0 else 0,
                    "volume": int(last['Volume']) if 'Volume' in last else 0,
                    "high": round(last['High'], 2),
                    "low": round(last['Low'], 2),
                    "market_cap": stock['market_cap'],
                    "open": round(last['Open'], 2),
                    "volatility": stock['volatility'],
                    "base_price": stock['base_price'],
                    "source": "yfinance"
                })
            else:
                sim = self._generate_realistic_price(stock)
                sim["source"] = "simulated"
                results.append(sim)
        return results

    def get_stock_history(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """Get historical data with caching"""
        cache_key = f"{symbol}_{period}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if (datetime.now() - entry["timestamp"]).seconds < 300:
                return entry["data"]

        # Try yfinance
        df = self.fetch_yfinance_data(symbol, period)
        if df is not None and len(df) > 20:
            self.cache[cache_key] = {"data": df, "timestamp": datetime.now()}
            return df

        # Fallback: generate synthetic history
        stock = next((s for s in self.EGYPTIAN_STOCKS if s['symbol'] == symbol), None)
        if not stock:
            return None

        days = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504}.get(period, 66)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')

        prices = [stock['base_price']]
        for _ in range(1, days):
            drift = (stock['base_price'] - prices[-1]) * 0.005
            shock = np.random.normal(drift, stock['volatility'] * prices[-1])
            prices.append(max(prices[-1] + shock, stock['base_price'] * 0.5))

        df = pd.DataFrame({
            'Open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
            'High': [p * (1 + abs(np.random.normal(0, stock['volatility']/2))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, stock['volatility']/2))) for p in prices],
            'Close': prices,
            'Volume': [int(stock['market_cap'] / (p * 100) * np.random.lognormal(0, 0.5)) for p in prices]
        }, index=dates)

        self.cache[cache_key] = {"data": df, "timestamp": datetime.now()}
        return df

data_engine = EGXDataEngine()

# ==================== ADVANCED TECHNICAL ANALYSIS ENGINE ====================
class TechnicalAnalyzer:
    """Comprehensive technical analysis with validation"""

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if df is None or len(df) < 30:
            return None

        df = df.copy()

        # RSI (14)
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']

        # Stochastic
        low_14 = df['Low'].rolling(14).min()
        high_14 = df['High'].rolling(14).max()
        df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
        df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['EMA_20'] = df['Close'].ewm(span=20).mean()

        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()

        # Volume
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA'].replace(0, np.nan)

        # Momentum & ROC
        df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
        df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100

        # ADX (Average Directional Index)
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = np.abs(minus_dm)

        tr = true_range
        atr = tr.rolling(14).mean()
        plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['ADX'] = dx.rolling(14).mean()

        return df

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> List[Tuple]:
        """Generate comprehensive trading signals"""
        if df is None or len(df) < 30:
            return []

        signals = []
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        # RSI Signals
        if pd.notna(latest.get('RSI')):
            if latest['RSI'] < 30:
                signals.append(("RSI", "شراء قوي", 2, "ذروة بيع", "oversold"))
            elif latest['RSI'] > 70:
                signals.append(("RSI", "بيع قوي", -2, "ذروة شراء", "overbought"))
            elif latest['RSI'] < 40:
                signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء", "bullish"))
            elif latest['RSI'] > 60:
                signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع", "bearish"))
            else:
                signals.append(("RSI", "محايد", 0, "لا إشارة", "neutral"))

        # MACD Signals
        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
            if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signals.append(("MACD", "شراء", 2, "تقاطع صاعد", "bullish"))
            elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                signals.append(("MACD", "بيع", -2, "تقاطع هابط", "bearish"))
            elif latest['MACD'] > latest['MACD_Signal']:
                signals.append(("MACD", "شراء ضعيف", 1, "MACD إيجابي", "bullish"))
            else:
                signals.append(("MACD", "بيع ضعيف", -1, "MACD سلبي", "bearish"))

        # Bollinger Signals
        if pd.notna(latest.get('Close')) and pd.notna(latest.get('BB_Lower')):
            if latest['Close'] < latest['BB_Lower']:
                signals.append(("Bollinger", "شراء قوي", 2, "تحت النطاق السفلي", "oversold"))
            elif latest['Close'] > latest['BB_Upper']:
                signals.append(("Bollinger", "بيع قوي", -2, "فوق النطاق العلوي", "overbought"))
            else:
                signals.append(("Bollinger", "محايد", 0, "داخل النطاق", "neutral"))

        # Stochastic
        if pd.notna(latest.get('Stoch_K')) and pd.notna(latest.get('Stoch_D')):
            if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
                signals.append(("Stochastic", "شراء", 1.5, "ذروة بيع", "oversold"))
            elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
                signals.append(("Stochastic", "بيع", -1.5, "ذروة شراء", "overbought"))
            else:
                signals.append(("Stochastic", "محايد", 0, "لا إشارة", "neutral"))

        # Moving Averages
        if pd.notna(latest.get('Close')) and pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
            if latest['Close'] > latest['SMA_20'] and latest['Close'] > latest['SMA_50'] and latest['SMA_20'] > latest['SMA_50']:
                signals.append(("MA", "شراء قوي", 1.5, "اتجاه صاعد قوي", "bullish"))
            elif latest['Close'] < latest['SMA_20'] and latest['Close'] < latest['SMA_50'] and latest['SMA_20'] < latest['SMA_50']:
                signals.append(("MA", "بيع قوي", -1.5, "اتجاه هابط قوي", "bearish"))
            elif latest['Close'] > latest['SMA_20']:
                signals.append(("MA", "شراء ضعيف", 0.5, "فوق SMA20", "bullish"))
            else:
                signals.append(("MA", "بيع ضعيف", -0.5, "تحت SMA20", "bearish"))

        # ADX (Trend Strength)
        if pd.notna(latest.get('ADX')):
            if latest['ADX'] > 25:
                signals.append(("ADX", "تأكيد", 0.5, "اتجاه قوي", "confirmation"))
            elif latest['ADX'] < 20:
                signals.append(("ADX", "تحذير", -0.3, "اتجاه ضعيف", "warning"))

        # Volume
        if pd.notna(latest.get('Volume_Ratio')):
            if latest['Volume_Ratio'] > 2.0:
                signals.append(("Volume", "تأكيد قوي", 1.0, "حجم تداول استثنائي", "confirmation"))
            elif latest['Volume_Ratio'] > 1.5:
                signals.append(("Volume", "تأكيد", 0.5, "حجم نشط", "confirmation"))
            elif latest['Volume_Ratio'] < 0.5:
                signals.append(("Volume", "ضعف", -0.5, "حجم ضعيف", "warning"))

        return signals

    @staticmethod
    def calculate_overall(signals: List[Tuple]) -> Tuple[str, float, str, str]:
        """Calculate overall signal with trend classification"""
        if not signals:
            return "HOLD", 0, "لا توجد بيانات كافية", "neutral"

        total_score = sum([s[2] for s in signals if len(s) > 2])

        # Determine trend direction
        bullish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bullish", "oversold", "confirmation"])
        bearish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bearish", "overbought", "warning"])

        if total_score >= 4:
            return "STRONG_BUY", total_score, "إشارة شراء قوية", "strong_bullish"
        elif total_score >= 2:
            return "BUY", total_score, "إشارة شراء", "bullish"
        elif total_score <= -4:
            return "STRONG_SELL", total_score, "إشارة بيع قوية", "strong_bearish"
        elif total_score <= -2:
            return "SELL", total_score, "إشارة بيع", "bearish"
        else:
            if bullish_count > bearish_count:
                return "HOLD", total_score, "انتظار - ميل صاعد", "weak_bullish"
            elif bearish_count > bullish_count:
                return "HOLD", total_score, "انتظار - ميل هابط", "weak_bearish"
            return "HOLD", total_score, "محايد", "neutral"

# ==================== ADVANCED RISK MANAGEMENT ENGINE ====================
class RiskEngine:
    """Professional risk management and position sizing"""

    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if returns.empty or returns.std() == 0:
            return 0.0
        return np.percentile(returns.dropna(), (1 - confidence) * 100)

    @staticmethod
    def calculate_expected_shortfall(returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Expected Shortfall (CVaR)"""
        var = RiskEngine.calculate_var(returns, confidence)
        return returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else var

    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Kelly Criterion for optimal position sizing"""
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return 0.0
        b = avg_win / avg_loss
        q = 1 - win_rate
        kelly = (win_rate * b - q) / b
        return max(0, min(kelly, 0.25))  # Cap at 25%

    @staticmethod
    def calculate_position_size(account_balance: float, risk_per_trade_pct: float, 
                                  entry_price: float, stop_loss: float) -> Tuple[int, float, float]:
        """Calculate optimal position size"""
        risk_amount = account_balance * (risk_per_trade_pct / 100)
        price_risk = abs(entry_price - stop_loss)
        if price_risk == 0:
            return 0, 0, 0
        shares = int(risk_amount / price_risk)
        position_value = shares * entry_price
        actual_risk_pct = (price_risk * shares) / account_balance * 100
        return shares, position_value, actual_risk_pct

    @staticmethod
    def analyze_risk_profile(df: pd.DataFrame, entry_price: float, stop_loss: float, 
                              take_profit: float, account_balance: float = 100000) -> dict:
        """Comprehensive risk analysis"""
        if df is None or len(df) < 20:
            return {}

        returns = df['Close'].pct_change().dropna()

        # Basic metrics
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized
        var_95 = RiskEngine.calculate_var(returns, 0.95) * 100
        var_99 = RiskEngine.calculate_var(returns, 0.99) * 100
        cvar_95 = RiskEngine.calculate_expected_shortfall(returns, 0.95) * 100

        # Risk/Reward
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        rr_ratio = reward / risk if risk > 0 else 0

        # Position sizing
        shares, position_value, actual_risk = RiskEngine.calculate_position_size(
            account_balance, st.session_state.risk_settings['max_risk_pct'], entry_price, stop_loss
        )

        # Win rate estimation from historical volatility
        positive_days = len(returns[returns > 0])
        total_days = len(returns[returns != 0])
        win_rate = positive_days / total_days if total_days > 0 else 0.5

        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
        kelly = RiskEngine.kelly_criterion(win_rate, avg_win, avg_loss)

        # Maximum consecutive losses
        consecutive_losses = 0
        max_consecutive = 0
        for r in returns:
            if r < 0:
                consecutive_losses += 1
                max_consecutive = max(max_consecutive, consecutive_losses)
            else:
                consecutive_losses = 0

        # Risk classification
        if actual_risk <= 1.0 and rr_ratio >= 2.0 and volatility < 30:
            risk_class = "منخفض"
            risk_color = "#10b981"
        elif actual_risk <= 2.5 and rr_ratio >= 1.5 and volatility < 50:
            risk_class = "متوسط"
            risk_color = "#f59e0b"
        else:
            risk_class = "عالي"
            risk_color = "#ef4444"

        return {
            "volatility_annual": round(volatility, 2),
            "var_95": round(var_95, 2),
            "var_99": round(var_99, 2),
            "cvar_95": round(cvar_95, 2),
            "rr_ratio": round(rr_ratio, 2),
            "risk_pct": round((risk / entry_price) * 100, 2),
            "reward_pct": round((reward / entry_price) * 100, 2),
            "shares": shares,
            "position_value": round(position_value, 2),
            "actual_risk_pct": round(actual_risk, 2),
            "win_rate": round(win_rate * 100, 1),
            "kelly_pct": round(kelly * 100, 2),
            "max_consecutive_losses": max_consecutive,
            "risk_class": risk_class,
            "risk_color": risk_color,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "recommendation": "مناسب" if risk_class in ["منخفض", "متوسط"] and rr_ratio >= 1.5 else "غير مناسب"
        }

    @staticmethod
    def generate_risk_report(alerts: List[dict]) -> dict:
        """Generate portfolio-level risk report"""
        if not alerts:
            return {}

        total_score = sum(a.get('score', 0) for a in alerts)
        avg_score = total_score / len(alerts)
        buy_signals = len([a for a in alerts if a.get('signal') in ['BUY', 'STRONG_BUY']])
        sell_signals = len([a for a in alerts if a.get('signal') in ['SELL', 'STRONG_SELL']])

        # Portfolio heat (concentration risk)
        if buy_signals > 0:
            avg_risk = sum(a.get('risk_pct', 0) for a in alerts if a.get('signal') in ['BUY', 'STRONG_BUY']) / buy_signals
        else:
            avg_risk = 0

        portfolio_heat = avg_risk * buy_signals

        return {
            "total_stocks": len(alerts),
            "buy_opportunities": buy_signals,
            "sell_alerts": sell_signals,
            "avg_score": round(avg_score, 2),
            "portfolio_heat": round(portfolio_heat, 2),
            "heat_status": "آمن" if portfolio_heat < 15 else "تحذير" if portfolio_heat < 25 else "خطير",
            "heat_color": "#10b981" if portfolio_heat < 15 else "#f59e0b" if portfolio_heat < 25 else "#ef4444",
            "diversification_score": round(100 - (buy_signals / len(alerts) * 50), 2) if alerts else 0
        }

ta_engine = TechnicalAnalyzer()
risk_engine = RiskEngine()

# ==================== AUTOMATED ANALYSIS ENGINE ====================
class AutomatedAnalyzer:
    """AI-powered market scanning"""

    @staticmethod
    def analyze_all(stocks_data: List[dict], market_type: str = "EGX") -> List[dict]:
        """Analyze all stocks with comprehensive scoring"""
        alerts = []
        progress = st.empty()

        for i, stock in enumerate(stocks_data):
            try:
                progress.text(f"تحليل {i+1}/{len(stocks_data)}: {stock['symbol']}...")

                df = data_engine.get_stock_history(stock['symbol'], "3mo")
                if df is None or len(df) < 30:
                    continue

                df = ta_engine.calculate_all(df)
                if df is None:
                    continue

                latest = df.iloc[-1]
                if pd.isna(latest.get('RSI')) or pd.isna(latest.get('MACD')):
                    continue

                signals = ta_engine.generate_signals(df)
                overall_signal, score, signal_text, trend = ta_engine.calculate_overall(signals)

                # Risk calculations
                atr = latest['ATR'] if pd.notna(latest.get('ATR')) else 0
                current_price = latest['Close']

                stop_loss = current_price - (atr * 2) if atr > 0 else current_price * 0.95
                take_profit_1 = current_price + (atr * 2) if atr > 0 else current_price * 1.05
                take_profit_2 = current_price + (atr * 3.5) if atr > 0 else current_price * 1.10

                # Advanced risk analysis
                risk_profile = risk_engine.analyze_risk_profile(
                    df, current_price, stop_loss, take_profit_1
                )

                # Trend strength
                trend_strength = 0
                if pd.notna(latest.get('Close')) and pd.notna(latest.get('SMA_20')):
                    trend_strength += 1 if latest['Close'] > latest['SMA_20'] else -1
                if pd.notna(latest.get('Close')) and pd.notna(latest.get('SMA_50')):
                    trend_strength += 1 if latest['Close'] > latest['SMA_50'] else -1
                if pd.notna(latest.get('ADX')) and latest['ADX'] > 25:
                    trend_strength += 1

                # Volume confirmation
                volume_confirm = latest.get('Volume_Ratio', 0) > 1.5 if pd.notna(latest.get('Volume_Ratio')) else False

                # Opportunity scoring (0-100)
                opportunity_score = 50  # Base score

                if pd.notna(latest.get('RSI')):
                    if latest['RSI'] < 30: opportunity_score += 20
                    elif latest['RSI'] < 40: opportunity_score += 10
                    elif latest['RSI'] > 70: opportunity_score -= 20

                if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
                    if latest['MACD'] > latest['MACD_Signal']:
                        opportunity_score += 15
                        if pd.notna(latest.get('MACD_Histogram')) and latest['MACD_Histogram'] > 0:
                            opportunity_score += 5

                if pd.notna(latest.get('BB_Position')):
                    if latest['BB_Position'] < 0.2: opportunity_score += 10
                    elif latest['BB_Position'] > 0.8: opportunity_score -= 10

                opportunity_score += trend_strength * 5
                if volume_confirm: opportunity_score += 10
                if risk_profile.get('rr_ratio', 0) > 2: opportunity_score += 10
                elif risk_profile.get('rr_ratio', 0) > 1.5: opportunity_score += 5
                if pd.notna(latest.get('Stoch_K')) and latest['Stoch_K'] < 20: opportunity_score += 5

                opportunity_score = max(0, min(100, opportunity_score))

                # Alert classification
                if opportunity_score >= 80 and overall_signal in ["STRONG_BUY", "BUY"]:
                    alert_level = "🔥 فرصة استثنائية"
                    alert_color = "#10b981"
                    priority = 1
                elif opportunity_score >= 65 and overall_signal in ["STRONG_BUY", "BUY"]:
                    alert_level = "🟢 فرصة شراء ممتازة"
                    alert_color = "#34d399"
                    priority = 2
                elif opportunity_score >= 50 and overall_signal in ["BUY", "HOLD"]:
                    alert_level = "🟡 مراقبة إيجابية"
                    alert_color = "#fbbf24"
                    priority = 3
                elif opportunity_score < 30 and overall_signal in ["SELL", "STRONG_SELL"]:
                    alert_level = "🔴 إشارة بيع"
                    alert_color = "#ef4444"
                    priority = 4
                else:
                    alert_level = "⚪ محايد"
                    alert_color = "#94a3b8"
                    priority = 5

                alerts.append({
                    "symbol": stock['symbol'],
                    "name": stock['name'],
                    "sector": stock['sector'],
                    "price": round(current_price, 2),
                    "change_pct": stock.get('change_pct', 0),
                    "signal": overall_signal,
                    "signal_text": signal_text,
                    "trend": trend,
                    "score": round(opportunity_score, 1),
                    "alert_level": alert_level,
                    "alert_color": alert_color,
                    "priority": priority,
                    "rsi": round(latest['RSI'], 1) if pd.notna(latest.get('RSI')) else 50,
                    "macd": round(latest['MACD'], 2) if pd.notna(latest.get('MACD')) else 0,
                    "bb_position": round(latest['BB_Position'], 2) if pd.notna(latest.get('BB_Position')) else 0.5,
                    "volume_ratio": round(latest['Volume_Ratio'], 1) if pd.notna(latest.get('Volume_Ratio')) else 1.0,
                    "adx": round(latest['ADX'], 1) if pd.notna(latest.get('ADX')) else 0,
                    "trend_strength": trend_strength,
                    "rr_ratio": risk_profile.get('rr_ratio', 0),
                    "stop_loss": round(stop_loss, 2),
                    "take_profit_1": round(take_profit_1, 2),
                    "take_profit_2": round(take_profit_2, 2),
                    "risk_pct": risk_profile.get('risk_pct', 0),
                    "reward_pct": risk_profile.get('reward_pct', 0),
                    "volatility": risk_profile.get('volatility_annual', 0),
                    "var_95": risk_profile.get('var_95', 0),
                    "risk_class": risk_profile.get('risk_class', 'غير معروف'),
                    "risk_color": risk_profile.get('risk_color', '#94a3b8'),
                    "recommendation": risk_profile.get('recommendation', 'غير معروف'),
                    "kelly": risk_profile.get('kelly_pct', 0),
                    "position_shares": risk_profile.get('shares', 0),
                    "position_value": risk_profile.get('position_value', 0),
                })
            except Exception as e:
                continue

        progress.empty()
        alerts.sort(key=lambda x: (x['priority'], -x['score']))
        return alerts

    @staticmethod
    def predict_prices(df: pd.DataFrame, days: int = 5) -> dict:
        """Advanced price prediction with confidence intervals"""
        try:
            prices = df['Close'].dropna().values
            if len(prices) < 30:
                return {'error': 'Insufficient data'}

            # Polynomial regression
            X = np.arange(len(prices)).reshape(-1, 1)
            y = prices
            poly = PolynomialFeatures(degree=3)
            X_poly = poly.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)

            # Future predictions
            future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
            future_X_poly = poly.transform(future_X)
            predictions = model.predict(future_X_poly)

            # Volatility-based confidence intervals
            volatility = df['Close'].pct_change().std() * prices[-1]

            combined = []
            for i in range(days):
                conf = max(0, min(100, 100 - (i * 12)))
                margin = volatility * (1 + i * 0.2)
                combined.append({
                    'day': i + 1,
                    'predicted': round(predictions[i], 2),
                    'lower_bound': round(predictions[i] - margin * 1.5, 2),
                    'upper_bound': round(predictions[i] + margin * 1.5, 2),
                    'confidence': conf
                })

            return {'combined': combined}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
        """Calculate support/resistance with Fibonacci"""
        try:
            recent = df.tail(window)
            lows = recent['Low'].nsmallest(3).values
            highs = recent['High'].nlargest(3).values

            swing_high = recent['High'].max()
            swing_low = recent['Low'].min()
            diff = swing_high - swing_low

            return {
                'supports': [round(l, 2) for l in lows],
                'resistances': [round(h, 2) for h in highs],
                'fibonacci': {
                    '0%': round(swing_high, 2),
                    '23.6%': round(swing_high - 0.236 * diff, 2),
                    '38.2%': round(swing_high - 0.382 * diff, 2),
                    '50%': round(swing_high - 0.5 * diff, 2),
                    '61.8%': round(swing_high - 0.618 * diff, 2),
                    '78.6%': round(swing_high - 0.786 * diff, 2),
                    '100%': round(swing_low, 2)
                },
                'current': round(df['Close'].iloc[-1], 2)
            }
        except Exception:
            return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0}

ai_engine = AutomatedAnalyzer()

# ==================== CORPORATE ACTIONS & DIVIDENDS ENGINE ====================
class CorporateEngine:
    """Corporate actions, dividends, and company announcements"""

    CORPORATE_DATA = {
        "COMI": {
            "company": "Commercial International Bank",
            "arabic_name": "البنك التجاري الدولي",
            "dividends": [
                {"date": "2026-04-15", "type": "نقدي", "amount": 2.50, "status": "تم التوزيع", "yield": 1.79},
                {"date": "2025-10-15", "type": "نقدي", "amount": 2.30, "status": "تم التوزيع", "yield": 1.64},
            ],
            "upcoming": {"date": "2026-10-15", "expected": 2.60, "type": "نقدي"},
            "meetings": [
                {"date": "2026-06-20", "type": "عمومية", "subject": "الموافقة على توزيعات الأرباح", "status": "معلن"},
            ],
            "news": [
                {"date": "2026-05-12", "title": "CIB يعلن عن نمو أرباح الربع الأول بنسبة 18%", "impact": "positive"},
                {"date": "2026-05-08", "title": "توقيع اتفاقية مع شركة تقنية مالية جديدة", "impact": "positive"},
            ]
        },
        "QNBE": {
            "company": "QNB Egypt",
            "arabic_name": "QNB مصر",
            "dividends": [
                {"date": "2026-03-25", "type": "نقدي", "amount": 3.20, "status": "تم التوزيع", "yield": 5.50},
            ],
            "upcoming": {"date": "2026-09-25", "expected": 3.30, "type": "نقدي"},
            "meetings": [],
            "news": [
                {"date": "2026-05-10", "title": "QNB مصر يفتفر فرعاً رقمياً جديداً في العاصمة الإدارية", "impact": "positive"},
            ]
        },
        "HDBK": {
            "company": "Housing & Development Bank",
            "arabic_name": "بنك الإسكان والتعمير",
            "dividends": [
                {"date": "2026-04-05", "type": "نقدي", "amount": 5.50, "status": "تم التوزيع", "yield": 3.73},
            ],
            "upcoming": {"date": "2026-10-05", "expected": 5.80, "type": "نقدي"},
            "meetings": [
                {"date": "2026-06-15", "type": "عمومية", "subject": "زيادة رأس المال", "status": "معلن"},
            ],
            "news": []
        },
        "TMGH": {
            "company": "Talaat Moustafa Group",
            "arabic_name": "طلعت مصطفى",
            "dividends": [
                {"date": "2026-04-08", "type": "نقدي", "amount": 2.80, "status": "تم التوزيع", "yield": 2.85},
            ],
            "upcoming": {"date": "2026-10-08", "expected": 3.00, "type": "نقدي"},
            "meetings": [],
            "news": [
                {"date": "2026-05-11", "title": "إطلاق مشروع مدينتي الجديدة - المرحلة الثالثة", "impact": "positive"},
            ]
        },
        "ETEL": {
            "company": "Telecom Egypt",
            "arabic_name": "المصرية للاتصالات",
            "dividends": [
                {"date": "2026-04-30", "type": "نقدي", "amount": 3.00, "status": "تم التوزيع", "yield": 3.05},
            ],
            "upcoming": {"date": "2026-10-30", "expected": 3.20, "type": "نقدي"},
            "meetings": [],
            "news": []
        },
        "EAST": {
            "company": "Eastern Tobacco",
            "arabic_name": "الشرقية للدخان",
            "dividends": [
                {"date": "2026-05-20", "type": "نقدي", "amount": 3.20, "status": "معلن", "yield": 7.94},
            ],
            "upcoming": None,
            "meetings": [
                {"date": "2026-05-25", "type": "عمومية", "subject": "الموافقة على التوزيعات", "status": "قريب"},
            ],
            "news": [
                {"date": "2026-05-13", "title": "الشرقية للدخان تعلن عن توزيعات نقدية 3.20 جنيه", "impact": "positive"},
            ]
        },
        "ABUK": {
            "company": "Abu Qir Fertilizers",
            "arabic_name": "أبو قير للأسمدة",
            "dividends": [
                {"date": "2026-05-12", "type": "نقدي", "amount": 4.50, "status": "معلن", "yield": 5.16},
            ],
            "upcoming": None,
            "meetings": [],
            "news": []
        },
        "SWDY": {
            "company": "El Sewedy Electric",
            "arabic_name": "السويدي إلكتريك",
            "dividends": [
                {"date": "2025-11-15", "type": "نقدي", "amount": 3.50, "status": "تم التوزيع", "yield": 3.91},
            ],
            "upcoming": {"date": "2026-11-15", "expected": 3.80, "type": "نقدي"},
            "meetings": [],
            "news": [
                {"date": "2026-05-09", "title": "السويدي تفوز بعقد كهرباء بقيمة 2.5 مليار جنيه", "impact": "positive"},
            ]
        },
    }

    @classmethod
    def get_company_data(cls, symbol: str) -> dict:
        return cls.CORPORATE_DATA.get(symbol, {
            "company": symbol,
            "arabic_name": symbol,
            "dividends": [],
            "upcoming": None,
            "meetings": [],
            "news": []
        })

    @classmethod
    def get_upcoming_dividends_all(cls) -> List[dict]:
        """Get all upcoming dividends across market"""
        upcoming = []
        for symbol, data in cls.CORPORATE_DATA.items():
            if data.get('upcoming'):
                upcoming.append({
                    'symbol': symbol,
                    'company': data['arabic_name'],
                    'date': data['upcoming']['date'],
                    'amount': data['upcoming']['expected'],
                    'type': data['upcoming']['type']
                })
            for div in data.get('dividends', []):
                if div['status'] in ['معلن', 'قريب']:
                    upcoming.append({
                        'symbol': symbol,
                        'company': data['arabic_name'],
                        'date': div['date'],
                        'amount': div['amount'],
                        'type': div['type']
                    })
        return sorted(upcoming, key=lambda x: x['date'])

    @classmethod
    def get_meetings(cls) -> List[dict]:
        meetings = []
        for symbol, data in cls.CORPORATE_DATA.items():
            for meeting in data.get('meetings', []):
                meetings.append({**meeting, 'symbol': symbol, 'company': data['arabic_name']})
        return sorted(meetings, key=lambda x: x['date'])

corp_engine = CorporateEngine()

# ==================== NEWS ENGINE ====================
class NewsEngine:
    """Real-time market news and sentiment"""

    NEWS_FEED = [
        {"time": "14:30", "title": "EGX30 يتجاوز 24800 نقطة للمرة الأولى منذ 2022", "type": "positive", "source": "البورصة المصرية", "impact_score": 8},
        {"time": "14:15", "title": "CIB يعلن عن توزيع أرباح نقدية 2.5 جنيه للسهم", "type": "positive", "source": "CIB", "impact_score": 9},
        {"time": "13:45", "title": "تراجع طفيف في مؤشر EGX100 مع جني الأرباح", "type": "negative", "source": "إيكونومي", "impact_score": 4},
        {"time": "13:20", "title": "المركزي: استقرار سعر الصرف عند 30.85 للدولار", "type": "neutral", "source": "البنك المركزي", "impact_score": 5},
        {"time": "12:50", "title": "e-Finance توقع اتفاقية رقمية مع الحكومة بقيمة 500 مليون", "type": "positive", "source": "e-Finance", "impact_score": 7},
        {"time": "12:15", "title": "ارتفاع حجم التداولات إلى 1.8 مليار جنيه", "type": "positive", "source": "البورصة", "impact_score": 6},
        {"time": "11:30", "title": "فوري تعلن عن نمو أرباح الربع الأول بنسبة 25%", "type": "positive", "source": "فوري", "impact_score": 8},
        {"time": "10:45", "title": "ضغوط بيعية على قطاع الأسمدة مع ارتفاع أسعار الغاز", "type": "negative", "source": "تحليلي", "impact_score": 5},
        {"time": "10:00", "title": "السويدي تفوز بعقد كهرباء جديد في السعودية", "type": "positive", "source": "السويدي", "impact_score": 7},
        {"time": "09:30", "title": "إيديتا تعلن عن زيادة أسعار المنتجات بنسبة 8%", "type": "neutral", "source": "إيديتا", "impact_score": 5},
    ]

    @classmethod
    def get_news(cls, sector: str = None) -> List[dict]:
        return cls.NEWS_FEED

    @classmethod
    def get_sentiment_score(cls) -> dict:
        """Calculate market sentiment from news"""
        positive = sum(n['impact_score'] for n in cls.NEWS_FEED if n['type'] == 'positive')
        negative = sum(n['impact_score'] for n in cls.NEWS_FEED if n['type'] == 'negative')
        neutral = sum(n['impact_score'] for n in cls.NEWS_FEED if n['type'] == 'neutral')
        total = positive + negative + neutral

        if total == 0:
            return {"score": 50, "mood": "محايد", "color": "#94a3b8"}

        score = (positive / total) * 100
        if score >= 60:
            return {"score": round(score, 1), "mood": "إيجابي", "color": "#10b981"}
        elif score <= 40:
            return {"score": round(score, 1), "mood": "سلبي", "color": "#ef4444"}
        return {"score": round(score, 1), "mood": "محايد", "color": "#f59e0b"}

news_engine = NewsEngine()

# ==================== CALLBACK FUNCTIONS (BUTTON FIX) ====================
def select_stock_callback(symbol):
    """Safe callback for stock selection"""
    st.session_state.selected_stock = symbol
    st.session_state.show_analysis = True
    st.session_state.analysis_symbol = symbol

def clear_analysis():
    """Clear analysis view"""
    st.session_state.show_analysis = False
    st.session_state.selected_stock = None
    st.session_state.analysis_symbol = None

def add_task_callback():
    """Add task from form"""
    if st.session_state.get('new_task_title'):
        st.session_state.tasks.append({
            "id": len(st.session_state.tasks) + 1,
            "title": st.session_state.new_task_title,
            "priority": st.session_state.new_task_priority,
            "category": st.session_state.new_task_category,
            "due": st.session_state.new_task_due.strftime("%Y-%m-%d"),
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d")
        })
        st.session_state.new_task_title = ""

def toggle_task(task_id):
    """Toggle task completion"""
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

def delete_task(task_id):
    """Delete task"""
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

def run_analysis_callback():
    """Run automated analysis and cache results"""
    with st.spinner("جاري تحليل السوق..."):
        prices = data_engine.get_live_prices()
        alerts = ai_engine.analyze_all(prices)
        st.session_state.alerts_cache = alerts
        st.session_state.alerts_timestamp = datetime.now()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px; padding: 16px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border-radius: 12px; border: 1px solid rgba(99,102,241,0.2);">
        <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 12px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 24px;">⚡</div>
        <h2 style="margin-top: 12px; font-size: 18px; font-weight: 700;">EGX Pro Terminal</h2>
        <p style="color: #64748b; font-size: 11px; margin-top: 4px;">v21.0 | AI-Powered Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Selection
    st.header("🌍 اختيار السوق")
    market = st.radio("", ["🇪🇬 السوق المصري", "🌍 الأسواق العالمية"], label_visibility="collapsed")
    is_egypt = "مصري" in market

    st.divider()

    # Risk Settings
    st.header("🛡️ إعدادات المخاطرة")
    st.session_state.risk_settings['max_risk_pct'] = st.slider("المخاطرة/صفقة %", 0.5, 5.0, 2.0, 0.5)
    st.session_state.risk_settings['max_portfolio_heat'] = st.slider("سخونة المحفظة %", 10.0, 50.0, 25.0, 5.0)
    st.session_state.risk_settings['min_rr'] = st.slider("الحد الأدنى R/R", 1.0, 3.0, 1.5, 0.5)

    st.divider()

    # Debug Mode
    st.header("🔧 أدوات النظام")
    st.session_state.debug_mode = st.toggle("وضع التصحيح", value=st.session_state.debug_mode)

    if st.session_state.debug_mode:
        st.info(f"الأخطاء: 0 | البيانات: {len(st.session_state.market_data_cache)} مخزنة")

    st.divider()

    # Task Summary
    st.header("📊 إحصائيات المهام")
    total_tasks = len(st.session_state.tasks)
    completed = sum(1 for t in st.session_state.tasks if t["completed"])
    pending = total_tasks - completed
    high_priority = sum(1 for t in st.session_state.tasks if t["priority"] == "high" and not t["completed"])

    c1, c2 = st.columns(2)
    c1.metric("الكل", total_tasks)
    c2.metric("مكتمل", completed)
    c1.metric("قيد التنفيذ", pending)
    c2.metric("عالية الأولوية", high_priority, delta_color="inverse")

    # Quick Actions
    st.divider()
    st.header("⚡ إجراءات سريعة")
    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.session_state.market_data_cache = {}
        st.session_state.alerts_cache = None
        st.toast("✅ تم تحديث البيانات")
    if st.button("📊 تحليل فوري", use_container_width=True, type="primary"):
        run_analysis_callback()
        st.toast("✅ تم إكمال التحليل")

# ==================== HEADER ====================
stocks_live = data_engine.get_live_prices()
df_live = pd.DataFrame(stocks_live)

best_stock = max(stocks_live, key=lambda x: x["change_pct"])
worst_stock = min(stocks_live, key=lambda x: x["change_pct"])

# Market indices (simulated based on real market data)
market_indices = {
    "EGX30": {"value": 24850.32, "change": 1.24, "vol": "1.2B"},
    "EGX70": {"value": 3245.18, "change": 0.89, "vol": "850M"},
    "EGX100": {"value": 8932.45, "change": -0.34, "vol": "2.1B"},
}

sentiment = news_engine.get_sentiment_score()

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 16px; background: linear-gradient(90deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05)); border-radius: 12px; border: 1px solid rgba(99,102,241,0.1);">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ EGX Pro Terminal v21
        </h1>
        <p style="color: #64748b; margin-top: 4px; font-size: 13px;">
            <span class="live-pulse"></span> السوق مفتوح | تحديث لحظي | {datetime.now().strftime("%H:%M:%S")}
        </p>
    </div>
    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <div style="padding: 10px 16px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px;">
            <span style="color: #64748b; font-size: 11px;">EGX30</span>
            <span style="color: #10b981; margin-right: 8px; font-size: 18px; font-weight: 700;">24,850</span>
            <span class="badge badge-green">+1.24%</span>
        </div>
        <div style="padding: 10px 16px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px;">
            <span style="color: #64748b; font-size: 11px;">مؤشر المزاج</span>
            <span style="color: {sentiment['color']}; margin-right: 8px; font-size: 16px; font-weight: 700;">{sentiment['mood']}</span>
        </div>
        <div style="padding: 10px 16px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 8px;">
            <span style="color: #64748b; font-size: 11px;">الأقوى</span>
            <span style="color: #fbbf24; margin-right: 8px; font-size: 16px; font-weight: 700;">{best_stock['symbol']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 رادار السوق", 
    "🤖 التحليل الآلي", 
    "📊 Backtesting", 
    "✅ المهام الذكية",
    "🏢 واجهة الشركات",
    "📰 الأخبار والمزاج",
    "🔮 التحليل المفصل"
])

# ==================== TAB 1: MARKET RADAR ====================
with tab1:
    # Market Indices Row
    idx_cols = st.columns(5)
    indices = [
        {"name": "EGX30", "value": 24850.32, "change": 1.24, "vol": "1.2B"},
        {"name": "EGX70", "value": 3245.18, "change": 0.89, "vol": "850M"},
        {"name": "EGX100", "value": 8932.45, "change": -0.34, "vol": "2.1B"},
        {"name": "EGX20", "value": 15680.12, "change": 1.05, "vol": "950M"},
        {"name": "الدولار", "value": 30.85, "change": 0.02, "vol": "CBE"},
    ]

    for i, idx in enumerate(indices):
        with idx_cols[i]:
            change_color = "#10b981" if idx['change'] >= 0 else "#ef4444"
            arrow = "▲" if idx['change'] >= 0 else "▼"
            st.markdown(f"""
            <div class="pro-panel" style="text-align: center;">
                <p style="color: #64748b; font-size: 11px; margin: 0; text-transform: uppercase;">{idx['name']}</p>
                <p style="font-size: 22px; font-weight: 700; margin: 4px 0; color: {change_color};">{idx['value']:,.2f}</p>
                <div style="display: flex; justify-content: center; gap: 8px;">
                    <span style="color: {change_color}; font-size: 12px; font-weight: 600;">{arrow} {abs(idx['change']):.2f}%</span>
                    <span style="color: #64748b; font-size: 11px;">{idx['vol']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Treemap + Top Movers
    row2_col1, row2_col2 = st.columns([2, 1])

    with row2_col1:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🗺️ خريطة السوق التفاعلية</span></div>', unsafe_allow_html=True)

        fig_treemap = px.treemap(
            df_live,
            path=[px.Constant("EGX"), 'sector', 'symbol'],
            values='volume',
            color='change_pct',
            color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
            color_continuous_midpoint=0,
        )
        fig_treemap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#94a3b8", size=11),
            height=380, margin=dict(t=0, b=0, l=0, r=0),
            coloraxis_colorbar=dict(tickfont=dict(color="#94a3b8", size=10), title=dict(text="%", font=dict(color="#94a3b8", size=10)))
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with row2_col2:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🚀 الأكثر نشاطاً</span></div>', unsafe_allow_html=True)

        top_movers = df_live.nlargest(8, 'change_pct')
        for _, stock in top_movers.iterrows():
            change_class = "status-up" if stock['change_pct'] >= 0 else "status-down"
            change_sign = "+" if stock['change_pct'] >= 0 else ""
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
                <div>
                    <span style="color: #fbbf24; font-weight: 600; font-size: 13px;">{stock['symbol']}</span>
                    <span style="color: #64748b; font-size: 11px; margin-right: 6px;">{stock['name'][:12]}</span>
                </div>
                <div style="text-align: left;">
                    <span style="font-size: 13px; font-weight: 600;">{stock['price']:.2f}</span>
                    <span class="{change_class}" style="font-size: 11px; margin-right: 4px;">{change_sign}{stock['change_pct']:.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Stock Grid with Working Buttons
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🎯 الأسهم المتاحة - اضغط للتحليل المفصل</span></div>', unsafe_allow_html=True)

    # Filters
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        search_term = st.text_input("🔍 البحث", placeholder="ابحث بالرمز أو اسم الشركة...", key="market_search", label_visibility="collapsed")
    with f_col2:
        sector_filter = st.selectbox("القطاع", ["الكل"] + sorted(df_live['sector'].unique().tolist()), key="market_sector", label_visibility="collapsed")

    display_stocks = df_live.copy()
    if search_term:
        mask = display_stocks['symbol'].str.contains(search_term, case=False) | display_stocks['name'].str.contains(search_term, case=False)
        display_stocks = display_stocks[mask]
    if sector_filter != "الكل":
        display_stocks = display_stocks[display_stocks['sector'] == sector_filter]

    # Stock cards grid
    stocks_per_row = 6
    stock_list = display_stocks.to_dict('records')

    for row_idx in range(0, len(stock_list), stocks_per_row):
        row_stocks = stock_list[row_idx:row_idx + stocks_per_row]
        btn_cols = st.columns(stocks_per_row)

        for i, stock in enumerate(row_stocks):
            with btn_cols[i]:
                change_class = "up" if stock['change_pct'] >= 0 else "down"
                change_sign = "+" if stock['change_pct'] >= 0 else ""
                source_badge = "🟢" if stock.get('source') == 'yfinance' else "🔵"

                st.markdown(f"""
                <div class="stock-card">
                    <div style="position: absolute; top: 4px; left: 4px; font-size: 8px;">{source_badge}</div>
                    <div class="stock-card-symbol">{stock['symbol']}</div>
                    <div class="stock-card-price">{stock['price']:.2f}</div>
                    <div class="stock-card-change {change_class}">{change_sign}{stock['change_pct']:.2f}%</div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 4px;">{stock['sector']}</div>
                </div>
                """, unsafe_allow_html=True)

                # WORKING BUTTON with on_click callback
                st.button(
                    f"تحليل {stock['symbol']}", 
                    key=f"analyze_{stock['symbol']}_{row_idx}",
                    on_click=select_stock_callback,
                    args=(stock['symbol'],),
                    use_container_width=True,
                    type="secondary"
                )

    st.markdown('</div>', unsafe_allow_html=True)

    # Sector Performance
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 أداء القطاعات</span></div>', unsafe_allow_html=True)

    sector_perf = df_live.groupby('sector').agg({
        'change_pct': 'mean',
        'volume': 'sum',
        'market_cap': 'sum'
    }).reset_index()
    sector_perf.columns = ['القطاع', 'التغيير %', 'الحجم', 'القيمة السوقية']

    fig_sector = px.bar(
        sector_perf,
        x='القطاع',
        y='التغيير %',
        color='التغيير %',
        color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
        text='التغيير %'
    )
    fig_sector.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_sector.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#94a3b8"),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        height=300, margin=dict(t=20, b=40)
    )
    st.plotly_chart(fig_sector, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: AUTOMATED ANALYSIS (AI) ====================
with tab2:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🤖 التحليل الآلي الذكي والتنبيهات اللحظية</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 16px;">
        <p style="color: #f87171; font-weight: 600; margin: 0; font-size: 13px;">⚠️ تحذير المخاطر</p>
        <p style="color: #fca5a5; font-size: 12px; margin-top: 4px;">التحليل الآلي يعتمد على البيانات التاريخية فقط. استخدم Stop Loss لحماية رأس مالك. التوقعات ليست توصيات استثمارية.</p>
    </div>
    """, unsafe_allow_html=True)

    # Analysis Controls
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])
    with ctrl_col1:
        min_score = st.slider("الحد الأدنى للدرجة", 0, 100, 55, key="ai_min_score")
    with ctrl_col2:
        max_risk = st.slider("الحد الأقصى للمخاطرة %", 0.5, 10.0, 5.0, 0.5, key="ai_max_risk")
    with ctrl_col3:
        min_rr = st.slider("الحد الأدنى R/R", 1.0, 5.0, 1.5, 0.5, key="ai_min_rr")

    # Run Analysis Button
    if st.button("🚀 تشغيل التحليل الآلي الشامل", type="primary", use_container_width=True, on_click=run_analysis_callback):
        pass  # Callback handles the work

    # Display cached results
    if st.session_state.alerts_cache is not None:
        alerts = st.session_state.alerts_cache

        # Portfolio Risk Report
        risk_report = risk_engine.generate_risk_report(alerts)

        st.subheader("📊 ملخص المخاطر والفرص")
        sum_cols = st.columns(5)
        metrics = [
            ("المحللة", len(alerts), "#818cf8"),
            ("فرص شراء", risk_report.get('buy_opportunities', 0), "#10b981"),
            ("إشارات بيع", risk_report.get('sell_alerts', 0), "#ef4444"),
            ("متوسط الدرجة", f"{risk_report.get('avg_score', 0):.1f}", "#fbbf24"),
            ("سخونة المحفظة", risk_report.get('heat_status', 'غير معروف'), risk_report.get('heat_color', '#94a3b8')),
        ]

        for i, (label, value, color) in enumerate(metrics):
            with sum_cols[i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid {color}30;">
                    <p style="color: #64748b; font-size: 11px; margin: 0;">{label}</p>
                    <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 4px 0;">{value}</p>
                </div>
                """, unsafe_allow_html=True)

        # Buy Opportunities
        buy_ops = [a for a in alerts if a['score'] >= min_score and a['signal'] in ['BUY', 'STRONG_BUY'] and a['risk_pct'] <= max_risk and a['rr_ratio'] >= min_rr]

        if buy_ops:
            st.subheader("🔥 أفضل فرص الشراء المؤكدة")
            for i, alert in enumerate(buy_ops[:8]):
                with st.expander(f"{i+1}. {alert['name']} ({alert['symbol']}) - درجة: {alert['score']} | R/R: {alert['rr_ratio']}", expanded=i < 2):

                    # Signal & Score
                    sig_cols = st.columns([1, 3, 1])
                    with sig_cols[0]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 12px; background: {alert['alert_color']}15; border: 1px solid {alert['alert_color']}40; border-radius: 8px;">
                            <p style="margin: 0; color: {alert['alert_color']}; font-size: 28px; font-weight: 700;">{alert['score']}</p>
                            <p style="margin: 4px 0 0 0; color: {alert['alert_color']}; font-size: 11px;">درجة الفرصة</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with sig_cols[1]:
                        st.markdown(f"""
                        <div>
                            <p style="margin: 0; font-weight: 600; font-size: 16px;">{alert['name']} | {alert['sector']}</p>
                            <p style="color: #64748b; font-size: 13px; margin: 4px 0;">
                                السعر: <b>{alert['price']}</b> | RSI: <b>{alert['rsi']}</b> | MACD: <b>{alert['macd']}</b> | ADX: <b>{alert['adx']}</b>
                            </p>
                            <p style="color: #64748b; font-size: 12px; margin: 4px 0;">
                                التقلب: {alert['volatility']}% | VaR(95%): {alert['var_95']}% | كيلي: {alert['kelly']}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    with sig_cols[2]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 8px; background: {alert['risk_color']}15; border: 1px solid {alert['risk_color']}40; border-radius: 8px;">
                            <p style="margin: 0; color: {alert['risk_color']}; font-size: 11px; font-weight: 600;">{alert['risk_class']}</p>
                            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 10px;">{alert['recommendation']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Risk Levels
                    risk_cols = st.columns(4)
                    risk_data = [
                        ("🛑 Stop Loss", alert['stop_loss'], alert['risk_pct'], "#ef4444"),
                        ("📍 السعر", alert['price'], 0, "#6366f1"),
                        ("🎯 الهدف 1", alert['take_profit_1'], alert['reward_pct'], "#10b981"),
                        ("🎯🎯 الهدف 2", alert['take_profit_2'], 0, "#fbbf24")
                    ]
                    for j, (label, value, pct, color) in enumerate(risk_data):
                        with risk_cols[j]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid {color}30;">
                                <p style="color: #64748b; font-size: 11px; margin: 0;">{label}</p>
                                <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 4px 0;">{value:.2f}</p>
                                {f'<p style="font-size: 10px; color: {color}; margin: 0;">{pct:.1f}%</p>' if pct else ''}
                            </div>
                            """, unsafe_allow_html=True)

                    # Position Sizing
                    pos_cols = st.columns(3)
                    with pos_cols[0]:
                        st.metric("الأسهم المقترحة", f"{alert['position_shares']}")
                    with pos_cols[1]:
                        st.metric("قيمة المركز", f"{alert['position_value']:,.0f} ج.م")
                    with pos_cols[2]:
                        st.metric("نسبة كيلي", f"{alert['kelly']}%")

                    # Action Button
                    st.button(
                        f"🔮 تحليل مفصل لـ {alert['symbol']}",
                        key=f"detail_{alert['symbol']}_tab2",
                        on_click=select_stock_callback,
                        args=(alert['symbol'],),
                        use_container_width=True,
                        type="primary"
                    )

        # Risk Alerts (Sell signals)
        risk_alerts = [a for a in alerts if a['signal'] in ['SELL', 'STRONG_SELL'] or (a['score'] < 30 and a['signal'] == 'HOLD')]
        if risk_alerts:
            st.subheader("🔴 إشارات الخطر والبيع")
            for alert in risk_alerts[:5]:
                st.markdown(f"""
                <div style="padding: 12px; background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.2); border-radius: 8px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #ef4444; font-weight: 600;">{alert['symbol']}</span>
                            <span style="color: #64748b; margin-right: 8px;">{alert['name']}</span>
                            <span style="color: #f59e0b; margin-right: 8px;">درجة: {alert['score']}</span>
                        </div>
                        <span style="color: #ef4444; font-size: 13px; font-weight: 600;">{alert['signal_text']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Full Table
        st.subheader("📋 الجدول التحليلي الكامل")
        table_data = []
        for alert in alerts:
            table_data.append({
                "الرمز": alert['symbol'],
                "الشركة": alert['name'],
                "القطاع": alert['sector'],
                "السعر": alert['price'],
                "الإشارة": alert['signal_text'],
                "الدرجة": alert['score'],
                "RSI": alert['rsi'],
                "MACD": alert['macd'],
                "R/R": alert['rr_ratio'],
                "المخاطرة%": alert['risk_pct'],
                "التقلب%": alert['volatility'],
                "Stop Loss": alert['stop_loss'],
                "الهدف": alert['take_profit_1']
            })

        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        # Export
        st.download_button(
            label="📥 تصدير التحليل CSV",
            data=df_table.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"egx_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("👈 اضغط 'تشغيل التحليل الآلي' لبدء المسح الشامل")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: BACKTESTING ====================
with tab3:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 محرك Backtesting متقدم</span></div>', unsafe_allow_html=True)

    bt_col1, bt_col2 = st.columns([1, 3])

    with bt_col1:
        bt_ticker = st.selectbox("السهم", df_live['symbol'].tolist(), key="bt_ticker")
        strategy = st.selectbox("الاستراتيجية", [
            "RSI_MACD - تقاطع الزخم",
            "MA_Crossover - تقاطع المتوسطات",
            "Bollinger - نطاقات بولينجر",
            "Mean_Reversion - العودة للمتوسط",
            "ADX_Trend - اتباع الاتجاه"
        ], key="bt_strategy")
        period = st.selectbox("الفترة", ["3mo", "6mo", "1y", "2y"], index=2, key="bt_period")
        initial_capital = st.number_input("رأس المال", value=100000, step=10000, key="bt_capital")

        run_bt = st.button("🚀 تشغيل الاختبار", type="primary", use_container_width=True)

    with bt_col2:
        if run_bt:
            with st.spinner("جاري التحليل والاختبار..."):
                df_bt = data_engine.get_stock_history(bt_ticker, period)

                if df_bt is None or df_bt.empty:
                    st.error("❌ تعذر جلب البيانات")
                else:
                    df_bt = df_bt[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    df_bt['Returns'] = df_bt['Close'].pct_change()

                    strategy_key = strategy.split(" - ")[0]

                    if strategy_key == "RSI_MACD":
                        delta = df_bt['Close'].diff()
                        gain = delta.clip(lower=0).rolling(14).mean()
                        loss = (-delta.clip(upper=0)).rolling(14).mean()
                        rsi = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
                        macd = df_bt['Close'].ewm(span=12).mean() - df_bt['Close'].ewm(span=26).mean()
                        signal = macd.ewm(span=9).mean()
                        df_bt['Signal'] = np.where((rsi < 35) & (macd > signal), 1, np.where((rsi > 65) & (macd < signal), -1, 0))

                    elif strategy_key == "MA_Crossover":
                        df_bt['MA50'] = df_bt['Close'].rolling(50).mean()
                        df_bt['MA200'] = df_bt['Close'].rolling(200).mean()
                        df_bt['Signal'] = np.where(df_bt['MA50'] > df_bt['MA200'], 1, -1)

                    elif strategy_key == "Bollinger":
                        bb_mid = df_bt['Close'].rolling(20).mean()
                        bb_std = df_bt['Close'].rolling(20).std()
                        df_bt['Signal'] = np.where(df_bt['Close'] < (bb_mid - 2*bb_std), 1, np.where(df_bt['Close'] > (bb_mid + 2*bb_std), -1, 0))

                    elif strategy_key == "Mean_Reversion":
                        df_bt['MA20'] = df_bt['Close'].rolling(20).mean()
                        df_bt['Deviation'] = (df_bt['Close'] - df_bt['MA20']) / df_bt['MA20']
                        df_bt['Signal'] = np.where(df_bt['Deviation'] < -0.03, 1, np.where(df_bt['Deviation'] > 0.03, -1, 0))

                    elif strategy_key == "ADX_Trend":
                        df_bt['Signal'] = np.where(df_bt['Close'] > df_bt['Close'].rolling(20).mean(), 1, -1)

                    df_bt['Position'] = df_bt['Signal'].diff().fillna(0)
                    df_bt['Strategy_Returns'] = df_bt['Position'].shift(1) * df_bt['Returns']
                    df_bt['Equity'] = initial_capital * (1 + df_bt['Strategy_Returns'].fillna(0)).cumprod()

                    total_return = (df_bt['Equity'].iloc[-1] / initial_capital - 1) * 100
                    buy_hold = (df_bt['Close'].iloc[-1] / df_bt['Close'].iloc[0] - 1) * 100
                    sharpe = (df_bt['Strategy_Returns'].mean() / df_bt['Strategy_Returns'].std() * np.sqrt(252)) if df_bt['Strategy_Returns'].std() != 0 else 0
                    max_dd = ((df_bt['Equity'] / df_bt['Equity'].cummax() - 1).min()) * 100
                    wins = len(df_bt[df_bt['Strategy_Returns'] > 0])
                    total_trades = len(df_bt[df_bt['Strategy_Returns'] != 0])
                    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

                    # Metrics
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("عائد الاستراتيجية", f"{total_return:+.2f}%", delta_color="normal" if total_return >= 0 else "inverse")
                    m2.metric("Buy & Hold", f"{buy_hold:+.2f}%", delta_color="normal" if buy_hold >= 0 else "inverse")
                    m3.metric("Sharpe Ratio", f"{sharpe:.2f}")
                    m4.metric("Win Rate", f"{win_rate:.1f}%")
                    m5.metric("Max Drawdown", f"{max_dd:.2f}%")

                    # Equity Curve
                    fig_equity = go.Figure()
                    fig_equity.add_trace(go.Scatter(
                        x=df_bt.index, y=df_bt['Equity'].values,
                        mode='lines', name='رأس المال',
                        line=dict(color='#6366f1', width=2),
                        fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'
                    ))
                    bh_curve = initial_capital * (1 + df_bt['Returns'].fillna(0)).cumprod()
                    fig_equity.add_trace(go.Scatter(
                        x=df_bt.index, y=bh_curve.values,
                        mode='lines', name='Buy & Hold',
                        line=dict(color='#fbbf24', width=2, dash='dash')
                    ))
                    fig_equity.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=350, margin=dict(t=40, b=40)
                    )
                    st.plotly_chart(fig_equity, use_container_width=True)

                    # Strategy Comparison
                    st.subheader("🏆 مقارنة الاستراتيجيات")
                    strategies = ["RSI_MACD", "MA_Crossover", "Bollinger", "Mean_Reversion", "ADX_Trend"]
                    comp_results = []

                    for strat in strategies:
                        # Quick simulation for each strategy
                        df_temp = df_bt[['Open', 'High', 'Low', 'Close', 'Volume', 'Returns']].copy()

                        if strat == "RSI_MACD":
                            delta = df_temp['Close'].diff()
                            gain = delta.clip(lower=0).rolling(14).mean()
                            loss = (-delta.clip(upper=0)).rolling(14).mean()
                            rsi = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
                            macd = df_temp['Close'].ewm(span=12).mean() - df_temp['Close'].ewm(span=26).mean()
                            signal = macd.ewm(span=9).mean()
                            df_temp['Sig'] = np.where((rsi < 35) & (macd > signal), 1, 0)
                        elif strat == "MA_Crossover":
                            df_temp['MA50'] = df_temp['Close'].rolling(50).mean()
                            df_temp['MA200'] = df_temp['Close'].rolling(200).mean()
                            df_temp['Sig'] = np.where(df_temp['MA50'] > df_temp['MA200'], 1, 0)
                        elif strat == "Bollinger":
                            bb_mid = df_temp['Close'].rolling(20).mean()
                            bb_std = df_temp['Close'].rolling(20).std()
                            df_temp['Sig'] = np.where(df_temp['Close'] < (bb_mid - 2*bb_std), 1, 0)
                        elif strat == "Mean_Reversion":
                            df_temp['MA20'] = df_temp['Close'].rolling(20).mean()
                            df_temp['Dev'] = (df_temp['Close'] - df_temp['MA20']) / df_temp['MA20']
                            df_temp['Sig'] = np.where(df_temp['Dev'] < -0.03, 1, 0)
                        else:
                            df_temp['Sig'] = np.where(df_temp['Close'] > df_temp['Close'].rolling(20).mean(), 1, 0)

                        df_temp['Pos'] = df_temp['Sig'].diff().fillna(0)
                        df_temp['StratRet'] = df_temp['Pos'].shift(1) * df_temp['Returns']
                        eq = initial_capital * (1 + df_temp['StratRet'].fillna(0)).cumprod()
                        ret = (eq.iloc[-1] / initial_capital - 1) * 100
                        sharpe_temp = (df_temp['StratRet'].mean() / df_temp['StratRet'].std() * np.sqrt(252)) if df_temp['StratRet'].std() != 0 else 0
                        trades = int(df_temp['Pos'].abs().sum() / 2)

                        comp_results.append({
                            "الاستراتيجية": strat,
                            "العائد %": round(ret, 2),
                            "Sharpe": round(sharpe_temp, 2),
                            "الصفقات": trades,
                            "الأفضل": "✅" if ret == max([r['العائد %'] for r in comp_results + [{"العائد %": ret}]] ) and len(comp_results) > 0 else ""
                        })

                    comp_df = pd.DataFrame(comp_results)
                    st.dataframe(comp_df, use_container_width=True, hide_index=True)
        else:
            st.info("👈 اختر السهم والاستراتيجية واضغط 'تشغيل الاختبار'")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: SMART TASKS ====================
with tab4:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">✅ المهام الذكية وإدارة المحفظة</span></div>', unsafe_allow_html=True)

    # Add Task Form
    with st.expander("➕ إضافة مهمة جديدة", expanded=False):
        t_col1, t_col2, t_col3 = st.columns([3, 1, 1])
        with t_col1:
            st.text_input("عنوان المهمة", placeholder="مثال: مراجعة أداء سهم CIB", key="new_task_title")
        with t_col2:
            st.selectbox("الأولوية", ["high", "medium", "low"], 
                        format_func=lambda x: {"high": "🔴 عالية", "medium": "🟡 متوسطة", "low": "🟢 منخفضة"}[x],
                        key="new_task_priority")
        with t_col3:
            st.selectbox("التصنيف", ["work", "personal", "learning", "urgent"],
                        format_func=lambda x: {"work": "💼 عمل", "personal": "👤 شخصي", "learning": "📚 تعلم", "urgent": "🚨 عاجل"}[x],
                        key="new_task_category")

        t_col4, t_col5 = st.columns([2, 1])
        with t_col4:
            st.date_input("تاريخ الاستحقاق", datetime.now() + timedelta(days=3), key="new_task_due")
        with t_col5:
            st.button("💾 حفظ المهمة", on_click=add_task_callback, use_container_width=True)

    # Filters
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...", key="task_search")
    with f_col2:
        filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"],
                                       format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x],
                                       key="filter_priority")
    with f_col3:
        filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"], key="filter_status")

    # Filter tasks
    filtered = st.session_state.tasks.copy()
    if task_search:
        filtered = [t for t in filtered if task_search.lower() in t["title"].lower()]
    if filter_priority != "الكل":
        filtered = [t for t in filtered if t["priority"] == filter_priority]
    if filter_status == "مكتمل":
        filtered = [t for t in filtered if t["completed"]]
    elif filter_status == "قيد التنفيذ":
        filtered = [t for t in filtered if not t["completed"]]

    priority_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
    category_icons = {"work": "💼", "personal": "👤", "learning": "📚", "urgent": "🚨"}

    # Display tasks
    for task in filtered:
        status_icon = "✅" if task["completed"] else "⬜"
        opacity = "opacity: 0.5;" if task["completed"] else ""
        p_color = priority_colors.get(task['priority'], '#94a3b8')

        st.markdown(f"""
        <div class="task-item" style="border-right-color: {p_color}; {opacity}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 18px;">{status_icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 14px;">{task['title']}</p>
                        <div style="display: flex; gap: 8px; margin-top: 4px;">
                            <span class="badge badge-blue">{category_icons[task['category']]} {task['category']}</span>
                            <span style="color: #64748b; font-size: 11px;">📅 {task['due']}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons for each task
        act_col1, act_col2 = st.columns([10, 2])
        with act_col1:
            st.checkbox("تم", value=task["completed"], key=f"check_{task['id']}", 
                       on_change=toggle_task, args=(task['id'],), label_visibility="collapsed")
        with act_col2:
            st.button("🗑️", key=f"del_{task['id']}", on_click=delete_task, args=(task['id'],), help="حذف")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 5: CORPORATE INTERFACE ====================
with tab5:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🏢 واجهة الشركات - التوزيعات والإجراءات</span></div>', unsafe_allow_html=True)

    # Company Selector
    corp_symbol = st.selectbox("اختر الشركة", 
                               [s['symbol'] for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] in corp_engine.CORPORATE_DATA],
                               format_func=lambda x: f"{x} - {next(s['name'] for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] == x)}",
                               key="corp_selector")

    corp_data = corp_engine.get_company_data(corp_symbol)
    stock_info = next((s for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] == corp_symbol), None)

    if corp_data and stock_info:
        # Company Header
        st.markdown(f"""
        <div class="corporate-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; color: #fbbf24; font-size: 22px;">{corp_data['arabic_name']}</h2>
                    <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px;">{corp_data['company']} | {stock_info['sector']}</p>
                </div>
                <div style="text-align: left;">
                    <p style="margin: 0; font-size: 24px; font-weight: 700; color: #f1f5f9;">{stock_info['base_price']:.2f}</p>
                    <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">السعر الأساسي</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs within corporate
        corp_tab1, corp_tab2, corp_tab3 = st.tabs(["💰 التوزيعات", "📅 الاجتماعات", "📰 أخبار الشركة"])

        with corp_tab1:
            st.subheader("📋 سجل التوزيعات")
            if corp_data['dividends']:
                div_df = pd.DataFrame(corp_data['dividends'])
                st.dataframe(div_df, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد توزيعات مسجلة")

            if corp_data.get('upcoming'):
                st.subheader("🎯 التوزيع القادم")
                up = corp_data['upcoming']
                st.markdown(f"""
                <div style="padding: 16px; background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2); border-radius: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="margin: 0; font-size: 18px; font-weight: 700; color: #10b981;">{up['expected']:.2f} ج.م</p>
                            <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px;">📅 {up['date']} | نوع: {up['type']}</p>
                        </div>
                        <span class="badge badge-green">معلن</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with corp_tab2:
            st.subheader("📅 اجتماعات الجمعية العمومية")
            if corp_data['meetings']:
                for meeting in corp_data['meetings']:
                    status_color = "#f59e0b" if meeting['status'] == 'قريب' else "#10b981"
                    st.markdown(f"""
                    <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid {status_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; font-weight: 600;">{meeting['subject']}</p>
                                <p style="color: #64748b; font-size: 12px; margin: 4px 0;">📅 {meeting['date']} | نوع: {meeting['type']}</p>
                            </div>
                            <span class="badge" style="background: {status_color}20; color: {status_color};">{meeting['status']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد اجتماعات معلنة")

        with corp_tab3:
            st.subheader("📰 آخر أخبار الشركة")
            if corp_data['news']:
                for news in corp_data['news']:
                    impact_color = "#10b981" if news['impact'] == 'positive' else "#ef4444" if news['impact'] == 'negative' else "#94a3b8"
                    st.markdown(f"""
                    <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid {impact_color};">
                        <p style="margin: 0; font-size: 13px; line-height: 1.5;">{news['title']}</p>
                        <p style="color: #64748b; font-size: 11px; margin: 4px 0 0 0;">📅 {news['date']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد أخبار حديثة")

    # Market-wide upcoming dividends
    st.divider()
    st.subheader("📅 التوزيعات القادمة عبر السوق")
    upcoming_all = corp_engine.get_upcoming_dividends_all()

    for div in upcoming_all[:6]:
        days_left = (datetime.strptime(div['date'], "%Y-%m-%d") - datetime.now()).days
        status_text = "غداً" if days_left <= 1 else f"بعد {days_left} يوم" if days_left <= 30 else div['date']
        status_color = "#ef4444" if days_left <= 3 else "#f59e0b" if days_left <= 14 else "#10b981"

        st.markdown(f"""
        <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;">💰</div>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 14px;">{div['company']} ({div['symbol']})</p>
                        <p style="color: #64748b; font-size: 12px; margin: 4px 0 0 0;">📅 {div['date']} | 💵 {div['amount']} ج.م</p>
                    </div>
                </div>
                <span class="badge" style="background: {status_color}20; color: {status_color};">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 6: NEWS & SENTIMENT ====================
with tab6:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📰 أخبار السوق وتحليل المزاج</span></div>', unsafe_allow_html=True)

    news_col1, news_col2 = st.columns([1, 2])

    with news_col1:
        st.subheader("🔥 آخر الأخبار")
        for news in news_engine.NEWS_FEED:
            news_color = "#10b981" if news['type'] == 'positive' else "#ef4444" if news['type'] == 'negative' else "#94a3b8"
            icon = "📈" if news['type'] == 'positive' else "📉" if news['type'] == 'negative' else "📊"
            impact_bars = "█" * (news['impact_score'] // 2) + "░" * (5 - news['impact_score'] // 2)

            st.markdown(f"""
            <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid {news_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="width: 100%;">
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                            <span style="color: #fbbf24; font-size: 11px; font-weight: 600;">{news['time']}</span>
                            <span class="badge badge-blue" style="font-size: 10px;">{news['source']}</span>
                            <span style="color: {news_color}; font-size: 10px;">تأثير: {impact_bars}</span>
                        </div>
                        <p style="margin: 0; font-size: 13px; line-height: 1.5;">{icon} {news['title']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with news_col2:
        st.subheader("📊 مؤشر المزاج السوقي")
        sentiment = news_engine.get_sentiment_score()

        # Sentiment Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment['score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "مؤشر المزاج", 'font': {'size': 24, 'color': '#e2e8f0'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                'bar': {'color': sentiment['color']},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(239,68,68,0.1)'},
                    {'range': [40, 60], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [60, 100], 'color': 'rgba(16,185,129,0.1)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", color="#94a3b8"),
            height=300, margin=dict(t=40, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Sector News Impact
        st.subheader("📈 تأثير الأخبار على القطاعات")
        sector_impact = []
        for sector in df_live['sector'].unique():
            sector_stocks = df_live[df_live['sector'] == sector]
            avg_change = sector_stocks['change_pct'].mean()
            sector_impact.append({"القطاع": sector, "التأثير %": round(avg_change, 2)})

        fig_impact = px.bar(
            pd.DataFrame(sector_impact),
            x="القطاع", y="التأثير %",
            color="التأثير %",
            color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981']
        )
        fig_impact.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#94a3b8"),
            height=250, margin=dict(t=20, b=40)
        )
        st.plotly_chart(fig_impact, use_container_width=True)

        # Quick Technical Analysis
        st.subheader("📊 التحليل الفني السريع")
        ta_stock = st.selectbox("السهم", df_live['symbol'].tolist(), key="ta_stock_tab6")

        df_ta = data_engine.get_stock_history(ta_stock, "3mo")
        if df_ta is not None and len(df_ta) > 30:
            df_ta = ta_engine.calculate_all(df_ta)
            if df_ta is not None:
                latest = df_ta.iloc[-1]

                ta_metrics = st.columns(4)
                metrics_data = [
                    ("RSI (14)", latest.get('RSI', 0), "normal" if 30 < latest.get('RSI', 50) < 70 else "inverse"),
                    ("MACD", latest.get('MACD', 0), "normal" if latest.get('MACD', 0) > 0 else "inverse"),
                    ("SMA 20", latest.get('SMA_20', 0), "normal"),
                    ("ATR", latest.get('ATR', 0), "off")
                ]

                for i, (label, value, delta_color) in enumerate(metrics_data):
                    with ta_metrics[i]:
                        st.metric(label, f"{value:.2f}" if pd.notna(value) else "N/A", delta_color=delta_color)

                # Mini chart
                fig_mini = go.Figure()
                fig_mini.add_trace(go.Scatter(
                    x=df_ta.index[-60:], y=df_ta['Close'].tail(60),
                    mode='lines', line=dict(color='#6366f1', width=2),
                    fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'
                ))
                if pd.notna(latest.get('SMA_20')):
                    fig_mini.add_trace(go.Scatter(
                        x=df_ta.index[-60:], y=df_ta['SMA_20'].tail(60),
                        mode='lines', line=dict(color='#fbbf24', width=1, dash='dash'), name='SMA 20'
                    ))
                fig_mini.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", color="#94a3b8"),
                    height=250, margin=dict(t=10, b=10, l=10, r=10), showlegend=False
                )
                st.plotly_chart(fig_mini, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 7: DETAILED ANALYSIS ====================
with tab7:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🔮 التحليل الذكي الشامل مع إدارة المخاطرة</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 16px;">
        <p style="color: #f87171; font-weight: 600; margin: 0; font-size: 13px;">⚠️ تحذير</p>
        <p style="color: #fca5a5; font-size: 12px; margin-top: 4px;">التوقعات نتائج رياضية للبيانات التاريخية فقط. لا تعتبر توصية استثمارية. استخدم Stop Loss دائماً.</p>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])
    with ctrl1:
        analysis_stock = st.selectbox("السهم", df_live['symbol'].tolist(), key="ai_stock_tab7")
    with ctrl2:
        analysis_period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="ai_period_tab7")
    with ctrl3:
        prediction_days = st.slider("أيام التوقع", 3, 30, 10, key="ai_days_tab7")
    with ctrl4:
        account_balance = st.number_input("رأس المال", value=100000, step=10000, key="ai_balance_tab7")

    if st.button("🔮 تشغيل التحليل الشامل", type="primary", use_container_width=True):
        with st.spinner("جاري التحليل الشامل..."):
            df = data_engine.get_stock_history(analysis_stock, analysis_period)

            if df is None or df.empty:
                st.error("❌ تعذر جلب البيانات.")
            else:
                df = ta_engine.calculate_all(df)
                if df is None:
                    st.error("❌ خطأ في حساب المؤشرات.")
                else:
                    signals = ta_engine.generate_signals(df)
                    overall_signal, score, signal_text, trend = ta_engine.calculate_overall(signals)
                    predictions = ai_engine.predict_prices(df, days=prediction_days)
                    sr_levels = ai_engine.calculate_support_resistance(df)

                    current_price = df['Close'].iloc[-1]
                    atr = df['ATR'].iloc[-1] if pd.notna(df['ATR'].iloc[-1]) else current_price * 0.02

                    stop_loss = current_price - (atr * 2)
                    take_profit_1 = current_price + (atr * 2)
                    take_profit_2 = current_price + (atr * 3.5)

                    # Risk Analysis
                    risk_profile = risk_engine.analyze_risk_profile(df, current_price, stop_loss, take_profit_1, account_balance)

                    # SIGNAL DISPLAY
                    st.subheader("🎯 إشارة التداول الرئيسية")
                    sig_cols = st.columns([1, 2, 1])
                    with sig_cols[1]:
                        if overall_signal == "STRONG_BUY":
                            st.markdown('<div class="signal-box signal-buy"><h2 style="margin: 0; color: #10b981; font-size: 32px;">🟢 شراء قوي</h2></div>', unsafe_allow_html=True)
                        elif overall_signal == "BUY":
                            st.markdown('<div class="signal-box signal-buy"><h2 style="margin: 0; color: #34d399; font-size: 28px;">🟢 شراء</h2></div>', unsafe_allow_html=True)
                        elif overall_signal == "STRONG_SELL":
                            st.markdown('<div class="signal-box signal-sell"><h2 style="margin: 0; color: #ef4444; font-size: 32px;">🔴 بيع قوي</h2></div>', unsafe_allow_html=True)
                        elif overall_signal == "SELL":
                            st.markdown('<div class="signal-box signal-sell"><h2 style="margin: 0; color: #f87171; font-size: 28px;">🔴 بيع</h2></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="signal-box signal-hold"><h2 style="margin: 0; color: #fbbf24; font-size: 28px;">🟡 انتظار</h2></div>', unsafe_allow_html=True)

                    # RISK LEVELS
                    st.subheader("🛡️ مستويات إدارة المخاطرة")
                    risk_cols = st.columns(4)
                    risk_data = [
                        ("🛑 Stop Loss", stop_loss, ((current_price-stop_loss)/current_price*100), "#ef4444"),
                        ("📍 السعر الحالي", current_price, 0, "#6366f1"),
                        ("🎯 الهدف 1", take_profit_1, ((take_profit_1-current_price)/current_price*100), "#10b981"),
                        ("🎯🎯 الهدف 2", take_profit_2, ((take_profit_2-current_price)/current_price*100), "#fbbf24")
                    ]
                    for i, (label, value, pct, color) in enumerate(risk_data):
                        with risk_cols[i]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid {color}30;">
                                <p style="color: #64748b; font-size: 11px; margin: 0;">{label}</p>
                                <p style="font-size: 24px; font-weight: 700; color: {color}; margin: 4px 0;">{value:.2f}</p>
                                {f'<p style="font-size: 11px; color: {color}; margin: 0;">{pct:.1f}%</p>' if pct else ''}
                            </div>
                            """, unsafe_allow_html=True)

                    # ADVANCED RISK METRICS
                    st.subheader("📊 تحليل المخاطرة المتقدم")
                    risk_metric_cols = st.columns(4)
                    risk_metrics = [
                        ("التقلب السنوي", f"{risk_profile.get('volatility_annual', 0):.1f}%", risk_profile.get('volatility_annual', 0) < 30),
                        ("VaR (95%)", f"{risk_profile.get('var_95', 0):.2f}%", risk_profile.get('var_95', 0) > -5),
                        ("CVaR (95%)", f"{risk_profile.get('cvar_95', 0):.2f}%", risk_profile.get('cvar_95', 0) > -8),
                        ("نسبة كيلي", f"{risk_profile.get('kelly_pct', 0):.1f}%", risk_profile.get('kelly_pct', 0) > 0)
                    ]
                    for i, (label, value, good) in enumerate(risk_metrics):
                        with risk_metric_cols[i]:
                            color = "#10b981" if good else "#ef4444"
                            st.markdown(f"""
                            <div class="risk-metric {('risk-low' if good else 'risk-high')}">
                                <p style="color: #64748b; font-size: 11px; margin: 0;">{label}</p>
                                <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 4px 0;">{value}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # POSITION SIZING
                    st.subheader("💰 توصية حجم المركز")
                    pos_cols = st.columns(4)
                    with pos_cols[0]:
                        st.metric("الأسهم المقترحة", f"{risk_profile.get('shares', 0)}")
                    with pos_cols[1]:
                        st.metric("قيمة المركز", f"{risk_profile.get('position_value', 0):,.0f} ج.م")
                    with pos_cols[2]:
                        st.metric("المخاطرة الفعلية", f"{risk_profile.get('actual_risk_pct', 0):.2f}%")
                    with pos_cols[3]:
                        st.metric("نسبة الربح/خسارة", f"{risk_profile.get('rr_ratio', 0):.2f}")

                    # Risk Classification
                    st.markdown(f"""
                    <div style="padding: 16px; background: {risk_profile.get('risk_color', '#94a3b8')}10; border: 1px solid {risk_profile.get('risk_color', '#94a3b8')}40; border-radius: 12px; margin: 16px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; font-size: 18px; font-weight: 700; color: {risk_profile.get('risk_color', '#94a3b8')};">تصنيف المخاطرة: {risk_profile.get('risk_class', 'غير معروف')}</p>
                                <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px;">التوصية: {risk_profile.get('recommendation', 'غير معروف')}</p>
                            </div>
                            <p style="margin: 0; font-size: 14px; color: #64748b;">أقصى خسائر متتالية: {risk_profile.get('max_consecutive_losses', 0)} يوم</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # TECHNICAL INDICATORS
                    st.subheader("📊 المؤشرات الفنية")
                    latest = df.iloc[-1]
                    ind_cols = st.columns(6)
                    indicators = [
                        ("RSI (14)", latest.get('RSI', 0), "#ef4444" if latest.get('RSI', 50) > 70 else "#10b981" if latest.get('RSI', 50) < 30 else "#fbbf24", "ذروة شراء" if latest.get('RSI', 50) > 70 else "ذروة بيع" if latest.get('RSI', 50) < 30 else "محايد"),
                        ("MACD", latest.get('MACD', 0), "#10b981" if latest.get('MACD', 0) > 0 else "#ef4444", "إيجابي" if latest.get('MACD', 0) > 0 else "سلبي"),
                        ("Bollinger", latest.get('BB_Position', 0.5), "#10b981" if latest.get('BB_Position', 0.5) < 0.2 else "#ef4444" if latest.get('BB_Position', 0.5) > 0.8 else "#fbbf24", "منطقة شراء" if latest.get('BB_Position', 0.5) < 0.2 else "منطقة بيع" if latest.get('BB_Position', 0.5) > 0.8 else "النطاق الأوسط"),
                        ("Stochastic", latest.get('Stoch_K', 50), "#10b981" if latest.get('Stoch_K', 50) < 20 else "#ef4444" if latest.get('Stoch_K', 50) > 80 else "#fbbf24", "ذروة بيع" if latest.get('Stoch_K', 50) < 20 else "ذروة شراء" if latest.get('Stoch_K', 50) > 80 else "محايد"),
                        ("SMA 20", latest.get('SMA_20', 0), "#10b981" if latest.get('Close', 0) > latest.get('SMA_20', 0) else "#ef4444", "صاعد" if latest.get('Close', 0) > latest.get('SMA_20', 0) else "هابط"),
                        ("ADX", latest.get('ADX', 0), "#10b981" if latest.get('ADX', 0) > 25 else "#fbbf24", "اتجاه قوي" if latest.get('ADX', 0) > 25 else "اتجاه ضعيف")
                    ]
                    for i, (label, value, color, text) in enumerate(indicators):
                        with ind_cols[i]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                                <p style="color: #64748b; font-size: 10px; margin: 0;">{label}</p>
                                <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 4px 0;">{value:.1f}</p>
                                <p style="font-size: 10px; color: {color}; margin: 0;">{text}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # SUPPORT/RESISTANCE
                    st.subheader("🎯 مستويات الدعم والمقاومة")
                    sr_cols = st.columns(2)
                    with sr_cols[0]:
                        st.markdown("**الدعم:**")
                        for s in sr_levels.get('supports', []):
                            st.markdown(f"<span style='color: #10b981; font-weight: 600;'>▲ {s}</span>", unsafe_allow_html=True)
                    with sr_cols[1]:
                        st.markdown("**المقاومة:**")
                        for r in sr_levels.get('resistances', []):
                            st.markdown(f"<span style='color: #ef4444; font-weight: 600;'>▼ {r}</span>", unsafe_allow_html=True)

                    # Fibonacci
                    st.markdown("**مستويات فيبوناتشي:**")
                    fib = sr_levels.get('fibonacci', {})
                    fib_cols = st.columns(len(fib) if fib else 1)
                    for i, (level, value) in enumerate(fib.items()):
                        with fib_cols[i]:
                            color = "#fbbf24" if level in ['38.2%', '61.8%'] else "#94a3b8"
                            st.markdown(f"""
                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 6px;">
                                <p style="color: #64748b; font-size: 10px; margin: 0;">{level}</p>
                                <p style="font-size: 14px; font-weight: 600; color: {color}; margin: 2px 0;">{value}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # PREDICTION CHART
                    if 'combined' in predictions:
                        st.subheader("🔮 توقعات الأسعار مع نطاقات الثقة")
                        pred_df = pd.DataFrame(predictions['combined'])

                        fig_pred = go.Figure()
                        hist_days = min(60, len(df))
                        fig_pred.add_trace(go.Scatter(
                            x=df.index[-hist_days:], y=df['Close'].tail(hist_days),
                            mode='lines', name='السعر الفعلي',
                            line=dict(color='#6366f1', width=2),
                            fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'
                        ))

                        last_date = df.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=prediction_days, freq='B')
                        pred_prices = [p['predicted'] for p in predictions['combined']]
                        upper = [p['upper_bound'] for p in predictions['combined']]
                        lower = [p['lower_bound'] for p in predictions['combined']]

                        fig_pred.add_trace(go.Scatter(
                            x=future_dates, y=pred_prices,
                            mode='lines+markers', name='التوقع',
                            line=dict(color='#fbbf24', width=3),
                            marker=dict(size=8, color='#fbbf24')
                        ))

                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=upper + list(reversed(pred_prices)),
                            fill='tonexty', fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                            name='الحد الأعلى'
                        ))

                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=list(reversed(pred_prices)) + lower,
                            fill='tonexty', fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                            name='الحد الأدنى'
                        ))

                        fig_pred.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444", annotation_text="Stop Loss", annotation_position="right")
                        fig_pred.add_hline(y=take_profit_1, line_dash="dash", line_color="#10b981", annotation_text="TP1", annotation_position="right")

                        fig_pred.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter", color="#94a3b8"),
                            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=450, margin=dict(t=40, b=40)
                        )
                        st.plotly_chart(fig_pred, use_container_width=True)

                    # CANDLESTICK CHART
                    st.subheader("📈 الرسم البياني التفاعلي")
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name='الشموع'
                    ))

                    if pd.notna(latest.get('SMA_20')):
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#6366f1', width=1)))
                    if pd.notna(latest.get('SMA_50')):
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#fbbf24', width=1)))
                    if pd.notna(latest.get('BB_Upper')):
                        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='rgba(16,185,129,0.5)', width=1, dash='dash')))
                        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='rgba(239,68,68,0.5)', width=1, dash='dash')))

                    fig.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444", annotation_text="SL", annotation_position="right")
                    fig.add_hline(y=take_profit_1, line_dash="dash", line_color="#10b981", annotation_text="TP1", annotation_position="right")

                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=450, margin=dict(t=40, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # VOLUME CHART
                    st.subheader("📊 حجم التداول")
                    fig_vol = go.Figure()
                    colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' for i in range(len(df))]
                    fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='الحجم'))
                    if pd.notna(df.get('Volume_SMA')).any():
                        fig_vol.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'], mode='lines', name='متوسط الحجم', line=dict(color='#fbbf24', width=2)))

                    fig_vol.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=250, margin=dict(t=40, b=20)
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
footer_cols = st.columns(3)

with footer_cols[0]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #64748b; font-size: 12px; margin: 0;">⚡ EGX Pro Terminal v21.0</p>
        <p style="color: #475569; font-size: 11px; margin: 4px 0;">نظام تحليلي احترافي | AI-Powered</p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[1]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #fbbf24; font-size: 13px; margin: 0; font-weight: 600;">
            🏆 الأقوى: {best_stock['symbol']} +{best_stock['change_pct']:.2f}% | 📉 الأضعف: {worst_stock['symbol']} {worst_stock['change_pct']:.2f}%
        </p>
        <p style="color: #475569; font-size: 11px; margin: 4px 0;">
            آخر تحديث: {datetime.now().strftime("%H:%M:%S")}
        </p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[2]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #475569; font-size: 11px; margin: 0;">
            © 2026 | جميع البيانات للتوضيح | التوقعات للأغراض التعليمية فقط
        </p>
        <p style="color: #475569; font-size: 10px; margin: 4px 0;">
            Backtesting | AI Analysis | Risk Management | Real-time Data
        </p>
    </div>
    """, unsafe_allow_html=True)

# Debug Console
if st.session_state.debug_mode:
    st.markdown("---")
    st.subheader("🔧 معلومات النظام")
    st.json({
        "cache_size": len(st.session_state.market_data_cache),
        "alerts_cached": st.session_state.alerts_cache is not None,
        "tasks_count": len(st.session_state.tasks),
        "selected_stock": st.session_state.selected_stock,
        "risk_settings": st.session_state.risk_settings,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
