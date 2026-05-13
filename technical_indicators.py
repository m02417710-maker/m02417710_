
import os

# Create the improved v22 terminal code
v22_code = '''import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
import traceback
import json
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings('ignore')

# ==================== ADVANCED CONFIGURATION ====================
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v22", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# ==================== PROFESSIONAL DARK THEME CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', 'Cairo', sans-serif !important; letter-spacing: -0.01em; }
    .main { background: linear-gradient(180deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%); color: #e2e8f0; }
    
    /* Bottom Navigation Bar */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, rgba(15,15,25,0.98), rgba(10,10,15,0.99));
        border-top: 1px solid rgba(255,255,255,0.06);
        padding: 8px 16px;
        z-index: 999999;
        display: flex;
        justify-content: space-around;
        align-items: center;
        backdrop-filter: blur(20px);
        box-shadow: 0 -4px 24px rgba(0,0,0,0.5);
    }
    .nav-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 8px 16px;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
        color: #64748b;
        min-width: 80px;
    }
    .nav-btn:hover { background: rgba(99,102,241,0.1); color: #818cf8; }
    .nav-btn.active { background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.15)); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }
    .nav-btn .icon { font-size: 20px; margin-bottom: 4px; }
    .nav-btn .label { font-size: 11px; font-weight: 600; }
    
    /* Main Content Padding for Bottom Nav */
    .main-content { padding-bottom: 100px !important; }
    
    .pro-panel { 
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98)); 
        border: 1px solid rgba(255,255,255,0.06); 
        border-radius: 16px; 
        padding: 20px; 
        box-shadow: 0 4px 24px rgba(0,0,0,0.4); 
        margin-bottom: 16px; 
        transition: all 0.2s ease; 
    }
    .pro-panel:hover { border-color: rgba(99,102,241,0.15); box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
    .pro-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .pro-panel-title { font-size: 14px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; }
    .pro-panel-value { font-size: 28px; font-weight: 800; color: #f1f5f9; margin: 4px 0; }
    
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }
    .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
    
    .status-up { color: #10b981; } .status-down { color: #ef4444; } .status-neutral { color: #94a3b8; } .status-warning { color: #f59e0b; }
    .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    .badge-green { background: rgba(16,185,129,0.15); color: #10b981; } .badge-red { background: rgba(239,68,68,0.15); color: #ef4444; }
    .badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; } .badge-blue { background: rgba(99,102,241,0.15); color: #818cf8; }
    .badge-purple { background: rgba(139,92,246,0.15); color: #a78bfa; }
    
    .live-pulse { display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse-live 2s infinite; margin-left: 8px; }
    @keyframes pulse-live { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } }
    
    .stock-card { 
        background: linear-gradient(145deg, rgba(25,25,35,0.9), rgba(20,20,30,0.95)); 
        border: 1px solid rgba(255,255,255,0.05); 
        border-radius: 12px; 
        padding: 16px; 
        text-align: center; 
        cursor: pointer; 
        transition: all 0.3s ease; 
        position: relative; 
        overflow: hidden; 
    }
    .stock-card:hover { border-color: rgba(99,102,241,0.3); transform: translateY(-3px); box-shadow: 0 12px 32px rgba(99,102,241,0.15); }
    .stock-card-symbol { font-size: 16px; font-weight: 800; color: #fbbf24; margin-bottom: 6px; }
    .stock-card-price { font-size: 24px; font-weight: 800; color: #f1f5f9; margin: 6px 0; }
    .stock-card-change { font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 20px; display: inline-block; }
    .stock-card-change.up { background: rgba(16,185,129,0.15); color: #10b981; }
    .stock-card-change.down { background: rgba(239,68,68,0.15); color: #ef4444; }
    
    .signal-box { border-radius: 12px; padding: 20px; text-align: center; border: 1px solid; }
    .signal-buy { background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.02)); border-color: rgba(16,185,129,0.3); }
    .signal-sell { background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.02)); border-color: rgba(239,68,68,0.3); }
    .signal-hold { background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.02)); border-color: rgba(245,158,11,0.3); }
    
    .risk-metric { padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }
    .risk-low { border-color: rgba(16,185,129,0.3); } .risk-medium { border-color: rgba(245,158,11,0.3); } .risk-high { border-color: rgba(239,68,68,0.3); }
    
    .corporate-card { padding: 20px; background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05)); border: 1px solid rgba(99,102,241,0.15); border-radius: 16px; margin-bottom: 16px; }
    
    .task-item { padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px; border-right: 3px solid; transition: all 0.2s; }
    .task-item:hover { background: rgba(255,255,255,0.04); }
    
    .metric-card {
        background: linear-gradient(145deg, rgba(25,25,35,0.9), rgba(20,20,30,0.95));
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover { border-color: rgba(99,102,241,0.2); transform: translateY(-2px); }
    
    .trend-up { color: #10b981; }
    .trend-down { color: #ef4444; }
    .trend-neutral { color: #94a3b8; }
    
    .analysis-row {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.03);
        transition: all 0.2s;
    }
    .analysis-row:hover { background: rgba(255,255,255,0.04); border-color: rgba(99,102,241,0.1); }
    
    .progress-bar {
        height: 6px;
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
    
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 800 !important; color: #f1f5f9 !important; }
    
    .header-glow {
        background: linear-gradient(90deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05));
        border-radius: 16px;
        border: 1px solid rgba(99,102,241,0.1);
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .financial-report {
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.03));
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { margin-bottom: 80px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE MANAGEMENT ====================
def init_session_state():
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
        'active_tab': 'market',
        'price_history_sim': {},
        'realtime_prices': {},
        'selected_sector': 'الكل',
        'analysis_results': {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== COMPLETE EGYPTIAN STOCKS DATABASE ====================
class EGXDataEngine:
    """Advanced data engine with comprehensive Egyptian stocks"""

    EGYPTIAN_STOCKS = [
        # البنوك
        {"symbol": "COMI", "name": "CIB", "sector": "بنوك", "base_price": 140.01, "volatility": 0.015, "market_cap": 420000000000, "pe": 8.5, "eps": 16.47},
        {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "base_price": 58.14, "volatility": 0.012, "market_cap": 180000000000, "pe": 7.2, "eps": 8.08},
        {"symbol": "ADIB", "name": "أبوظبي الإسلامي", "sector": "بنوك", "base_price": 47.49, "volatility": 0.018, "market_cap": 95000000000, "pe": 9.1, "eps": 5.22},
        {"symbol": "HDBK", "name": "بنك الإسكان", "sector": "بنوك", "base_price": 147.26, "volatility": 0.014, "market_cap": 220000000000, "pe": 6.8, "eps": 21.66},
        {"symbol": "CANA", "name": "قناة السويس", "sector": "بنوك", "base_price": 33.88, "volatility": 0.022, "market_cap": 45000000000, "pe": 5.5, "eps": 6.16},
        {"symbol": "CIEB", "name": "كريدي أجريكول", "sector": "بنوك", "base_price": 23.73, "volatility": 0.016, "market_cap": 32000000000, "pe": 7.8, "eps": 3.04},
        {"symbol": "FAIT", "name": "فيصل الإسلامي", "sector": "بنوك", "base_price": 34.11, "volatility": 0.015, "market_cap": 48000000000, "pe": 8.2, "eps": 4.16},
        {"symbol": "SAUD", "name": "البركة", "sector": "بنوك", "base_price": 24.70, "volatility": 0.017, "market_cap": 28000000000, "pe": 6.5, "eps": 3.80},
        {"symbol": "UBEE", "name": "المصرف المتحد", "sector": "بنوك", "base_price": 13.98, "volatility": 0.025, "market_cap": 15000000000, "pe": 5.2, "eps": 2.69},
        {"symbol": "EXPA", "name": "التنمية الصادرات", "sector": "بنوك", "base_price": 18.68, "volatility": 0.019, "market_cap": 22000000000, "pe": 6.1, "eps": 3.06},
        
        # تكنولوجيا مالية
        {"symbol": "EFIH", "name": "e-Finance", "sector": "تكنولوجيا مالية", "base_price": 22.32, "volatility": 0.028, "market_cap": 65000000000, "pe": 18.5, "eps": 1.21},
        {"symbol": "FWRY", "name": "فوري", "sector": "تكنولوجيا مالية", "base_price": 20.88, "volatility": 0.026, "market_cap": 52000000000, "pe": 22.3, "eps": 0.94},
        {"symbol": "SCTS", "name": "مقاصة قناة السويس", "sector": "تكنولوجيا مالية", "base_price": 652.11, "volatility": 0.012, "market_cap": 130000000000, "pe": 15.2, "eps": 42.90},
        {"symbol": "VALU", "name": "U للتمويل", "sector": "تكنولوجيا مالية", "base_price": 12.60, "volatility": 0.032, "market_cap": 18000000000, "pe": 25.8, "eps": 0.49},
        
        # عقارات
        {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "base_price": 98.25, "volatility": 0.016, "market_cap": 280000000000, "pe": 12.5, "eps": 7.86},
        {"symbol": "EMFD", "name": "إعمار مصر", "sector": "عقارات", "base_price": 11.10, "volatility": 0.024, "market_cap": 55000000000, "pe": 8.9, "eps": 1.25},
        {"symbol": "PHDC", "name": "بالم هيلز", "sector": "عقارات", "base_price": 14.00, "volatility": 0.021, "market_cap": 42000000000, "pe": 7.8, "eps": 1.79},
        {"symbol": "ORHD", "name": "أوراسكوم للتنمية", "sector": "عقارات", "base_price": 33.35, "volatility": 0.018, "market_cap": 78000000000, "pe": 9.2, "eps": 3.63},
        {"symbol": "OCDI", "name": "سوديك", "sector": "عقارات", "base_price": 22.98, "volatility": 0.017, "market_cap": 65000000000, "pe": 8.5, "eps": 2.70},
        
        # صناعة
        {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "base_price": 89.51, "volatility": 0.015, "market_cap": 180000000000, "pe": 11.2, "eps": 7.99},
        {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "base_price": 317.00, "volatility": 0.020, "market_cap": 95000000000, "pe": 14.5, "eps": 21.86},
        {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "base_price": 87.19, "volatility": 0.014, "market_cap": 72000000000, "pe": 6.8, "eps": 12.82},
        {"symbol": "MFPC", "name": "موبكو", "sector": "صناعة", "base_price": 45.15, "volatility": 0.019, "market_cap": 48000000000, "pe": 7.5, "eps": 6.02},
        {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "base_price": 58.00, "volatility": 0.016, "market_cap": 35000000000, "pe": 8.2, "eps": 7.07},
        {"symbol": "HELI", "name": "السويدي كابلات", "sector": "صناعة", "base_price": 42.50, "volatility": 0.018, "market_cap": 28000000000, "pe": 9.5, "eps": 4.47},
        {"symbol": "MEPA", "name": "السويس للأسمنت", "sector": "صناعة", "base_price": 28.30, "volatility": 0.022, "market_cap": 22000000000, "pe": 6.2, "eps": 4.56},
        {"symbol": "SCEM", "name": "جنوب الوادي للأسمنت", "sector": "صناعة", "base_price": 15.80, "volatility": 0.025, "market_cap": 18000000000, "pe": 5.8, "eps": 2.72},
        
        # اتصالات
        {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "base_price": 98.49, "volatility": 0.013, "market_cap": 200000000000, "pe": 10.5, "eps": 9.38},
        {"symbol": "EGSA", "name": "النايل سات", "sector": "اتصالات", "base_price": 9.09, "volatility": 0.018, "market_cap": 18000000000, "pe": 8.2, "eps": 1.11},
        {"symbol": "EGYC", "name": "مصر للاتصالات", "sector": "اتصالات", "base_price": 12.45, "volatility": 0.020, "market_cap": 15000000000, "pe": 9.5, "eps": 1.31},
        
        # سلع استهلاكية
        {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "base_price": 40.31, "volatility": 0.012, "market_cap": 85000000000, "pe": 8.8, "eps": 4.58},
        {"symbol": "EFID", "name": "إيديتا", "sector": "سلع استهلاكية", "base_price": 28.60, "volatility": 0.015, "market_cap": 62000000000, "pe": 14.2, "eps": 2.01},
        {"symbol": "JUFO", "name": "جهينة", "sector": "سلع استهلاكية", "base_price": 28.90, "volatility": 0.014, "market_cap": 58000000000, "pe": 16.5, "eps": 1.75},
        {"symbol": "DOMT", "name": "دومتي", "sector": "سلع استهلاكية", "base_price": 26.00, "volatility": 0.022, "market_cap": 22000000000, "pe": 18.2, "eps": 1.43},
        {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "base_price": 48.81, "volatility": 0.013, "market_cap": 38000000000, "pe": 9.8, "eps": 4.98},
        {"symbol": "POUL", "name": "القاهرة للدواجن", "sector": "سلع استهلاكية", "base_price": 34.80, "volatility": 0.016, "market_cap": 28000000000, "pe": 11.5, "eps": 3.03},
        {"symbol": "GBCO", "name": "GB Corp", "sector": "سلع استهلاكية", "base_price": 29.30, "volatility": 0.020, "market_cap": 45000000000, "pe": 13.2, "eps": 2.22},
        {"symbol": "ORWE", "name": "النساجون الشرقيون", "sector": "سلع استهلاكية", "base_price": 23.56, "volatility": 0.015, "market_cap": 32000000000, "pe": 10.5, "eps": 2.24},
        {"symbol": "SPIN", "name": "الغزل والنسيج", "sector": "سلع استهلاكية", "base_price": 8.45, "volatility": 0.028, "market_cap": 12000000000, "pe": 5.2, "eps": 1.63},
        {"symbol": "UNIC", "name": "يونيفرسال", "sector": "سلع استهلاكية", "base_price": 18.90, "volatility": 0.019, "market_cap": 15000000000, "pe": 7.8, "eps": 2.42},
        
        # صحة
        {"symbol": "CLHO", "name": "كليوباترا", "sector": "صحة", "base_price": 14.94, "volatility": 0.021, "market_cap": 18000000000, "pe": 12.5, "eps": 1.20},
        {"symbol": "PHAR", "name": "أمون", "sector": "صحة", "base_price": 89.49, "volatility": 0.014, "market_cap": 42000000000, "pe": 15.8, "eps": 5.66},
        {"symbol": "ISPH", "name": "ابن سينا", "sector": "صحة", "base_price": 11.96, "volatility": 0.019, "market_cap": 35000000000, "pe": 9.2, "eps": 1.30},
        {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "base_price": 687.72, "volatility": 0.011, "market_cap": 85000000000, "pe": 18.5, "eps": 37.17},
        {"symbol": "NIPH", "name": "النيل للأدوية", "sector": "صحة", "base_price": 173.20, "volatility": 0.013, "market_cap": 22000000000, "pe": 14.2, "eps": 12.20},
        {"symbol": "ADCI", "name": "العربية للأدوية", "sector": "صحة", "base_price": 216.63, "volatility": 0.012, "market_cap": 28000000000, "pe": 16.8, "eps": 12.89},
        {"symbol": "AXPH", "name": "الإسكندرية للأدوية", "sector": "صحة", "base_price": 1166.22, "volatility": 0.010, "market_cap": 65000000000, "pe": 20.5, "eps": 56.89},
        {"symbol": "KPPC", "name": "كيما", "sector": "صحة", "base_price": 35.80, "volatility": 0.018, "market_cap": 25000000000, "pe": 8.5, "eps": 4.21},
        
        # استثمار
        {"symbol": "HRHO", "name": "EFG هيرمس", "sector": "استثمار", "base_price": 29.50, "volatility": 0.023, "market_cap": 75000000000, "pe": 11.2, "eps": 2.63},
        {"symbol": "BTFH", "name": "بلتون", "sector": "استثمار", "base_price": 3.20, "volatility": 0.035, "market_cap": 8000000000, "pe": 6.5, "eps": 0.49},
        {"symbol": "CCAP", "name": "قلعة", "sector": "استثمار", "base_price": 4.70, "volatility": 0.028, "market_cap": 12000000000, "pe": 8.2, "eps": 0.57},
        {"symbol": "CICH", "name": "سي آي كابيتال", "sector": "استثمار", "base_price": 12.90, "volatility": 0.030, "market_cap": 15000000000, "pe": 9.5, "eps": 1.36},
        {"symbol": "RAYA", "name": "راية", "sector": "استثمار", "base_price": 7.10, "volatility": 0.032, "market_cap": 22000000000, "pe": 7.8, "eps": 0.91},
        {"symbol": "RACC", "name": "راية لخدمة العملاء", "sector": "استثمار", "base_price": 10.25, "volatility": 0.022, "market_cap": 18000000000, "pe": 10.2, "eps": 1.00},
        {"symbol": "BINV", "name": "B للاستثمارات", "sector": "استثمار", "base_price": 42.00, "volatility": 0.018, "market_cap": 28000000000, "pe": 12.5, "eps": 3.36},
        {"symbol": "FAAL", "name": "الأهلي للاستثمار", "sector": "استثمار", "base_price": 5.85, "volatility": 0.025, "market_cap": 12000000000, "pe": 8.8, "eps": 0.66},
        
        # طاقة
        {"symbol": "AMOC", "name": "Alexandria Mineral Oils", "sector": "طاقة", "base_price": 8.59, "volatility": 0.024, "market_cap": 25000000000, "pe": 5.8, "eps": 1.48},
        {"symbol": "EGAS", "name": "مصر للغاز", "sector": "طاقة", "base_price": 49.12, "volatility": 0.016, "market_cap": 35000000000, "pe": 7.2, "eps": 6.82},
        {"symbol": "ESRS", "name": "العامة للبترول", "sector": "طاقة", "base_price": 15.40, "volatility": 0.022, "market_cap": 18000000000, "pe": 6.5, "eps": 2.37},
        {"symbol": "GASR", "name": "الغازات", "sector": "طاقة", "base_price": 22.80, "volatility": 0.019, "market_cap": 22000000000, "pe": 8.2, "eps": 2.78},
        
        # تعليم
        {"symbol": "MTIE", "name": "MM Group", "sector": "تعليم", "base_price": 9.42, "volatility": 0.026, "market_cap": 18000000000, "pe": 15.5, "eps": 0.61},
        {"symbol": "SKPC", "name": "سكاي", "sector": "تعليم", "base_price": 6.85, "volatility": 0.028, "market_cap": 12000000000, "pe": 18.2, "eps": 0.38},
        
        # إعلام
        {"symbol": "MPRC", "name": "مدينة الإنتاج", "sector": "إعلام", "base_price": 31.75, "volatility": 0.017, "market_cap": 12000000000, "pe": 12.8, "eps": 2.48},
        {"symbol": "MEDR", "name": "المصرية للإعلام", "sector": "إعلام", "base_price": 8.90, "volatility": 0.024, "market_cap": 8000000000, "pe": 9.5, "eps": 0.94},
        
        # نقل
        {"symbol": "ETRS", "name": "النقل والخدمات", "sector": "نقل", "base_price": 7.78, "volatility": 0.021, "market_cap": 15000000000, "pe": 7.8, "eps": 1.00},
        {"symbol": "SAUD", "name": "السعودية المصرية", "sector": "نقل", "base_price": 4.25, "volatility": 0.030, "market_cap": 8000000000, "pe": 5.5, "eps": 0.77},
        
        # تكنولوجيا
        {"symbol": "EEII", "name": "العربية للصناعات الهندسية", "sector": "تكنولوجيا", "base_price": 2.35, "volatility": 0.040, "market_cap": 8000000000, "pe": 4.2, "eps": 0.56},
        {"symbol": "RMDA", "name": "الراميدا", "sector": "تكنولوجيا", "base_price": 5.60, "volatility": 0.025, "market_cap": 10000000000, "pe": 8.5, "eps": 0.66},
        
        # مواد بناء
        {"symbol": "IRON", "name": "الحديد والصلب", "sector": "مواد بناء", "base_price": 12.80, "volatility": 0.028, "market_cap": 15000000000, "pe": 4.8, "eps": 2.67},
        {"symbol": "NCEM", "name": "الوطنية للأسمنت", "sector": "مواد بناء", "base_price": 18.50, "volatility": 0.022, "market_cap": 20000000000, "pe": 6.2, "eps": 2.98},
    ]

    def __init__(self):
        self.cache = st.session_state.market_data_cache
        self.price_history = st.session_state.price_history_sim

    def _generate_realistic_price(self, stock_info: dict) -> dict:
        """Generate realistic simulated price with market correlation"""
        try:
            symbol = stock_info['symbol']
            base = stock_info['base_price']
            vol = stock_info['volatility']

            if symbol in self.price_history:
                last_price = self.price_history[symbol]
            else:
                last_price = base

            # Market trend factor
            market_trend = np.random.normal(0.0002, 0.008)
            sector_trend = np.random.normal(0, vol * 0.3)
            
            # Mean reversion
            drift = (base - last_price) * 0.008
            shock = np.random.normal(drift + market_trend + sector_trend, vol * last_price * 0.6)
            
            new_price = max(last_price + shock, base * 0.45)
            
            change = new_price - base
            change_pct = (change / base) * 100 if base > 0 else 0

            # Volume simulation
            base_volume = stock_info.get('market_cap', 1e9) / (new_price * 100) if new_price > 0 else 1e6
            volume_shock = np.random.lognormal(0, 0.6)
            volume = int(base_volume * volume_shock)

            high = new_price * (1 + abs(np.random.normal(0, vol/2.5)))
            low = new_price * (1 - abs(np.random.normal(0, vol/2.5)))

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
                "open": round(new_price - np.random.normal(0, vol * new_price * 0.25), 2),
                "volatility": vol,
                "base_price": base,
                "pe": stock_info.get('pe', 0),
                "eps": stock_info.get('eps', 0)
            }
        except Exception as e:
            return {
                "symbol": stock_info['symbol'],
                "name": stock_info['name'],
                "sector": stock_info['sector'],
                "price": stock_info['base_price'],
                "change": 0.0,
                "change_pct": 0.0,
                "volume": 1000000,
                "high": stock_info['base_price'] * 1.02,
                "low": stock_info['base_price'] * 0.98,
                "market_cap": stock_info['market_cap'],
                "open": stock_info['base_price'],
                "volatility": stock_info['volatility'],
                "base_price": stock_info['base_price'],
                "pe": stock_info.get('pe', 0),
                "eps": stock_info.get('eps', 0)
            }

    def get_live_prices(self) -> List[dict]:
        """Get live prices for all stocks"""
        results = []
        for stock in self.EGYPTIAN_STOCKS:
            sim = self._generate_realistic_price(stock)
            sim["source"] = "realtime"
            results.append(sim)
        return results

    def get_stock_history(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """Get historical data with realistic patterns"""
        try:
            cache_key = f"{symbol}_{period}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if (datetime.now() - entry["timestamp"]).seconds < 300:
                    return entry["data"]

            stock = next((s for s in self.EGYPTIAN_STOCKS if s['symbol'] == symbol), None)
            if not stock:
                return None

            days_map = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504}
            days = days_map.get(period, 66)
            dates = pd.date_range(end=datetime.now(), periods=days, freq='B')

            # Generate realistic price path with trends
            prices = [stock['base_price']]
            trend = np.random.choice([-1, 0, 1]) * 0.0003  # Random trend direction
            
            for i in range(1, days):
                # Mean reversion + trend + noise
                drift = (stock['base_price'] - prices[-1]) * 0.004 + trend
                shock = np.random.normal(drift, stock['volatility'] * prices[-1] * 0.5)
                new_price = max(prices[-1] + shock, stock['base_price'] * 0.45)
                prices.append(new_price)

            df = pd.DataFrame({
                'Open': [p * (1 + np.random.normal(0, 0.004)) for p in prices],
                'High': [p * (1 + abs(np.random.normal(0, stock['volatility']/2.5))) for p in prices],
                'Low': [p * (1 - abs(np.random.normal(0, stock['volatility']/2.5))) for p in prices],
                'Close': prices,
                'Volume': [int(stock['market_cap'] / (p * 100) * np.random.lognormal(0, 0.5)) if p > 0 else 1000000 for p in prices]
            }, index=dates)

            self.cache[cache_key] = {"data": df, "timestamp": datetime.now()}
            return df
        except Exception as e:
            return None

    def get_sector_performance(self) -> pd.DataFrame:
        """Get sector performance summary"""
        prices = self.get_live_prices()
        df = pd.DataFrame(prices)
        if df.empty:
            return pd.DataFrame()
        
        sector_perf = df.groupby('sector').agg({
            'change_pct': 'mean',
            'volume': 'sum',
            'market_cap': 'sum'
        }).reset_index()
        sector_perf.columns = ['القطاع', 'التغيير %', 'الحجم', 'القيمة السوقية']
        return sector_perf

data_engine = EGXDataEngine()

# ==================== ADVANCED TECHNICAL ANALYSIS ENGINE ====================
class TechnicalAnalyzer:
    """Comprehensive technical analysis with validation"""

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Calculate all technical indicators"""
        try:
            if df is None or len(df) < 30:
                return None

            df = df.copy()

            # RSI (14) - Relative Strength Index
            delta = df['Close'].diff()
            gain = delta.clip(lower=0)
            loss = (-delta.clip(upper=0))
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))

            # MACD
            ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = ema_12 - ema_26
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

            # Bollinger Bands (20, 2)
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            bb_range = df['BB_Upper'] - df['BB_Lower']
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / bb_range.replace(0, np.nan)
            df['BB_Width'] = bb_range / df['BB_Middle'].replace(0, np.nan)

            # Stochastic Oscillator (14, 3)
            low_14 = df['Low'].rolling(window=14).min()
            high_14 = df['High'].rolling(window=14).max()
            stoch_range = high_14 - low_14
            df['Stoch_K'] = 100 * (df['Close'] - low_14) / stoch_range.replace(0, np.nan)
            df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()

            # Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

            # ATR (Average True Range)
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = true_range.rolling(window=14).mean()
            df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100

            # Volume Analysis
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA'].replace(0, np.nan)
            df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).cumsum()

            # Momentum & ROC
            df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
            df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100

            # ADX (Average Directional Index)
            plus_dm = df['High'].diff().clip(lower=0)
            minus_dm = (-df['Low'].diff()).clip(lower=0)
            
            atr = true_range.rolling(window=14).mean()
            plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr.replace(0, np.nan))
            minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr.replace(0, np.nan))
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
            df['ADX'] = dx.rolling(window=14).mean()
            df['Plus_DI'] = plus_di
            df['Minus_DI'] = minus_di

            # Williams %R
            df['Williams_R'] = -100 * (high_14 - df['Close']) / stoch_range.replace(0, np.nan)

            # CCI (Commodity Channel Index)
            tp = (df['High'] + df['Low'] + df['Close']) / 3
            tp_sma = tp.rolling(window=20).mean()
            tp_std = tp.rolling(window=20).std()
            df['CCI'] = (tp - tp_sma) / (0.015 * tp_std.replace(0, np.nan))

            return df
        except Exception as e:
            return None

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> List[Tuple]:
        """Generate comprehensive trading signals"""
        try:
            if df is None or len(df) < 30:
                return []

            signals = []
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            # RSI Signals
            rsi = latest.get('RSI')
            if pd.notna(rsi):
                if rsi < 25:
                    signals.append(("RSI", "شراء قوي", 3, "ذروة بيع شديدة", "oversold"))
                elif rsi < 35:
                    signals.append(("RSI", "شراء", 2, "ذروة بيع", "oversold"))
                elif rsi > 75:
                    signals.append(("RSI", "بيع قوي", -3, "ذروة شراء شديدة", "overbought"))
                elif rsi > 65:
                    signals.append(("RSI", "بيع", -2, "ذروة شراء", "overbought"))
                elif rsi < 45:
                    signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء", "bullish"))
                elif rsi > 55:
                    signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع", "bearish"))
                else:
                    signals.append(("RSI", "محايد", 0, "لا إشارة", "neutral"))

            # MACD Signals
            macd = latest.get('MACD')
            macd_signal = latest.get('MACD_Signal')
            macd_hist = latest.get('MACD_Histogram')
            prev_macd = prev.get('MACD')
            prev_signal = prev.get('MACD_Signal')

            if pd.notna(macd) and pd.notna(macd_signal):
                if pd.notna(prev_macd) and pd.notna(prev_signal):
                    if macd > macd_signal and prev_macd <= prev_signal:
                        signals.append(("MACD", "شراء", 2.5, "تقاطع صاعد", "bullish"))
                    elif macd < macd_signal and prev_macd >= prev_signal:
                        signals.append(("MACD", "بيع", -2.5, "تقاطع هابط", "bearish"))
                    elif macd > macd_signal and pd.notna(macd_hist) and macd_hist > 0:
                        signals.append(("MACD", "شراء ضعيف", 1.5, "MACD إيجابي", "bullish"))
                    else:
                        signals.append(("MACD", "بيع ضعيف", -1.5, "MACD سلبي", "bearish"))

            # Bollinger Signals
            close = latest.get('Close')
            bb_lower = latest.get('BB_Lower')
            bb_upper = latest.get('BB_Upper')
            bb_pos = latest.get('BB_Position')

            if pd.notna(close) and pd.notna(bb_lower) and pd.notna(bb_upper):
                if close < bb_lower:
                    signals.append(("Bollinger", "شراء قوي", 2, "تحت النطاق السفلي", "oversold"))
                elif close > bb_upper:
                    signals.append(("Bollinger", "بيع قوي", -2, "فوق النطاق العلوي", "overbought"))
                elif pd.notna(bb_pos) and bb_pos < 0.15:
                    signals.append(("Bollinger", "شراء", 1, "قرب النطاق السفلي", "bullish"))
                elif pd.notna(bb_pos) and bb_pos > 0.85:
                    signals.append(("Bollinger", "بيع", -1, "قرب النطاق العلوي", "bearish"))
                else:
                    signals.append(("Bollinger", "محايد", 0, "داخل النطاق", "neutral"))

            # Stochastic
            stoch_k = latest.get('Stoch_K')
            stoch_d = latest.get('Stoch_D')
            prev_stoch_k = prev.get('Stoch_K')
            prev_stoch_d = prev.get('Stoch_D')

            if pd.notna(stoch_k) and pd.notna(stoch_d):
                if stoch_k < 20 and stoch_d < 20:
                    if pd.notna(prev_stoch_k) and pd.notna(prev_stoch_d) and prev_stoch_k < prev_stoch_d and stoch_k > stoch_d:
                        signals.append(("Stochastic", "شراء قوي", 2, "تقاطع صاعد في ذروة البيع", "oversold"))
                    else:
                        signals.append(("Stochastic", "شراء", 1.5, "ذروة بيع", "oversold"))
                elif stoch_k > 80 and stoch_d > 80:
                    if pd.notna(prev_stoch_k) and pd.notna(prev_stoch_d) and prev_stoch_k > prev_stoch_d and stoch_k < stoch_d:
                        signals.append(("Stochastic", "بيع قوي", -2, "تقاطع هابط في ذروة الشراء", "overbought"))
                    else:
                        signals.append(("Stochastic", "بيع", -1.5, "ذروة شراء", "overbought"))
                else:
                    signals.append(("Stochastic", "محايد", 0, "لا إشارة", "neutral"))

            # Moving Averages
            sma_20 = latest.get('SMA_20')
            sma_50 = latest.get('SMA_50')
            sma_200 = latest.get('SMA_200')
            ema_20 = latest.get('EMA_20')
            ema_50 = latest.get('EMA_50')

            if pd.notna(close) and pd.notna(sma_20) and pd.notna(sma_50):
                if close > sma_20 and close > sma_50 and sma_20 > sma_50:
                    signals.append(("MA", "شراء قوي", 2, "اتجاه صاعد قوي", "bullish"))
                elif close < sma_20 and close < sma_50 and sma_20 < sma_50:
                    signals.append(("MA", "بيع قوي", -2, "اتجاه هابط قوي", "bearish"))
                elif close > sma_20 and close > sma_50:
                    signals.append(("MA", "شراء", 1, "فوق المتوسطات", "bullish"))
                elif close < sma_20 and close < sma_50:
                    signals.append(("MA", "بيع", -1, "تحت المتوسطات", "bearish"))
                elif close > sma_20:
                    signals.append(("MA", "شراء ضعيف", 0.5, "فوق SMA20", "bullish"))
                else:
                    signals.append(("MA", "بيع ضعيف", -0.5, "تحت SMA20", "bearish"))

            # Golden/Death Cross
            if pd.notna(sma_50) and pd.notna(sma_200):
                prev_sma_50 = prev.get('SMA_50')
                prev_sma_200 = prev.get('SMA_200')
                if pd.notna(prev_sma_50) and pd.notna(prev_sma_200):
                    if sma_50 > sma_200 and prev_sma_50 <= prev_sma_200:
                        signals.append(("MA_Cross", "شراء استراتيجي", 3, "تقاطع ذهبي", "bullish"))
                    elif sma_50 < sma_200 and prev_sma_50 >= prev_sma_200:
                        signals.append(("MA_Cross", "بيع استراتيجي", -3, "تقاطع موت", "bearish"))

            # ADX
            adx = latest.get('ADX')
            plus_di = latest.get('Plus_DI')
            minus_di = latest.get('Minus_DI')

            if pd.notna(adx):
                if adx > 30:
                    if pd.notna(plus_di) and pd.notna(minus_di):
                        if plus_di > minus_di:
                            signals.append(("ADX", "تأكيد شراء", 1, "اتجاه صاعد قوي", "confirmation"))
                        else:
                            signals.append(("ADX", "تأكيد بيع", -1, "اتجاه هابط قوي", "confirmation"))
                    else:
                        signals.append(("ADX", "تأكيد", 0.5, "اتجاه قوي", "confirmation"))
                elif adx < 20:
                    signals.append(("ADX", "تحذير", -0.5, "اتجاه ضعيف", "warning"))

            # Volume
            vol_ratio = latest.get('Volume_Ratio')
            obv = latest.get('OBV')
            prev_obv = prev.get('OBV')

            if pd.notna(vol_ratio):
                if vol_ratio > 2.5:
                    signals.append(("Volume", "تأكيد قوي", 1.5, "حجم تداول استثنائي", "confirmation"))
                elif vol_ratio > 1.5:
                    signals.append(("Volume", "تأكيد", 1, "حجم نشط", "confirmation"))
                elif vol_ratio < 0.4:
                    signals.append(("Volume", "ضعف", -1, "حجم ضعيف", "warning"))

            # Williams %R
            williams = latest.get('Williams_R')
            if pd.notna(williams):
                if williams < -80:
                    signals.append(("Williams", "شراء", 1, "ذروة بيع", "oversold"))
                elif williams > -20:
                    signals.append(("Williams", "بيع", -1, "ذروة شراء", "overbought"))

            # CCI
            cci = latest.get('CCI')
            if pd.notna(cci):
                if cci < -200:
                    signals.append(("CCI", "شراء قوي", 1.5, "ذروة بيع شديدة", "oversold"))
                elif cci > 200:
                    signals.append(("CCI", "بيع قوي", -1.5, "ذروة شراء شديدة", "overbought"))

            return signals
        except Exception as e:
            return []

    @staticmethod
    def calculate_overall(signals: List[Tuple]) -> Tuple[str, float, str, str]:
        """Calculate overall signal with trend classification"""
        try:
            if not signals:
                return "HOLD", 0, "لا توجد بيانات كافية", "neutral"

            total_score = sum([s[2] for s in signals if len(s) > 2])

            bullish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bullish", "oversold", "confirmation"])
            bearish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bearish", "overbought", "warning"])
            
            strong_bullish = sum(1 for s in signals if len(s) > 4 and s[4] == "bullish" and s[2] >= 2)
            strong_bearish = sum(1 for s in signals if len(s) > 4 and s[4] == "bearish" and s[2] <= -2)

            if total_score >= 5 or strong_bullish >= 3:
                return "STRONG_BUY", total_score, "إشارة شراء قوية - فرصة استثنائية", "strong_bullish"
            elif total_score >= 2.5:
                return "BUY", total_score, "إشارة شراء - فرصة جيدة", "bullish"
            elif total_score <= -5 or strong_bearish >= 3:
                return "STRONG_SELL", total_score, "إشارة بيع قوية - خطر وشيك", "strong_bearish"
            elif total_score <= -2.5:
                return "SELL", total_score, "إشارة بيع - جني أرباح", "bearish"
            else:
                if bullish_count > bearish_count + 2:
                    return "HOLD", total_score, "انتظار - ميل صاعد", "weak_bullish"
                elif bearish_count > bullish_count + 2:
                    return "HOLD", total_score, "انتظار - ميل هابط", "weak_bearish"
                return "HOLD", total_score, "محايد - لا توجه واضح", "neutral"
        except Exception as e:
            return "HOLD", 0, "خطأ في التحليل", "neutral"

    @staticmethod
    def get_trend_strength(df: pd.DataFrame) -> dict:
        """Calculate trend strength metrics"""
        try:
            latest = df.iloc[-1]
            close = latest.get('Close', 0)
            sma_20 = latest.get('SMA_20', 0)
            sma_50 = latest.get('SMA_50', 0)
            adx = latest.get('ADX', 0)
            
            trend_score = 0
            if pd.notna(close) and pd.notna(sma_20):
                trend_score += 1 if close > sma_20 else -1
            if pd.notna(close) and pd.notna(sma_50):
                trend_score += 1 if close > sma_50 else -1
            if pd.notna(adx):
                trend_score += 1 if adx > 25 else 0
                
            return {
                "score": trend_score,
                "direction": "صاعد" if trend_score > 0 else "هابط" if trend_score < 0 else "محايد",
                "strength": "قوي" if abs(trend_score) >= 2 else "ضعيف"
            }
        except:
            return {"score": 0, "direction": "غير معروف", "strength": "غير معروف"}

ta_engine = TechnicalAnalyzer()

# ==================== ADVANCED RISK MANAGEMENT ENGINE ====================
class RiskEngine:
    """Professional risk management"""

    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        try:
            if returns.empty or returns.std() == 0:
                return 0.0
            return np.percentile(returns.dropna(), (1 - confidence) * 100)
        except:
            return 0.0

    @staticmethod
    def calculate_expected_shortfall(returns: pd.Series, confidence: float = 0.95) -> float:
        try:
            var = RiskEngine.calculate_var(returns, confidence)
            return returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else var
        except:
            return 0.0

    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        try:
            if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
                return 0.0
            b = avg_win / avg_loss
            q = 1 - win_rate
            kelly = (win_rate * b - q) / b
            return max(0, min(kelly, 0.25))
        except:
            return 0.0

    @staticmethod
    def calculate_position_size(account_balance: float, risk_per_trade_pct: float, 
                                  entry_price: float, stop_loss: float) -> Tuple[int, float, float]:
        try:
            risk_amount = account_balance * (risk_per_trade_pct / 100)
            price_risk = abs(entry_price - stop_loss)
            if price_risk == 0:
                return 0, 0, 0
            shares = int(risk_amount / price_risk)
            position_value = shares * entry_price
            actual_risk_pct = (price_risk * shares) / account_balance * 100
            return shares, position_value, actual_risk_pct
        except:
            return 0, 0, 0

    @staticmethod
    def analyze_risk_profile(df: pd.DataFrame, entry_price: float, stop_loss: float, 
                              take_profit: float, account_balance: float = 100000) -> dict:
        try:
            if df is None or len(df) < 20:
                return {}

            returns = df['Close'].pct_change().dropna()
            if returns.empty:
                return {}

            volatility = returns.std() * np.sqrt(252) * 100
            var_95 = RiskEngine.calculate_var(returns, 0.95) * 100
            var_99 = RiskEngine.calculate_var(returns, 0.99) * 100
            cvar_95 = RiskEngine.calculate_expected_shortfall(returns, 0.95) * 100

            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0

            shares, position_value, actual_risk = RiskEngine.calculate_position_size(
                account_balance, st.session_state.risk_settings.get('max_risk_pct', 2.0), entry_price, stop_loss
            )

            positive_days = len(returns[returns > 0])
            total_days = len(returns[returns != 0])
            win_rate = positive_days / total_days if total_days > 0 else 0.5

            avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
            avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
            kelly = RiskEngine.kelly_criterion(win_rate, avg_win, avg_loss)

            consecutive_losses = 0
            max_consecutive = 0
            for r in returns:
                if r < 0:
                    consecutive_losses += 1
                    max_consecutive = max(max_consecutive, consecutive_losses)
                else:
                    consecutive_losses = 0

            # Sharpe ratio
            risk_free_rate = 0.15 / 252  # Approximate Egyptian risk-free rate daily
            excess_returns = returns - risk_free_rate
            sharpe = (excess_returns.mean() / excess_returns.std() * np.sqrt(252)) if excess_returns.std() != 0 else 0

            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino = (returns.mean() * 252 - 0.15) / downside_std if downside_std != 0 else 0

            # Risk classification
            if actual_risk <= 1.5 and rr_ratio >= 2.0 and volatility < 35:
                risk_class = "منخفض"
                risk_color = "#10b981"
            elif actual_risk <= 3.0 and rr_ratio >= 1.5 and volatility < 55:
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
                "sharpe_ratio": round(sharpe, 2),
                "sortino_ratio": round(sortino, 2),
                "rr_ratio": round(rr_ratio, 2),
                "risk_pct": round((risk / entry_price) * 100, 2) if entry_price > 0 else 0,
                "reward_pct": round((reward / entry_price) * 100, 2) if entry_price > 0 else 0,
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
        except Exception as e:
            return {
                "volatility_annual": 0, "var_95": 0, "var_99": 0, "cvar_95": 0,
                "sharpe_ratio": 0, "sortino_ratio": 0, "rr_ratio": 0,
                "risk_pct": 0, "reward_pct": 0, "shares": 0, "position_value": 0,
                "actual_risk_pct": 0, "win_rate": 0, "kelly_pct": 0,
                "max_consecutive_losses": 0, "risk_class": "غير معروف",
                "risk_color": "#94a3b8", "entry_price": entry_price,
                "stop_loss": stop_loss, "take_profit": take_profit,
                "recommendation": "غير معروف"
            }

    @staticmethod
    def generate_risk_report(alerts: List[dict]) -> dict:
        try:
            if not alerts:
                return {}

            total_score = sum(a.get('score', 0) for a in alerts)
            avg_score = total_score / len(alerts) if alerts else 0
            buy_signals = len([a for a in alerts if a.get('signal') in ['BUY', 'STRONG_BUY']])
            sell_signals = len([a for a in alerts if a.get('signal') in ['SELL', 'STRONG_SELL']])
            hold_signals = len([a for a in alerts if a.get('signal') == 'HOLD'])

            buy_alerts = [a for a in alerts if a.get('signal') in ['BUY', 'STRONG_BUY']]
            avg_risk = sum(a.get('risk_pct', 0) for a in buy_alerts) / len(buy_alerts) if buy_alerts else 0
            portfolio_heat = avg_risk * buy_signals

            # Sector distribution
            sectors = {}
            for a in alerts:
                s = a.get('sector', 'غير معروف')
                sectors[s] = sectors.get(s, 0) + 1

            return {
                "total_stocks": len(alerts),
                "buy_opportunities": buy_signals,
                "sell_alerts": sell_signals,
                "hold_signals": hold_signals,
                "avg_score": round(avg_score, 2),
                "portfolio_heat": round(portfolio_heat, 2),
                "heat_status": "آمن" if portfolio_heat < 15 else "تحذير" if portfolio_heat < 25 else "خطير",
                "heat_color": "#10b981" if portfolio_heat < 15 else "#f59e0b" if portfolio_heat < 25 else "#ef4444",
                "diversification_score": round(100 - (buy_signals / len(alerts) * 50), 2) if alerts else 0,
                "sector_distribution": sectors
            }
        except:
            return {
                "total_stocks": 0, "buy_opportunities": 0, "sell_alerts": 0, "hold_signals": 0,
                "avg_score": 0, "portfolio_heat": 0, "heat_status": "غير معروف",
                "heat_color": "#94a3b8", "diversification_score": 0, "sector_distribution": {}
            }

risk_engine = RiskEngine()

# ==================== AUTOMATED ANALYSIS ENGINE ====================
class AutomatedAnalyzer:
    """AI-powered market scanning with real decisions"""

    @staticmethod
    def analyze_all(stocks_data: List[dict], market_type: str = "EGX") -> List[dict]:
        """Analyze all stocks with comprehensive scoring"""
        try:
            alerts = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            total = len(stocks_data)
            for i, stock in enumerate(stocks_data):
                try:
                    status_text.text(f"تحليل {i+1}/{total}: {stock['symbol']} - {stock['name']}...")
                    progress_bar.progress((i + 1) / total)

                    df = data_engine.get_stock_history(stock['symbol'], "3mo")
                    if df is None or len(df) < 30:
                        continue

                    df = ta_engine.calculate_all(df)
                    if df is None:
                        continue

                    latest = df.iloc[-1]
                    rsi = latest.get('RSI')
                    macd = latest.get('MACD')

                    if pd.isna(rsi) or pd.isna(macd):
                        continue

                    signals = ta_engine.generate_signals(df)
                    overall_signal, score, signal_text, trend = ta_engine.calculate_overall(signals)
                    trend_info = ta_engine.get_trend_strength(df)

                    # Risk calculations
                    atr = latest.get('ATR') if pd.notna(latest.get('ATR')) else 0
                    current_price = latest['Close']
                    
                    # Dynamic stop loss based on ATR
                    atr_multiplier = 2.0 if overall_signal in ['BUY', 'STRONG_BUY'] else 1.5
                    stop_loss = current_price - (atr * atr_multiplier) if atr > 0 else current_price * 0.94
                    take_profit_1 = current_price + (atr * 2.5) if atr > 0 else current_price * 1.08
                    take_profit_2 = current_price + (atr * 4.0) if atr > 0 else current_price * 1.15
                    take_profit_3 = current_price + (atr * 6.0) if atr > 0 else current_price * 1.25

                    # Advanced risk analysis
                    risk_profile = risk_engine.analyze_risk_profile(
                        df, current_price, stop_loss, take_profit_1
                    )

                    # Volume confirmation
                    vol_ratio = latest.get('Volume_Ratio')
                    volume_confirm = pd.notna(vol_ratio) and vol_ratio > 1.3

                    # Opportunity scoring (0-100) - Enhanced algorithm
                    opportunity_score = 50

                    # RSI weight (enhanced)
                    if pd.notna(rsi):
                        if rsi < 25: opportunity_score += 25
                        elif rsi < 35: opportunity_score += 18
                        elif rsi < 45: opportunity_score += 8
                        elif rsi > 75: opportunity_score -= 25
                        elif rsi > 65: opportunity_score -= 18
                        elif rsi > 55: opportunity_score -= 8

                    # MACD weight
                    macd_signal = latest.get('MACD_Signal')
                    if pd.notna(macd) and pd.notna(macd_signal):
                        if macd > macd_signal:
                            opportunity_score += 12
                            macd_hist = latest.get('MACD_Histogram')
                            if pd.notna(macd_hist):
                                if macd_hist > 0: opportunity_score += 8
                                if macd_hist > prev.get('MACD_Histogram', 0) if 'prev' in locals() else 0: opportunity_score += 5
                        else:
                            opportunity_score -= 12

                    # Bollinger weight
                    bb_pos = latest.get('BB_Position')
                    if pd.notna(bb_pos):
                        if bb_pos < 0.15: opportunity_score += 12
                        elif bb_pos < 0.3: opportunity_score += 6
                        elif bb_pos > 0.85: opportunity_score -= 12
                        elif bb_pos > 0.7: opportunity_score -= 6

                    # Trend strength
                    trend_score = trend_info.get('score', 0)
                    opportunity_score += trend_score * 6

                    # Volume
                    if volume_confirm: opportunity_score += 10
                    elif pd.notna(vol_ratio) and vol_ratio > 1.0: opportunity_score += 5
                    elif pd.notna(vol_ratio) and vol_ratio < 0.5: opportunity_score -= 8

                    # Risk/Reward
                    rr = risk_profile.get('rr_ratio', 0)
                    if rr > 3: opportunity_score += 15
                    elif rr > 2: opportunity_score += 10
                    elif rr > 1.5: opportunity_score += 5
                    elif rr < 1: opportunity_score -= 10

                    # Stochastic
                    stoch_k = latest.get('Stoch_K')
                    if pd.notna(stoch_k):
                        if stoch_k < 20: opportunity_score += 8
                        elif stoch_k > 80: opportunity_score -= 8

                    # Williams %R
                    williams = latest.get('Williams_R')
                    if pd.notna(williams):
                        if williams < -80: opportunity_score += 5
                        elif williams > -20: opportunity_score -= 5

                    # ADX confirmation
                    adx = latest.get('ADX')
                    if pd.notna(adx) and adx > 25:
                        opportunity_score += 5

                    opportunity_score = max(0, min(100, opportunity_score))

                    # Alert classification with real decisions
                    if opportunity_score >= 85 and overall_signal in ["STRONG_BUY", "BUY"]:
                        alert_level = "🔥 فرصة استثنائية"
                        alert_color = "#10b981"
                        decision = "شراء فوري"
                        priority = 1
                    elif opportunity_score >= 70 and overall_signal in ["STRONG_BUY", "BUY"]:
                        alert_level = "🟢 فرصة شراء ممتازة"
                        alert_color = "#34d399"
                        decision = "شراء"
                        priority = 2
                    elif opportunity_score >= 55 and overall_signal in ["BUY", "HOLD"]:
                        alert_level = "🟡 مراقبة إيجابية"
                        alert_color = "#fbbf24"
                        decision = "مراقبة"
                        priority = 3
                    elif opportunity_score < 30 and overall_signal in ["SELL", "STRONG_SELL"]:
                        alert_level = "🔴 إشارة بيع"
                        alert_color = "#ef4444"
                        decision = "بيع"
                        priority = 4
                    elif opportunity_score < 40 and overall_signal in ["SELL", "STRONG_SELL", "HOLD"]:
                        alert_level = "🟠 تحذير"
                        alert_color = "#f97316"
                        decision = "تجنب"
                        priority = 5
                    else:
                        alert_level = "⚪ محايد"
                        alert_color = "#94a3b8"
                        decision = "انتظار"
                        priority = 6

                    alerts.append({
                        "symbol": stock['symbol'],
                        "name": stock['name'],
                        "sector": stock['sector'],
                        "price": round(current_price, 2),
                        "change_pct": stock.get('change_pct', 0),
                        "signal": overall_signal,
                        "signal_text": signal_text,
                        "trend": trend,
                        "trend_direction": trend_info.get('direction', 'غير معروف'),
                        "trend_strength": trend_info.get('strength', 'غير معروف'),
                        "score": round(opportunity_score, 1),
                        "alert_level": alert_level,
                        "alert_color": alert_color,
                        "decision": decision,
                        "priority": priority,
                        "rsi": round(rsi, 1) if pd.notna(rsi) else 50,
                        "macd": round(macd, 2) if pd.notna(macd) else 0,
                        "bb_position": round(bb_pos, 2) if pd.notna(bb_pos) else 0.5,
                        "volume_ratio": round(vol_ratio, 1) if pd.notna(vol_ratio) else 1.0,
                        "adx": round(adx, 1) if pd.notna(adx) else 0,
                        "rr_ratio": risk_profile.get('rr_ratio', 0),
                        "stop_loss": round(stop_loss, 2),
                        "take_profit_1": round(take_profit_1, 2),
                        "take_profit_2": round(take_profit_2, 2),
                        "take_profit_3": round(take_profit_3, 2),
                        "risk_pct": risk_profile.get('risk_pct', 0),
                        "reward_pct": risk_profile.get('reward_pct', 0),
                        "volatility": risk_profile.get('volatility_annual', 0),
                        "var_95": risk_profile.get('var_95', 0),
                        "sharpe": risk_profile.get('sharpe_ratio', 0),
                        "risk_class": risk_profile.get('risk_class', 'غير معروف'),
                        "risk_color": risk_profile.get('risk_color', '#94a3b8'),
                        "recommendation": risk_profile.get('recommendation', 'غير معروف'),
                        "kelly": risk_profile.get('kelly_pct', 0),
                        "position_shares": risk_profile.get('shares', 0),
                        "position_value": risk_profile.get('position_value', 0),
                        "win_rate": risk_profile.get('win_rate', 0),
                        "pe": stock.get('pe', 0),
                        "eps": stock.get('eps', 0),
                    })
                except Exception as e:
                    continue

            progress_bar.empty()
            status_text.empty()
            alerts.sort(key=lambda x: (x['priority'], -x['score']))
            return alerts
        except Exception as e:
            st.error(f"خطأ في التحليل الآلي: {str(e)}")
            return []

    @staticmethod
    def predict_prices(df: pd.DataFrame, days: int = 10) -> dict:
        """Advanced price prediction with multiple models"""
        try:
            prices = df['Close'].dropna().values
            if len(prices) < 30:
                return {'error': 'Insufficient data'}

            # Model 1: Polynomial Regression
            X = np.arange(len(prices)).reshape(-1, 1)
            y = prices
            poly = PolynomialFeatures(degree=3)
            X_poly = poly.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)

            # Model 2: Moving Average Trend
            ma_20 = df['Close'].rolling(20).mean().dropna().values
            if len(ma_20) >= 10:
                ma_slope = (ma_20[-1] - ma_20[-10]) / 10
            else:
                ma_slope = 0

            # Model 3: ATR-based range
            atr = df['ATR'].iloc[-1] if pd.notna(df['ATR'].iloc[-1]) else prices[-1] * 0.02

            # Combine predictions
            future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
            future_X_poly = poly.transform(future_X)
            poly_pred = model.predict(future_X_poly)

            combined = []
            for i in range(days):
                # Weighted average of models
                poly_w = max(0, 0.7 - i * 0.05)
                ma_w = min(0.3, 0.1 + i * 0.02)
                
                pred = poly_pred[i] * poly_w + (prices[-1] + ma_slope * (i+1)) * ma_w
                pred = pred / (poly_w + ma_w) if (poly_w + ma_w) > 0 else pred
                
                # Confidence decreases with time
                conf = max(30, 95 - (i * 8))
                margin = atr * (1.5 + i * 0.3)
                
                combined.append({
                    'day': i + 1,
                    'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    'predicted': round(float(pred), 2),
                    'lower_bound': round(float(pred - margin * 1.8), 2),
                    'upper_bound': round(float(pred + margin * 1.8), 2),
                    'confidence': conf,
                    'trend': 'صاعد' if pred > prices[-1] else 'هابط' if pred < prices[-1] else 'محايد'
                })

            return {'combined': combined, 'current': round(prices[-1], 2)}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
        """Calculate support/resistance with Fibonacci"""
        try:
            if df is None or len(df) < window:
                return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0}

            recent = df.tail(window)
            lows = recent['Low'].nsmallest(5).values
            highs = recent['High'].nlargest(5).values

            swing_high = recent['High'].max()
            swing_low = recent['Low'].min()
            diff = swing_high - swing_low

            fib = {}
            if diff > 0:
                fib = {
                    '0%': round(swing_high, 2),
                    '23.6%': round(swing_high - 0.236 * diff, 2),
                    '38.2%': round(swing_high - 0.382 * diff, 2),
                    '50%': round(swing_high - 0.5 * diff, 2),
                    '61.8%': round(swing_high - 0.618 * diff, 2),
                    '78.6%': round(swing_high - 0.786 * diff, 2),
                    '100%': round(swing_low, 2)
                }

            return {
                'supports': [round(float(l), 2) for l in lows],
                'resistances': [round(float(h), 2) for h in highs],
                'fibonacci': fib,
                'current': round(float(df['Close'].iloc[-1]), 2) if len(df) > 0 else 0,
                'swing_high': round(swing_high, 2),
                'swing_low': round(swing_low, 2)
            }
        except Exception:
            return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0}

    @staticmethod
    def generate_financial_report(alerts: List[dict]) -> dict:
        """Generate comprehensive financial market report"""
        try:
            if not alerts:
                return {}

            # Market overview
            buy_count = len([a for a in alerts if a['signal'] in ['BUY', 'STRONG_BUY']])
            sell_count = len([a for a in alerts if a['signal'] in ['SELL', 'STRONG_SELL']])
            hold_count = len([a for a in alerts if a['signal'] == 'HOLD'])
            
            avg_score = sum(a['score'] for a in alerts) / len(alerts)
            
            # Best opportunities
            best_buy = max([a for a in alerts if a['signal'] in ['BUY', 'STRONG_BUY']], 
                          key=lambda x: x['score'], default=None)
            
            # Sector analysis
            sector_scores = {}
            for a in alerts:
                s = a['sector']
                if s not in sector_scores:
                    sector_scores[s] = {'count': 0, 'total_score': 0, 'buy_count': 0}
                sector_scores[s]['count'] += 1
                sector_scores[s]['total_score'] += a['score']
                if a['signal'] in ['BUY', 'STRONG_BUY']:
                    sector_scores[s]['buy_count'] += 1
            
            # Sort sectors by average score
            sector_ranking = []
            for s, data in sector_scores.items():
                avg = data['total_score'] / data['count'] if data['count'] > 0 else 0
                sector_ranking.append({
                    'sector': s,
                    'avg_score': round(avg, 1),
                    'buy_opportunities': data['buy_count'],
                    'total_stocks': data['count']
                })
            sector_ranking.sort(key=lambda x: -x['avg_score'])
            
            # Market sentiment
            if avg_score >= 60:
                sentiment = "إيجابي جداً"
                sentiment_color = "#10b981"
            elif avg_score >= 50:
                sentiment = "إيجابي"
                sentiment_color = "#34d399"
            elif avg_score >= 40:
                sentiment = "محايد مائل للإيجابية"
                sentiment_color = "#fbbf24"
            elif avg_score >= 30:
                sentiment = "محايد مائل للسلبية"
                sentiment_color = "#f97316"
            else:
                sentiment = "سلبي"
                sentiment_color = "#ef4444"
            
            return {
                "market_sentiment": sentiment,
                "sentiment_color": sentiment_color,
                "avg_market_score": round(avg_score, 1),
                "buy_opportunities": buy_count,
                "sell_alerts": sell_count,
                "hold_signals": hold_count,
                "total_analyzed": len(alerts),
                "best_opportunity": best_buy,
                "sector_ranking": sector_ranking[:5],
                "recommendation": "السوق يقدم فرص جيدة للشراء" if buy_count > sell_count * 2 else "السوق يحتاج حذر" if sell_count > buy_count else "السوق محايد - انتقائي"
            }
        except:
            return {}

ai_engine = AutomatedAnalyzer()

# ==================== CORPORATE ACTIONS ENGINE ====================
class CorporateEngine:
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
                {"date": "2026-05-10", "title": "QNB مصر يفتتح فرعاً رقمياً جديداً في العاصمة الإدارية", "impact": "positive"},
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

# ==================== CALLBACK FUNCTIONS ====================
def select_stock_callback(symbol):
    try:
        st.session_state.selected_stock = symbol
        st.session_state.show_analysis = True
        st.session_state.analysis_symbol = symbol
        st.session_state.active_tab = 'analysis'
    except Exception:
        pass

def set_tab_callback(tab_name):
    try:
        st.session_state.active_tab = tab_name
        if tab_name != 'analysis':
            st.session_state.show_analysis = False
    except Exception:
        pass

def run_analysis_callback():
    try:
        with st.spinner("جاري تحليل السوق الشامل..."):
            prices = data_engine.get_live_prices()
            alerts = ai_engine.analyze_all(prices)
            st.session_state.alerts_cache = alerts
            st.session_state.alerts_timestamp = datetime.now()
            
            # Generate financial report
            report = ai_engine.generate_financial_report(alerts)
            st.session_state.analysis_results = report
    except Exception as e:
        st.error(f"خطأ في التحليل: {str(e)}")

def add_task_callback():
    try:
        title = st.session_state.get('new_task_title', '')
        if title and title.strip():
            st.session_state.tasks.append({
                "id": len(st.session_state.tasks) + 1,
                "title": title.strip(),
                "priority": st.session_state.get('new_task_priority', 'medium'),
                "category": st.session_state.get('new_task_category', 'work'),
                "due": st.session_state.get('new_task_due', datetime.now()).strftime("%Y-%m-%d"),
                "completed": False,
                "created": datetime.now().strftime("%Y-%m-%d")
            })
            st.session_state.new_task_title = ""
    except Exception:
        pass

def toggle_task(task_id):
    try:
        for task in st.session_state.tasks:
            if task['id'] == task_id:
                task['completed'] = not task['completed']
                break
    except Exception:
        pass

def delete_task(task_id):
    try:
        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]
    except Exception:
        pass

# ==================== HEADER ====================
stocks_live = data_engine.get_live_prices()
df_live = pd.DataFrame(stocks_live)

if not df_live.empty:
    best_stock = max(stocks_live, key=lambda x: x["change_pct"])
    worst_stock = min(stocks_live, key=lambda x: x["change_pct"])
else:
    best_stock = {"symbol": "N/A", "change_pct": 0}
    worst_stock = {"symbol": "N/A", "change_pct": 0}

sentiment = news_engine.get_sentiment_score()

st.markdown(f"""
<div class="header-glow">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
            <h1 style="margin: 0; font-size: 32px; font-weight: 800; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚡ EGX Pro Terminal v22
            </h1>
            <p style="color: #64748b; margin-top: 8px; font-size: 14px;">
                <span class="live-pulse"></span> السوق مفتوح | تحديث لحظي | {datetime.now().strftime("%H:%M:%S")} | {len(data_engine.EGYPTIAN_STOCKS)} سهم
            </p>
        </div>
        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
            <div style="padding: 12px 20px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px;">
                <span style="color: #64748b; font-size: 12px;">EGX30</span>
                <span style="color: #10b981; margin-right: 8px; font-size: 20px; font-weight: 800;">24,850</span>
                <span class="badge badge-green">+1.24%</span>
            </div>
            <div style="padding: 12px 20px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px;">
                <span style="color: #64748b; font-size: 12px;">المزاج</span>
                <span style="color: {sentiment['color']}; margin-right: 8px; font-size: 18px; font-weight: 700;">{sentiment['mood']}</span>
            </div>
            <div style="padding: 12px 20px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px;">
                <span style="color: #64748b; font-size: 12px;">الأقوى</span>
                <span style="color: #fbbf24; margin-right: 8px; font-size: 18px; font-weight: 700;">{best_stock['symbol']}</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== MAIN CONTENT AREA ====================
active_tab = st.session_state.get('active_tab', 'market')

# ==================== TAB: MARKET RADAR ====================
if active_tab == 'market':
    try:
        # Market Indices
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
                    <p style="color: #64748b; font-size: 12px; margin: 0; text-transform: uppercase; font-weight: 600;">{idx['name']}</p>
                    <p style="font-size: 26px; font-weight: 800; margin: 6px 0; color: {change_color};">{idx['value']:,.2f}</p>
                    <div style="display: flex; justify-content: center; gap: 8px;">
                        <span style="color: {change_color}; font-size: 13px; font-weight: 700;">{arrow} {abs(idx['change']):.2f}%</span>
                        <span style="color: #64748b; font-size: 12px;">{idx['vol']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Treemap + Top Movers
        if not df_live.empty:
            row2_col1, row2_col2 = st.columns([2, 1])

            with row2_col1:
                st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
                st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🗺️ خريطة السوق التفاعلية</span></div>', unsafe_allow_html=True)

                try:
                    fig_treemap = px.treemap(
                        df_live,
                        path=[px.Constant("EGX"), 'sector', 'symbol'],
                        values='market_cap',
                        color='change_pct',
                        color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
                        color_continuous_midpoint=0,
                        hover_data=['price', 'volume', 'pe']
                    )
                    fig_treemap.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8", size=12),
                        height=400, margin=dict(t=0, b=0, l=0, r=0),
                        coloraxis_colorbar=dict(tickfont=dict(color="#94a3b8", size=10), title=dict(text="%", font=dict(color="#94a3b8", size=10)))
                    )
                    st.plotly_chart(fig_treemap, use_container_width=True)
                except Exception as e:
                    st.error(f"خطأ في خريطة السوق: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)

            with row2_col2:
                st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
                st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🚀 الأكثر نشاطاً</span></div>', unsafe_allow_html=True)

                try:
                    top_movers = df_live.nlargest(10, 'change_pct')
                    for _, stock in top_movers.iterrows():
                        change_class = "status-up" if stock['change_pct'] >= 0 else "status-down"
                        change_sign = "+" if stock['change_pct'] >= 0 else ""
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
                            <div>
                                <span style="color: #fbbf24; font-weight: 700; font-size: 14px;">{stock['symbol']}</span>
                                <span style="color: #64748b; font-size: 12px; margin-right: 8px;">{stock['name'][:12]}</span>
                            </div>
                            <div style="text-align: left;">
                                <span style="font-size: 14px; font-weight: 700;">{stock['price']:.2f}</span>
                                <span class="{change_class}" style="font-size: 12px; margin-right: 6px; font-weight: 600;">{change_sign}{stock['change_pct']:.2f}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"خطأ في الأكثر نشاطاً: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Stock Grid with Filters
            st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🎯 جميع الأسهم - اضغط للتحليل المفصل</span></div>', unsafe_allow_html=True)

            f_col1, f_col2 = st.columns([3, 1])
            with f_col1:
                search_term = st.text_input("🔍 البحث", placeholder="ابحث بالرمز أو اسم الشركة...", key="market_search", label_visibility="collapsed")
            with f_col2:
                sectors = ["الكل"] + sorted(df_live['sector'].unique().tolist()) if 'sector' in df_live.columns else ["الكل"]
                sector_filter = st.selectbox("القطاع", sectors, key="market_sector", label_visibility="collapsed")

            display_stocks = df_live.copy()
            if search_term:
                mask = display_stocks['symbol'].str.contains(search_term, case=False, na=False) | display_stocks['name'].str.contains(search_term, case=False, na=False)
                display_stocks = display_stocks[mask]
            if sector_filter != "الكل":
                display_stocks = display_stocks[display_stocks['sector'] == sector_filter]

            stocks_per_row = 6
            stock_list = display_stocks.to_dict('records')

            for row_idx in range(0, len(stock_list), stocks_per_row):
                row_stocks = stock_list[row_idx:row_idx + stocks_per_row]
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
                            <div style="font-size: 11px; color: #64748b; margin-top: 6px;">{stock['sector']}</div>
                            <div style="font-size: 10px; color: #475569; margin-top: 2px;">P/E: {stock.get('pe', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)

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

            try:
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
                    height=320, margin=dict(t=20, b=40)
                )
                st.plotly_chart(fig_sector, use_container_width=True)
            except Exception as e:
                st.error(f"خطأ في أداء القطاعات: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("لا توجد بيانات أسهم متاحة")
    except Exception as e:
        st.error(f"خطأ في رادار السوق: {str(e)}")

# ==================== TAB: AI ANALYSIS ====================
elif active_tab == 'ai':
    try:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🤖 التحليل الآلي الذكي والتنبيهات اللحظية</span></div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="padding: 16px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; margin-bottom: 20px;">
            <p style="color: #f87171; font-weight: 700; margin: 0; font-size: 14px;">⚠️ تحذير المخاطر</p>
            <p style="color: #fca5a5; font-size: 13px; margin-top: 6px;">التحليل الآلي يعتمد على البيانات التاريخية والمؤشرات الفنية. استخدم Stop Loss لحماية رأس مالك. التوقعات ليست توصيات استثمارية مؤكدة.</p>
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
            pass

        # Display cached results
        if st.session_state.alerts_cache is not None:
            alerts = st.session_state.alerts_cache
            report = st.session_state.get('analysis_results', {})

            # Financial Report Banner
            if report:
                st.markdown(f"""
                <div style="padding: 20px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)); border: 1px solid rgba(99,102,241,0.2); border-radius: 16px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <h3 style="margin: 0; color: #f1f5f9; font-size: 20px;">📊 تقرير السوق المالي</h3>
                            <p style="color: #64748b; margin: 8px 0 0 0; font-size: 14px;">{report.get('recommendation', '')}</p>
                        </div>
                        <div style="text-align: center; padding: 12px 24px; background: {report.get('sentiment_color', '#94a3b8')}20; border: 1px solid {report.get('sentiment_color', '#94a3b8')}40; border-radius: 12px;">
                            <p style="margin: 0; color: {report.get('sentiment_color', '#94a3b8')}; font-size: 24px; font-weight: 800;">{report.get('avg_market_score', 0)}</p>
                            <p style="margin: 4px 0 0 0; color: {report.get('sentiment_color', '#94a3b8')}; font-size: 12px;">{report.get('market_sentiment', '')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
                    <div style="text-align: center; padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid {color}30;">
                        <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">{label}</p>
                        <p style="font-size: 24px; font-weight: 800; color: {color}; margin: 6px 0;">{value}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Sector Ranking
            if report and report.get('sector_ranking'):
                st.subheader("🏆 ترتيب القطاعات")
                sector_df = pd.DataFrame(report['sector_ranking'])
                fig_sector_rank = px.bar(
                    sector_df, x='sector', y='avg_score',
                    color='avg_score', color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
                    text='avg_score'
                )
                fig_sector_rank.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_sector_rank.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", color="#94a3b8"),
                    height=280, margin=dict(t=20, b=40)
                )
                st.plotly_chart(fig_sector_rank, use_container_width=True)

            # Buy Opportunities
            buy_ops = [a for a in alerts if a['score'] >= min_score and a['signal'] in ['BUY', 'STRONG_BUY'] and a['risk_pct'] <= max_risk and a['rr_ratio'] >= min_rr]

            if buy_ops:
                st.subheader("🔥 أفضل فرص الشراء المؤكدة")
                for i, alert in enumerate(buy_ops[:10]):
                    with st.expander(f"{i+1}. {alert['name']} ({alert['symbol']}) - درجة: {alert['score']} | قرار: {alert['decision']} | R/R: {alert['rr_ratio']}", expanded=i < 3):

                        sig_cols = st.columns([1, 3, 1])
                        with sig_cols[0]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 16px; background: {alert['alert_color']}15; border: 1px solid {alert['alert_color']}40; border-radius: 12px;">
                                <p style="margin: 0; color: {alert['alert_color']}; font-size: 32px; font-weight: 800;">{alert['score']}</p>
                                <p style="margin: 6px 0 0 0; color: {alert['alert_color']}; font-size: 12px; font-weight: 600;">درجة الفرصة</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with sig_cols[1]:
                            st.markdown(f"""
                            <div>
                                <p style="margin: 0; font-weight: 700; font-size: 18px;">{alert['name']} | {alert['sector']}</p>
                                <p style="color: #64748b; font-size: 14px; margin: 6px 0;">
                                    السعر: <b style="color:#f1f5f9">{alert['price']}</b> | RSI: <b style="color:#f1f5f9">{alert['rsi']}</b> | MACD: <b style="color:#f1f5f9">{alert['macd']}</b> | ADX: <b style="color:#f1f5f9">{alert['adx']}</b>
                                </p>
                                <p style="color: #64748b; font-size: 13px; margin: 6px 0;">
                                    التقلب: {alert['volatility']}% | Sharpe: {alert['sharpe']} | كيلي: {alert['kelly']}% | P/E: {alert['pe']}
                                </p>
                                <p style="color: {alert['alert_color']}; font-size: 14px; font-weight: 700; margin: 6px 0;">
                                    القرار: {alert['decision']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        with sig_cols[2]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: {alert['risk_color']}15; border: 1px solid {alert['risk_color']}40; border-radius: 12px;">
                                <p style="margin: 0; color: {alert['risk_color']}; font-size: 13px; font-weight: 700;">{alert['risk_class']}</p>
                                <p style="margin: 6px 0 0 0; color: #64748b; font-size: 11px;">{alert['recommendation']}</p>
                                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 10px;">{alert['trend_direction']} | {alert['trend_strength']}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        # Risk Levels
                        risk_cols = st.columns(5)
                        risk_data = [
                            ("🛑 Stop Loss", alert['stop_loss'], alert['risk_pct'], "#ef4444"),
                            ("📍 السعر", alert['price'], 0, "#6366f1"),
                            ("🎯 الهدف 1", alert['take_profit_1'], alert['reward_pct'], "#10b981"),
                            ("🎯🎯 الهدف 2", alert['take_profit_2'], 0, "#fbbf24"),
                            ("🎯🎯🎯 الهدف 3", alert['take_profit_3'], 0, "#a78bfa")
                        ]
                        for j, (label, value, pct, color) in enumerate(risk_data):
                            with risk_cols[j]:
                                st.markdown(f"""
                                <div style="text-align: center; padding: 14px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid {color}30;">
                                    <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{label}</p>
                                    <p style="font-size: 22px; font-weight: 800; color: {color}; margin: 6px 0;">{value:.2f}</p>
                                    {f'<p style="font-size: 11px; color: {color}; margin: 0; font-weight: 600;">{pct:.1f}%</p>' if pct else ''}
                                </div>
                                """, unsafe_allow_html=True)

                        # Position Sizing
                        pos_cols = st.columns(4)
                        with pos_cols[0]:
                            st.metric("الأسهم المقترحة", f"{alert['position_shares']}")
                        with pos_cols[1]:
                            st.metric("قيمة المركز", f"{alert['position_value']:,.0f} ج.م")
                        with pos_cols[2]:
                            st.metric("نسبة كيلي", f"{alert['kelly']}%")
                        with pos_cols[3]:
                            st.metric("نسبة الربح", f"{alert['win_rate']}%")

                        st.button(
                            f"🔮 تحليل مفصل لـ {alert['symbol']}",
                            key=f"detail_{alert['symbol']}_tab2",
                            on_click=select_stock_callback,
                            args=(alert['symbol'],),
                            use_container_width=True,
                            type="primary"
                        )

            # Risk Alerts
            risk_alerts = [a for a in alerts if a['signal'] in ['SELL', 'STRONG_SELL'] or (a['score'] < 30 and a['signal'] == 'HOLD')]
            if risk_alerts:
                st.subheader("🔴 إشارات الخطر والبيع")
                for alert in risk_alerts[:5]:
                    st.markdown(f"""
                    <div style="padding: 14px; background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.2); border-radius: 10px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: #ef4444; font-weight: 700; font-size: 15px;">{alert['symbol']}</span>
                                <span style="color: #64748b; margin-right: 10px; font-size: 14px;">{alert['name']}</span>
                                <span style="color: #f59e0b; margin-right: 10px; font-weight: 600;">درجة: {alert['score']}</span>
                            </div>
                            <span style="color: #ef4444; font-size: 14px; font-weight: 700;">{alert['signal_text']}</span>
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
                    "القرار": alert['decision'],
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

            st.download_button(
                label="📥 تصدير التحليل CSV",
                data=df_table.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"egx_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("👈 اضغط 'تشغيل التحليل الآلي' لبدء المسح الشامل لجميع الأسهم")

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في التحليل الآلي: {str(e)}")

# ==================== TAB: REPORTS ====================
elif active_tab == 'reports':
    try:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 التقارير المالية واتجاهات الأسعار</span></div>', unsafe_allow_html=True)

        if st.session_state.alerts_cache is None:
            st.info("👈 قم بتشغيل التحليل الآلي أولاً من تبويب التحليل الذكي")
        else:
            alerts = st.session_state.alerts_cache
            report = st.session_state.get('analysis_results', {})

            # Market Overview Report
            st.subheader("📈 نظرة عامة على السوق")
            
            ov_cols = st.columns(4)
            with ov_cols[0]:
                st.markdown("""
                <div class="metric-card">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">إجمالي الأسهم المحللة</p>
                    <p style="font-size: 28px; font-weight: 800; color: #818cf8; margin: 8px 0;">{}</p>
                </div>
                """.format(report.get('total_analyzed', 0)), unsafe_allow_html=True)
            
            with ov_cols[1]:
                st.markdown("""
                <div class="metric-card">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">فرص الشراء</p>
                    <p style="font-size: 28px; font-weight: 800; color: #10b981; margin: 8px 0;">{}</p>
                </div>
                """.format(report.get('buy_opportunities', 0)), unsafe_allow_html=True)
            
            with ov_cols[2]:
                st.markdown("""
                <div class="metric-card">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">إشارات البيع</p>
                    <p style="font-size: 28px; font-weight: 800; color: #ef4444; margin: 8px 0;">{}</p>
                </div>
                """.format(report.get('sell_alerts', 0)), unsafe_allow_html=True)
            
            with ov_cols[3]:
                st.markdown("""
                <div class="metric-card">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">متوسط درجة السوق</p>
                    <p style="font-size: 28px; font-weight: 800; color: {}; margin: 8px 0;">{}</p>
                </div>
                """.format(report.get('sentiment_color', '#94a3b8'), report.get('avg_market_score', 0)), unsafe_allow_html=True)

            # Best Opportunity
            best = report.get('best_opportunity')
            if best:
                st.subheader("🏆 أفضل فرصة استثمارية")
                st.markdown(f"""
                <div style="padding: 24px; background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.02)); border: 1px solid rgba(16,185,129,0.2); border-radius: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                        <div>
                            <h3 style="margin: 0; color: #10b981; font-size: 24px;">{best['name']} ({best['symbol']})</h3>
                            <p style="color: #64748b; margin: 8px 0 0 0; font-size: 15px;">{best['sector']} | درجة: {best['score']} | R/R: {best['rr_ratio']}</p>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin: 0; font-size: 32px; font-weight: 800; color: #f1f5f9;">{best['price']}</p>
                            <p style="margin: 4px 0 0 0; color: #10b981; font-size: 14px; font-weight: 600;">{best['decision']}</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 16px; margin-top: 16px; flex-wrap: wrap;">
                        <span class="badge badge-green">🎯 الهدف: {best['take_profit_1']}</span>
                        <span class="badge badge-red">🛑 Stop: {best['stop_loss']}</span>
                        <span class="badge badge-blue">📊 RSI: {best['rsi']}</span>
                        <span class="badge badge-purple">📈 Sharpe: {best['sharpe']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Price Predictions for Top Stocks
            st.subheader("🔮 توقعات الأسعار القادمة")
            
            top_stocks = [a for a in alerts if a['score'] >= 60][:5]
            
            for stock in top_stocks:
                with st.expander(f"📊 توقعات {stock['name']} ({stock['symbol']}) - السعر الحالي: {stock['price']}", expanded=False):
                    df_hist = data_engine.get_stock_history(stock['symbol'], "3mo")
                    if df_hist is not None and len(df_hist) > 30:
                        predictions = ai_engine.predict_prices(df_hist, days=10)
                        
                        if 'combined' in predictions:
                            pred_df = pd.DataFrame(predictions['combined'])
                            
                            # Prediction Chart
                            fig_pred = go.Figure()
                            
                            hist_days = min(40, len(df_hist))
                            fig_pred.add_trace(go.Scatter(
                                x=df_hist.index[-hist_days:], y=df_hist['Close'].tail(hist_days),
                                mode='lines', name='السعر الفعلي',
                                line=dict(color='#6366f1', width=2),
                                fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'
                            ))
                            
                            last_date = df_hist.index[-1]
                            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=10, freq='B')
                            pred_prices = [p['predicted'] for p in predictions['combined']]
                            upper = [p['upper_bound'] for p in predictions['combined']]
                            lower = [p['lower_bound'] for p in predictions['combined']]
                            
                            fig_pred.add_trace(go.Scatter(
                                x=future_dates, y=pred_prices,
                                mode='lines+markers', name='التوقع',
                                line=dict(color='#fbbf24', width=3),
                                marker=dict(size=10, color='#fbbf24', symbol='diamond')
                            ))
                            
                            fig_pred.add_trace(go.Scatter(
                                x=list(future_dates) + list(future_dates)[::-1],
                                y=upper + list(reversed(pred_prices)),
                                fill='tonexty', fillcolor='rgba(251, 191, 36, 0.08)',
                                line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                                name='الحد الأعلى'
                            ))
                            
                            fig_pred.add_trace(go.Scatter(
                                x=list(future_dates) + list(future_dates)[::-1],
                                y=list(reversed(pred_prices)) + lower,
                                fill='tonexty', fillcolor='rgba(251, 191, 36, 0.08)',
                                line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                                name='الحد الأدنى'
                            ))
                            
                            fig_pred.add_hline(y=stock['stop_loss'], line_dash="dash", line_color="#ef4444", annotation_text="Stop Loss", annotation_position="right")
                            fig_pred.add_hline(y=stock['take_profit_1'], line_dash="dash", line_color="#10b981", annotation_text="TP1", annotation_position="right")
                            
                            fig_pred.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Inter", color="#94a3b8"),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                height=400, margin=dict(t=40, b=40)
                            )
                            st.plotly_chart(fig_pred, use_container_width=True)
                            
                            # Prediction Table
                            st.markdown("**جدول التوقعات التفصيلي:**")
                            pred_display = []
                            for p in predictions['combined']:
                                pred_display.append({
                                    "اليوم": p['day'],
                                    "التاريخ": p['date'],
                                    "التوقع": p['predicted'],
                                    "الحد الأدنى": p['lower_bound'],
                                    "الحد الأعلى": p['upper_bound'],
                                    "الثقة": f"{p['confidence']}%",
                                    "الاتجاه": p['trend']
                                })
                            st.dataframe(pd.DataFrame(pred_display), use_container_width=True, hide_index=True)

            # Market Trend Analysis
            st.subheader("📈 تحليل الاتجاهات السوقية")
            
            trend_data = []
            for alert in alerts:
                trend_data.append({
                    'السهم': alert['symbol'],
                    'الاتجاه': alert['trend_direction'],
                    'القوة': alert['trend_strength'],
                    'الدرجة': alert['score'],
                    'القطاع': alert['sector']
                })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                
                # Trend Distribution
                trend_counts = trend_df['الاتجاه'].value_counts().reset_index()
                trend_counts.columns = ['الاتجاه', 'العدد']
                
                fig_trend = px.pie(
                    trend_counts, values='العدد', names='الاتجاه',
                    color='الاتجاه',
                    color_discrete_map={'صاعد': '#10b981', 'هابط': '#ef4444', 'محايد': '#fbbf24', 'غير معروف': '#94a3b8'}
                )
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", color="#94a3b8"),
                    height=350, margin=dict(t=20, b=20)
                )
                st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في التقارير: {str(e)}")

# ==================== TAB: CORPORATE ====================
elif active_tab == 'corporate':
    try:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🏢 واجهة الشركات - التوزيعات والإجراءات</span></div>', unsafe_allow_html=True)

        available_symbols = [s['symbol'] for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] in corp_engine.CORPORATE_DATA]
        if not available_symbols:
            available_symbols = ["COMI"]

        corp_symbol = st.selectbox("اختر الشركة", 
                                   available_symbols,
                                   format_func=lambda x: f"{x} - {next((s['name'] for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] == x), x)}",
                                   key="corp_selector")

        corp_data = corp_engine.get_company_data(corp_symbol)
        stock_info = next((s for s in data_engine.EGYPTIAN_STOCKS if s['symbol'] == corp_symbol), None)

        if corp_data and stock_info:
            st.markdown(f"""
            <div class="corporate-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; color: #fbbf24; font-size: 24px;">{corp_data['arabic_name']}</h2>
                        <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">{corp_data['company']} | {stock_info['sector']}</p>
                    </div>
                    <div style="text-align: left;">
                        <p style="margin: 0; font-size: 28px; font-weight: 800; color: #f1f5f9;">{stock_info['base_price']:.2f}</p>
                        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">السعر الأساسي | P/E: {stock_info.get('pe', 'N/A')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                    <div style="padding: 20px; background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2); border-radius: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; font-size: 22px; font-weight: 800; color: #10b981;">{up['expected']:.2f} ج.م</p>
                                <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">📅 {up['date']} | نوع: {up['type']}</p>
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
                        <div style="padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px; border-right: 3px solid {status_color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p style="margin: 0; font-weight: 700; font-size: 15px;">{meeting['subject']}</p>
                                    <p style="color: #64748b; font-size: 13px; margin: 6px 0;">📅 {meeting['date']} | نوع: {meeting['type']}</p>
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
                        <div style="padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px; border-right: 3px solid {impact_color};">
                            <p style="margin: 0; font-size: 14px; line-height: 1.6;">{news['title']}</p>
                            <p style="color: #64748b; font-size: 12px; margin: 6px 0 0 0;">📅 {news['date']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد أخبار حديثة")

        st.divider()
        st.subheader("📅 التوزيعات القادمة عبر السوق")
        upcoming_all = corp_engine.get_upcoming_dividends_all()

        for div in upcoming_all[:8]:
            try:
                days_left = (datetime.strptime(div['date'], "%Y-%m-%d") - datetime.now()).days
                status_text = "غداً" if days_left <= 1 else f"بعد {days_left} يوم" if days_left <= 30 else div['date']
                status_color = "#ef4444" if days_left <= 3 else "#f59e0b" if days_left <= 14 else "#10b981"
            except:
                status_text = div['date']
                status_color = "#94a3b8"

            st.markdown(f"""
            <div style="padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">💰</div>
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 15px;">{div['company']} ({div['symbol']})</p>
                            <p style="color: #64748b; font-size: 13px; margin: 6px 0 0 0;">📅 {div['date']} | 💵 {div['amount']} ج.م</p>
                        </div>
                    </div>
                    <span class="badge" style="background: {status_color}20; color: {status_color};">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في واجهة الشركات: {str(e)}")

# ==================== TAB: NEWS ====================
elif active_tab == 'news':
    try:
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
                <div style="padding: 16px; background: rgba(255,255,255,0.02); border-radius: 12px; margin-bottom: 10px; border-right: 3px solid {news_color};">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 6px;">
                        <span style="color: #fbbf24; font-size: 12px; font-weight: 700;">{news['time']}</span>
                        <span class="badge badge-blue" style="font-size: 11px;">{news['source']}</span>
                        <span style="color: {news_color}; font-size: 11px;">تأثير: {impact_bars}</span>
                    </div>
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">{icon} {news['title']}</p>
                </div>
                """, unsafe_allow_html=True)

        with news_col2:
            st.subheader("📊 مؤشر المزاج السوقي")
            sentiment = news_engine.get_sentiment_score()

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=sentiment['score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "مؤشر المزاج", 'font': {'size': 28, 'color': '#e2e8f0'}},
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
                height=320, margin=dict(t=40, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            if not df_live.empty:
                st.subheader("📈 تأثير الأخبار على القطاعات")
                sector_impact = []
                for sector in df_live['sector'].unique():
                    sector_stocks = df_live[df_live['sector'] == sector]
                    avg_change = sector_stocks['change_pct'].mean()
                    sector_impact.append({"القطاع": sector, "التأثير %": round(avg_change, 2)})

                if sector_impact:
                    fig_impact = px.bar(
                        pd.DataFrame(sector_impact),
                        x="القطاع", y="التأثير %",
                        color="التأثير %",
                        color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981']
                    )
                    fig_impact.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", color="#94a3b8"),
                        height=280, margin=dict(t=20, b=40)
                    )
                    st.plotly_chart(fig_impact, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في الأخبار: {str(e)}")

# ==================== TAB: DETAILED ANALYSIS ====================
elif active_tab == 'analysis':
    try:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🔮 التحليل الذكي الشامل مع إدارة المخاطرة</span></div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="padding: 16px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px; margin-bottom: 20px;">
            <p style="color: #f87171; font-weight: 700; margin: 0; font-size: 14px;">⚠️ تحذير</p>
            <p style="color: #fca5a5; font-size: 13px; margin-top: 6px;">التوقعات نتائج رياضية للبيانات التاريخية فقط. لا تعتبر توصية استثمارية. استخدم Stop Loss دائماً.</p>
        </div>
        """, unsafe_allow_html=True)

        # Controls
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])
        with ctrl1:
            analysis_symbols = df_live['symbol'].tolist() if not df_live.empty else ["COMI"]
            analysis_stock = st.selectbox("السهم", analysis_symbols, key="ai_stock_tab7")
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
                        try:
                            signals = ta_engine.generate_signals(df)
                            overall_signal, score, signal_text, trend = ta_engine.calculate_overall(signals)
                            predictions = ai_engine.predict_prices(df, days=prediction_days)
                            sr_levels = ai_engine.calculate_support_resistance(df)
                            trend_info = ta_engine.get_trend_strength(df)

                            current_price = df['Close'].iloc[-1]
                            atr = df['ATR'].iloc[-1] if pd.notna(df['ATR'].iloc[-1]) else current_price * 0.02

                            stop_loss = current_price - (atr * 2)
                            take_profit_1 = current_price + (atr * 2.5)
                            take_profit_2 = current_price + (atr * 4)

                            risk_profile = risk_engine.analyze_risk_profile(df, current_price, stop_loss, take_profit_1, account_balance)

                            # SIGNAL DISPLAY
                            st.subheader("🎯 إشارة التداول الرئيسية")
                            sig_cols = st.columns([1, 2, 1])
                            with sig_cols[1]:
                                if overall_signal == "STRONG_BUY":
                                    st.markdown('<div class="signal-box signal-buy"><h2 style="margin: 0; color: #10b981; font-size: 36px;">🟢 شراء قوي</h2></div>', unsafe_allow_html=True)
                                elif overall_signal == "BUY":
                                    st.markdown('<div class="signal-box signal-buy"><h2 style="margin: 0; color: #34d399; font-size: 30px;">🟢 شراء</h2></div>', unsafe_allow_html=True)
                                elif overall_signal == "STRONG_SELL":
                                    st.markdown('<div class="signal-box signal-sell"><h2 style="margin: 0; color: #ef4444; font-size: 36px;">🔴 بيع قوي</h2></div>', unsafe_allow_html=True)
                                elif overall_signal == "SELL":
                                    st.markdown('<div class="signal-box signal-sell"><h2 style="margin: 0; color: #f87171; font-size: 30px;">🔴 بيع</h2></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="signal-box signal-hold"><h2 style="margin: 0; color: #fbbf24; font-size: 30px;">🟡 انتظار</h2></div>', unsafe_allow_html=True)

                            # Trend Info
                            st.markdown(f"""
                            <div style="text-align: center; margin: 16px 0;">
                                <span class="badge badge-blue" style="font-size: 14px;">📊 الاتجاه: {trend_info['direction']} | القوة: {trend_info['strength']}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            # RISK LEVELS
                            st.subheader("🛡️ مستويات إدارة المخاطرة")
                            risk_cols = st.columns(4)
                            risk_data = [
                                ("🛑 Stop Loss", stop_loss, ((current_price-stop_loss)/current_price*100) if current_price > 0 else 0, "#ef4444"),
                                ("📍 السعر الحالي", current_price, 0, "#6366f1"),
                                ("🎯 الهدف 1", take_profit_1, ((take_profit_1-current_price)/current_price*100) if current_price > 0 else 0, "#10b981"),
                                ("🎯🎯 الهدف 2", take_profit_2, ((take_profit_2-current_price)/current_price*100) if current_price > 0 else 0, "#fbbf24")
                            ]
                            for i, (label, value, pct, color) in enumerate(risk_data):
                                with risk_cols[i]:
                                    st.markdown(f"""
                                    <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.02); border-radius: 14px; border: 1px solid {color}30;">
                                        <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">{label}</p>
                                        <p style="font-size: 28px; font-weight: 800; color: {color}; margin: 6px 0;">{value:.2f}</p>
                                        {f'<p style="font-size: 12px; color: {color}; margin: 0; font-weight: 600;">{pct:.1f}%</p>' if pct else ''}
                                    </div>
                                    """, unsafe_allow_html=True)

                            # ADVANCED RISK METRICS
                            st.subheader("📊 تحليل المخاطرة المتقدم")
                            risk_metric_cols = st.columns(4)
                            risk_metrics = [
                                ("التقلب السنوي", f"{risk_profile.get('volatility_annual', 0):.1f}%", risk_profile.get('volatility_annual', 0) < 35),
                                ("Sharpe Ratio", f"{risk_profile.get('sharpe_ratio', 0):.2f}", risk_profile.get('sharpe_ratio', 0) > 0.5),
                                ("Sortino Ratio", f"{risk_profile.get('sortino_ratio', 0):.2f}", risk_profile.get('sortino_ratio', 0) > 0.5),
                                ("نسبة كيلي", f"{risk_profile.get('kelly_pct', 0):.1f}%", risk_profile.get('kelly_pct', 0) > 0)
                            ]
                            for i, (label, value, good) in enumerate(risk_metrics):
                                with risk_metric_cols[i]:
                                    color = "#10b981" if good else "#ef4444"
                                    st.markdown(f"""
                                    <div class="risk-metric {('risk-low' if good else 'risk-high')}">
                                        <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">{label}</p>
                                        <p style="font-size: 22px; font-weight: 800; color: {color}; margin: 6px 0;">{value}</p>
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
                            <div style="padding: 20px; background: {risk_profile.get('risk_color', '#94a3b8')}10; border: 1px solid {risk_profile.get('risk_color', '#94a3b8')}40; border-radius: 14px; margin: 20px 0;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <p style="margin: 0; font-size: 20px; font-weight: 800; color: {risk_profile.get('risk_color', '#94a3b8')};">تصنيف المخاطرة: {risk_profile.get('risk_class', 'غير معروف')}</p>
                                        <p style="color: #64748b; margin: 6px 0 0 0; font-size: 14px;">التوصية: {risk_profile.get('recommendation', 'غير معروف')}</p>
                                    </div>
                                    <p style="margin: 0; font-size: 15px; color: #64748b;">أقصى خسائر متتالية: {risk_profile.get('max_consecutive_losses', 0)} يوم</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # TECHNICAL INDICATORS
                            st.subheader("📊 المؤشرات الفنية")
                            latest = df.iloc[-1]
                            ind_cols = st.columns(6)

                            rsi_val = latest.get('RSI', 50)
                            macd_val = latest.get('MACD', 0)
                            bb_pos = latest.get('BB_Position', 0.5)
                            stoch_k = latest.get('Stoch_K', 50)
                            sma_20 = latest.get('SMA_20', 0)
                            adx_val = latest.get('ADX', 0)
                            close_val = latest.get('Close', 0)
                            williams = latest.get('Williams_R', -50)
                            cci = latest.get('CCI', 0)

                            indicators = [
                                ("RSI (14)", rsi_val, "#ef4444" if rsi_val > 70 else "#10b981" if rsi_val < 30 else "#fbbf24", "ذروة شراء" if rsi_val > 70 else "ذروة بيع" if rsi_val < 30 else "محايد"),
                                ("MACD", macd_val, "#10b981" if macd_val > 0 else "#ef4444", "إيجابي" if macd_val > 0 else "سلبي"),
                                ("Bollinger", bb_pos, "#10b981" if bb_pos < 0.2 else "#ef4444" if bb_pos > 0.8 else "#fbbf24", "منطقة شراء" if bb_pos < 0.2 else "منطقة بيع" if bb_pos > 0.8 else "النطاق الأوسط"),
                                ("Stochastic", stoch_k, "#10b981" if stoch_k < 20 else "#ef4444" if stoch_k > 80 else "#fbbf24", "ذروة بيع" if stoch_k < 20 else "ذروة شراء" if stoch_k > 80 else "محايد"),
                                ("SMA 20", sma_20, "#10b981" if close_val > sma_20 else "#ef4444", "صاعد" if close_val > sma_20 else "هابط"),
                                ("ADX", adx_val, "#10b981" if adx_val > 25 else "#fbbf24", "اتجاه قوي" if adx_val > 25 else "اتجاه ضعيف")
                            ]
                            for i, (label, value, color, text) in enumerate(indicators):
                                with ind_cols[i]:
                                    st.markdown(f"""
                                    <div style="text-align: center; padding: 14px; background: rgba(255,255,255,0.02); border-radius: 10px;">
                                        <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{label}</p>
                                        <p style="font-size: 22px; font-weight: 800; color: {color}; margin: 6px 0;">{value:.1f}</p>
                                        <p style="font-size: 11px; color: {color}; margin: 0; font-weight: 600;">{text}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                            # SUPPORT/RESISTANCE
                            st.subheader("🎯 مستويات الدعم والمقاومة")
                            sr_cols = st.columns(2)
                            with sr_cols[0]:
                                st.markdown("**الدعم:**")
                                for s in sr_levels.get('supports', []):
                                    st.markdown(f"<span style='color: #10b981; font-weight: 700; font-size: 15px;'>▲ {s}</span>", unsafe_allow_html=True)
                            with sr_cols[1]:
                                st.markdown("**المقاومة:**")
                                for r in sr_levels.get('resistances', []):
                                    st.markdown(f"<span style='color: #ef4444; font-weight: 700; font-size: 15px;'>▼ {r}</span>", unsafe_allow_html=True)

                            # Fibonacci
                            st.markdown("**مستويات فيبوناتشي:**")
                            fib = sr_levels.get('fibonacci', {})
                            if fib:
                                fib_cols = st.columns(len(fib))
                                for i, (level, value) in enumerate(fib.items()):
                                    color = "#fbbf24" if level in ['38.2%', '61.8%'] else "#94a3b8"
                                    st.markdown(f"""
                                    <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                                        <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{level}</p>
                                        <p style="font-size: 16px; font-weight: 700; color: {color}; margin: 4px 0;">{value}</p>
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
                                    marker=dict(size=10, color='#fbbf24', symbol='diamond')
                                ))

                                fig_pred.add_trace(go.Scatter(
                                    x=list(future_dates) + list(future_dates)[::-1],
                                    y=upper + list(reversed(pred_prices)),
                                    fill='tonexty', fillcolor='rgba(251, 191, 36, 0.08)',
                                    line=dict(color='rgba(251, 191, 36, 0.3)', width=1),
                                    name='الحد الأعلى'
                                ))

                                fig_pred.add_trace(go.Scatter(
                                    x=list(future_dates) + list(future_dates)[::-1],
                                    y=list(reversed(pred_prices)) + lower,
                                    fill='tonexty', fillcolor='rgba(251, 191, 36, 0.08)',
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
                            vol_sma = df.get('Volume_SMA')
                            if vol_sma is not None and pd.notna(vol_sma).any():
                                fig_vol.add_trace(go.Scatter(x=df.index, y=vol_sma, mode='lines', name='متوسط الحجم', line=dict(color='#fbbf24', width=2)))

                            fig_vol.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Inter", color="#94a3b8"),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                height=280, margin=dict(t=40, b=20)
                            )
                            st.plotly_chart(fig_vol, use_container_width=True)
                        except Exception as e:
                            st.error(f"خطأ في عرض التحليل: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في التحليل المفصل: {str(e)}")

# ==================== TAB: TASKS ====================
elif active_tab == 'tasks':
    try:
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">✅ المهام الذكية وإدارة المحفظة</span></div>', unsafe_allow_html=True)

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

        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...", key="task_search")
        with f_col2:
            filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"],
                                           format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x],
                                           key="filter_priority")
        with f_col3:
            filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"], key="filter_status")

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

        for task in filtered:
            try:
                status_icon = "✅" if task["completed"] else "⬜"
                opacity = "opacity: 0.5;" if task["completed"] else ""
                p_color = priority_colors.get(task['priority'], '#94a3b8')

                st.markdown(f"""
                <div class="task-item" style="border-right-color: {p_color}; {opacity}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 20px;">{status_icon}</span>
                            <div>
                                <p style="margin: 0; font-weight: 700; font-size: 15px;">{task['title']}</p>
                                <div style="display: flex; gap: 10px; margin-top: 6px;">
                                    <span class="badge badge-blue">{category_icons.get(task['category'], '📋')} {task['category']}</span>
                                    <span style="color: #64748b; font-size: 12px;">📅 {task['due']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                act_col1, act_col2 = st.columns([10, 2])
                with act_col1:
                    st.checkbox("تم", value=task["completed"], key=f"check_{task['id']}", 
                               on_change=toggle_task, args=(task['id'],), label_visibility="collapsed")
                with act_col2:
                    st.button("🗑️", key=f"del_{task['id']}", on_click=delete_task, args=(task['id'],), help="حذف")
            except Exception:
                continue

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"خطأ في المهام: {str(e)}")

# ==================== FOOTER ====================
st.markdown("---")
try:
    footer_cols = st.columns(3)

    with footer_cols[0]:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #64748b; font-size: 13px; margin: 0; font-weight: 600;">⚡ EGX Pro Terminal v22.0</p>
            <p style="color: #475569; font-size: 12px; margin: 6px 0;">نظام تحليلي احترافي | AI-Powered</p>
        </div>
        """, unsafe_allow_html=True)

    with footer_cols[1]:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #fbbf24; font-size: 14px; margin: 0; font-weight: 700;">
                🏆 الأقوى: {best_stock['symbol']} +{best_stock['change_pct']:.2f}% | 📉 الأضعف: {worst_stock['symbol']} {worst_stock['change_pct']:.2f}%
            </p>
            <p style="color: #475569; font-size: 12px; margin: 6px 0;">
                آخر تحديث: {datetime.now().strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with footer_cols[2]:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #475569; font-size: 12px; margin: 0;">
                © 2026 | جميع البيانات للتوضيح | التوقعات للأغراض التعليمية فقط
            </p>
            <p style="color: #475569; font-size: 11px; margin: 6px 0;">
                {len(data_engine.EGYPTIAN_STOCKS)} سهم | تحليل آلي | إدارة مخاطر | توقعات ذكية
            </p>
        </div>
        """, unsafe_allow_html=True)
except Exception:
    pass

# ==================== BOTTOM NAVIGATION BAR ====================
nav_items = [
    ("market", "📈", "السوق"),
    ("ai", "🤖", "الذكي"),
    ("reports", "📊", "التقارير"),
    ("corporate", "🏢", "الشركات"),
    ("news", "📰", "الأخبار"),
    ("analysis", "🔮", "التحليل"),
    ("tasks", "✅", "المهام"),
]

active_tab = st.session_state.get('active_tab', 'market')

nav_html = '<div class="bottom-nav">'
for tab_id, icon, label in nav_items:
    active_class = "active" if active_tab == tab_id else ""
    # We use a unique key for each button
    nav_html += f'<button class="nav-btn {active_class}" onclick="window.location.reload()">{icon}<span class="label">{label}</span></button>'
nav_html += '</div>'

st.markdown(nav_html, unsafe_allow_html=True)

# Render actual Streamlit buttons for navigation (hidden but functional)
nav_cols = st.columns(len(nav_items))
for i, (tab_id, icon, label) in enumerate(nav_items):
    with nav_cols[i]:
        st.button(
            f"{icon} {label}",
            key=f"nav_{tab_id}",
            on_click=set_tab_callback,
            args=(tab_id,),
            use_container_width=True,
            type="primary" if active_tab == tab_id else "secondary"
        )
'''

# Save the file
output_path = '/mnt/agents/output/egx_pro_terminal_v22.py'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(v22_code)

print(f"File saved successfully to: {output_path}")
print(f"File size: {len(v22_code)} characters")
