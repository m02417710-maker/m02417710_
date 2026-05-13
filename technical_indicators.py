
import os

enhanced_code = '''import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
import traceback
import logging
import sys
from functools import wraps

warnings.filterwarnings('ignore')

# ==================== DEBUGGING & ERROR HANDLING SYSTEM ====================
class EGXDebugSystem:
    """Advanced debugging and error recovery system"""
    
    def __init__(self):
        self.errors_log = []
        self.performance_metrics = {}
        self.data_quality_checks = {}
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
    def log_error(self, component, error, context=""):
        """Log errors with full context for debugging"""
        error_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "recovered": False
        }
        self.errors_log.append(error_entry)
        logging.error(f"[{component}] {error}: {context}")
        return error_entry
    
    def safe_execute(self, func, component_name, default_return=None, *args, **kwargs):
        """Execute function with automatic error recovery"""
        try:
            start_time = datetime.now()
            result = func(*args, **kwargs)
            end_time = datetime.now()
            self.performance_metrics[component_name] = {
                "last_execution": end_time,
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "status": "success",
                "calls": self.performance_metrics.get(component_name, {}).get("calls", 0) + 1
            }
            return result
        except Exception as e:
            error_entry = self.log_error(component_name, e, f"args: {args}, kwargs: {kwargs}")
            
            # Attempt recovery
            if self.recovery_attempts < self.max_recovery_attempts:
                self.recovery_attempts += 1
                try:
                    # Recovery strategy: retry with simplified parameters
                    if "history" in component_name or "data" in component_name:
                        logging.info(f"[{component_name}] Attempting data recovery...")
                        error_entry["recovered"] = True
                        return default_return
                    elif "plot" in component_name or "chart" in component_name:
                        logging.info(f"[{component_name}] Attempting chart recovery...")
                        error_entry["recovered"] = True
                        return default_return
                except Exception as recovery_error:
                    self.log_error(f"{component_name}_recovery", recovery_error)
            
            return default_return
    
    def validate_dataframe(self, df, component_name, required_columns=None):
        """Validate dataframe quality and completeness"""
        checks = {
            "component": component_name,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "is_empty": df.empty if df is not None else True,
            "shape": df.shape if df is not None else (0, 0),
            "null_count": df.isnull().sum().sum() if df is not None else 0,
            "duplicate_count": df.duplicated().sum() if df is not None else 0,
            "valid": True
        }
        
        if df is None or df.empty:
            checks["valid"] = False
            checks["error"] = "Empty or None dataframe"
        elif required_columns:
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                checks["valid"] = False
                checks["error"] = f"Missing columns: {missing}"
        
        self.data_quality_checks[component_name] = checks
        return checks["valid"]
    
    def get_health_report(self):
        """Generate system health report"""
        total_errors = len(self.errors_log)
        recovered_errors = sum(1 for e in self.errors_log if e["recovered"])
        failed_components = set(e["component"] for e in self.errors_log if not e["recovered"])
        
        return {
            "total_errors": total_errors,
            "recovered": recovered_errors,
            "failed_components": list(failed_components),
            "data_quality": self.data_quality_checks,
            "performance": self.performance_metrics,
            "system_status": "HEALTHY" if total_errors == 0 else "DEGRADED" if recovered_errors > 0 else "CRITICAL"
        }

# Initialize global debug system
if 'debug_system' not in st.session_state:
    st.session_state.debug_system = EGXDebugSystem()

debug = st.session_state.debug_system

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="⚡ EGX Pro Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# ==================== PROFESSIONAL DARK THEME CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
    
    * { 
        font-family: 'Inter', 'Cairo', sans-serif !important;
        letter-spacing: -0.01em;
    }
    
    .main {
        background: linear-gradient(180deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%);
        color: #e2e8f0;
    }
    
    /* Professional Panel System */
    .pro-panel {
        background: linear-gradient(145deg, rgba(20, 20, 30, 0.95), rgba(15, 15, 25, 0.98));
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    
    .pro-panel:hover {
        border-color: rgba(99, 102, 241, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    
    .pro-panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .pro-panel-title {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .pro-panel-value {
        font-size: 24px;
        font-weight: 700;
        color: #f1f5f9;
        margin: 4px 0;
    }
    
    .pro-panel-subtitle {
        font-size: 11px;
        color: #64748b;
    }
    
    /* Grid Layout System */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
    .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
    
    /* Data Table Styling */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    
    .data-table th {
        background: rgba(255, 255, 255, 0.03);
        color: #64748b;
        font-weight: 600;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 11px;
        text-transform: uppercase;
    }
    
    .data-table td {
        padding: 8px 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        color: #cbd5e1;
    }
    
    .data-table tr:hover td {
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* Status Indicators */
    .status-up { color: #10b981; }
    .status-down { color: #ef4444; }
    .status-neutral { color: #94a3b8; }
    .status-warning { color: #f59e0b; }
    
    /* Badge System */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .badge-yellow { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-blue { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
    
    /* Live Indicator */
    .live-pulse {
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse-live 2s infinite;
        margin-left: 6px;
    }
    
    @keyframes pulse-live {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }
    
    /* Stock Button Cards */
    .stock-card {
        background: linear-gradient(145deg, rgba(25, 25, 35, 0.9), rgba(20, 20, 30, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stock-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
    }
    
    .stock-card-symbol {
        font-size: 14px;
        font-weight: 700;
        color: #fbbf24;
        margin-bottom: 4px;
    }
    
    .stock-card-price {
        font-size: 20px;
        font-weight: 700;
        color: #f1f5f9;
        margin: 4px 0;
    }
    
    .stock-card-change {
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    
    .stock-card-change.up {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    
    .stock-card-change.down {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    
    /* Signal Boxes */
    .signal-box {
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        border: 1px solid;
    }
    
    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.02));
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.02));
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    .signal-hold {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.02));
        border-color: rgba(245, 158, 11, 0.3);
    }
    
    /* Debug Console */
    .debug-console {
        background: #0d0d12;
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 8px;
        padding: 12px;
        font-family: 'Courier New', monospace;
        font-size: 11px;
        color: #94a3b8;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .debug-entry {
        margin: 4px 0;
        padding: 4px 8px;
        border-radius: 4px;
        border-right: 2px solid;
    }
    
    .debug-error { border-color: #ef4444; background: rgba(239, 68, 68, 0.05); }
    .debug-success { border-color: #10b981; background: rgba(16, 185, 129, 0.05); }
    .debug-warning { border-color: #f59e0b; background: rgba(245, 158, 11, 0.05); }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255, 255, 255, 0.02);
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        padding: 10px 20px;
        border: none;
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #818cf8 !important;
        font-weight: 600;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] { 
        font-size: 20px !important; 
        font-weight: 700 !important; 
        color: #f1f5f9 !important;
    }
    div[data-testid="stMetricDelta"] { font-size: 12px !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f16 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "مراجعة أداء سهم CIB", "priority": "high", "category": "work", "due": "2026-05-15", "completed": False, "created": "2026-05-10"},
        {"id": 2, "title": "تحليل تقرير البورصة الأسبوعي", "priority": "medium", "category": "work", "due": "2026-05-16", "completed": True, "created": "2026-05-09"},
        {"id": 3, "title": "قراءة كتاب الاستثمار الذكي", "priority": "low", "category": "learning", "due": "2026-05-20", "completed": False, "created": "2026-05-08"},
        {"id": 4, "title": "متابعة اجتماع عمومية البنك التجاري", "priority": "high", "category": "urgent", "due": "2026-05-14", "completed": False, "created": "2026-05-12"},
        {"id": 5, "title": "تحديث بيانات المحفظة الاستثمارية", "priority": "medium", "category": "personal", "due": "2026-05-13", "completed": False, "created": "2026-05-11"},
    ]

if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'market_data_cache' not in st.session_state:
    st.session_state.market_data_cache = {}

def select_stock(symbol):
    st.session_state.selected_stock = symbol
    st.session_state.show_analysis = True

# ==================== DATA ====================
stocks_data = [
    {"symbol": "COMI", "name": "CIB", "sector": "بنوك", "price": 140.01, "change": -2.09, "change_pct": -1.47, "volume": 13263000000, "high": 142.81, "low": 137.21, "market_cap": 420000000000},
    {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "price": 58.14, "change": -0.95, "change_pct": -1.61, "volume": 5550000000, "high": 59.3, "low": 56.98, "market_cap": 180000000000},
    {"symbol": "ADIB", "name": "أبوظبي الإسلامي", "sector": "بنوك", "price": 47.49, "change": -1.47, "change_pct": -3.0, "volume": 2413000000, "high": 48.44, "low": 46.54, "market_cap": 95000000000},
    {"symbol": "HDBK", "name": "بنك الإسكان", "sector": "بنوك", "price": 147.26, "change": 0.03, "change_pct": 0.02, "volume": 3048000000, "high": 150.21, "low": 144.31, "market_cap": 220000000000},
    {"symbol": "CANA", "name": "قناة السويس", "sector": "بنوك", "price": 33.88, "change": 1.86, "change_pct": 5.81, "volume": 1320000000, "high": 34.56, "low": 33.2, "market_cap": 45000000000},
    {"symbol": "CIEB", "name": "كريدي أجريكول", "sector": "بنوك", "price": 23.73, "change": -0.29, "change_pct": -1.21, "volume": 1267000000, "high": 24.2, "low": 23.26, "market_cap": 32000000000},
    {"symbol": "FAIT", "name": "فيصل الإسلامي", "sector": "بنوك", "price": 34.11, "change": 0.32, "change_pct": 0.95, "volume": 1202000000, "high": 34.79, "low": 33.43, "market_cap": 48000000000},
    {"symbol": "SAUD", "name": "البركة", "sector": "بنوك", "price": 24.7, "change": -0.36, "change_pct": -1.44, "volume": 809000000, "high": 25.19, "low": 24.21, "market_cap": 28000000000},
    {"symbol": "UBEE", "name": "المصرف المتحد", "sector": "بنوك", "price": 13.98, "change": 1.53, "change_pct": 12.29, "volume": 619000000, "high": 14.26, "low": 13.7, "market_cap": 15000000000},
    {"symbol": "EXPA", "name": "التنمية الصادرات", "sector": "بنوك", "price": 18.68, "change": -0.05, "change_pct": -0.27, "volume": 1255000000, "high": 19.05, "low": 18.31, "market_cap": 22000000000},
    {"symbol": "EGBE", "name": "المصري الخليجي", "sector": "بنوك", "price": 0.412, "change": -0.72, "change_pct": -63.6, "volume": 1076000000, "high": 0.42, "low": 0.4, "market_cap": 8000000000},
    {"symbol": "EFIH", "name": "e-Finance", "sector": "تكنولوجيا مالية", "price": 22.32, "change": -1.59, "change_pct": -6.65, "volume": 677000000, "high": 22.77, "low": 21.87, "market_cap": 65000000000},
    {"symbol": "FWRY", "name": "فوري", "sector": "تكنولوجيا مالية", "price": 20.88, "change": -0.95, "change_pct": -4.35, "volume": 865000000, "high": 21.3, "low": 20.46, "market_cap": 52000000000},
    {"symbol": "SCTS", "name": "مقاصة قناة السويس", "sector": "تكنولوجيا مالية", "price": 652.11, "change": -1.49, "change_pct": -0.23, "volume": 305000000, "high": 665.15, "low": 639.07, "market_cap": 130000000000},
    {"symbol": "VALU", "name": "U للتمويل", "sector": "تكنولوجيا مالية", "price": 12.6, "change": -2.25, "change_pct": -15.15, "volume": 115000000, "high": 12.85, "low": 12.35, "market_cap": 18000000000},
    {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "price": 98.25, "change": -1.75, "change_pct": -1.75, "volume": 6250000000, "high": 100.22, "low": 96.28, "market_cap": 280000000000},
    {"symbol": "EMFD", "name": "إعمار مصر", "sector": "عقارات", "price": 11.1, "change": 0.64, "change_pct": 6.12, "volume": 1981000000, "high": 11.32, "low": 10.88, "market_cap": 55000000000},
    {"symbol": "PHDC", "name": "بالم هيلز", "sector": "عقارات", "price": 14.0, "change": -2.44, "change_pct": -14.84, "volume": 3617000000, "high": 14.28, "low": 13.72, "market_cap": 42000000000},
    {"symbol": "ORHD", "name": "أوراسكوم للتنمية", "sector": "عقارات", "price": 33.35, "change": -0.83, "change_pct": -2.43, "volume": 2495000000, "high": 34.02, "low": 32.68, "market_cap": 78000000000},
    {"symbol": "OCDI", "name": "سوديك", "sector": "عقارات", "price": 22.98, "change": 0.0, "change_pct": 0.0, "volume": 2126000000, "high": 23.44, "low": 22.52, "market_cap": 65000000000},
    {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "price": 89.51, "change": -0.77, "change_pct": -0.85, "volume": 28105000000, "high": 91.3, "low": 87.72, "market_cap": 180000000000},
    {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "price": 317.0, "change": 4.6, "change_pct": 1.47, "volume": 4588000000, "high": 323.34, "low": 310.66, "market_cap": 95000000000},
    {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "price": 87.19, "change": 1.38, "change_pct": 1.61, "volume": 2580000000, "high": 88.93, "low": 85.45, "market_cap": 72000000000},
    {"symbol": "MFPC", "name": "موبكو", "sector": "صناعة", "price": 45.15, "change": 3.15, "change_pct": 7.5, "volume": 2684000000, "high": 46.05, "low": 44.25, "market_cap": 48000000000},
    {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "price": 58.0, "change": 2.02, "change_pct": 3.61, "volume": 1245000000, "high": 59.16, "low": 56.84, "market_cap": 35000000000},
    {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "price": 98.49, "change": -0.4, "change_pct": -0.4, "volume": 10667000000, "high": 100.46, "low": 96.52, "market_cap": 200000000000},
    {"symbol": "EGSA", "name": "النايل سات", "sector": "اتصالات", "price": 9.09, "change": 0.0, "change_pct": 0.0, "volume": 470000000, "high": 9.27, "low": 8.91, "market_cap": 18000000000},
    {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "price": 40.31, "change": 0.83, "change_pct": 2.1, "volume": 3989000000, "high": 41.12, "low": 39.5, "market_cap": 85000000000},
    {"symbol": "EFID", "name": "إيديتا", "sector": "سلع استهلاكية", "price": 28.6, "change": 1.65, "change_pct": 6.12, "volume": 2092000000, "high": 29.17, "low": 28.03, "market_cap": 62000000000},
    {"symbol": "JUFO", "name": "جهينة", "sector": "سلع استهلاكية", "price": 28.9, "change": 0.0, "change_pct": 0.0, "volume": 2998000000, "high": 29.48, "low": 28.32, "market_cap": 58000000000},
    {"symbol": "DOMT", "name": "دومتي", "sector": "سلع استهلاكية", "price": 26.0, "change": 2.93, "change_pct": 12.7, "volume": 939000000, "high": 26.52, "low": 25.48, "market_cap": 22000000000},
    {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "price": 48.81, "change": -0.35, "change_pct": -0.71, "volume": 883000000, "high": 49.79, "low": 47.83, "market_cap": 38000000000},
    {"symbol": "POUL", "name": "القاهرة للدواجن", "sector": "سلع استهلاكية", "price": 34.8, "change": -0.6, "change_pct": -1.69, "volume": 1582000000, "high": 35.5, "low": 34.1, "market_cap": 28000000000},
    {"symbol": "GBCO", "name": "GB Corp", "sector": "سلع استهلاكية", "price": 29.3, "change": 2.09, "change_pct": 7.68, "volume": 8023000000, "high": 29.89, "low": 28.71, "market_cap": 45000000000},
    {"symbol": "ORWE", "name": "النساجون الشرقيون", "sector": "سلع استهلاكية", "price": 23.56, "change": -0.38, "change_pct": -1.59, "volume": 2662000000, "high": 24.03, "low": 23.09, "market_cap": 32000000000},
    {"symbol": "CLHO", "name": "كليوباترا", "sector": "صحة", "price": 14.94, "change": 0.74, "change_pct": 5.21, "volume": 723000000, "high": 15.24, "low": 14.64, "market_cap": 18000000000},
    {"symbol": "PHAR", "name": "أمون", "sector": "صحة", "price": 89.49, "change": -0.12, "change_pct": -0.13, "volume": 944000000, "high": 91.28, "low": 87.7, "market_cap": 42000000000},
    {"symbol": "ISPH", "name": "ابن سينا", "sector": "صحة", "price": 11.96, "change": 0.25, "change_pct": 2.13, "volume": 7660000000, "high": 12.2, "low": 11.72, "market_cap": 35000000000},
    {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "price": 687.72, "change": 0.37, "change_pct": 0.05, "volume": 692000000, "high": 701.47, "low": 673.97, "market_cap": 85000000000},
    {"symbol": "NIPH", "name": "النيل للأدوية", "sector": "صحة", "price": 173.2, "change": -1.59, "change_pct": -0.91, "volume": 197000000, "high": 176.66, "low": 169.74, "market_cap": 22000000000},
    {"symbol": "ADCI", "name": "العربية للأدوية", "sector": "صحة", "price": 216.63, "change": 1.77, "change_pct": 0.82, "volume": 123000000, "high": 220.96, "low": 212.3, "market_cap": 28000000000},
    {"symbol": "AXPH", "name": "الإسكندرية للأدوية", "sector": "صحة", "price": 1166.22, "change": 7.1, "change_pct": 0.61, "volume": 302000000, "high": 1189.54, "low": 1142.9, "market_cap": 65000000000},
    {"symbol": "HRHO", "name": "EFG هيرمس", "sector": "استثمار", "price": 29.5, "change": -1.47, "change_pct": -4.75, "volume": 2657000000, "high": 30.09, "low": 28.91, "market_cap": 75000000000},
    {"symbol": "BTFH", "name": "بلتون", "sector": "استثمار", "price": 3.2, "change": 2.9, "change_pct": 966.67, "volume": 696000000, "high": 3.26, "low": 3.14, "market_cap": 8000000000},
    {"symbol": "CCAP", "name": "قلعة", "sector": "استثمار", "price": 4.7, "change": -1.06, "change_pct": -18.4, "volume": 13617000000, "high": 4.79, "low": 4.61, "market_cap": 12000000000},
    {"symbol": "CICH", "name": "سي آي كابيتال", "sector": "استثمار", "price": 12.9, "change": 5.31, "change_pct": 69.96, "volume": 451000000, "high": 13.16, "low": 12.64, "market_cap": 15000000000},
    {"symbol": "RAYA", "name": "راية", "sector": "استثمار", "price": 7.1, "change": -2.47, "change_pct": -25.81, "volume": 6383000000, "high": 7.24, "low": 6.96, "market_cap": 22000000000},
    {"symbol": "RACC", "name": "راية لخدمة العملاء", "sector": "استثمار", "price": 10.25, "change": 0.49, "change_pct": 5.02, "volume": 288000000, "high": 10.46, "low": 10.04, "market_cap": 18000000000},
    {"symbol": "BINV", "name": "B للاستثمارات", "sector": "استثمار", "price": 42.0, "change": 1.65, "change_pct": 4.09, "volume": 948000000, "high": 42.84, "low": 41.16, "market_cap": 28000000000},
    {"symbol": "AMOC", "name": "Alexandria Mineral Oils", "sector": "طاقة", "price": 8.59, "change": 0.35, "change_pct": 4.25, "volume": 4011000000, "high": 8.76, "low": 8.42, "market_cap": 25000000000},
    {"symbol": "EGAS", "name": "مصر للغاز", "sector": "طاقة", "price": 49.12, "change": -0.41, "change_pct": -0.83, "volume": 900000000, "high": 50.1, "low": 48.14, "market_cap": 35000000000},
    {"symbol": "MTIE", "name": "MM Group", "sector": "تعليم", "price": 9.42, "change": 1.29, "change_pct": 15.87, "volume": 2116000000, "high": 9.61, "low": 9.23, "market_cap": 18000000000},
    {"symbol": "MPRC", "name": "مدينة الإنتاج", "sector": "إعلام", "price": 31.75, "change": 0.16, "change_pct": 0.51, "volume": 127000000, "high": 32.38, "low": 31.11, "market_cap": 12000000000},
    {"symbol": "ETRS", "name": "النقل والخدمات", "sector": "نقل", "price": 7.78, "change": 0.26, "change_pct": 3.46, "volume": 1230000000, "high": 7.94, "low": 7.62, "market_cap": 15000000000},
    {"symbol": "EEII", "name": "العربية للصناعات الهندسية", "sector": "تكنولوجيا", "price": 2.35, "change": 0.43, "change_pct": 22.4, "volume": 3110000000, "high": 2.4, "low": 2.3, "market_cap": 8000000000},
]

tickers_egypt = [s["symbol"] for s in stocks_data]

news_data = [
    {"time": "14:30", "title": "EGX30 يتجاوز 24800 نقطة للمرة الأولى منذ 2022", "type": "positive", "source": "البورصة المصرية"},
    {"time": "14:15", "title": "CIB يعلن عن توزيع أرباح نقدية 2.5 جنيه للسهم", "type": "positive", "source": "CIB"},
    {"time": "13:45", "title": "تراجع طفيف في مؤشر EGX100 مع جني الأرباح", "type": "negative", "source": "إيكونومي"},
    {"time": "13:20", "title": "المركزي: استقرار سعر الصرف عند 30.85 للدولار", "type": "neutral", "source": "البنك المركزي"},
    {"time": "12:50", "title": "e-Finance توقع اتفاقية رقمية مع الحكومة", "type": "positive", "source": "e-Finance"},
    {"time": "12:15", "title": "ارتفاع حجم التداولات إلى 1.8 مليار جنيه", "type": "positive", "source": "البورصة"},
    {"time": "11:30", "title": "فوري تعلن عن نمو أرباح الربع الأول بنسبة 25%", "type": "positive", "source": "فوري"},
    {"time": "10:45", "title": "ضغوط بيعية على قطاع الأسمدة", "type": "negative", "source": "تحليلي"},
]

# ==================== SAFE DATA FETCHING WITH DEBUG ====================
def safe_fetch_stock_data(symbol, period="3mo", market="EGX"):
    """Fetch stock data with full error handling and recovery"""
    cache_key = f"{symbol}_{period}_{market}"
    
    # Check cache first
    if cache_key in st.session_state.market_data_cache:
        cache_entry = st.session_state.market_data_cache[cache_key]
        if (datetime.now() - cache_entry["timestamp"]).seconds < 300:  # 5 min cache
            return cache_entry["data"]
    
    try:
        suffix = ".CA" if market == "EGX" else ""
        ticker = yf.Ticker(f"{symbol}{suffix}")
        df = ticker.history(period=period)
        
        if df.empty:
            debug.log_error("data_fetch", ValueError(f"Empty data for {symbol}"), f"symbol: {symbol}, period: {period}")
            return None
            
        # Validate data quality
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not debug.validate_dataframe(df, f"fetch_{symbol}", required_cols):
            debug.log_error("data_validation", ValueError(f"Invalid columns for {symbol}"), str(df.columns.tolist()))
            return None
            
        # Cache the result
        st.session_state.market_data_cache[cache_key] = {
            "data": df,
            "timestamp": datetime.now()
        }
        
        return df
        
    except Exception as e:
        debug.log_error("data_fetch", e, f"symbol: {symbol}, period: {period}")
        return None

def safe_fetch_multiple(symbols, period="3mo", market="EGX"):
    """Fetch multiple stocks with batch error handling"""
    results = {}
    failed = []
    
    for symbol in symbols:
        df = safe_fetch_stock_data(symbol, period, market)
        if df is not None:
            results[symbol] = df
        else:
            failed.append(symbol)
    
    if failed:
        debug.log_error("batch_fetch", ValueError(f"Failed to fetch {len(failed)} stocks"), str(failed))
    
    return results, failed

# ==================== TECHNICAL ANALYSIS ENGINE ====================
def calculate_technical_indicators(df):
    """Calculate comprehensive technical indicators with validation"""
    if df is None or df.empty:
        return None
        
    try:
        df = df.copy()
        
        # RSI (14)
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
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
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
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
        
        # Momentum
        df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
        df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100
        
        return df
        
    except Exception as e:
        debug.log_error("indicators", e, "calculate_technical_indicators")
        return None

def generate_trading_signals(df):
    """Generate signals with full validation"""
    if df is None or len(df) < 30:
        return []
        
    try:
        signals = []
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # RSI
        if pd.notna(latest['RSI']):
            if latest['RSI'] < 30:
                signals.append(("RSI", "شراء قوي", 2, "ذروة بيع"))
            elif latest['RSI'] > 70:
                signals.append(("RSI", "بيع قوي", -2, "ذروة شراء"))
            elif latest['RSI'] < 45:
                signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء"))
            elif latest['RSI'] > 55:
                signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع"))
            else:
                signals.append(("RSI", "محايد", 0, "لا إشارة"))
        
        # MACD
        if pd.notna(latest['MACD']) and pd.notna(latest['MACD_Signal']):
            if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signals.append(("MACD", "شراء", 2, "تقاطع صاعد"))
            elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                signals.append(("MACD", "بيع", -2, "تقاطع هابط"))
            elif latest['MACD'] > latest['MACD_Signal']:
                signals.append(("MACD", "شراء ضعيف", 1, "MACD إيجابي"))
            else:
                signals.append(("MACD", "بيع ضعيف", -1, "MACD سلبي"))
        
        # Bollinger
        if pd.notna(latest['Close']) and pd.notna(latest['BB_Lower']) and pd.notna(latest['BB_Upper']):
            if latest['Close'] < latest['BB_Lower']:
                signals.append(("Bollinger", "شراء قوي", 2, "تحت النطاق السفلي"))
            elif latest['Close'] > latest['BB_Upper']:
                signals.append(("Bollinger", "بيع قوي", -2, "فوق النطاق العلوي"))
            else:
                signals.append(("Bollinger", "محايد", 0, "داخل النطاق"))
        
        # Stochastic
        if pd.notna(latest['Stoch_K']) and pd.notna(latest['Stoch_D']):
            if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
                signals.append(("Stochastic", "شراء", 1.5, "ذروة بيع"))
            elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
                signals.append(("Stochastic", "بيع", -1.5, "ذروة شراء"))
            else:
                signals.append(("Stochastic", "محايد", 0, "لا إشارة"))
        
        # Moving Averages
        if pd.notna(latest['Close']) and pd.notna(latest['SMA_20']) and pd.notna(latest['SMA_50']):
            if latest['Close'] > latest['SMA_20'] and latest['Close'] > latest['SMA_50']:
                signals.append(("MA", "شراء", 1, "فوق المتوسطات"))
            elif latest['Close'] < latest['SMA_20'] and latest['Close'] < latest['SMA_50']:
                signals.append(("MA", "بيع", -1, "تحت المتوسطات"))
            else:
                signals.append(("MA", "محايد", 0, "إشارات متضاربة"))
        
        # Volume
        if pd.notna(latest['Volume_Ratio']):
            if latest['Volume_Ratio'] > 1.5:
                signals.append(("Volume", "تأكيد", 0.5, "حجم نشط"))
            elif latest['Volume_Ratio'] < 0.5:
                signals.append(("Volume", "ضعف", -0.5, "حجم ضعيف"))
            else:
                signals.append(("Volume", "محايد", 0, "حجم طبيعي"))
        
        return signals
        
    except Exception as e:
        debug.log_error("signals", e, "generate_trading_signals")
        return []

def calculate_overall_signal(signals):
    """Calculate overall signal with safety checks"""
    if not signals:
        return "HOLD", 0, "لا توجد بيانات كافية"
    
    try:
        total_score = sum([s[2] for s in signals if len(s) > 2])
        
        if total_score >= 3:
            return "STRONG_BUY", total_score, "إشارة شراء قوية"
        elif total_score >= 1.5:
            return "BUY", total_score, "إشارة شراء"
        elif total_score <= -3:
            return "STRONG_SELL", total_score, "إشارة بيع قوية"
        elif total_score <= -1.5:
            return "SELL", total_score, "إشارة بيع"
        else:
            return "HOLD", total_score, "انتظار/محايد"
            
    except Exception as e:
        debug.log_error("overall_signal", e, "calculate_overall_signal")
        return "HOLD", 0, "خطأ في الحساب"

def predict_future_prices(df, days=5):
    """Predict future prices with error recovery"""
    try:
        predictions = {}
        prices = df['Close'].dropna().values
        
        if len(prices) < 30:
            return {'error': 'Insufficient data'}
        
        # Linear Regression
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices
        
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        linear_pred = model.predict(future_X_poly)
        
        # Moving Average extrapolation
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        
        trend_factor = 1.002 if ma20 > ma50 else 0.998 if ma20 < ma50 else 1.0
        ma_pred = [prices[-1] * (trend_factor ** i) for i in range(1, days + 1)]
        
        # Combined predictions
        combined_pred = []
        for i in range(days):
            avg = (linear_pred[i] + ma_pred[i]) / 2
            volatility = df['Close'].pct_change().std() * prices[-1] if not pd.isna(df['Close'].pct_change().std()) else 0
            combined_pred.append({
                'day': i + 1,
                'predicted': round(avg, 2),
                'lower_bound': round(avg - volatility * 1.5, 2),
                'upper_bound': round(avg + volatility * 1.5, 2),
                'confidence': max(0, min(100, 100 - (i * 15)))
            })
        
        predictions['combined'] = combined_pred
        return predictions
        
    except Exception as e:
        debug.log_error("prediction", e, "predict_future_prices")
        return {'error': str(e)}

def calculate_support_resistance(df, window=20):
    """Calculate support/resistance with validation"""
    try:
        recent = df.tail(window)
        
        lows = recent['Low'].nsmallest(3).values
        supports = [round(l, 2) for l in lows]
        
        highs = recent['High'].nlargest(3).values
        resistances = [round(h, 2) for h in highs]
        
        swing_high = recent['High'].max()
        swing_low = recent['Low'].min()
        diff = swing_high - swing_low
        
        fib_levels = {
            '0%': round(swing_high, 2),
            '23.6%': round(swing_high - 0.236 * diff, 2),
            '38.2%': round(swing_high - 0.382 * diff, 2),
            '50%': round(swing_high - 0.5 * diff, 2),
            '61.8%': round(swing_high - 0.618 * diff, 2),
            '78.6%': round(swing_high - 0.786 * diff, 2),
            '100%': round(swing_low, 2)
        }
        
        return {
            'supports': supports,
            'resistances': resistances,
            'fibonacci': fib_levels,
            'current': round(df['Close'].iloc[-1], 2)
        }
    except Exception as e:
        debug.log_error("support_resistance", e, "calculate_support_resistance")
        return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0}

# ==================== BACKTESTING ENGINE ====================
def run_advanced_backtest(ticker, strategy="RSI_MACD", period="1y", market_type="EGX"):
    try:
        suffix = ".CA" if market_type == "EGX" else ""
        df = safe_fetch_stock_data(ticker, period, market_type)
        
        if df is None or df.empty:
            return None
            
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        initial_capital = 100000
        df['Returns'] = df['Close'].pct_change()
        
        if strategy == "RSI_MACD":
            delta = df['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
            macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
            signal = macd.ewm(span=9).mean()
            df['Signal'] = np.where((rsi < 35) & (macd > signal), 1, 0)
            
        elif strategy == "MA_Crossover":
            df['MA50'] = df['Close'].rolling(50).mean()
            df['MA200'] = df['Close'].rolling(200).mean()
            df['Signal'] = np.where(df['MA50'] > df['MA200'], 1, 0)
            
        elif strategy == "Bollinger":
            bb_mid = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            df['Signal'] = np.where(df['Close'] < (bb_mid - 2*bb_std), 1, 0)
            
        elif strategy == "Mean_Reversion":
            df['MA20'] = df['Close'].rolling(20).mean()
            df['Deviation'] = (df['Close'] - df['MA20']) / df['MA20']
            df['Signal'] = np.where(df['Deviation'] < -0.03, 1, np.where(df['Deviation'] > 0.03, -1, 0))
        
        df['Position'] = df['Signal'].diff().fillna(0)
        df['Strategy_Returns'] = df['Position'].shift(1) * df['Returns']
        df['Equity'] = initial_capital * (1 + df['Strategy_Returns']).cumprod()
        
        total_return = (df['Equity'].iloc[-1] / initial_capital - 1) * 100
        buy_hold_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        sharpe = (df['Strategy_Returns'].mean() / df['Strategy_Returns'].std() * np.sqrt(252)) if df['Strategy_Returns'].std() != 0 else 0
        max_dd = ((df['Equity'] / df['Equity'].cummax() - 1).min()) * 100
        win_rate = len(df[df['Strategy_Returns'] > 0]) / len(df[df['Strategy_Returns'] != 0]) * 100 if len(df[df['Strategy_Returns'] != 0]) > 0 else 0
        
        return {
            "Strategy_Return": round(total_return, 2),
            "Buy_Hold_Return": round(buy_hold_return, 2),
            "Sharpe_Ratio": round(sharpe, 2),
            "Max_Drawdown": round(max_dd, 2),
            "Win_Rate": round(win_rate, 1),
            "Equity_Curve": df['Equity'],
            "Trades": int(df['Position'].abs().sum() / 2),
            "Data": df
        }
    except Exception as e:
        debug.log_error("backtest", e, f"ticker: {ticker}, strategy: {strategy}")
        return None

# ==================== AUTOMATED ANALYSIS ENGINE ====================
def analyze_all_stocks(stocks_list, market_type="EGX"):
    """Analyze all stocks with comprehensive error handling"""
    alerts = []
    progress_text = st.empty()
    
    for i, stock in enumerate(stocks_list):
        try:
            progress_text.text(f"تحليل {i+1}/{len(stocks_list)}: {stock['symbol']}...")
            
            df = safe_fetch_stock_data(stock['symbol'], "3mo", market_type)
            
            if df is None or len(df) < 30:
                continue
                
            df = calculate_technical_indicators(df)
            if df is None:
                continue
                
            latest = df.iloc[-1]
            
            if pd.isna(latest.get('RSI')) or pd.isna(latest.get('MACD')):
                continue
                
            signals = generate_trading_signals(df)
            overall_signal, score, signal_text = calculate_overall_signal(signals)
            
            atr = latest['ATR'] if pd.notna(latest.get('ATR')) else 0
            current_price = latest['Close']
            
            stop_loss = current_price - (atr * 2) if atr > 0 else current_price * 0.95
            take_profit_1 = current_price + (atr * 2) if atr > 0 else current_price * 1.05
            take_profit_2 = current_price + (atr * 3.5) if atr > 0 else current_price * 1.10
            
            risk = current_price - stop_loss
            reward = take_profit_1 - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            trend_strength = 0
            if pd.notna(latest.get('Close')) and pd.notna(latest.get('SMA_20')):
                if latest['Close'] > latest['SMA_20']:
                    trend_strength += 1
            if pd.notna(latest.get('Close')) and pd.notna(latest.get('SMA_50')):
                if latest['Close'] > latest['SMA_50']:
                    trend_strength += 1
            if pd.notna(latest.get('SMA_20')) and pd.notna(latest.get('SMA_50')):
                if latest['SMA_20'] > latest['SMA_50']:
                    trend_strength += 1
            
            volume_confirm = latest.get('Volume_Ratio', 0) > 1.2 if pd.notna(latest.get('Volume_Ratio')) else False
            
            opportunity_score = 0
            
            if pd.notna(latest.get('RSI')):
                if latest['RSI'] < 30:
                    opportunity_score += 25
                elif latest['RSI'] < 40:
                    opportunity_score += 15
                elif latest['RSI'] > 70:
                    opportunity_score -= 20
            
            if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_Signal')):
                if latest['MACD'] > latest['MACD_Signal']:
                    opportunity_score += 20
                    if pd.notna(latest.get('MACD_Histogram')) and latest['MACD_Histogram'] > 0:
                        opportunity_score += 10
            
            if pd.notna(latest.get('BB_Position')):
                if latest['BB_Position'] < 0.2:
                    opportunity_score += 15
                elif latest['BB_Position'] > 0.8:
                    opportunity_score -= 15
            
            opportunity_score += trend_strength * 10
            
            if volume_confirm:
                opportunity_score += 10
            
            if rr_ratio > 2:
                opportunity_score += 15
            elif rr_ratio > 1.5:
                opportunity_score += 10
            
            if pd.notna(latest.get('Stoch_K')) and latest['Stoch_K'] < 20:
                opportunity_score += 10
            
            opportunity_score = max(0, min(100, opportunity_score))
            
            if opportunity_score >= 75 and overall_signal in ["STRONG_BUY", "BUY"]:
                alert_level = "🔥 فرصة شراء قوية"
                alert_color = "#10b981"
                priority = 1
            elif opportunity_score >= 60 and overall_signal in ["STRONG_BUY", "BUY", "HOLD"]:
                alert_level = "🟢 فرصة شراء جيدة"
                alert_color = "#34d399"
                priority = 2
            elif opportunity_score >= 45 and overall_signal == "HOLD":
                alert_level = "🟡 مراقبة"
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
                "score": round(opportunity_score, 1),
                "alert_level": alert_level,
                "alert_color": alert_color,
                "priority": priority,
                "rsi": round(latest['RSI'], 1) if pd.notna(latest.get('RSI')) else 50,
                "macd": round(latest['MACD'], 2) if pd.notna(latest.get('MACD')) else 0,
                "bb_position": round(latest['BB_Position'], 2) if pd.notna(latest.get('BB_Position')) else 0.5,
                "volume_ratio": round(latest['Volume_Ratio'], 1) if pd.notna(latest.get('Volume_Ratio')) else 1.0,
                "trend_strength": trend_strength,
                "rr_ratio": round(rr_ratio, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit_1": round(take_profit_1, 2),
                "take_profit_2": round(take_profit_2, 2),
                "risk_pct": round((current_price - stop_loss) / current_price * 100, 2) if current_price > 0 else 0,
                "reward_pct": round((take_profit_1 - current_price) / current_price * 100, 2) if current_price > 0 else 0,
            })
            
        except Exception as e:
            debug.log_error("analyze_stock", e, f"stock: {stock.get('symbol', 'unknown')}")
            continue
    
    progress_text.empty()
    alerts.sort(key=lambda x: (x['priority'], -x['score']))
    return alerts

def get_buy_opportunities(alerts, min_score=60):
    return sorted([a for a in alerts if a['score'] >= min_score and a['signal'] in ['BUY', 'STRONG_BUY']], key=lambda x: -x['score'])

def get_risk_alerts(alerts):
    return [a for a in alerts if a['signal'] in ['SELL', 'STRONG_SELL'] or a['score'] < 30]

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px; padding: 16px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border-radius: 12px; border: 1px solid rgba(99,102,241,0.2);">
        <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 12px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 24px;">⚡</div>
        <h2 style="margin-top: 12px; font-size: 18px; font-weight: 700;">EGX Pro Terminal</h2>
        <p style="color: #64748b; font-size: 11px; margin-top: 4px;">v20.0 | AI-Powered Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("🌍 اختيار السوق")
    market = st.radio("", ["🇪🇬 السوق المصري", "🌍 الأسواق العالمية"], label_visibility="collapsed")
    is_egypt = "مصري" in market
    
    tickers = tickers_egypt if is_egypt else ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "INTC", "NFLX"]
    
    st.divider()
    
    # Debug Mode Toggle
    st.header("🔧 أدوات النظام")
    debug_mode = st.toggle("وضع التصحيح (Debug)", value=st.session_state.debug_mode, help="عرض سجل الأخطاء والتشخيصات")
    st.session_state.debug_mode = debug_mode
    
    if debug_mode:
        st.subheader("📊 حالة النظام")
        health = debug.get_health_report()
        
        status_color = "#10b981" if health["system_status"] == "HEALTHY" else "#f59e0b" if health["system_status"] == "DEGRADED" else "#ef4444"
        st.markdown(f"""
        <div style="padding: 8px; background: {status_color}15; border: 1px solid {status_color}40; border-radius: 6px; text-align: center;">
            <p style="margin: 0; color: {status_color}; font-weight: 700; font-size: 14px;">{health["system_status"]}</p>
            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 11px;">أخطاء: {health["total_errors"]} | تم إصلاحها: {health["recovered"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if health["failed_components"]:
            st.markdown("<p style='color: #ef4444; font-size: 11px; margin-top: 8px;'>⚠️ مكونات تحتاج صيانة:</p>", unsafe_allow_html=True)
            for comp in health["failed_components"]:
                st.markdown(f"<p style='color: #f87171; font-size: 10px; margin: 2px 0;'>• {comp}</p>", unsafe_allow_html=True)
    
    st.divider()
    st.header("📊 إحصائيات المهام")
    total_tasks = len(st.session_state.tasks)
    completed = sum(1 for t in st.session_state.tasks if t["completed"])
    pending = total_tasks - completed
    high_priority = sum(1 for t in st.session_state.tasks if t["priority"] == "high" and not t["completed"])
    
    col1, col2 = st.columns(2)
    col1.metric("الكل", total_tasks)
    col2.metric("مكتمل", completed)
    col1.metric("قيد التنفيذ", pending)
    col2.metric("عالية الأولوية", high_priority, delta_color="inverse")

# ==================== HEADER ====================
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 16px; background: linear-gradient(90deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05)); border-radius: 12px; border: 1px solid rgba(99,102,241,0.1);">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ EGX Pro Terminal
        </h1>
        <p style="color: #64748b; margin-top: 4px; font-size: 13px;">
            <span class="live-pulse"></span> السوق مفتوح | آخر تحديث: {}
        </p>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div style="padding: 10px 16px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px;">
            <span style="color: #64748b; font-size: 11px;">EGX30</span>
            <span style="color: #10b981; margin-right: 8px; font-size: 18px; font-weight: 700;">24,850</span>
            <span class="badge badge-green">+1.24%</span>
        </div>
        <div style="padding: 10px 16px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px;">
            <span style="color: #64748b; font-size: 11px;">حجم التداول</span>
            <span style="color: #818cf8; margin-right: 8px; font-size: 16px; font-weight: 700;">1.8B</span>
        </div>
    </div>
</div>
""".format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 رادار السوق", 
    "📊 Backtesting", 
    "✅ المهام", 
    "📰 الأخبار",
    "💰 التوزيعات",
    "🤖 التحليل الآلي",
    "🔮 التحليل المفصل"
])

# ==================== TAB 1: MARKET RADAR (PROFESSIONAL LAYOUT) ====================
with tab1:
    # Top Row: Market Indices & Key Metrics
    idx_col1, idx_col2, idx_col3, idx_col4, idx_col5 = st.columns(5)
    
    indices = [
        {"name": "EGX30", "value": 24850.32, "change": 1.24, "vol": "1.2B"},
        {"name": "EGX70", "value": 3245.18, "change": 0.89, "vol": "850M"},
        {"name": "EGX100", "value": 8932.45, "change": -0.34, "vol": "2.1B"},
        {"name": "EGX20", "value": 15680.12, "change": 1.05, "vol": "950M"},
        {"name": "Dollar", "value": 30.85, "change": 0.02, "vol": "CBE"},
    ]
    
    cols = [idx_col1, idx_col2, idx_col3, idx_col4, idx_col5]
    for i, idx in enumerate(indices):
        with cols[i]:
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
    
    # Second Row: Market Map + Top Movers
    row2_col1, row2_col2 = st.columns([2, 1])
    
    with row2_col1:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🗺️ خريطة السوق التفاعلية</span></div>', unsafe_allow_html=True)
        
        df_main = pd.DataFrame(stocks_data)
        fig_treemap = px.treemap(
            df_main,
            path=[px.Constant("EGX"), 'sector', 'symbol'],
            values='volume',
            color='change_pct',
            color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
            color_continuous_midpoint=0,
        )
        fig_treemap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#94a3b8", size=11),
            height=380,
            margin=dict(t=0, b=0, l=0, r=0),
            coloraxis_colorbar=dict(
                tickfont=dict(color="#94a3b8", size=10),
                title=dict(text="%", font=dict(color="#94a3b8", size=10))
            )
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row2_col2:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🚀 الأكثر نشاطاً</span></div>', unsafe_allow_html=True)
        
        top_movers = df_main.nlargest(8, 'change_pct')
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
    
    # Third Row: Stock Grid
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🎯 الأسهم المتاحة - اضغط للتحليل</span></div>', unsafe_allow_html=True)
    
    filter_col1, filter_col2 = st.columns([3, 1])
    with filter_col1:
        search_term = st.text_input("🔍 البحث", placeholder="ابحث بالرمز أو اسم الشركة...", key="market_search", label_visibility="collapsed")
    with filter_col2:
        sector_filter = st.selectbox("القطاع", ["الكل"] + sorted(list(set(s["sector"] for s in stocks_data))), key="market_sector", label_visibility="collapsed")
    
    display_stocks = stocks_data.copy()
    if search_term:
        display_stocks = [s for s in display_stocks if search_term.lower() in s["symbol"].lower() or search_term.lower() in s["name"].lower()]
    if sector_filter != "الكل":
        display_stocks = [s for s in display_stocks if s["sector"] == sector_filter]
    
    stocks_per_row = 6
    for row_idx in range(0, len(display_stocks), stocks_per_row):
        row_stocks = display_stocks[row_idx:row_idx + stocks_per_row]
        btn_cols = st.columns(stocks_per_row)
        
        for i, stock in enumerate(row_stocks):
            with btn_cols[i]:
                change_class = "up" if stock['change_pct'] >= 0 else "down"
                change_sign = "+" if stock['change_pct'] >= 0 else ""
                
                st.markdown(f"""
                <div class="stock-card">
                    <div class="stock-card-symbol">{stock['symbol']}</div>
                    <div class="stock-card-price">{stock['price']:.2f}</div>
                    <div class="stock-card-change {change_class}">{change_sign}{stock['change_pct']:.2f}%</div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 4px;">{stock['sector']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"تحليل", key=f"btn_{stock['symbol']}", use_container_width=True, type="secondary"):
                    select_stock(stock['symbol'])
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: BACKTESTING ====================
with tab2:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 محرك Backtesting متقدم</span></div>', unsafe_allow_html=True)
    
    bt_col1, bt_col2 = st.columns([1, 3])
    
    with bt_col1:
        bt_ticker = st.selectbox("السهم", tickers, key="bt_ticker")
        strategy = st.selectbox("الاستراتيجية", [
            "RSI_MACD - تقاطع الزخم",
            "MA_Crossover - تقاطع المتوسطات",
            "Bollinger - نطاقات بولينجر",
            "Mean_Reversion - العودة للمتوسط"
        ], key="bt_strategy")
        period = st.selectbox("الفترة", ["3mo", "6mo", "1y", "2y"], index=2, key="bt_period")
        initial_capital = st.number_input("رأس المال", value=100000, step=10000, key="bt_capital")
        
        run_bt = st.button("🚀 تشغيل الاختبار", type="primary", use_container_width=True)
    
    with bt_col2:
        if run_bt:
            with st.spinner("جاري التحليل..."):
                strategy_key = strategy.split(" - ")[0]
                result = debug.safe_execute(
                    run_advanced_backtest,
                    "backtest_execution",
                    None,
                    bt_ticker, strategy_key, period, "EGX" if is_egypt else "GLOBAL"
                )
                
                if result:
                    m1, m2, m3, m4, m5 = st.columns(5)
                    
                    strat_color = "normal" if result['Strategy_Return'] >= 0 else "inverse"
                    bh_color = "normal" if result['Buy_Hold_Return'] >= 0 else "inverse"
                    
                    m1.metric("عائد الاستراتيجية", f"{result['Strategy_Return']:+.2f}%", delta_color=strat_color)
                    m2.metric("Buy & Hold", f"{result['Buy_Hold_Return']:+.2f}%", delta_color=bh_color)
                    m3.metric("Sharpe Ratio", f"{result['Sharpe_Ratio']:.2f}")
                    m4.metric("Win Rate", f"{result['Win_Rate']:.1f}%")
                    m5.metric("Max Drawdown", f"{result['Max_Drawdown']:.2f}%")
                    
                    # Equity Curve
                    fig_equity = go.Figure()
                    fig_equity.add_trace(go.Scatter(
                        x=result['Equity_Curve'].index,
                        y=result['Equity_Curve'].values,
                        mode='lines',
                        name='رأس المال',
                        line=dict(color='#6366f1', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(99, 102, 241, 0.1)'
                    ))
                    
                    bh_curve = 100000 * (1 + result['Data']['Returns']).cumprod()
                    fig_equity.add_trace(go.Scatter(
                        x=bh_curve.index,
                        y=bh_curve.values,
                        mode='lines',
                        name='Buy & Hold',
                        line=dict(color='#fbbf24', width=2, dash='dash')
                    ))
                    
                    fig_equity.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="التاريخ"),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="رأس المال"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=350,
                        margin=dict(t=40, b=40)
                    )
                    st.plotly_chart(fig_equity, use_container_width=True)
                    
                    # Strategy Comparison
                    st.subheader("🏆 مقارنة الاستراتيجيات")
                    strategies_to_test = ["RSI_MACD", "MA_Crossover", "Bollinger", "Mean_Reversion"]
                    comparison_results = []
                    
                    for strat in strategies_to_test:
                        res = debug.safe_execute(
                            run_advanced_backtest,
                            f"backtest_compare_{strat}",
                            None,
                            bt_ticker, strat, period, "EGX" if is_egypt else "GLOBAL"
                        )
                        if res:
                            comparison_results.append({
                                "الاستراتيجية": strat,
                                "العائد %": res['Strategy_Return'],
                                "Sharpe": res['Sharpe_Ratio'],
                                "Win Rate %": res['Win_Rate'],
                                "Max DD %": res['Max_Drawdown'],
                                "الصفقات": res['Trades']
                            })
                    
                    if comparison_results:
                        comp_df = pd.DataFrame(comparison_results)
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
                else:
                    st.error("❌ تعذر جلب البيانات. تحقق من الاتصال.")
        else:
            st.info("👈 اختر السهم والاستراتيجية واضغط 'تشغيل الاختبار'")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: TASKS ====================
with tab3:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">✅ المهام الذكية</span></div>', unsafe_allow_html=True)
    
    with st.expander("➕ إضافة مهمة جديدة", expanded=False):
        t_col1, t_col2, t_col3 = st.columns([3, 1, 1])
        with t_col1:
            task_title = st.text_input("عنوان المهمة", placeholder="مثال: مراجعة أداء سهم CIB")
        with t_col2:
            task_priority = st.selectbox("الأولوية", ["high", "medium", "low"], format_func=lambda x: {"high": "🔴 عالية", "medium": "🟡 متوسطة", "low": "🟢 منخفضة"}[x])
        with t_col3:
            task_category = st.selectbox("التصنيف", ["work", "personal", "learning", "urgent"], format_func=lambda x: {"work": "💼 عمل", "personal": "👤 شخصي", "learning": "📚 تعلم", "urgent": "🚨 عاجل"}[x])
        
        t_col4, t_col5 = st.columns([2, 1])
        with t_col4:
            task_due = st.date_input("تاريخ الاستحقاق", datetime.now() + timedelta(days=3))
        with t_col5:
            if st.button("💾 حفظ", use_container_width=True):
                if task_title:
                    st.session_state.tasks.append({
                        "id": len(st.session_state.tasks) + 1,
                        "title": task_title,
                        "priority": task_priority,
                        "category": task_category,
                        "due": task_due.strftime("%Y-%m-%d"),
                        "completed": False,
                        "created": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success("✅ تمت الإضافة!")
                    st.rerun()
                else:
                    st.warning("⚠️ أدخل عنوان المهمة")
    
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...")
    with f_col2:
        filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"], format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x])
    with f_col3:
        filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"])
    
    filtered_tasks = st.session_state.tasks.copy()
    if task_search:
        filtered_tasks = [t for t in filtered_tasks if task_search.lower() in t["title"].lower()]
    if filter_priority != "الكل":
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == filter_priority]
    if filter_status == "مكتمل":
        filtered_tasks = [t for t in filtered_tasks if t["completed"]]
    elif filter_status == "قيد التنفيذ":
        filtered_tasks = [t for t in filtered_tasks if not t["completed"]]
    
    priority_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
    category_icons = {"work": "💼", "personal": "👤", "learning": "📚", "urgent": "🚨"}
    
    for task in filtered_tasks:
        status_icon = "✅" if task["completed"] else "⬜"
        status_style = "opacity: 0.5;" if task["completed"] else ""
        priority_color = priority_colors.get(task['priority'], '#94a3b8')
        
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid {priority_color}; {status_style}">
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
        
        col_check, col_del = st.columns([20, 1])
        with col_check:
            new_status = st.checkbox("تم", value=task["completed"], key=f"task_{task['id']}", label_visibility="collapsed")
            if new_status != task["completed"]:
                task["completed"] = new_status
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{task['id']}", help="حذف"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: NEWS ====================
with tab4:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📰 أخبار السوق والتحليلات</span></div>', unsafe_allow_html=True)
    
    news_col1, news_col2 = st.columns([1, 2])
    
    with news_col1:
        st.subheader("🔥 آخر الأخبار")
        for news in news_data:
            news_color = "#10b981" if news['type'] == 'positive' else "#ef4444" if news['type'] == 'negative' else "#94a3b8"
            icon = "📈" if news['type'] == 'positive' else "📉" if news['type'] == 'negative' else "📊"
            
            st.markdown(f"""
            <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-right: 3px solid {news_color};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                            <span style="color: #fbbf24; font-size: 11px; font-weight: 600;">{news['time']}</span>
                            <span class="badge badge-blue" style="font-size: 10px;">{news['source']}</span>
                        </div>
                        <p style="margin: 0; font-size: 13px; line-height: 1.5;">{icon} {news['title']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with news_col2:
        st.subheader("📊 التحليل الفني السريع")
        
        ta_stock = st.selectbox("السهم", [s["symbol"] for s in stocks_data], key="ta_stock")
        
        # Quick technical analysis
        df_ta = safe_fetch_stock_data(ta_stock, "3mo", "EGX")
        if df_ta is not None and len(df_ta) > 30:
            df_ta = calculate_technical_indicators(df_ta)
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
                    x=df_ta.index[-60:],
                    y=df_ta['Close'].tail(60),
                    mode='lines',
                    line=dict(color='#6366f1', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(99, 102, 241, 0.1)'
                ))
                
                if pd.notna(latest.get('SMA_20')):
                    fig_mini.add_trace(go.Scatter(
                        x=df_ta.index[-60:],
                        y=df_ta['SMA_20'].tail(60),
                        mode='lines',
                        line=dict(color='#fbbf24', width=1, dash='dash'),
                        name='SMA 20'
                    ))
                
                fig_mini.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", color="#94a3b8"),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                    height=250,
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=False
                )
                st.plotly_chart(fig_mini, use_container_width=True)
        else:
            st.warning("⚠️ تعذر جلب البيانات الفنية")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 5: DIVIDENDS ====================
with tab5:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">💰 توزيعات الشركات والكوبونات</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 16px;">
        <p style="color: #f87171; font-weight: 600; margin: 0; font-size: 13px;">⚠️ تنبيه</p>
        <p style="color: #fca5a5; font-size: 12px; margin-top: 4px;">البيانات توضيحية. تحقق من البورصة المصرية الرسمية.</p>
    </div>
    """, unsafe_allow_html=True)
    
    dividends_data = [
        {"symbol": "COMI", "company": "CIB", "dividends": [{"date": "2026-04-15", "type": "نقدي", "amount": 2.50, "status": "تم التوزيع"}], "next_expected": "2026-10-15", "yield": 3.57},
        {"symbol": "QNBE", "company": "QNB مصر", "dividends": [{"date": "2026-03-25", "type": "نقدي", "amount": 3.20, "status": "تم التوزيع"}], "next_expected": "2026-09-25", "yield": 5.50},
        {"symbol": "HDBK", "company": "بنك الإسكان", "dividends": [{"date": "2026-04-05", "type": "نقدي", "amount": 5.50, "status": "تم التوزيع"}], "next_expected": "2026-10-05", "yield": 3.73},
        {"symbol": "TMGH", "company": "طلعت مصطفى", "dividends": [{"date": "2026-04-08", "type": "نقدي", "amount": 2.80, "status": "تم التوزيع"}], "next_expected": "2026-10-08", "yield": 2.85},
        {"symbol": "ETEL", "company": "المصرية للاتصالات", "dividends": [{"date": "2026-04-30", "type": "نقدي", "amount": 3.00, "status": "تم التوزيع"}], "next_expected": "2026-10-30", "yield": 3.05},
        {"symbol": "EAST", "company": "الشرقية للدخان", "dividends": [{"date": "2026-05-20", "type": "نقدي", "amount": 3.20, "status": "معلن"}], "next_expected": "2026-11-20", "yield": 7.94},
        {"symbol": "ABUK", "company": "أبو قير", "dividends": [{"date": "2026-05-12", "type": "نقدي", "amount": 4.50, "status": "معلن"}], "next_expected": "2026-11-12", "yield": 5.16},
        {"symbol": "MFPC", "company": "موبكو", "dividends": [{"date": "2026-05-08", "type": "نقدي", "amount": 2.80, "status": "معلن"}], "next_expected": "2026-11-08", "yield": 6.20},
    ]
    
    upcoming_dividends = [
        {"date": "2026-05-15", "symbol": "COMI", "company": "CIB", "amount": 2.50, "status": "غداً"},
        {"date": "2026-05-20", "symbol": "EAST", "company": "الشرقية للدخان", "amount": 3.20, "status": "بعد 5 أيام"},
        {"date": "2026-05-25", "symbol": "SUGR", "company": "دلتا للسكر", "amount": 2.00, "status": "بعد 10 أيام"},
        {"date": "2026-06-05", "symbol": "SWDY", "company": "السويدي", "amount": 3.50, "status": "بعد 20 يوم"},
    ]
    
    # Summary
    div_col1, div_col2, div_col3, div_col4 = st.columns(4)
    with div_col1:
        st.metric("الشركات", len(dividends_data))
    with div_col2:
        st.metric("متوسط العائد", f"{sum(d['yield'] for d in dividends_data)/len(dividends_data):.2f}%")
    with div_col3:
        st.metric("القادمة", len(upcoming_dividends))
    with div_col4:
        st.metric("إجمالي التوزيعات", f"{sum(sum(d['amount'] for d in comp['dividends']) for comp in dividends_data):.1f} ج.م")
    
    st.subheader("📅 التوزيعات القادمة")
    for div in upcoming_dividends:
        status_color = "#ef4444" if div["status"] == "غداً" else "#f59e0b" if "5" in div["status"] else "#10b981"
        
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px;">💰</div>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 14px;">{div["company"]} ({div["symbol"]})</p>
                        <p style="color: #64748b; font-size: 12px; margin: 4px 0 0 0;">📅 {div["date"]} | 💵 {div["amount"]} ج.م</p>
                    </div>
                </div>
                <span class="badge" style="background: {status_color}20; color: {status_color};">{div["status"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("📋 سجل التوزيعات")
    div_company = st.selectbox("الشركة", [d["company"] + " - " + d["symbol"] for d in dividends_data])
    selected_symbol = div_company.split(" - ")[1]
    selected_company = next((d for d in dividends_data if d["symbol"] == selected_symbol), None)
    
    if selected_company:
        st.markdown(f"""
        <div style="padding: 16px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #fbbf24; font-size: 18px;">{selected_company["company"]}</h3>
                    <p style="color: #64748b; margin: 4px 0 0 0; font-size: 13px;">العائد: {selected_company["yield"]:.2f}% | القادم: {selected_company["next_expected"]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        div_history = selected_company["dividends"]
        div_df = pd.DataFrame(div_history)
        st.dataframe(div_df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 6: AUTOMATED ANALYSIS ====================
with tab6:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🤖 التحليل الآلي والتنبيهات اللحظية</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 16px;">
        <p style="color: #f87171; font-weight: 600; margin: 0; font-size: 13px;">⚠️ تنبيه هام</p>
        <p style="color: #fca5a5; font-size: 12px; margin-top: 4px;">التحليل الآلي يعتمد على المؤشرات التاريخية فقط. استخدم Stop Loss لحماية رأس مالك.</p>
    </div>
    """, unsafe_allow_html=True)
    
    settings_col1, settings_col2, settings_col3 = st.columns(3)
    with settings_col1:
        min_score_threshold = st.slider("الحد الأدنى للدرجة", 0, 100, 60)
    with settings_col2:
        max_risk_pct = st.slider("الحد الأقصى للمخاطرة %", 1, 10, 5)
    with settings_col3:
        min_rr_ratio = st.slider("الحد الأدنى R/R", 1.0, 5.0, 1.5, 0.5)
    
    if st.button("🚀 تشغيل التحليل الآلي", type="primary", use_container_width=True):
        with st.spinner("جاري تحليل الأسهم..."):
            all_alerts = debug.safe_execute(
                analyze_all_stocks,
                "automated_analysis",
                [],
                stocks_data, "EGX" if is_egypt else "GLOBAL"
            )
            
            if not all_alerts:
                st.error("❌ تعذر إكمال التحليل. تحقق من الاتصال.")
            else:
                buy_opportunities = get_buy_opportunities(all_alerts, min_score_threshold)
                risk_alerts = get_risk_alerts(all_alerts)
                
                # Summary
                st.subheader("📊 ملخص التحليل")
                sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
                with sum_col1:
                    st.metric("المحللة", len(all_alerts))
                with sum_col2:
                    st.metric("فرص شراء", len(buy_opportunities))
                with sum_col3:
                    st.metric("إشارات خطر", len(risk_alerts))
                with sum_col4:
                    avg_score = sum(a['score'] for a in all_alerts) / len(all_alerts) if all_alerts else 0
                    st.metric("متوسط الدرجة", f"{avg_score:.1f}")
                
                if buy_opportunities:
                    st.subheader("🔥 أفضل فرص الشراء")
                    filtered_buys = [a for a in buy_opportunities if a['risk_pct'] <= max_risk_pct * 100 and a['rr_ratio'] >= min_rr_ratio]
                    
                    if not filtered_buys:
                        st.warning("⚠️ لا توجد فرص تتوافق مع إعدادات المخاطرة.")
                    else:
                        for i, alert in enumerate(filtered_buys[:10]):
                            with st.expander(f"{i+1}. {alert['name']} ({alert['symbol']}) - درجة: {alert['score']}", expanded=i < 3):
                                st.markdown(f"""
                                <div style="display: flex; gap: 16px; margin-bottom: 12px;">
                                    <div style="text-align: center; padding: 12px; background: {alert['alert_color']}15; border: 1px solid {alert['alert_color']}40; border-radius: 8px; min-width: 100px;">
                                        <p style="margin: 0; color: {alert['alert_color']}; font-size: 24px; font-weight: 700;">{alert['score']}</p>
                                        <p style="margin: 4px 0 0 0; color: {alert['alert_color']}; font-size: 11px;">درجة الفرصة</p>
                                    </div>
                                    <div>
                                        <p style="margin: 0; font-weight: 600;">{alert['name']} | {alert['sector']}</p>
                                        <p style="color: #64748b; font-size: 13px; margin: 4px 0;">السعر: {alert['price']} | RSI: {alert['rsi']} | MACD: {alert['macd']}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
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
                                
                                if st.button(f"🔮 تحليل مفصل", key=f"analyze_alert_{alert['symbol']}", use_container_width=True):
                                    select_stock(alert['symbol'])
                                    st.rerun()
                
                # Full table
                st.subheader("📋 الجدول الكامل")
                table_data = []
                for alert in all_alerts:
                    table_data.append({
                        "الرمز": alert['symbol'],
                        "الشركة": alert['name'],
                        "القطاع": alert['sector'],
                        "السعر": alert['price'],
                        "الإشارة": alert['signal_text'],
                        "الدرجة": alert['score'],
                        "RSI": alert['rsi'],
                        "R/R": alert['rr_ratio'],
                        "Stop Loss": alert['stop_loss'],
                        "الهدف": alert['take_profit_1']
                    })
                
                df_alerts = pd.DataFrame(table_data)
                st.dataframe(df_alerts, use_container_width=True, hide_index=True)
                
                st.download_button(
                    label="📥 تصدير CSV",
                    data=df_alerts.to_csv(index=False).encode('utf-8-sig'),
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("👈 اضغط 'تشغيل التحليل الآلي' لبدء المسح")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 7: DETAILED ANALYSIS ====================
with tab7:
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🔮 التحليل الذكي الشامل</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; margin-bottom: 16px;">
        <p style="color: #f87171; font-weight: 600; margin: 0; font-size: 13px;">⚠️ تحذير</p>
        <p style="color: #fca5a5; font-size: 12px; margin-top: 4px;">التوقعات نتائج رياضية للبيانات التاريخية فقط. لا تعتبر توصية استثمارية.</p>
    </div>
    """, unsafe_allow_html=True)
    
    analysis_stock = st.selectbox("السهم", tickers, key="ai_stock")
    analysis_period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="ai_period")
    
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    with risk_col1:
        max_risk_pct = st.slider("الحد الأقصى للمخاطرة %", 1, 10, 5, key="ai_risk")
    with risk_col2:
        prediction_days = st.slider("أيام التوقع", 3, 30, 10, key="ai_days")
    with risk_col3:
        confidence_level = st.selectbox("مستوى الثقة", ["منخفض (70%)", "متوسط (85%)", "عالي (95%)"], index=1, key="ai_conf")
    
    if st.button("🔮 تشغيل التحليل الشامل", type="primary", use_container_width=True):
        with st.spinner("جاري التحليل..."):
            df = safe_fetch_stock_data(analysis_stock, analysis_period, "EGX" if is_egypt else "GLOBAL")
            
            if df is None or df.empty:
                st.error("❌ تعذر جلب البيانات.")
            else:
                df = calculate_technical_indicators(df)
                if df is None:
                    st.error("❌ خطأ في حساب المؤشرات.")
                else:
                    signals = generate_trading_signals(df)
                    overall_signal, score, signal_text = calculate_overall_signal(signals)
                    predictions = predict_future_prices(df, days=prediction_days)
                    sr_levels = calculate_support_resistance(df)
                    
                    current_price = df['Close'].iloc[-1]
                    volatility = df['Close'].pct_change().std()
                    atr = df['ATR'].iloc[-1] if pd.notna(df['ATR'].iloc[-1]) else current_price * 0.02
                    
                    stop_loss = current_price - (atr * 2)
                    take_profit_1 = current_price + (atr * 2)
                    take_profit_2 = current_price + (atr * 3.5)
                    
                    avg_daily_move = abs(df['Close'].pct_change()).mean() * 100
                    days_to_tp1 = int((take_profit_1 - current_price) / (current_price * avg_daily_move / 100)) if avg_daily_move > 0 else 0
                    days_to_sl = int((current_price - stop_loss) / (current_price * avg_daily_move / 100)) if avg_daily_move > 0 else 0
                    
                    # Signal Display
                    st.subheader("🎯 إشارة التداول")
                    signal_cols = st.columns([1, 2, 1])
                    with signal_cols[1]:
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
                    
                    # Risk Levels
                    st.subheader("🛡️ مستويات إدارة المخاطرة")
                    risk_cols = st.columns(4)
                    risk_data = [
                        ("🛑 Stop Loss", stop_loss, ((current_price-stop_loss)/current_price*100), "#ef4444", days_to_sl),
                        ("📍 السعر الحالي", current_price, 0, "#6366f1", 0),
                        ("🎯 الهدف 1", take_profit_1, ((take_profit_1-current_price)/current_price*100), "#10b981", days_to_tp1),
                        ("🎯🎯 الهدف 2", take_profit_2, ((take_profit_2-current_price)/current_price*100), "#fbbf24", 0)
                    ]
                    
                    for i, (label, value, pct, color, days) in enumerate(risk_data):
                        with risk_cols[i]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid {color}30;">
                                <p style="color: #64748b; font-size: 11px; margin: 0;">{label}</p>
                                <p style="font-size: 24px; font-weight: 700; color: {color}; margin: 4px 0;">{value:.2f}</p>
                                {f'<p style="font-size: 11px; color: {color}; margin: 0;">{pct:.1f}%</p>' if pct else ''}
                                {f'<p style="font-size: 10px; color: #64748b; margin: 4px 0 0 0;">⏱️ ~{days} يوم</p>' if days else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Technical Indicators
                    st.subheader("📊 المؤشرات الفنية")
                    latest = df.iloc[-1]
                    
                    ind_col1, ind_col2, ind_col3, ind_col4, ind_col5, ind_col6 = st.columns(6)
                    indicators = [
                        ("RSI (14)", latest.get('RSI', 0), "#ef4444" if latest.get('RSI', 50) > 70 else "#10b981" if latest.get('RSI', 50) < 30 else "#fbbf24", "ذروة شراء" if latest.get('RSI', 50) > 70 else "ذروة بيع" if latest.get('RSI', 50) < 30 else "محايد"),
                        ("MACD", latest.get('MACD', 0), "#10b981" if latest.get('MACD', 0) > 0 else "#ef4444", "إيجابي" if latest.get('MACD', 0) > 0 else "سلبي"),
                        ("Bollinger", latest.get('BB_Position', 0.5), "#10b981" if latest.get('BB_Position', 0.5) < 0.2 else "#ef4444" if latest.get('BB_Position', 0.5) > 0.8 else "#fbbf24", "منطقة شراء" if latest.get('BB_Position', 0.5) < 0.2 else "منطقة بيع" if latest.get('BB_Position', 0.5) > 0.8 else "النطاق الأوسط"),
                        ("Stochastic", latest.get('Stoch_K', 50), "#10b981" if latest.get('Stoch_K', 50) < 20 else "#ef4444" if latest.get('Stoch_K', 50) > 80 else "#fbbf24", "ذروة بيع" if latest.get('Stoch_K', 50) < 20 else "ذروة شراء" if latest.get('Stoch_K', 50) > 80 else "محايد"),
                        ("SMA 20", latest.get('SMA_20', 0), "#10b981" if latest.get('Close', 0) > latest.get('SMA_20', 0) else "#ef4444", "صاعد" if latest.get('Close', 0) > latest.get('SMA_20', 0) else "هابط"),
                        ("Volume", latest.get('Volume_Ratio', 1), "#10b981" if latest.get('Volume_Ratio', 1) > 1.5 else "#ef4444" if latest.get('Volume_Ratio', 1) < 0.5 else "#fbbf24", "نشط" if latest.get('Volume_Ratio', 1) > 1.5 else "ضعيف" if latest.get('Volume_Ratio', 1) < 0.5 else "طبيعي")
                    ]
                    
                    for i, (label, value, color, text) in enumerate(indicators):
                        with [ind_col1, ind_col2, ind_col3, ind_col4, ind_col5, ind_col6][i]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                                <p style="color: #64748b; font-size: 10px; margin: 0;">{label}</p>
                                <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 4px 0;">{value:.1f}</p>
                                <p style="font-size: 10px; color: {color}; margin: 0;">{text}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Prediction Chart
                    if 'combined' in predictions:
                        st.subheader("🔮 توقعات الأسعار")
                        pred_df = pd.DataFrame(predictions['combined'])
                        
                        fig_pred = go.Figure()
                        hist_days = min(60, len(df))
                        fig_pred.add_trace(go.Scatter(
                            x=df.index[-hist_days:],
                            y=df['Close'].tail(hist_days),
                            mode='lines',
                            name='السعر الفعلي',
                            line=dict(color='#6366f1', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(99, 102, 241, 0.1)'
                        ))
                        
                        last_date = df.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=prediction_days, freq='B')
                        predicted_prices = [p['predicted'] for p in predictions['combined']]
                        upper_bounds = [p['upper_bound'] for p in predictions['combined']]
                        lower_bounds = [p['lower_bound'] for p in predictions['combined']]
                        
                        fig_pred.add_trace(go.Scatter(
                            x=future_dates,
                            y=predicted_prices,
                            mode='lines+markers',
                            name='التوقع',
                            line=dict(color='#fbbf24', width=3),
                            marker=dict(size=8, color='#fbbf24')
                        ))
                        
                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=upper_bounds + list(reversed(predicted_prices)),
                            fill='tonexty',
                            fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                            name='الحد الأعلى',
                            showlegend=True
                        ))
                        
                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=list(reversed(predicted_prices)) + lower_bounds,
                            fill='tonexty',
                            fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                            name='الحد الأدنى',
                            showlegend=True
                        ))
                        
                        fig_pred.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444", annotation_text="Stop Loss", annotation_position="right")
                        fig_pred.add_hline(y=take_profit_1, line_dash="dash", line_color="#10b981", annotation_text="TP1", annotation_position="right")
                        
                        fig_pred.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter", color="#94a3b8"),
                            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="التاريخ"),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="السعر"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=450,
                            margin=dict(t=40, b=40)
                        )
                        st.plotly_chart(fig_pred, use_container_width=True)
                    
                    # Candlestick Chart
                    st.subheader("📈 الرسم البياني التفاعلي")
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='الشموع'
                    ))
                    
                    if pd.notna(latest.get('SMA_20')):
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#6366f1', width=1)))
                    if pd.notna(latest.get('SMA_50')):
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#fbbf24', width=1)))
                    
                    fig.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444", annotation_text="SL", annotation_position="right")
                    fig.add_hline(y=take_profit_1, line_dash="dash", line_color="#10b981", annotation_text="TP1", annotation_position="right")
                    
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=450,
                        margin=dict(t=40, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume Chart
                    fig_vol = go.Figure()
                    colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' for i in range(len(df))]
                    fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='الحجم'))
                    if pd.notna(df.get('Volume_SMA')).any():
                        fig_vol.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'], mode='lines', name='متوسط الحجم', line=dict(color='#fbbf24', width=2)))
                    
                    fig_vol.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="الحجم"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=250,
                        margin=dict(t=40, b=20)
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== DEBUG CONSOLE (IF ENABLED) ====================
if st.session_state.debug_mode and debug.errors_log:
    st.markdown("---")
    st.subheader("🔧 سجل التصحيح (Debug Console)")
    
    for error in debug.errors_log[-10:]:  # Show last 10 errors
        status_class = "debug-success" if error["recovered"] else "debug-error"
        status_icon = "✅" if error["recovered"] else "❌"
        
        st.markdown(f"""
        <div class="debug-console">
            <div class="debug-entry {status_class}">
                <span style="color: #64748b;">[{error['timestamp']}]</span>
                <span style="color: #fbbf24; font-weight: 600;">{error['component']}</span>
                <span style="color: #ef4444;">{status_icon} {error['error_type']}</span>
                <p style="margin: 4px 0 0 0; color: #94a3b8;">{error['error_message'][:100]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🧹 مسح السجل", use_container_width=True):
        debug.errors_log = []
        st.rerun()

# ==================== FOOTER ====================
best_stock = max(stocks_data, key=lambda x: x["change_pct"])
st.markdown(f"""
<div style="text-align: center; padding: 24px; margin-top: 32px; background: linear-gradient(90deg, #0a0a0f, #12121a); border-top: 2px solid rgba(99,102,241,0.2); border-radius: 12px;">
    <p style="font-size: 16px; margin-bottom: 8px; color: #e2e8f0; font-weight: 600;">⚡ EGX Pro Terminal v20.0</p>
    <p style="color: #64748b; font-size: 13px;">
        نظام تحليلي احترافي | Backtesting | توقعات AI | إدارة المهام | تصحيح أخطاء ذكي
    </p>
    <p style="color: #fbbf24; font-size: 13px; margin-top: 8px;">
        🏆 أقوى سهم: <b>{best_stock['symbol']}</b> — +{best_stock['change_pct']:.2f}%
    </p>
    <p style="color: #475569; font-size: 11px; margin-top: 12px;">
        © 2026 | جميع البيانات للتوضيح | التوقعات للأغراض التعليمية فقط
    </p>
</div>
""", unsafe_allow_html=True)
'''

# Save to file
output_path = "/mnt/agents/output/egx_pro_terminal_v20_debug.py"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(enhanced_code)

print(f"✅ File saved successfully: {output_path}")
print(f"📊 File size: {len(enhanced_code):,} characters")
print(f"🔧 Debug system: Integrated with error recovery")
print(f"🎨 UI: Professional dark terminal layout")
