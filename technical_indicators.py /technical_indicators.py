import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
import os

warnings.filterwarnings('ignore')

# ==================== ADVANCED CONFIGURATION ====================
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v24 | نظام التوصيات الذكي", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL DARK THEME CSS v24 ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', 'Cairo', sans-serif !important; letter-spacing: -0.01em; }
    .main { background: linear-gradient(180deg, #07070d 0%, #0f0f1a 50%, #07070d 100%); color: #e2e8f0; }

    /* ===== ENHANCED SIDEBAR ===== */
    .nav-item {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 6px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 13px;
        font-weight: 500;
        color: #94a3b8;
        border: 1px solid transparent;
        position: relative;
        overflow: hidden;
    }
    .nav-item:hover {
        background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
        color: #e2e8f0;
        border-color: rgba(99,102,241,0.25);
        transform: translateX(4px);
    }
    .nav-item.active {
        background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.15));
        color: #818cf8;
        border-color: rgba(99,102,241,0.4);
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(99,102,241,0.15);
    }
    .nav-item.active::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #6366f1, #8b5cf6);
        border-radius: 0 3px 3px 0;
    }
    .nav-icon { font-size: 18px; width: 28px; text-align: center; }
    .nav-badge {
        margin-right: auto;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 700;
        background: rgba(16,185,129,0.2);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
    }

    /* ===== ENHANCED STOCK CARDS ===== */
    .stock-card-rect {
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 16px 18px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    .stock-card-rect:hover {
        border-color: rgba(99,102,241,0.3);
        transform: translateX(5px) translateY(-2px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.12);
    }
    .stock-card-rect::before {
        content: '';
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: transparent;
        transition: all 0.3s;
        border-radius: 0 14px 14px 0;
    }
    .stock-card-rect.buy-signal::before { background: linear-gradient(180deg, #10b981, #059669); }
    .stock-card-rect.sell-signal::before { background: linear-gradient(180deg, #ef4444, #dc2626); }
    .stock-card-rect.hold-signal::before { background: linear-gradient(180deg, #f59e0b, #d97706); }
    .stock-card-rect.neutral-signal::before { background: linear-gradient(180deg, #64748b, #475569); }

    .stock-rect-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
    .stock-rect-symbol { font-size: 16px; font-weight: 800; color: #fbbf24; letter-spacing: 0.02em; }
    .stock-rect-name { font-size: 12px; color: #64748b; }
    .stock-rect-sector { font-size: 11px; color: #475569; }

    .stock-rect-price-section { text-align: left; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; min-width: 90px; }
    .stock-rect-price { font-size: 19px; font-weight: 800; color: #f1f5f9; }
    .stock-rect-change { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 20px; display: inline-block; }
    .stock-rect-change.up { background: rgba(16,185,129,0.15); color: #10b981; }
    .stock-rect-change.down { background: rgba(239,68,68,0.15); color: #ef4444; }

    /* ===== RECOMMENDATION BADGES ===== */
    .rec-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.02em;
        gap: 4px;
    }
    .rec-strong-buy { background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05)); color: #10b981; border: 1px solid rgba(16,185,129,0.3); box-shadow: 0 2px 8px rgba(16,185,129,0.15); }
    .rec-buy { background: linear-gradient(135deg, rgba(52,211,153,0.15), rgba(52,211,153,0.05)); color: #34d399; border: 1px solid rgba(52,211,153,0.25); }
    .rec-hold { background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05)); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
    .rec-sell { background: linear-gradient(135deg, rgba(248,113,113,0.15), rgba(248,113,113,0.05)); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }
    .rec-strong-sell { background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.05)); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); box-shadow: 0 2px 8px rgba(239,68,68,0.15); }
    .rec-watch { background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(99,102,241,0.05)); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }

    /* ===== COMPACT BUTTONS ===== */
    .card-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .btn-compact {
        flex: 1;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(99,102,241,0.25);
        background: rgba(99,102,241,0.08);
        color: #818cf8;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    .btn-compact:hover {
        background: rgba(99,102,241,0.15);
        border-color: rgba(99,102,241,0.4);
        color: #a5b4fc;
        transform: translateY(-1px);
    }

    .badge { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; }
    .badge-green { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }
    .badge-red { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
    .badge-yellow { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
    .badge-blue { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
    .badge-purple { background: rgba(139,92,246,0.12); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }

    .pro-panel { 
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98)); 
        border: 1px solid rgba(255,255,255,0.06); 
        border-radius: 16px; 
        padding: 24px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.5); 
        margin-bottom: 20px; 
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .pro-panel:hover { border-color: rgba(99,102,241,0.15); }
    .pro-panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.06); }
    .pro-panel-title { font-size: 15px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; }

    .status-up { color: #10b981; } .status-down { color: #ef4444; } .status-neutral { color: #94a3b8; } .status-warning { color: #f59e0b; }
    .live-pulse { display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse-live 2s infinite; margin-left: 8px; box-shadow: 0 0 8px #10b981; }
    @keyframes pulse-live { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } }

    .signal-box { border-radius: 14px; padding: 28px; text-align: center; border: 1px solid; transition: all 0.3s ease; }
    .signal-box:hover { transform: translateY(-2px); }
    .signal-buy { background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.02)); border-color: rgba(16,185,129,0.4); }
    .signal-sell { background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(239,68,68,0.02)); border-color: rgba(239,68,68,0.4); }
    .signal-hold { background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(245,158,11,0.02)); border-color: rgba(245,158,11,0.4); }

    .indicator-card { padding: 20px; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px; transition: all 0.2s; }
    .indicator-card:hover { border-color: rgba(99,102,241,0.15); transform: translateY(-1px); }
    .indicator-value { font-size: 28px; font-weight: 800; margin: 8px 0; }
    .indicator-desc { font-size: 12px; color: #64748b; line-height: 1.6; }

    .pillar-card { padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.02); transition: all 0.3s; }
    .pillar-card:hover { border-color: rgba(99,102,241,0.25); transform: translateY(-3px); box-shadow: 0 4px 20px rgba(99,102,241,0.08); }
    .pillar-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; }
    .pillar-score { font-size: 26px; font-weight: 800; }
    .pillar-bar { height: 6px; border-radius: 3px; background: rgba(255,255,255,0.05); overflow: hidden; margin-top: 8px; }
    .pillar-fill { height: 100%; border-radius: 3px; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }

    .task-item { padding: 14px; background: rgba(255,255,255,0.02); border-radius: 10px; margin-bottom: 10px; border-right: 3px solid; transition: all 0.2s; }
    .task-item:hover { background: rgba(255,255,255,0.04); transform: translateX(2px); }

    .fund-card {
        padding: 20px;
        background: linear-gradient(145deg, rgba(25,25,35,0.9), rgba(20,20,30,0.95));
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    .fund-card:hover { border-color: rgba(99,102,241,0.2); transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }

    .dividend-card {
        padding: 16px;
        background: rgba(16,185,129,0.03);
        border: 1px solid rgba(16,185,129,0.1);
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s;
    }
    .dividend-card:hover { border-color: rgba(16,185,129,0.25); transform: translateX(3px); }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: #f1f5f9 !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0a14 0%, #131326 100%); border-right: 1px solid rgba(255,255,255,0.05); }

    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .sub-nav {
        display: flex;
        gap: 8px;
        margin-bottom: 24px;
        padding: 8px;
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .sub-nav-item {
        padding: 10px 18px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
        background: transparent;
        flex: 1;
        text-align: center;
    }
    .sub-nav-item:hover { color: #e2e8f0; background: rgba(255,255,255,0.03); }
    .sub-nav-item.active { background: rgba(99,102,241,0.15); color: #818cf8; }

    /* ===== RECOMMENDATION PANEL ===== */
    .rec-panel {
        background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.04));
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .rec-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
    }
    .rec-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .rec-title {
        font-size: 16px;
        font-weight: 700;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .rec-count {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(16,185,129,0.15);
        color: #34d399;
        border: 1px solid rgba(16,185,129,0.3);
    }

    /* ===== TRENDING TICKER ===== */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background: rgba(99,102,241,0.05);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 8px;
        padding: 10px 0;
        margin-bottom: 20px;
        white-space: nowrap;
    }
    .ticker {
        display: inline-block;
        animation: ticker 30s linear infinite;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item {
        display: inline-block;
        padding: 0 24px;
        font-size: 13px;
        font-weight: 600;
    }

    /* ===== SCORE RING ===== */
    .score-ring {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        font-weight: 800;
        font-size: 18px;
    }
    .score-ring::before {
        content: '';
        position: absolute;
        inset: 4px;
        border-radius: 50%;
        background: #12121a;
    }
    .score-ring span {
        position: relative;
        z-index: 1;
    }

    /* ===== HEATMAP CELL ===== */
    .heatmap-cell {
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        transition: all 0.2s;
        cursor: pointer;
    }
    .heatmap-cell:hover { transform: scale(1.05); z-index: 10; }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session_state():
    defaults = {
        'selected_stock': None,
        'show_analysis': False,
        'analysis_symbol': None,
        'market_data_cache': {},
        'price_history_sim': {},
        'alerts_cache': None,
        'alerts_timestamp': None,
        'risk_settings': {'max_risk_pct': 2.0, 'max_portfolio_heat': 25.0, 'min_rr': 1.5},
        'tasks': [
            {"id": 1, "title": "مراجعة أداء سهم CIB", "priority": "high", "category": "work", "due": "2026-05-15", "completed": False},
            {"id": 2, "title": "تحليل تقرير البورصة الأسبوعي", "priority": "medium", "category": "work", "due": "2026-05-16", "completed": True},
            {"id": 3, "title": "قراءة كتاب الاستثمار الذكي", "priority": "low", "category": "learning", "due": "2026-05-20", "completed": False},
            {"id": 4, "title": "متابعة اجتماع عمومية البنك التجاري", "priority": "high", "category": "urgent", "due": "2026-05-14", "completed": False},
            {"id": 5, "title": "تحديث بيانات المحفظة الاستثمارية", "priority": "medium", "category": "personal", "due": "2026-05-13", "completed": False},
        ],
        'active_section': 'market',
        'active_subsection': None,
        'company_fundamental_data': {},
        'edit_company_symbol': None,
        'eod_recommendations': None,
        'eod_timestamp': None,
        'global_recommendations': None,
        'last_scan_time': None,
        'watchlist': [],
        'notification_queue': [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== ENHANCED DATA ENGINE ====================
class EGXDataEngine:
    """Advanced data engine with all EGX stocks"""

    EGYPTIAN_STOCKS = [
        # البنوك
        {"symbol": "COMI", "name": "البنك التجاري الدولي (CIB)", "sector": "بنوك", "base_price": 140.01, "volatility": 0.015, "market_cap": 420000000000, "beta": 1.05},
        {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "base_price": 58.14, "volatility": 0.012, "market_cap": 180000000000, "beta": 0.98},
        {"symbol": "ADIB", "name": "أبوظبي الإسلامي - مصر", "sector": "بنوك", "base_price": 47.49, "volatility": 0.018, "market_cap": 95000000000, "beta": 1.12},
        {"symbol": "HDBK", "name": "بنك الإسكان والتعمير", "sector": "بنوك", "base_price": 147.26, "volatility": 0.014, "market_cap": 220000000000, "beta": 0.92},
        {"symbol": "CANA", "name": "بنك قناة السويس", "sector": "بنوك", "base_price": 33.88, "volatility": 0.022, "market_cap": 45000000000, "beta": 1.25},
        {"symbol": "CIEB", "name": "كريدي أجريكول مصر", "sector": "بنوك", "base_price": 23.73, "volatility": 0.016, "market_cap": 32000000000, "beta": 0.88},
        {"symbol": "FAIT", "name": "بنك فيصل الإسلامي", "sector": "بنوك", "base_price": 34.11, "volatility": 0.015, "market_cap": 48000000000, "beta": 1.08},
        {"symbol": "SAUD", "name": "البنك البركة", "sector": "بنوك", "base_price": 24.70, "volatility": 0.017, "market_cap": 28000000000, "beta": 1.15},
        {"symbol": "UBEE", "name": "المصرف المتحد", "sector": "بنوك", "base_price": 13.98, "volatility": 0.025, "market_cap": 15000000000, "beta": 1.30},
        {"symbol": "EXPA", "name": "بنك التنمية والصادرات", "sector": "بنوك", "base_price": 18.68, "volatility": 0.019, "market_cap": 22000000000, "beta": 1.18},
        {"symbol": "BCDE", "name": "بنك القاهرة", "sector": "بنوك", "base_price": 19.50, "volatility": 0.020, "market_cap": 25000000000, "beta": 1.20},
        {"symbol": "NSGB", "name": "بنك ناصر الاجتماعي", "sector": "بنوك", "base_price": 21.30, "volatility": 0.018, "market_cap": 18000000000, "beta": 1.10},
        {"symbol": "MIDB", "name": "المصرف الدولي", "sector": "بنوك", "base_price": 16.80, "volatility": 0.021, "market_cap": 12000000000, "beta": 1.22},
        {"symbol": "ALHR", "name": "العربية لتمويل المساكن", "sector": "بنوك", "base_price": 8.45, "volatility": 0.028, "market_cap": 6500000000, "beta": 1.35},

        # تكنولوجيا مالية
        {"symbol": "EFIH", "name": "e-Finance للاستثمار", "sector": "تكنولوجيا مالية", "base_price": 22.32, "volatility": 0.028, "market_cap": 65000000000, "beta": 1.45},
        {"symbol": "FWRY", "name": "فوري لتكنولوجيا البنوك", "sector": "تكنولوجيا مالية", "base_price": 20.88, "volatility": 0.026, "market_cap": 52000000000, "beta": 1.38},
        {"symbol": "SCTS", "name": "مقاصة قناة السويس", "sector": "تكنولوجيا مالية", "base_price": 652.11, "volatility": 0.012, "market_cap": 130000000000, "beta": 0.85},
        {"symbol": "VALU", "name": "U للتمويل متناهي الصغر", "sector": "تكنولوجيا مالية", "base_price": 12.60, "volatility": 0.032, "market_cap": 18000000000, "beta": 1.55},
        {"symbol": "PAYH", "name": "Paymob Holdings", "sector": "تكنولوجيا مالية", "base_price": 15.40, "volatility": 0.035, "market_cap": 22000000000, "beta": 1.60},
        {"symbol": "MPAY", "name": "مدفوعات رقمية", "sector": "تكنولوجيا مالية", "base_price": 9.80, "volatility": 0.030, "market_cap": 14000000000, "beta": 1.48},

        # عقارات
        {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "base_price": 98.25, "volatility": 0.016, "market_cap": 280000000000, "beta": 1.02},
        {"symbol": "EMFD", "name": "إعمار مصر للتنمية", "sector": "عقارات", "base_price": 11.10, "volatility": 0.024, "market_cap": 55000000000, "beta": 1.28},
        {"symbol": "PHDC", "name": "بالم هيلز للتطوير", "sector": "عقارات", "base_price": 14.00, "volatility": 0.021, "market_cap": 42000000000, "beta": 1.22},
        {"symbol": "ORHD", "name": "أوراسكوم للتنمية", "sector": "عقارات", "base_price": 33.35, "volatility": 0.018, "market_cap": 78000000000, "beta": 1.15},
        {"symbol": "OCDI", "name": "السادس من أكتوبر للتنمية (سوديك)", "sector": "عقارات", "base_price": 22.98, "volatility": 0.017, "market_cap": 65000000000, "beta": 1.08},
        {"symbol": "HELI", "name": "الهلال والصليب الأحمر", "sector": "عقارات", "base_price": 7.85, "volatility": 0.026, "market_cap": 18000000000, "beta": 1.32},
        {"symbol": "ELSH", "name": "الشمس للإسكان", "sector": "عقارات", "base_price": 5.40, "volatility": 0.028, "market_cap": 8500000000, "beta": 1.40},
        {"symbol": "MNHD", "name": "مدينة نصر للإسكان", "sector": "عقارات", "base_price": 18.60, "volatility": 0.019, "market_cap": 25000000000, "beta": 1.18},
        {"symbol": "NREA", "name": "الرؤية للتطوير العقاري", "sector": "عقارات", "base_price": 4.20, "volatility": 0.032, "market_cap": 5500000000, "beta": 1.45},
        {"symbol": "ELEC", "name": "العاصمة الإدارية للاستثمار", "sector": "عقارات", "base_price": 3.85, "volatility": 0.035, "market_cap": 4200000000, "beta": 1.55},

        # صناعة
        {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "base_price": 89.51, "volatility": 0.015, "market_cap": 180000000000, "beta": 0.95},
        {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "base_price": 317.00, "volatility": 0.020, "market_cap": 95000000000, "beta": 1.10},
        {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "base_price": 87.19, "volatility": 0.014, "market_cap": 72000000000, "beta": 0.90},
        {"symbol": "MFPC", "name": "موبكو للأسمدة", "sector": "صناعة", "base_price": 45.15, "volatility": 0.019, "market_cap": 48000000000, "beta": 1.05},
        {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "base_price": 58.00, "volatility": 0.016, "market_cap": 35000000000, "beta": 1.12},
        {"symbol": "CEFM", "name": "السويس للأسمنت", "sector": "صناعة", "base_price": 42.30, "volatility": 0.018, "market_cap": 28000000000, "beta": 1.15},
        {"symbol": "SCEM", "name": "جنوب الوادي للأسمنت", "sector": "صناعة", "base_price": 28.50, "volatility": 0.020, "market_cap": 22000000000, "beta": 1.18},
        {"symbol": "MICH", "name": "المصرية للاتصالات (صناعة)", "sector": "صناعة", "base_price": 15.20, "volatility": 0.022, "market_cap": 12000000000, "beta": 1.25},
        {"symbol": "HELI2", "name": "الهلال للصناعات الغذائية", "sector": "صناعة", "base_price": 12.80, "volatility": 0.024, "market_cap": 9500000000, "beta": 1.28},
        {"symbol": "SPIN", "name": "الغزل والنسيج", "sector": "صناعة", "base_price": 6.40, "volatility": 0.030, "market_cap": 4500000000, "beta": 1.42},
        {"symbol": "MEPA", "name": "العربية للمحابس", "sector": "صناعة", "base_price": 9.60, "volatility": 0.025, "market_cap": 6800000000, "beta": 1.30},
        {"symbol": "MISR", "name": "مصر لصناعة الكيماويات", "sector": "صناعة", "base_price": 14.20, "volatility": 0.022, "market_cap": 8500000000, "beta": 1.22},
        {"symbol": "KZPC", "name": "كيما", "sector": "صناعة", "base_price": 32.80, "volatility": 0.017, "market_cap": 18000000000, "beta": 1.15},
        {"symbol": "EPCO", "name": "النصر لحل الألياف", "sector": "صناعة", "base_price": 8.90, "volatility": 0.026, "market_cap": 5200000000, "beta": 1.35},
        {"symbol": "NMPH", "name": "النصر لمحطمات البلاستيك", "sector": "صناعة", "base_price": 5.30, "volatility": 0.032, "market_cap": 3200000000, "beta": 1.48},
        {"symbol": "MOSC", "name": "المصرية للنشا والخميرة", "sector": "صناعة", "base_price": 18.40, "volatility": 0.019, "market_cap": 12000000000, "beta": 1.18},
        {"symbol": "UNIO", "name": "يونيفرسال للشحن", "sector": "صناعة", "base_price": 11.70, "volatility": 0.023, "market_cap": 7500000000, "beta": 1.28},

        # اتصالات
        {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "base_price": 98.49, "volatility": 0.013, "market_cap": 200000000000, "beta": 0.78},
        {"symbol": "EGSA", "name": "النايل سات", "sector": "اتصالات", "base_price": 9.09, "volatility": 0.018, "market_cap": 18000000000, "beta": 1.20},
        {"symbol": "TELE", "name": "اتصالات مصر", "sector": "اتصالات", "base_price": 0.75, "volatility": 0.015, "market_cap": 8500000000, "beta": 0.85},
        {"symbol": "MENA", "name": "MENA القابضة", "sector": "اتصالات", "base_price": 3.20, "volatility": 0.028, "market_cap": 4500000000, "beta": 1.38},

        # سلع استهلاكية
        {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "base_price": 40.31, "volatility": 0.012, "market_cap": 85000000000, "beta": 0.72},
        {"symbol": "EFID", "name": "إيديتا للصناعات الغذائية", "sector": "سلع استهلاكية", "base_price": 28.60, "volatility": 0.015, "market_cap": 62000000000, "beta": 0.88},
        {"symbol": "JUFO", "name": "جهينة للصناعات الغذائية", "sector": "سلع استهلاكية", "base_price": 28.90, "volatility": 0.014, "market_cap": 58000000000, "beta": 0.85},
        {"symbol": "DOMT", "name": "دومتي للأغذية", "sector": "سلع استهلاكية", "base_price": 26.00, "volatility": 0.022, "market_cap": 22000000000, "beta": 1.35},
        {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "base_price": 48.81, "volatility": 0.013, "market_cap": 38000000000, "beta": 0.92},
        {"symbol": "POUL", "name": "القاهرة للدواجن", "sector": "سلع استهلاكية", "base_price": 34.80, "volatility": 0.016, "market_cap": 28000000000, "beta": 1.05},
        {"symbol": "GBCO", "name": "GB Corp", "sector": "سلع استهلاكية", "base_price": 29.30, "volatility": 0.020, "market_cap": 45000000000, "beta": 1.18},
        {"symbol": "ORWE", "name": "النساجون الشرقيون", "sector": "سلع استهلاكية", "base_price": 23.56, "volatility": 0.015, "market_cap": 32000000000, "beta": 1.10},
        {"symbol": "FIHO", "name": "الفجر للزيوت", "sector": "سلع استهلاكية", "base_price": 19.40, "volatility": 0.018, "market_cap": 15000000000, "beta": 1.15},
        {"symbol": "CERA", "name": "سيراميكا كليوباترا", "sector": "سلع استهلاكية", "base_price": 4.80, "volatility": 0.035, "market_cap": 3800000000, "beta": 1.52},
        {"symbol": "RAKT", "name": "راكتا للورق", "sector": "سلع استهلاكية", "base_price": 3.90, "volatility": 0.032, "market_cap": 2800000000, "beta": 1.45},
        {"symbol": "MILS", "name": "مطاحن شرق الدلتا", "sector": "سلع استهلاكية", "base_price": 22.50, "volatility": 0.016, "market_cap": 12000000000, "beta": 1.08},
        {"symbol": "WATA", "name": "الوادى للصناعات الغذائية", "sector": "سلع استهلاكية", "base_price": 7.60, "volatility": 0.028, "market_cap": 5500000000, "beta": 1.38},
        {"symbol": "PRCL", "name": "بيراميزا للاستثمار", "sector": "سلع استهلاكية", "base_price": 2.80, "volatility": 0.040, "market_cap": 1800000000, "beta": 1.65},
        {"symbol": "MEPA2", "name": "المصرية للمنتجات الغذائية", "sector": "سلع استهلاكية", "base_price": 5.40, "volatility": 0.030, "market_cap": 3200000000, "beta": 1.42},

        # صحة
        {"symbol": "CLHO", "name": "كليوباترا للادوية", "sector": "صحة", "base_price": 14.94, "volatility": 0.021, "market_cap": 18000000000, "beta": 1.25},
        {"symbol": "PHAR", "name": "أمون للصناعات الدوائية", "sector": "صحة", "base_price": 89.49, "volatility": 0.014, "market_cap": 42000000000, "beta": 0.95},
        {"symbol": "ISPH", "name": "ابن سينا فارما", "sector": "صحة", "base_price": 11.96, "volatility": 0.019, "market_cap": 35000000000, "beta": 1.15},
        {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "base_price": 687.72, "volatility": 0.011, "market_cap": 85000000000, "beta": 0.68},
        {"symbol": "NIPH", "name": "النيل للأدوية", "sector": "صحة", "base_price": 173.20, "volatility": 0.013, "market_cap": 22000000000, "beta": 0.82},
        {"symbol": "ADCI", "name": "العربية للأدوية", "sector": "صحة", "base_price": 216.63, "volatility": 0.012, "market_cap": 28000000000, "beta": 0.75},
        {"symbol": "AXPH", "name": "الإسكندرية للأدوية", "sector": "صحة", "base_price": 1166.22, "volatility": 0.010, "market_cap": 65000000000, "beta": 0.65},
        {"symbol": "KAPH", "name": "القاهرة للأدوية", "sector": "صحة", "base_price": 45.80, "volatility": 0.015, "market_cap": 12000000000, "beta": 0.90},
        {"symbol": "MEDC", "name": "الدلتا للأدوية", "sector": "صحة", "base_price": 32.40, "volatility": 0.017, "market_cap": 8500000000, "beta": 0.95},
        {"symbol": "EPHO", "name": "العربية لصناعة المواد البلاستيكية", "sector": "صحة", "base_price": 8.70, "volatility": 0.024, "market_cap": 4500000000, "beta": 1.28},
        {"symbol": "UPAP", "name": "يونيباك للأدوية", "sector": "صحة", "base_price": 15.60, "volatility": 0.018, "market_cap": 6500000000, "beta": 1.12},

        # استثمار
        {"symbol": "HRHO", "name": "EFG هيرمس القابضة", "sector": "استثمار", "base_price": 29.50, "volatility": 0.023, "market_cap": 75000000000, "beta": 1.35},
        {"symbol": "BTFH", "name": "بلتون المالية القابضة", "sector": "استثمار", "base_price": 3.20, "volatility": 0.035, "market_cap": 8000000000, "beta": 1.65},
        {"symbol": "CCAP", "name": "قلعة القابضة", "sector": "استثمار", "base_price": 4.70, "volatility": 0.028, "market_cap": 12000000000, "beta": 1.55},
        {"symbol": "CICH", "name": "سي آي كابيتال", "sector": "استثمار", "base_price": 12.90, "volatility": 0.030, "market_cap": 15000000000, "beta": 1.48},
        {"symbol": "RAYA", "name": "راية القابضة", "sector": "استثمار", "base_price": 7.10, "volatility": 0.032, "market_cap": 22000000000, "beta": 1.52},
        {"symbol": "RACC", "name": "راية لخدمة العملاء", "sector": "استثمار", "base_price": 10.25, "volatility": 0.022, "market_cap": 18000000000, "beta": 1.28},
        {"symbol": "BINV", "name": "B للاستثمارات القابضة", "sector": "استثمار", "base_price": 42.00, "volatility": 0.018, "market_cap": 28000000000, "beta": 1.12},
        {"symbol": "FAITA", "name": "فاينانشال للاستثمار", "sector": "استثمار", "base_price": 6.80, "volatility": 0.030, "market_cap": 9500000000, "beta": 1.45},
        {"symbol": "SHRM", "name": "الشرقيون للاستثمار", "sector": "استثمار", "base_price": 4.20, "volatility": 0.032, "market_cap": 5500000000, "beta": 1.50},
        {"symbol": "AIND", "name": "العربية للصناعات الدقيقة", "sector": "استثمار", "base_price": 3.50, "volatility": 0.035, "market_cap": 4200000000, "beta": 1.55},
        {"symbol": "MCRO", "name": "Macro Capital", "sector": "استثمار", "base_price": 8.90, "volatility": 0.025, "market_cap": 7500000000, "beta": 1.38},

        # طاقة
        {"symbol": "AMOC", "name": "Alexandria Mineral Oils", "sector": "طاقة", "base_price": 8.59, "volatility": 0.024, "market_cap": 25000000000, "beta": 1.20},
        {"symbol": "EGAS", "name": "مصر للغاز الطبيعي", "sector": "طاقة", "base_price": 49.12, "volatility": 0.016, "market_cap": 35000000000, "beta": 0.95},
        {"symbol": "CEOG", "name": "القاهرة للزيوت", "sector": "طاقة", "base_price": 12.40, "volatility": 0.022, "market_cap": 8500000000, "beta": 1.18},
        {"symbol": "MPCO", "name": "ميدكو للطاقة", "sector": "طاقة", "base_price": 18.90, "volatility": 0.020, "market_cap": 12000000000, "beta": 1.15},
        {"symbol": "TAQA", "name": "طاقة عربية", "sector": "طاقة", "base_price": 2.40, "volatility": 0.038, "market_cap": 3500000000, "beta": 1.62},
        {"symbol": "SOLA", "name": "الشمس للطاقة", "sector": "طاقة", "base_price": 5.60, "volatility": 0.032, "market_cap": 4800000000, "beta": 1.48},

        # تعليم
        {"symbol": "MTIE", "name": "MM Group للتعليم", "sector": "تعليم", "base_price": 9.42, "volatility": 0.026, "market_cap": 18000000000, "beta": 1.38},
        {"symbol": "EDUC", "name": "التعليمية", "sector": "تعليم", "base_price": 4.80, "volatility": 0.030, "market_cap": 6500000000, "beta": 1.45},
        {"symbol": "ELAB", "name": "العربية للتعليم", "sector": "تعليم", "base_price": 3.20, "volatility": 0.035, "market_cap": 3800000000, "beta": 1.55},
        {"symbol": "NILE", "name": "النيل للتعليم", "sector": "تعليم", "base_price": 7.40, "volatility": 0.028, "market_cap": 8500000000, "beta": 1.42},

        # إعلام
        {"symbol": "MPRC", "name": "مدينة الإنتاج الإعلامي", "sector": "إعلام", "base_price": 31.75, "volatility": 0.017, "market_cap": 12000000000, "beta": 1.15},
        {"symbol": "MEDIA", "name": "المصرية للإعلام", "sector": "إعلام", "base_price": 5.80, "volatility": 0.028, "market_cap": 4500000000, "beta": 1.38},
        {"symbol": "SHOW", "name": "شوكولاتة للإنتاج الفني", "sector": "إعلام", "base_price": 2.90, "volatility": 0.040, "market_cap": 2200000000, "beta": 1.65},

        # نقل
        {"symbol": "ETRS", "name": "النقل والخدمات اللوجستية", "sector": "نقل", "base_price": 7.78, "volatility": 0.021, "market_cap": 15000000000, "beta": 1.22},
        {"symbol": "MTRS", "name": "مصر للنقل", "sector": "نقل", "base_price": 12.30, "volatility": 0.019, "market_cap": 8500000000, "beta": 1.15},
        {"symbol": "AIR", "name": "القابضة للنقل البري والبحري", "sector": "نقل", "base_price": 4.50, "volatility": 0.028, "market_cap": 3800000000, "beta": 1.40},
        {"symbol": "CONT", "name": "الكونتيننتال لحل الألياف", "sector": "نقل", "base_price": 8.20, "volatility": 0.024, "market_cap": 5500000000, "beta": 1.32},

        # تكنولوجيا
        {"symbol": "EEII", "name": "العربية للصناعات الهندسية", "sector": "تكنولوجيا", "base_price": 2.35, "volatility": 0.040, "market_cap": 8000000000, "beta": 1.75},
        {"symbol": "TECH", "name": "المصرية للتكنولوجيا", "sector": "تكنولوجيا", "base_price": 6.40, "volatility": 0.035, "market_cap": 5500000000, "beta": 1.58},
        {"symbol": "INTE", "name": "العربية للحاسبات", "sector": "تكنولوجيا", "base_price": 4.80, "volatility": 0.032, "market_cap": 4200000000, "beta": 1.48},
        {"symbol": "SOFT", "name": "السوفت وير للتكنولوجيا", "sector": "تكنولوجيا", "base_price": 3.60, "volatility": 0.038, "market_cap": 2800000000, "beta": 1.62},

        # سياحة
        {"symbol": "TRIP", "name": "العربية للاستثمارات السياحية", "sector": "سياحة", "base_price": 1.80, "volatility": 0.045, "market_cap": 2200000000, "beta": 1.85},
        {"symbol": "HOTR", "name": "العالمية للاستثمار السياحي", "sector": "سياحة", "base_price": 3.40, "volatility": 0.038, "market_cap": 3500000000, "beta": 1.68},
        {"symbol": "PYRA", "name": "بيراميزا للفنادق", "sector": "سياحة", "base_price": 2.60, "volatility": 0.042, "market_cap": 2800000000, "beta": 1.72},
        {"symbol": "TOUR", "name": "النصر للسياحة والصيانة", "sector": "سياحة", "base_price": 5.20, "volatility": 0.030, "market_cap": 4800000000, "beta": 1.45},

        # تأمين
        {"symbol": "GIGR", "name": "الجمهورية للتأمين", "sector": "تأمين", "base_price": 18.40, "volatility": 0.018, "market_cap": 9500000000, "beta": 1.12},
        {"symbol": "MICH2", "name": "المصرية للتأمين", "sector": "تأمين", "base_price": 22.80, "volatility": 0.016, "market_cap": 12000000000, "beta": 1.08},
        {"symbol": "ALKA", "name": "الأهلية للتأمين", "sector": "تأمين", "base_price": 14.60, "volatility": 0.019, "market_cap": 7500000000, "beta": 1.15},
        {"symbol": "SINA", "name": "سيناء للتأمين", "sector": "تأمين", "base_price": 8.90, "volatility": 0.022, "market_cap": 4500000000, "beta": 1.25},
        {"symbol": "CHRI", "name": "تأمين المصريين", "sector": "تأمين", "base_price": 11.20, "volatility": 0.020, "market_cap": 6200000000, "beta": 1.18},
        {"symbol": "DELT", "name": "الدلتا للتأمين", "sector": "تأمين", "base_price": 7.40, "volatility": 0.024, "market_cap": 3800000000, "beta": 1.28},

        # أغذية
        {"symbol": "FOOD", "name": "الدولية للأغذية", "sector": "أغذية", "base_price": 16.80, "volatility": 0.017, "market_cap": 8500000000, "beta": 1.10},
        {"symbol": "FARM", "name": "الفارما للأغذية", "sector": "أغذية", "base_price": 9.20, "volatility": 0.022, "market_cap": 5200000000, "beta": 1.22},
        {"symbol": "DAIR", "name": "النصر للألبان", "sector": "أغذية", "base_price": 12.60, "volatility": 0.019, "market_cap": 6800000000, "beta": 1.15},
        {"symbol": "BAKE", "name": "القاهرة للزيوت والصابون", "sector": "أغذية", "base_price": 8.40, "volatility": 0.024, "market_cap": 4200000000, "beta": 1.28},
        {"symbol": "CANN", "name": "القناة للتوزيع", "sector": "أغذية", "base_price": 5.80, "volatility": 0.028, "market_cap": 3200000000, "beta": 1.35},
        {"symbol": "OILS", "name": "الزيوت المستخلصة", "sector": "أغذية", "base_price": 4.20, "volatility": 0.032, "market_cap": 2200000000, "beta": 1.42},

        # مواد بناء
        {"symbol": "IRON", "name": "حديد عز", "sector": "مواد بناء", "base_price": 68.40, "volatility": 0.018, "market_cap": 35000000000, "beta": 1.15},
        {"symbol": "STEE", "name": "العز الدخيلة", "sector": "مواد بناء", "base_price": 42.80, "volatility": 0.020, "market_cap": 22000000000, "beta": 1.20},
        {"symbol": "CERA2", "name": "سيراميكا ريماس", "sector": "مواد بناء", "base_price": 3.80, "volatility": 0.035, "market_cap": 2800000000, "beta": 1.48},
        {"symbol": "GLAS", "name": "العاملة للزجاج", "sector": "مواد بناء", "base_price": 6.20, "volatility": 0.028, "market_cap": 3800000000, "beta": 1.38},
        {"symbol": "PAINT", "name": "السويس للدهانات", "sector": "مواد بناء", "base_price": 9.80, "volatility": 0.022, "market_cap": 5200000000, "beta": 1.25},
        {"symbol": "BRIC", "name": "النصر لمواد البناء", "sector": "مواد بناء", "base_price": 5.40, "volatility": 0.030, "market_cap": 3200000000, "beta": 1.42},

        # خدمات
        {"symbol": "SERV", "name": "الخدمات الملاحية", "sector": "خدمات", "base_price": 14.20, "volatility": 0.019, "market_cap": 7500000000, "beta": 1.12},
        {"symbol": "CLEAN", "name": "النصر للخدمات", "sector": "خدمات", "base_price": 7.80, "volatility": 0.025, "market_cap": 4200000000, "beta": 1.30},
        {"symbol": "MAINT", "name": "الصيانة للخدمات", "sector": "خدمات", "base_price": 4.60, "volatility": 0.032, "market_cap": 2500000000, "beta": 1.45},
        {"symbol": "SECU", "name": "العربية للأمن", "sector": "خدمات", "base_price": 3.20, "volatility": 0.038, "market_cap": 1800000000, "beta": 1.58},
    ]

    def __init__(self):
        self.cache = st.session_state.market_data_cache
        self.price_history = st.session_state.price_history_sim
        self._seed = int(datetime.now().timestamp()) % 10000

    def _generate_realistic_price(self, stock_info: dict) -> dict:
        try:
            symbol = stock_info['symbol']
            base = stock_info['base_price']
            vol = stock_info['volatility']
            beta = stock_info.get('beta', 1.0)
            market_trend = np.sin(datetime.now().hour / 3.0) * 0.003

            if symbol in self.price_history:
                last_price = self.price_history[symbol]
            else:
                np.random.seed(self._seed + hash(symbol) % 1000)
                last_price = base * (1 + np.random.normal(0, vol * 0.5))

            np.random.seed(int(datetime.now().timestamp() * 1000) % 100000 + hash(symbol) % 1000)
            mean_reversion = (base - last_price) * 0.02
            drift = mean_reversion + (market_trend * beta)
            shock = np.random.normal(drift, vol * last_price * 0.8)
            new_price = last_price + shock
            new_price = max(new_price, base * 0.70)
            new_price = min(new_price, base * 1.50)

            change = new_price - base
            change_pct = (change / base) * 100 if base > 0 else 0
            base_volume = stock_info.get('market_cap', 1e9) / (new_price * 100) if new_price > 0 else 1e6
            vol_multiplier = 1.0 + abs(change_pct) * 2
            volume_shock = np.random.lognormal(0, 0.4)
            volume = int(base_volume * vol_multiplier * volume_shock)

            intraday_vol = vol * 0.6
            high = new_price * (1 + abs(np.random.normal(0, intraday_vol)))
            low = new_price * (1 - abs(np.random.normal(0, intraday_vol)))
            open_price = new_price - np.random.normal(0, intraday_vol * new_price * 0.5)
            vwap = new_price * (1 + np.random.normal(0, vol * 0.3))

            self.price_history[symbol] = new_price

            return {
                "symbol": symbol, "name": stock_info['name'], "sector": stock_info['sector'],
                "price": round(new_price, 2), "change": round(change, 2), "change_pct": round(change_pct, 2),
                "volume": volume, "high": round(high, 2), "low": round(low, 2),
                "open": round(open_price, 2), "vwap": round(vwap, 2),
                "market_cap": stock_info['market_cap'], "volatility": vol,
                "base_price": base, "beta": beta, "source": "live_sim"
            }
        except Exception:
            return {
                "symbol": stock_info['symbol'], "name": stock_info['name'], "sector": stock_info['sector'],
                "price": stock_info['base_price'], "change": 0.0, "change_pct": 0.0,
                "volume": 1000000, "high": stock_info['base_price'] * 1.02, "low": stock_info['base_price'] * 0.98,
                "open": stock_info['base_price'], "vwap": stock_info['base_price'],
                "market_cap": stock_info['market_cap'], "volatility": stock_info['volatility'],
                "base_price": stock_info['base_price'], "beta": stock_info.get('beta', 1.0), "source": "fallback"
            }

    def get_live_prices(self) -> List[dict]:
        return [self._generate_realistic_price(stock) for stock in self.EGYPTIAN_STOCKS]

    def get_stock_history(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        try:
            cache_key = f"{symbol}_{period}"
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if (datetime.now() - entry["timestamp"]).seconds < 300:
                    return entry["data"]

            stock = next((s for s in self.EGYPTIAN_STOCKS if s['symbol'] == symbol), None)
            if not stock:
                return None

            days = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504}.get(period, 66)
            dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
            np.random.seed(hash(symbol) % 10000)

            prices = [stock['base_price']]
            returns = []
            for i in range(1, days):
                mean_rev = (stock['base_price'] - prices[-1]) * 0.005
                if len(returns) > 5:
                    recent_vol = np.std(returns[-5:]) * np.sqrt(252)
                    vol_adjust = min(max(recent_vol / (stock['volatility'] * np.sqrt(252)), 0.5), 2.0)
                else:
                    vol_adjust = 1.0
                daily_vol = stock['volatility'] * vol_adjust / np.sqrt(252)
                daily_return = np.random.normal(mean_rev / prices[-1], daily_vol)
                new_price = prices[-1] * (1 + daily_return)
                new_price = max(new_price, stock['base_price'] * 0.60)
                new_price = min(new_price, stock['base_price'] * 1.80)
                prices.append(new_price)
                returns.append(daily_return)

            df = pd.DataFrame(index=dates)
            df['Close'] = prices
            df['Open'] = df['Close'].shift(1) * (1 + np.random.normal(0, stock['volatility'] * 0.3, days))
            df.loc[df.index[0], 'Open'] = prices[0] * (1 + np.random.normal(0, stock['volatility'] * 0.3))
            df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + abs(np.random.normal(0, stock['volatility'] * 0.4, days)))
            df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - abs(np.random.normal(0, stock['volatility'] * 0.4, days)))
            df['High'] = np.maximum(df['High'], df[['Open', 'Close']].max(axis=1) * 1.001)
            df['Low'] = np.minimum(df['Low'], df[['Open', 'Close']].min(axis=1) * 0.999)

            base_vol = stock['market_cap'] / (df['Close'] * 100)
            volume_pattern = np.random.lognormal(0, 0.5, days)
            price_changes = df['Close'].pct_change().abs().fillna(0)
            vol_spike = 1 + price_changes * 10
            df['Volume'] = (base_vol * volume_pattern * vol_spike).astype(int)

            self.cache[cache_key] = {"data": df, "timestamp": datetime.now()}
            return df
        except Exception:
            return None

# Initialize data engine
data_engine = EGXDataEngine()

# ==================== TECHNICAL ANALYSIS ENGINE ====================
class TechnicalAnalyzer:
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        try:
            if df is None or len(df) < 30:
                return None
            df = df.copy()

            delta = df['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss.replace(0, np.nan)
            df['RSI'] = 100 - (100 / (1 + rs))

            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

            df['BB_Middle'] = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            bb_range = df['BB_Upper'] - df['BB_Lower']
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / bb_range.replace(0, np.nan)
            df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'].replace(0, np.nan)
            df['BB_Squeeze'] = df['BB_Width'] < df['BB_Width'].rolling(50).mean() * 0.6

            low_14 = df['Low'].rolling(14).min()
            high_14 = df['High'].rolling(14).max()
            stoch_range = high_14 - low_14
            df['Stoch_K'] = 100 * (df['Close'] - low_14) / stoch_range.replace(0, np.nan)
            df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

            df['SMA_10'] = df['Close'].rolling(10).mean()
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            df['SMA_200'] = df['Close'].rolling(200).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

            df['Golden_Cross'] = (df['SMA_50'] > df['SMA_200']) & (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1))
            df['Death_Cross'] = (df['SMA_50'] < df['SMA_200']) & (df['SMA_50'].shift(1) >= df['SMA_200'].shift(1))

            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['ATR'] = true_range.rolling(14).mean()
            df['ATR_Pct'] = df['ATR'] / df['Close'] * 100

            df['Volume_SMA'] = df['Volume'].rolling(20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA'].replace(0, np.nan)

            df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
            df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100

            plus_dm = df['High'].diff().clip(lower=0)
            minus_dm = df['Low'].diff().clip(upper=0).abs()
            atr = true_range.rolling(14).mean()
            plus_di = 100 * (plus_dm.rolling(14).mean() / atr.replace(0, np.nan))
            minus_di = 100 * (minus_dm.rolling(14).mean() / atr.replace(0, np.nan))
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
            df['ADX'] = dx.rolling(14).mean()
            df['Plus_DI'] = plus_di
            df['Minus_DI'] = minus_di

            obv = [0]
            for i in range(1, len(df)):
                if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                    obv.append(obv[-1] + df['Volume'].iloc[i])
                elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                    obv.append(obv[-1] - df['Volume'].iloc[i])
                else:
                    obv.append(obv[-1])
            df['OBV'] = obv
            df['OBV_SMA'] = df['OBV'].rolling(20).mean()
            df['Williams_R'] = -100 * (high_14 - df['Close']) / stoch_range.replace(0, np.nan)

            tp = (df['High'] + df['Low'] + df['Close']) / 3
            tp_sma = tp.rolling(20).mean()
            tp_std = tp.rolling(20).std()
            df['CCI'] = (tp - tp_sma) / (0.015 * tp_std.replace(0, np.nan))

            return df
        except Exception:
            return None

    @staticmethod
    def generate_signals(df: pd.DataFrame) -> List[Tuple]:
        try:
            if df is None or len(df) < 30:
                return []
            signals = []
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            rsi = latest.get('RSI')
            if pd.notna(rsi):
                if rsi < 30: signals.append(("RSI", "شراء قوي", 2, "ذروة بيع", "oversold", f"RSI = {rsi:.1f} < 30"))
                elif rsi > 70: signals.append(("RSI", "بيع قوي", -2, "ذروة شراء", "overbought", f"RSI = {rsi:.1f} > 70"))
                elif rsi < 40: signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء", "bullish", f"RSI = {rsi:.1f} < 40"))
                elif rsi > 60: signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع", "bearish", f"RSI = {rsi:.1f} > 60"))
                else: signals.append(("RSI", "محايد", 0, "لا إشارة", "neutral", f"RSI = {rsi:.1f}"))

            macd = latest.get('MACD')
            macd_signal = latest.get('MACD_Signal')
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal: signals.append(("MACD", "شراء", 1, "MACD إيجابي", "bullish", f"MACD ({macd:.2f}) فوق Signal"))
                else: signals.append(("MACD", "بيع", -1, "MACD سلبي", "bearish", f"MACD ({macd:.2f}) تحت Signal"))

            close = latest.get('Close')
            bb_lower = latest.get('BB_Lower')
            bb_upper = latest.get('BB_Upper')
            if pd.notna(close) and pd.notna(bb_lower) and pd.notna(bb_upper):
                if close < bb_lower: signals.append(("Bollinger", "شراء قوي", 2, "تحت النطاق السفلي", "oversold", f"السعر تحت BB Lower"))
                elif close > bb_upper: signals.append(("Bollinger", "بيع قوي", -2, "فوق النطاق العلوي", "overbought", f"السعر فوق BB Upper"))
                else: signals.append(("Bollinger", "محايد", 0, "داخل النطاق", "neutral", "السعر داخل النطاق"))

            stoch_k = latest.get('Stoch_K')
            if pd.notna(stoch_k):
                if stoch_k < 20: signals.append(("Stochastic", "شراء", 1.5, "ذروة بيع", "oversold", f"Stoch K={stoch_k:.1f} < 20"))
                elif stoch_k > 80: signals.append(("Stochastic", "بيع", -1.5, "ذروة شراء", "overbought", f"Stoch K={stoch_k:.1f} > 80"))

            sma_20 = latest.get('SMA_20')
            sma_50 = latest.get('SMA_50')
            if pd.notna(close) and pd.notna(sma_20):
                if close > sma_20: signals.append(("MA", "شراء ضعيف", 0.5, "فوق SMA20", "bullish", "السعر فوق SMA20"))
                else: signals.append(("MA", "بيع ضعيف", -0.5, "تحت SMA20", "bearish", "السعر تحت SMA20"))

            if latest.get('Golden_Cross'): signals.append(("MA_Cross", "شراء استراتيجي", 2.5, "تقاطع ذهبي", "strong_bullish", "SMA50 عبر SMA200 للأعلى"))
            if latest.get('Death_Cross'): signals.append(("MA_Cross", "بيع استراتيجي", -2.5, "تقاطع ميت", "strong_bearish", "SMA50 عبر SMA200 للأسفل"))

            adx = latest.get('ADX')
            if pd.notna(adx):
                if adx > 25: signals.append(("ADX", "تأكيد", 0.5, "اتجاه قوي", "confirmation", f"ADX = {adx:.1f} > 25"))
                elif adx < 20: signals.append(("ADX", "تحذير", -0.3, "اتجاه ضعيف", "warning", f"ADX = {adx:.1f} < 20"))

            vol_ratio = latest.get('Volume_Ratio')
            if pd.notna(vol_ratio):
                if vol_ratio > 2.0: signals.append(("Volume", "تأكيد قوي", 1.0, "حجم استثنائي", "confirmation", f"حجم {vol_ratio:.1f}x المتوسط"))
                elif vol_ratio < 0.5: signals.append(("Volume", "ضعف", -0.5, "حجم ضعيف", "warning", f"حجم {vol_ratio:.1f}x المتوسط"))

            return signals
        except Exception:
            return []

    @staticmethod
    def calculate_overall(signals: List[Tuple]) -> Tuple[str, float, str, str, List[str]]:
        try:
            if not signals:
                return "HOLD", 0, "لا توجد بيانات كافية", "neutral", []
            total_score = sum([s[2] for s in signals if len(s) > 2])
            bullish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bullish", "oversold", "confirmation"])
            bearish_count = sum(1 for s in signals if len(s) > 4 and s[4] in ["bearish", "overbought", "warning"])
            reasons = [s[5] for s in signals if len(s) > 5]

            if total_score >= 4: return "STRONG_BUY", total_score, "إشارة شراء قوية", "strong_bullish", reasons[:5]
            elif total_score >= 2: return "BUY", total_score, "إشارة شراء", "bullish", reasons[:5]
            elif total_score <= -4: return "STRONG_SELL", total_score, "إشارة بيع قوية", "strong_bearish", reasons[:5]
            elif total_score <= -2: return "SELL", total_score, "إشارة بيع", "bearish", reasons[:5]
            else:
                trend = "weak_bullish" if bullish_count > bearish_count else "weak_bearish" if bearish_count > bullish_count else "neutral"
                text = "انتظار - ميل صاعد" if bullish_count > bearish_count else "انتظار - ميل هابط" if bearish_count > bullish_count else "محايد"
                return "HOLD", total_score, text, trend, reasons[:3]
        except Exception:
            return "HOLD", 0, "خطأ", "neutral", []

ta_engine = TechnicalAnalyzer()

# ==================== FUNDAMENTAL DATA ENGINE ====================
class FundamentalDataEngine:
    SECTOR_PROFILES = {
        "بنوك": {"margin": 0.25, "current_ratio": 1.1, "debt_eq": 0.8, "asset_turn": 0.05, "ccc": -30, "int_cov": 4.0},
        "تكنولوجيا مالية": {"margin": 0.18, "current_ratio": 1.8, "debt_eq": 0.3, "asset_turn": 0.6, "ccc": 20, "int_cov": 8.0},
        "عقارات": {"margin": 0.22, "current_ratio": 1.5, "debt_eq": 0.9, "asset_turn": 0.25, "ccc": 180, "int_cov": 2.5},
        "صناعة": {"margin": 0.12, "current_ratio": 1.4, "debt_eq": 0.6, "asset_turn": 0.7, "ccc": 60, "int_cov": 5.0},
        "اتصالات": {"margin": 0.28, "current_ratio": 1.2, "debt_eq": 0.5, "asset_turn": 0.5, "ccc": 45, "int_cov": 6.0},
        "سلع استهلاكية": {"margin": 0.08, "current_ratio": 1.3, "debt_eq": 0.4, "asset_turn": 1.2, "ccc": 30, "int_cov": 7.0},
        "صحة": {"margin": 0.15, "current_ratio": 2.0, "debt_eq": 0.2, "asset_turn": 0.8, "ccc": 75, "int_cov": 9.0},
        "استثمار": {"margin": 0.35, "current_ratio": 1.6, "debt_eq": 0.5, "asset_turn": 0.3, "ccc": 10, "int_cov": 5.5},
        "طاقة": {"margin": 0.10, "current_ratio": 1.3, "debt_eq": 0.7, "asset_turn": 0.6, "ccc": 25, "int_cov": 4.5},
        "تعليم": {"margin": 0.20, "current_ratio": 1.4, "debt_eq": 0.4, "asset_turn": 0.4, "ccc": 15, "int_cov": 6.5},
        "إعلام": {"margin": 0.14, "current_ratio": 1.2, "debt_eq": 0.5, "asset_turn": 0.5, "ccc": 40, "int_cov": 5.0},
        "نقل": {"margin": 0.11, "current_ratio": 1.1, "debt_eq": 0.8, "asset_turn": 0.8, "ccc": 20, "int_cov": 3.5},
        "تكنولوجيا": {"margin": 0.16, "current_ratio": 1.7, "debt_eq": 0.3, "asset_turn": 0.9, "ccc": 35, "int_cov": 8.5},
        "سياحة": {"margin": 0.18, "current_ratio": 1.3, "debt_eq": 0.6, "asset_turn": 0.4, "ccc": 30, "int_cov": 4.0},
        "تأمين": {"margin": 0.12, "current_ratio": 1.4, "debt_eq": 0.4, "asset_turn": 0.3, "ccc": 15, "int_cov": 6.0},
        "أغذية": {"margin": 0.10, "current_ratio": 1.5, "debt_eq": 0.4, "asset_turn": 1.0, "ccc": 40, "int_cov": 7.0},
        "مواد بناء": {"margin": 0.14, "current_ratio": 1.4, "debt_eq": 0.6, "asset_turn": 0.8, "ccc": 50, "int_cov": 5.0},
        "خدمات": {"margin": 0.15, "current_ratio": 1.3, "debt_eq": 0.5, "asset_turn": 0.6, "ccc": 25, "int_cov": 5.5},
    }

    def __init__(self):
        self.user_edits = st.session_state.get('company_fundamental_data', {})

    def generate_fundamentals(self, stock_info: dict) -> dict:
        symbol = stock_info['symbol']
        sector = stock_info.get('sector', 'صناعة')
        market_cap = stock_info.get('market_cap', 1e9)
        base_price = stock_info.get('base_price', 10)

        if symbol in self.user_edits:
            return self.user_edits[symbol]

        profile = self.SECTOR_PROFILES.get(sector, self.SECTOR_PROFILES["صناعة"])
        np.random.seed(hash(symbol) % 10000)

        revenue = market_cap * np.random.uniform(0.5, 2.0) * (1 / max(profile['asset_turn'], 0.1))
        net_margin = profile['margin'] * np.random.uniform(0.7, 1.3)
        operating_margin = net_margin * np.random.uniform(1.2, 1.8)
        gross_margin = operating_margin * np.random.uniform(1.1, 1.4)
        gross_margin = min(gross_margin, 0.65)
        operating_margin = min(operating_margin, 0.45)
        net_margin = max(min(net_margin, 0.35), 0.02)

        cogs = revenue * (1 - gross_margin)
        operating_income = revenue * operating_margin
        net_income = revenue * net_margin

        total_assets = revenue / max(profile['asset_turn'], 0.1)
        equity = market_cap / np.random.uniform(1.0, 2.5)
        total_debt = equity * profile['debt_eq'] * np.random.uniform(0.8, 1.2)
        current_assets = total_assets * np.random.uniform(0.25, 0.45)
        current_liabilities = current_assets / (profile['current_ratio'] * np.random.uniform(0.8, 1.2))
        cash = current_assets * np.random.uniform(0.15, 0.35)
        inventory = current_assets * np.random.uniform(0.2, 0.4) if sector not in ["بنوك", "استثمار", "اتصالات"] else current_assets * 0.05
        receivables = revenue * np.random.uniform(0.08, 0.20)
        payables = cogs * np.random.uniform(0.15, 0.30)
        interest_expense = total_debt * np.random.uniform(0.04, 0.12)
        working_capital = current_assets - current_liabilities

        quick_assets = current_assets - inventory
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 1.5
        quick_ratio = quick_assets / current_liabilities if current_liabilities > 0 else 1.0
        cash_ratio = cash / current_liabilities if current_liabilities > 0 else 0.5
        roa = net_income / total_assets if total_assets > 0 else 0
        roe = net_income / equity if equity > 0 else 0
        inventory_turnover = cogs / inventory if inventory > 0 else 0
        inventory_days = 365 / inventory_turnover if inventory_turnover > 0 else 0
        receivables_days = (receivables / revenue) * 365 if revenue > 0 else 0
        payables_days = (payables / cogs) * 365 if cogs > 0 else 0
        asset_turnover = revenue / total_assets if total_assets > 0 else 0
        ccc = inventory_days + receivables_days - payables_days
        debt_ratio = total_debt / total_assets if total_assets > 0 else 0
        debt_to_equity = total_debt / equity if equity > 0 else 0
        interest_coverage = operating_income / interest_expense if interest_expense > 0 else 999

        profitability_score = min(100, ((gross_margin / 0.4) * 20 + (operating_margin / 0.25) * 20 + (net_margin / 0.20) * 20 + (roa / 0.10) * 20 + (roe / 0.15) * 20))
        liquidity_score = min(100, ((current_ratio / 2.0) * 30 + (quick_ratio / 1.5) * 30 + (cash_ratio / 1.0) * 20 + (1 if working_capital > 0 else 0) * 20))
        efficiency_score = min(100, ((asset_turnover / 1.0) * 25 + (100 if ccc < 0 else max(0, 100 - ccc)) * 25 + (inventory_turnover / 6) * 25 + (25 if receivables_days < 45 else max(0, 25 - (receivables_days - 45) / 2))))
        leverage_score = min(100, ((1 - debt_ratio) * 30 + max(0, (1 - debt_to_equity / 1.5)) * 30 + min(interest_coverage / 5, 1) * 40))
        overall_financial = (profitability_score + liquidity_score + efficiency_score + leverage_score) / 4

        return {
            "symbol": symbol, "name": stock_info['name'], "sector": sector, "market_cap": market_cap,
            "revenue": round(revenue, 0), "cogs": round(cogs, 0), "operating_income": round(operating_income, 0),
            "net_income": round(net_income, 0), "gross_margin": round(gross_margin * 100, 2),
            "operating_margin": round(operating_margin * 100, 2), "net_margin": round(net_margin * 100, 2),
            "total_assets": round(total_assets, 0), "total_equity": round(equity, 0), "total_debt": round(total_debt, 0),
            "current_assets": round(current_assets, 0), "current_liabilities": round(current_liabilities, 0),
            "cash": round(cash, 0), "inventory": round(inventory, 0), "receivables": round(receivables, 0),
            "payables": round(payables, 0), "working_capital": round(working_capital, 0),
            "interest_expense": round(interest_expense, 0), "current_ratio": round(current_ratio, 2),
            "quick_ratio": round(quick_ratio, 2), "cash_ratio": round(cash_ratio, 2), "roa": round(roa * 100, 2),
            "roe": round(roe * 100, 2), "inventory_turnover": round(inventory_turnover, 2),
            "inventory_days": round(inventory_days, 1), "receivables_days": round(receivables_days, 1),
            "payables_days": round(payables_days, 1), "asset_turnover": round(asset_turnover, 2),
            "ccc": round(ccc, 1), "debt_ratio": round(debt_ratio * 100, 2), "debt_to_equity": round(debt_to_equity, 2),
            "interest_coverage": round(interest_coverage, 2), "profitability_score": round(profitability_score, 1),
            "liquidity_score": round(liquidity_score, 1), "efficiency_score": round(efficiency_score, 1),
            "leverage_score": round(leverage_score, 1), "overall_score": round(overall_financial, 1),
            "source": "simulated"
        }

    def get_fundamentals(self, symbol: str) -> Optional[dict]:
        stock = next((s for s in EGXDataEngine.EGYPTIAN_STOCKS if s['symbol'] == symbol), None)
        if not stock:
            return None
        return self.generate_fundamentals(stock)

    def save_user_data(self, symbol: str, data: dict):
        if 'company_fundamental_data' not in st.session_state:
            st.session_state.company_fundamental_data = {}
        st.session_state.company_fundamental_data[symbol] = data
        self.user_edits = st.session_state.company_fundamental_data

fundamental_engine = FundamentalDataEngine()

# ==================== INVESTMENT FUNDS DATA ====================
class FundsEngine:
    FUNDS = [
        {"name": "صندوق الأهرام لأسهم النيل", "type": "أسهم", "nav": 18.45, "change": 1.24, "aum": 850000000, "ytd": 12.5, "risk": "عالي", "top_holdings": ["COMI", "TMGH", "EAST"]},
        {"name": "صندوق مصر للاستثمار", "type": "أسهم", "nav": 22.30, "change": 0.89, "aum": 1200000000, "ytd": 8.2, "risk": "عالي", "top_holdings": ["COMI", "ETEL", "SWDY"]},
        {"name": "صندوق CIB للاستثمار", "type": "أسهم", "nav": 15.80, "change": -0.45, "aum": 650000000, "ytd": 5.1, "risk": "عالي", "top_holdings": ["COMI", "QNBE", "FWRY"]},
        {"name": "صندوق النيل للاستثمار", "type": "أسهم", "nav": 12.60, "change": 1.85, "aum": 420000000, "ytd": 15.3, "risk": "عالي", "top_holdings": ["TMGH", "PHDC", "ORHD"]},
        {"name": "صندوق القاهرة للاستثمار", "type": "أسهم", "nav": 9.40, "change": 0.65, "aum": 280000000, "ytd": 6.8, "risk": "عالي", "top_holdings": ["EAST", "EFID", "JUFO"]},
        {"name": "صندوق المؤشر المصري", "type": "ETF", "nav": 248.50, "change": 1.24, "aum": 2500000000, "ytd": 10.2, "risk": "متوسط", "top_holdings": ["COMI", "ETEL", "TMGH"]},
        {"name": "صندوق EGX30 ETF", "type": "ETF", "nav": 12.42, "change": 1.24, "aum": 1800000000, "ytd": 10.2, "risk": "متوسط", "top_holdings": ["COMI", "ETEL", "TMGH", "SWDY"]},
        {"name": "صندوق الدخل الثابت", "type": "دخل ثابت", "nav": 10.85, "change": 0.15, "aum": 950000000, "ytd": 4.2, "risk": "منخفض", "top_holdings": ["HDBK", "QNBE", "ADIB"]},
        {"name": "صندوق أدوات الدخل", "type": "دخل ثابت", "nav": 11.20, "change": 0.22, "aum": 720000000, "ytd": 3.8, "risk": "منخفض", "top_holdings": ["CIEB", "CANA", "FAIT"]},
        {"name": "صندوق النقد المصري", "type": "نقد", "nav": 1.00, "change": 0.01, "aum": 3500000000, "ytd": 2.1, "risk": "منخفض جداً", "top_holdings": []},
        {"name": "صندودق العقاري المصري", "type": "عقاري", "nav": 8.90, "change": 0.75, "aum": 450000000, "ytd": 7.5, "risk": "متوسط", "top_holdings": ["TMGH", "EMFD", "PHDC"]},
        {"name": "صندوق الطاقة المتجددة", "type": "قطاعي", "nav": 6.40, "change": 1.45, "aum": 320000000, "ytd": 18.2, "risk": "عالي", "top_holdings": ["EGAS", "AMOC", "TAQA"]},
        {"name": "صندوق الصحة المصري", "type": "قطاعي", "nav": 14.20, "change": 0.95, "aum": 280000000, "ytd": 9.5, "risk": "متوسط", "top_holdings": ["MIPH", "PHAR", "AXPH"]},
        {"name": "صندوق التكنولوجيا", "type": "قطاعي", "nav": 11.80, "change": 2.10, "aum": 380000000, "ytd": 22.5, "risk": "عالي", "top_holdings": ["EFIH", "FWRY", "SCTS"]},
        {"name": "صندوق الاستثمار الإسلامي", "type": "إسلامي", "nav": 13.50, "change": 0.55, "aum": 550000000, "ytd": 6.8, "risk": "متوسط", "top_holdings": ["ADIB", "FAIT", "SAUD"]},
    ]

    @staticmethod
    def get_all_funds() -> List[dict]:
        return FundsEngine.FUNDS

    @staticmethod
    def get_fund_by_type(fund_type: str) -> List[dict]:
        return [f for f in FundsEngine.FUNDS if f['type'] == fund_type]

funds_engine = FundsEngine()

# ==================== DIVIDENDS ENGINE ====================
class DividendsEngine:
    DIVIDENDS = [
        {"symbol": "COMI", "name": "CIB", "sector": "بنوك", "dividend_date": "2026-04-15", "amount": 4.50, "share_price": 140.01, "yield": 3.21, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "dividend_date": "2026-03-20", "amount": 2.80, "share_price": 58.14, "yield": 4.82, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "dividend_date": "2026-05-10", "amount": 3.20, "share_price": 98.49, "yield": 3.25, "frequency": "نصف سنوي", "status": "قريب"},
        {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "dividend_date": "2026-05-25", "amount": 5.50, "share_price": 40.31, "yield": 13.64, "frequency": "ربع سنوي", "status": "قريب"},
        {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "dividend_date": "2026-04-28", "amount": 4.20, "share_price": 87.19, "yield": 4.82, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "dividend_date": "2026-06-05", "amount": 3.80, "share_price": 89.51, "yield": 4.25, "frequency": "سنوي", "status": "معلن"},
        {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "dividend_date": "2026-05-18", "amount": 2.40, "share_price": 98.25, "yield": 2.44, "frequency": "نصف سنوي", "status": "قريب"},
        {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "dividend_date": "2026-04-10", "amount": 12.50, "share_price": 687.72, "yield": 1.82, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "dividend_date": "2026-06-20", "amount": 2.20, "share_price": 48.81, "yield": 4.51, "frequency": "سنوي", "status": "معلن"},
        {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "dividend_date": "2026-05-30", "amount": 8.50, "share_price": 317.00, "yield": 2.68, "frequency": "سنوي", "status": "معلن"},
        {"symbol": "HRHO", "name": "EFG هيرمس", "sector": "استثمار", "dividend_date": "2026-04-22", "amount": 1.80, "share_price": 29.50, "yield": 6.10, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "HDBK", "name": "بنك الإسكان", "sector": "بنوك", "dividend_date": "2026-05-12", "amount": 5.20, "share_price": 147.26, "yield": 3.53, "frequency": "سنوي", "status": "قريب"},
        {"symbol": "ADIB", "name": "أبوظبي الإسلامي", "sector": "بنوك", "dividend_date": "2026-03-15", "amount": 1.90, "share_price": 47.49, "yield": 4.00, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "ORHD", "name": "أوراسكوم للتنمية", "sector": "عقارات", "dividend_date": "2026-06-15", "amount": 1.50, "share_price": 33.35, "yield": 4.50, "frequency": "نصف سنوي", "status": "معلن"},
        {"symbol": "PHDC", "name": "بالم هيلز", "sector": "عقارات", "dividend_date": "2026-05-22", "amount": 0.80, "share_price": 14.00, "yield": 5.71, "frequency": "نصف سنوي", "status": "قريب"},
        {"symbol": "CANA", "name": "قناة السويس", "sector": "بنوك", "dividend_date": "2026-04-05", "amount": 1.20, "share_price": 33.88, "yield": 3.54, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "MFPC", "name": "موبكو", "sector": "صناعة", "dividend_date": "2026-06-10", "amount": 2.50, "share_price": 45.15, "yield": 5.54, "frequency": "سنوي", "status": "معلن"},
        {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "dividend_date": "2026-05-08", "amount": 2.80, "share_price": 58.00, "yield": 4.83, "frequency": "سنوي", "status": "قريب"},
        {"symbol": "EFID", "name": "إيديتا", "sector": "سلع استهلاكية", "dividend_date": "2026-04-18", "amount": 1.40, "share_price": 28.60, "yield": 4.90, "frequency": "سنوي", "status": "تم التوزيع"},
        {"symbol": "JUFO", "name": "جهينة", "sector": "سلع استهلاكية", "dividend_date": "2026-05-05", "amount": 1.30, "share_price": 28.90, "yield": 4.50, "frequency": "سنوي", "status": "قريب"},
    ]

    @staticmethod
    def get_all_dividends() -> List[dict]:
        return DividendsEngine.DIVIDENDS

    @staticmethod
    def get_upcoming_dividends() -> List[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [d for d in DividendsEngine.DIVIDENDS if d['dividend_date'] >= today and d['status'] in ['قريب', 'معلن']]

    @staticmethod
    def get_sector_yields() -> dict:
        sectors = {}
        for d in DividendsEngine.DIVIDENDS:
            sector = d['sector']
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(d['yield'])
        return {k: round(sum(v)/len(v), 2) for k, v in sectors.items()}

dividends_engine = DividendsEngine()

# ==================== RISK ENGINE ====================
class RiskEngine:
    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        try:
            if returns.empty or returns.std() == 0:
                return 0.0
            return np.percentile(returns.dropna(), (1 - confidence) * 100)
        except:
            return 0.0

    @staticmethod
    def analyze_risk_profile(df: pd.DataFrame, entry_price: float, stop_loss: float, take_profit: float, account_balance: float = 100000) -> dict:
        try:
            if df is None or len(df) < 20:
                return {}
            returns = df['Close'].pct_change().dropna()
            if returns.empty:
                return {}

            volatility = returns.std() * np.sqrt(252) * 100
            var_95 = RiskEngine.calculate_var(returns, 0.95) * 100
            cvar_95 = returns[returns <= (var_95/100)].mean() * 100 if len(returns[returns <= (var_95/100)]) > 0 else var_95

            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0

            risk_amount = account_balance * (st.session_state.risk_settings.get('max_risk_pct', 2.0) / 100)
            price_risk = abs(entry_price - stop_loss)
            shares = int(risk_amount / price_risk) if price_risk > 0 else 0
            position_value = shares * entry_price
            actual_risk_pct = (price_risk * shares) / account_balance * 100

            positive_days = len(returns[returns > 0])
            total_days = len(returns[returns != 0])
            win_rate = positive_days / total_days if total_days > 0 else 0.5

            sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0
            downside_returns = returns[returns < 0]
            sortino = (returns.mean() / downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() != 0 else 0

            cumulative = (1 + returns).cumprod()
            peak = cumulative.expanding().max()
            drawdown = (cumulative - peak) / peak
            max_dd = drawdown.min()
            calmar = (returns.mean() * 252) / abs(max_dd) if max_dd != 0 else 0

            if actual_risk_pct <= 1.0 and rr_ratio >= 2.0 and volatility < 30:
                risk_class = "منخفض"; risk_color = "#10b981"
            elif actual_risk_pct <= 2.5 and rr_ratio >= 1.5 and volatility < 50:
                risk_class = "متوسط"; risk_color = "#f59e0b"
            else:
                risk_class = "عالي"; risk_color = "#ef4444"

            return {
                "volatility_annual": round(volatility, 2), "var_95": round(var_95, 2), "cvar_95": round(cvar_95, 2),
                "rr_ratio": round(rr_ratio, 2), "risk_pct": round((risk / entry_price) * 100, 2) if entry_price > 0 else 0,
                "reward_pct": round((reward / entry_price) * 100, 2) if entry_price > 0 else 0,
                "shares": shares, "position_value": round(position_value, 2), "actual_risk_pct": round(actual_risk_pct, 2),
                "win_rate": round(win_rate * 100, 1), "sharpe": round(sharpe, 2), "sortino": round(sortino, 2),
                "calmar": round(calmar, 2), "max_drawdown": round(max_dd * 100, 2),
                "risk_class": risk_class, "risk_color": risk_color,
                "entry_price": entry_price, "stop_loss": stop_loss, "take_profit": take_profit,
                "recommendation": "مناسب" if risk_class in ["منخفض", "متوسط"] and rr_ratio >= 1.5 else "غير مناسب"
            }
        except Exception:
            return {
                "volatility_annual": 0, "var_95": 0, "cvar_95": 0, "rr_ratio": 0, "risk_pct": 0, "reward_pct": 0,
                "shares": 0, "position_value": 0, "actual_risk_pct": 0, "win_rate": 0, "sharpe": 0, "sortino": 0,
                "calmar": 0, "max_drawdown": 0, "risk_class": "غير معروف", "risk_color": "#94a3b8",
                "entry_price": entry_price, "stop_loss": stop_loss, "take_profit": take_profit, "recommendation": "غير معروف"
            }

risk_engine = RiskEngine()

# ==================== AI AUTOMATED ANALYZER ====================
class AutomatedAnalyzer:
    @staticmethod
    def analyze_all(stocks_data: List[dict]) -> List[dict]:
        alerts = []
        for stock in stocks_data:
            try:
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
                overall_signal, score, signal_text, trend, reasons = ta_engine.calculate_overall(signals)

                atr = latest.get('ATR') if pd.notna(latest.get('ATR')) else 0
                current_price = latest['Close']
                stop_loss = current_price - (atr * 2) if atr > 0 else current_price * 0.95
                take_profit_1 = current_price + (atr * 2) if atr > 0 else current_price * 1.05

                risk_profile = risk_engine.analyze_risk_profile(df, current_price, stop_loss, take_profit_1)

                opportunity_score = 50
                if pd.notna(rsi):
                    if rsi < 30: opportunity_score += 20
                    elif rsi < 40: opportunity_score += 10
                    elif rsi > 70: opportunity_score -= 20

                macd_signal = latest.get('MACD_Signal')
                if pd.notna(macd) and pd.notna(macd_signal):
                    if macd > macd_signal: opportunity_score += 15

                bb_pos = latest.get('BB_Position')
                if pd.notna(bb_pos):
                    if bb_pos < 0.2: opportunity_score += 10
                    elif bb_pos > 0.8: opportunity_score -= 10

                vol_ratio = latest.get('Volume_Ratio')
                if pd.notna(vol_ratio) and vol_ratio > 1.5: opportunity_score += 10

                rr = risk_profile.get('rr_ratio', 0)
                if rr > 2: opportunity_score += 10
                elif rr > 1.5: opportunity_score += 5

                opportunity_score = max(0, min(100, opportunity_score))

                if opportunity_score >= 80 and overall_signal in ["STRONG_BUY", "BUY"]:
                    alert_level = "🔥 فرصة استثنائية"; alert_color = "#10b981"; priority = 1
                elif opportunity_score >= 65 and overall_signal in ["STRONG_BUY", "BUY"]:
                    alert_level = "🟢 فرصة شراء ممتازة"; alert_color = "#34d399"; priority = 2
                elif opportunity_score >= 50 and overall_signal in ["BUY", "HOLD"]:
                    alert_level = "🟡 مراقبة إيجابية"; alert_color = "#fbbf24"; priority = 3
                elif opportunity_score < 30 and overall_signal in ["SELL", "STRONG_SELL"]:
                    alert_level = "🔴 إشارة بيع"; alert_color = "#ef4444"; priority = 4
                else:
                    alert_level = "⚪ محايد"; alert_color = "#94a3b8"; priority = 5

                alerts.append({
                    "symbol": stock['symbol'], "name": stock['name'], "sector": stock['sector'],
                    "price": round(current_price, 2), "change_pct": stock.get('change_pct', 0),
                    "signal": overall_signal, "signal_text": signal_text, "trend": trend,
                    "score": round(opportunity_score, 1), "alert_level": alert_level, "alert_color": alert_color,
                    "priority": priority, "rsi": round(rsi, 1) if pd.notna(rsi) else 50,
                    "macd": round(macd, 2) if pd.notna(macd) else 0,
                    "bb_position": round(bb_pos, 2) if pd.notna(bb_pos) else 0.5,
                    "volume_ratio": round(vol_ratio, 1) if pd.notna(vol_ratio) else 1.0,
                    "adx": round(latest.get('ADX'), 1) if pd.notna(latest.get('ADX')) else 0,
                    "rr_ratio": risk_profile.get('rr_ratio', 0), "stop_loss": round(stop_loss, 2),
                    "take_profit_1": round(take_profit_1, 2), "risk_pct": risk_profile.get('risk_pct', 0),
                    "reward_pct": risk_profile.get('reward_pct', 0), "volatility": risk_profile.get('volatility_annual', 0),
                    "var_95": risk_profile.get('var_95', 0), "risk_class": risk_profile.get('risk_class', 'غير معروف'),
                    "risk_color": risk_profile.get('risk_color', '#94a3b8'),
                    "recommendation": risk_profile.get('recommendation', 'غير معروف'),
                    "position_shares": risk_profile.get('shares', 0),
                    "position_value": risk_profile.get('position_value', 0),
                    "sharpe": risk_profile.get('sharpe', 0), "reasons": reasons[:3],
                })
            except Exception:
                continue
        alerts.sort(key=lambda x: (x['priority'], -x['score']))
        return alerts

    @staticmethod
    def predict_prices(df: pd.DataFrame, days: int = 5) -> dict:
        try:
            prices = df['Close'].dropna().values
            if len(prices) < 30:
                return {'error': 'Insufficient data'}
            x = np.arange(len(prices))
            z = np.polyfit(x, prices, 1)
            linear_pred = np.poly1d(z)
            poly = np.polyfit(x, prices, 3)
            poly_pred = np.poly1d(poly)
            ema_values = df['Close'].ewm(span=10).mean().values
            ema_slope = (ema_values[-1] - ema_values[-5]) / 5 if len(ema_values) >= 5 else 0

            combined = []
            for i in range(days):
                day = i + 1
                lin = linear_pred(len(prices) + i)
                poly_val = poly_pred(len(prices) + i)
                ema = ema_values[-1] + ema_slope * day
                pred = lin * 0.3 + poly_val * 0.4 + ema * 0.3
                conf = max(0, min(100, 100 - (day * 10)))
                volatility = df['Close'].pct_change().std() * prices[-1]
                margin = volatility * (1 + day * 0.3)
                combined.append({
                    'day': day, 'predicted': round(float(pred), 2),
                    'lower_bound': round(float(pred - margin * 1.5), 2),
                    'upper_bound': round(float(pred + margin * 1.5), 2),
                    'confidence': conf
                })
            return {'combined': combined}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> dict:
        try:
            if df is None or len(df) < window:
                return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0, 'pivot': 0}
            recent = df.tail(window)
            lows = recent['Low'].nsmallest(5).values
            highs = recent['High'].nlargest(5).values
            swing_high = recent['High'].max()
            swing_low = recent['Low'].min()
            diff = swing_high - swing_low
            current = df['Close'].iloc[-1]
            pivot = (swing_high + swing_low + current) / 3
            r1 = 2 * pivot - swing_low
            s1 = 2 * pivot - swing_high
            r2 = pivot + (swing_high - swing_low)
            s2 = pivot - (swing_high - swing_low)

            fib = {}
            if diff > 0:
                fib = {
                    '0%': round(swing_high, 2), '23.6%': round(swing_high - 0.236 * diff, 2),
                    '38.2%': round(swing_high - 0.382 * diff, 2), '50%': round(swing_high - 0.5 * diff, 2),
                    '61.8%': round(swing_high - 0.618 * diff, 2), '78.6%': round(swing_high - 0.786 * diff, 2),
                    '100%': round(swing_low, 2)
                }
            return {
                'supports': [round(float(l), 2) for l in lows],
                'resistances': [round(float(h), 2) for h in highs],
                'fibonacci': fib, 'current': round(float(current), 2),
                'pivot': round(float(pivot), 2), 'r1': round(float(r1), 2),
                's1': round(float(s1), 2), 'r2': round(float(r2), 2), 's2': round(float(s2), 2)
            }
        except Exception:
            return {'supports': [], 'resistances': [], 'fibonacci': {}, 'current': 0, 'pivot': 0}

ai_engine = AutomatedAnalyzer()

# ==================== UNIFIED RECOMMENDATION ENGINE v24 ====================
class UnifiedRecommendationEngine:
    """
    نظام التوصيات الموحد v24
    يعمل في جميع التبويبات مع تحديث مستمر
    """

    RECOMMENDATION_CACHE = {}
    LAST_UPDATE = None

    @staticmethod
    def get_market_session_status() -> dict:
        now = datetime.now()
        hour = now.hour
        if hour < 10:
            return {"status": "مغلق", "phase": "قبل الافتتاح", "color": "#64748b", "icon": "🌙", "is_open": False}
        elif hour < 10 or (hour == 10 and now.minute < 30):
            return {"status": "افتتاح", "phase": "جلسة الافتتاح", "color": "#fbbf24", "icon": "🌅", "is_open": True}
        elif hour < 14 or (hour == 14 and now.minute < 30):
            return {"status": "مفتوح", "phase": "الجلسة العادية", "color": "#10b981", "icon": "☀️", "is_open": True}
        elif hour == 14 and now.minute >= 30 and now.minute < 45:
            return {"status": "ختام", "phase": "جلسة الختام", "color": "#f59e0b", "icon": "🌇", "is_open": True}
        else:
            return {"status": "مغلق", "phase": "بعد الإغلاق", "color": "#6366f1", "icon": "🌙", "is_open": False}

    @staticmethod
    def generate_single_recommendation(stock: dict, market_summary: dict = None) -> dict:
        """Generate recommendation for a single stock"""
        try:
            symbol = stock['symbol']
            df = data_engine.get_stock_history(symbol, "3mo")
            if df is None or len(df) < 30:
                return None

            df = ta_engine.calculate_all(df)
            if df is None:
                return None

            latest = df.iloc[-1]
            signals = ta_engine.generate_signals(df)
            overall_signal, score, signal_text, trend, reasons = ta_engine.calculate_overall(signals)

            current_price = stock['price']
            daily_change = stock['change_pct']

            # Volume analysis
            base_volume = stock.get('market_cap', 1e9) / (current_price * 100) if current_price > 0 else 1e6
            daily_volume_ratio = stock.get('volume', base_volume) / base_volume

            # Support/Resistance
            sr_levels = ai_engine.calculate_support_resistance(df)
            supports = sr_levels.get('supports', [])
            resistances = sr_levels.get('resistances', [])
            nearest_support = max([s for s in supports if s < current_price], default=current_price * 0.95)
            nearest_resistance = min([r for r in resistances if r > current_price], default=current_price * 1.05)
            support_distance = (current_price - nearest_support) / current_price * 100
            resistance_distance = (nearest_resistance - current_price) / current_price * 100

            # Enhanced EOD scoring
            eod_score = 50

            # Technical signal weight (30%)
            if overall_signal == "STRONG_BUY": eod_score += 18
            elif overall_signal == "BUY": eod_score += 12
            elif overall_signal == "STRONG_SELL": eod_score -= 18
            elif overall_signal == "SELL": eod_score -= 12

            # Daily performance weight (20%)
            if daily_change > 5: eod_score -= 8
            elif daily_change > 3: eod_score -= 4
            elif daily_change < -5: eod_score += 8
            elif daily_change < -3: eod_score += 4
            elif 0 < daily_change < 2: eod_score += 3

            # Volume confirmation (15%)
            if daily_volume_ratio > 2: 
                if daily_change > 0: eod_score += 6
                else: eod_score -= 6
            elif daily_volume_ratio > 1.5:
                if daily_change > 0: eod_score += 3
                else: eod_score -= 3

            # Support/Resistance proximity (15%)
            if support_distance < 2: eod_score += 8
            elif resistance_distance < 2: eod_score -= 8

            # Market sentiment alignment (10%)
            if market_summary:
                sentiment = market_summary.get('sentiment', 'محايد')
                if sentiment in ['إيجابي قوي', 'إيجابي'] and overall_signal in ['BUY', 'STRONG_BUY']:
                    eod_score += 4
                elif sentiment in ['سلبي قوي', 'سلبي'] and overall_signal in ['SELL', 'STRONG_SELL']:
                    eod_score += 4

            # Candlestick patterns (10%)
            open_price = stock.get('open', current_price)
            high_price = stock.get('high', current_price)
            low_price = stock.get('low', current_price)
            body = abs(current_price - open_price)
            upper_shadow = high_price - max(open_price, current_price)
            lower_shadow = min(open_price, current_price) - low_price
            total_range = high_price - low_price if high_price != low_price else 1

            if current_price > open_price:
                if lower_shadow > body * 2: eod_score += 6  # Hammer
                if body > total_range * 0.6: eod_score += 4  # Strong bullish
            else:
                if upper_shadow > body * 2: eod_score -= 6  # Shooting star
                if body > total_range * 0.6: eod_score -= 4  # Strong bearish

            # Fundamental score integration (if available)
            fund_data = fundamental_engine.get_fundamentals(symbol)
            if fund_data:
                fin_score = fund_data.get('overall_score', 50)
                if fin_score >= 70: eod_score += 3
                elif fin_score < 40: eod_score -= 3

            eod_score = max(0, min(100, eod_score))

            # Determine recommendation
            if eod_score >= 80:
                rec_action = "شراء قوي"; rec_icon = "🟢"; rec_color = "#10b981"; rec_type = "STRONG_BUY"
                urgency = "فوري"; hold_period = "1-3 أيام"
            elif eod_score >= 65:
                rec_action = "شراء"; rec_icon = "🟢"; rec_color = "#34d399"; rec_type = "BUY"
                urgency = "قريب"; hold_period = "2-5 أيام"
            elif eod_score >= 50:
                rec_action = "شراء محتمل"; rec_icon = "🟡"; rec_color = "#fbbf24"; rec_type = "WEAK_BUY"
                urgency = "مراقبة"; hold_period = "3-7 أيام"
            elif eod_score <= 20:
                rec_action = "بيع قوي"; rec_icon = "🔴"; rec_color = "#ef4444"; rec_type = "STRONG_SELL"
                urgency = "فوري"; hold_period = "تصفية"
            elif eod_score <= 35:
                rec_action = "بيع"; rec_icon = "🔴"; rec_color = "#f87171"; rec_type = "SELL"
                urgency = "قريب"; hold_period = "تصفية"
            elif eod_score <= 45:
                rec_action = "بيع محتمل"; rec_icon = "🟠"; rec_color = "#f59e0b"; rec_type = "WEAK_SELL"
                urgency = "مراقبة"; hold_period = "تصفية تدريجية"
            else:
                rec_action = "انتظار"; rec_icon = "⚪"; rec_color = "#94a3b8"; rec_type = "HOLD"
                urgency = "-"; hold_period = "-"

            # Calculate targets
            atr = latest.get('ATR') if pd.notna(latest.get('ATR')) else current_price * 0.02
            if rec_type in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
                entry = current_price
                stop = current_price - (atr * 2)
                target1 = current_price + (atr * 2)
                target2 = current_price + (atr * 3.5)
            elif rec_type in ['STRONG_SELL', 'SELL', 'WEAK_SELL']:
                entry = current_price
                stop = current_price + (atr * 2)
                target1 = current_price - (atr * 2)
                target2 = current_price - (atr * 3.5)
            else:
                entry = current_price
                stop = current_price * 0.95
                target1 = current_price * 1.05
                target2 = current_price * 1.10

            return {
                "symbol": symbol, "name": stock['name'], "sector": stock['sector'],
                "price": current_price, "change_pct": daily_change,
                "eod_score": round(eod_score, 1), "rec_action": rec_action,
                "rec_icon": rec_icon, "rec_color": rec_color, "rec_type": rec_type,
                "urgency": urgency, "hold_period": hold_period,
                "entry": round(entry, 2), "stop_loss": round(stop, 2),
                "target1": round(target1, 2), "target2": round(target2, 2),
                "support": round(nearest_support, 2), "resistance": round(nearest_resistance, 2),
                "volume_ratio": round(daily_volume_ratio, 1),
                "technical_signal": signal_text, "score": score,
                "rsi": round(latest.get('RSI'), 1) if pd.notna(latest.get('RSI')) else 50,
                "adx": round(latest.get('ADX'), 1) if pd.notna(latest.get('ADX')) else 0,
                "reasons": reasons[:3], "timestamp": datetime.now().strftime("%H:%M:%S"),
                "fundamental_score": fund_data.get('overall_score', 50) if fund_data else 50,
                "bb_position": round(latest.get('BB_Position'), 2) if pd.notna(latest.get('BB_Position')) else 0.5,
            }
        except Exception:
            return None

    @staticmethod
    def generate_all_recommendations(stocks_data: List[dict]) -> List[dict]:
        """Generate recommendations for all stocks"""
        # Generate market summary first
        market_summary = UnifiedRecommendationEngine.generate_market_summary(stocks_data)

        recommendations = []
        for stock in stocks_data:
            rec = UnifiedRecommendationEngine.generate_single_recommendation(stock, market_summary)
            if rec:
                recommendations.append(rec)

        # Sort: Buys first (by score desc), then holds, then sells (by score asc)
        recommendations.sort(key=lambda x: (
            0 if x['rec_type'] in ['STRONG_BUY', 'BUY'] else
            1 if x['rec_type'] == 'WEAK_BUY' else
            2 if x['rec_type'] == 'HOLD' else
            3 if x['rec_type'] == 'WEAK_SELL' else 4,
            -x['eod_score'] if x['rec_type'] in ['STRONG_BUY', 'BUY', 'WEAK_BUY'] else x['eod_score']
        ))

        # Cache results
        UnifiedRecommendationEngine.RECOMMENDATION_CACHE = {
            'recommendations': recommendations,
            'market_summary': market_summary,
            'timestamp': datetime.now()
        }
        UnifiedRecommendationEngine.LAST_UPDATE = datetime.now()

        return recommendations

    @staticmethod
    def generate_market_summary(stocks_data: List[dict]) -> dict:
        try:
            if not stocks_data:
                return {}
            advancers = [s for s in stocks_data if s['change_pct'] > 0]
            decliners = [s for s in stocks_data if s['change_pct'] < 0]
            advancer_pct = len(advancers) / len(stocks_data) * 100 if stocks_data else 0

            if advancer_pct >= 60: sentiment = "إيجابي قوي"; sentiment_color = "#10b981"; sentiment_icon = "🟢"
            elif advancer_pct >= 50: sentiment = "إيجابي"; sentiment_color = "#34d399"; sentiment_icon = "🟢"
            elif advancer_pct >= 40: sentiment = "محايد"; sentiment_color = "#fbbf24"; sentiment_icon = "🟡"
            elif advancer_pct >= 30: sentiment = "سلبي"; sentiment_color = "#f87171"; sentiment_icon = "🔴"
            else: sentiment = "سلبي قوي"; sentiment_color = "#ef4444"; sentiment_icon = "🔴"

            sectors = {}
            for s in stocks_data:
                sector = s['sector']
                if sector not in sectors: sectors[sector] = []
                sectors[sector].append(s['change_pct'])
            sector_perf = {k: round(sum(v)/len(v), 2) for k, v in sectors.items()}

            return {
                "advancers": len(advancers), "decliners": len(decliners),
                "advancer_pct": round(advancer_pct, 1), "sector_perf": sector_perf,
                "sentiment": sentiment, "sentiment_color": sentiment_color, "sentiment_icon": sentiment_icon,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception:
            return {}

    @staticmethod
    def get_cached_recommendations() -> dict:
        cache = UnifiedRecommendationEngine.RECOMMENDATION_CACHE
        if not cache or not cache.get('timestamp'):
            return None
        # Check if cache is fresh (< 5 minutes)
        if (datetime.now() - cache['timestamp']).seconds < 300:
            return cache
        return None

    @staticmethod
    def get_recommendation_stats(recommendations: List[dict]) -> dict:
        if not recommendations:
            return {}
        buy_recs = [r for r in recommendations if r['rec_type'] in ['STRONG_BUY', 'BUY']]
        sell_recs = [r for r in recommendations if r['rec_type'] in ['STRONG_SELL', 'SELL']]

        sectors_buy = {}
        sectors_sell = {}
        for r in buy_recs: sectors_buy[r['sector']] = sectors_buy.get(r['sector'], 0) + 1
        for r in sell_recs: sectors_sell[r['sector']] = sectors_sell.get(r['sector'], 0) + 1

        return {
            "total": len(recommendations),
            "strong_buy": len([r for r in buy_recs if r['rec_type'] == 'STRONG_BUY']),
            "buy": len([r for r in buy_recs if r['rec_type'] == 'BUY']),
            "weak_buy": len([r for r in recommendations if r['rec_type'] == 'WEAK_BUY']),
            "hold": len([r for r in recommendations if r['rec_type'] == 'HOLD']),
            "weak_sell": len([r for r in recommendations if r['rec_type'] == 'WEAK_SELL']),
            "sell": len([r for r in sell_recs if r['rec_type'] == 'SELL']),
            "strong_sell": len([r for r in sell_recs if r['rec_type'] == 'STRONG_SELL']),
            "top_buy_sector": max(sectors_buy.items(), key=lambda x: x[1])[0] if sectors_buy else "N/A",
            "top_sell_sector": max(sectors_sell.items(), key=lambda x: x[1])[0] if sectors_sell else "N/A",
        }

    @staticmethod
    def get_recommendation_badge(rec_type: str, text: str = None) -> str:
        """Get HTML badge for recommendation type"""
        badges = {
            "STRONG_BUY": ('rec-strong-buy', 'شراء قوي'),
            "BUY": ('rec-buy', 'شراء'),
            "WEAK_BUY": ('rec-hold', 'شراء محتمل'),
            "HOLD": ('rec-hold', 'انتظار'),
            "WEAK_SELL": ('rec-sell', 'بيع محتمل'),
            "SELL": ('rec-sell', 'بيع'),
            "STRONG_SELL": ('rec-strong-sell', 'بيع قوي'),
        }
        css_class, default_text = badges.get(rec_type, ('rec-hold', 'محايد'))
        display_text = text if text else default_text
        return f'<span class="rec-badge {css_class}">{display_text}</span>'

# Initialize unified engine
rec_engine = UnifiedRecommendationEngine()

# ==================== CALLBACKS ====================
def select_stock_callback(symbol):
    st.session_state.selected_stock = symbol
    st.session_state.show_analysis = True
    st.session_state.analysis_symbol = symbol
    st.session_state.active_section = 'analysis'
    st.session_state.active_subsection = None

def set_section(section, subsection=None):
    st.session_state.active_section = section
    st.session_state.active_subsection = subsection

def clear_analysis():
    st.session_state.show_analysis = False
    st.session_state.selected_stock = None
    st.session_state.analysis_symbol = None

def run_analysis_callback():
    with st.spinner("جاري تحليل السوق..."):
        prices = data_engine.get_live_prices()
        alerts = ai_engine.analyze_all(prices)
        st.session_state.alerts_cache = alerts
        st.session_state.alerts_timestamp = datetime.now()

def run_global_recommendations():
    with st.spinner("جاري تحليل جميع الأسهم وإنشاء التوصيات الموحدة..."):
        prices = data_engine.get_live_prices()
        recs = rec_engine.generate_all_recommendations(prices)
        st.session_state.global_recommendations = recs
        st.session_state.last_scan_time = datetime.now()
        st.toast("✅ تم تحديث التوصيات في جميع التبويبات!")

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
                "completed": False
            })
            st.session_state.new_task_title = ""
    except Exception:
        pass

def toggle_task(task_id):
    for task in st.session_state.tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task_id]

def edit_company_callback(symbol):
    st.session_state.edit_company_symbol = symbol
    st.session_state.selected_stock = symbol
    st.session_state.active_section = 'fundamental'

def save_company_data(symbol):
    try:
        data = {
            "symbol": symbol, "revenue": st.session_state.get(f"edit_rev_{symbol}", 0),
            "cogs": st.session_state.get(f"edit_cogs_{symbol}", 0),
            "operating_income": st.session_state.get(f"edit_op_{symbol}", 0),
            "net_income": st.session_state.get(f"edit_net_{symbol}", 0),
            "total_assets": st.session_state.get(f"edit_assets_{symbol}", 0),
            "total_equity": st.session_state.get(f"edit_eq_{symbol}", 0),
            "total_debt": st.session_state.get(f"edit_debt_{symbol}", 0),
            "current_assets": st.session_state.get(f"edit_ca_{symbol}", 0),
            "current_liabilities": st.session_state.get(f"edit_cl_{symbol}", 0),
            "cash": st.session_state.get(f"edit_cash_{symbol}", 0),
            "inventory": st.session_state.get(f"edit_inv_{symbol}", 0),
            "receivables": st.session_state.get(f"edit_rec_{symbol}", 0),
            "payables": st.session_state.get(f"edit_pay_{symbol}", 0),
            "interest_expense": st.session_state.get(f"edit_int_{symbol}", 0),
            "source": "user_edited"
        }
        revenue = data['revenue']; cogs = data['cogs']; op_income = data['operating_income']
        net_income = data['net_income']; total_assets = data['total_assets']; equity = data['total_equity']
        debt = data['total_debt']; ca = data['current_assets']; cl = data['current_liabilities']
        cash = data['cash']; inventory = data['inventory']; rec = data['receivables']
        pay = data['payables']; interest = data['interest_expense']

        data['gross_margin'] = round(((revenue - cogs) / revenue * 100), 2) if revenue else 0
        data['operating_margin'] = round((op_income / revenue * 100), 2) if revenue else 0
        data['net_margin'] = round((net_income / revenue * 100), 2) if revenue else 0
        data['roa'] = round((net_income / total_assets * 100), 2) if total_assets else 0
        data['roe'] = round((net_income / equity * 100), 2) if equity else 0
        data['current_ratio'] = round(ca / cl, 2) if cl else 0
        data['quick_ratio'] = round((ca - inventory) / cl, 2) if cl else 0
        data['cash_ratio'] = round(cash / cl, 2) if cl else 0
        data['working_capital'] = round(ca - cl, 0)
        data['inventory_turnover'] = round(cogs / inventory, 2) if inventory else 0
        data['inventory_days'] = round(365 / data['inventory_turnover'], 1) if data['inventory_turnover'] else 0
        data['receivables_days'] = round((rec / revenue) * 365, 1) if revenue else 0
        data['payables_days'] = round((pay / cogs) * 365, 1) if cogs else 0
        data['ccc'] = round(data['inventory_days'] + data['receivables_days'] - data['payables_days'], 1)
        data['asset_turnover'] = round(revenue / total_assets, 2) if total_assets else 0
        data['debt_ratio'] = round(debt / total_assets * 100, 2) if total_assets else 0
        data['debt_to_equity'] = round(debt / equity, 2) if equity else 0
        data['interest_coverage'] = round(op_income / interest, 2) if interest else 999

        fundamental_engine.save_user_data(symbol, data)
        st.session_state.edit_company_symbol = None
        st.toast(f"✅ تم حفظ بيانات {symbol}")
    except Exception as e:
        st.error(f"خطأ في الحفظ: {str(e)}")

# ==================== HELPER FUNCTIONS ====================
def get_rec_badge_class(rec_type):
    mapping = {
        "STRONG_BUY": "rec-strong-buy",
        "BUY": "rec-buy", 
        "WEAK_BUY": "rec-hold",
        "HOLD": "rec-hold",
        "WEAK_SELL": "rec-sell",
        "SELL": "rec-sell",
        "STRONG_SELL": "rec-strong-sell"
    }
    return mapping.get(rec_type, "rec-hold")

def get_rec_text(rec_type):
    mapping = {
        "STRONG_BUY": "شراء قوي",
        "BUY": "شراء",
        "WEAK_BUY": "شراء محتمل", 
        "HOLD": "انتظار",
        "WEAK_SELL": "بيع محتمل",
        "SELL": "بيع",
        "STRONG_SELL": "بيع قوي"
    }
    return mapping.get(rec_type, "محايد")

def get_rec_color(rec_type):
    mapping = {
        "STRONG_BUY": "#10b981",
        "BUY": "#34d399",
        "WEAK_BUY": "#fbbf24",
        "HOLD": "#94a3b8",
        "WEAK_SELL": "#f59e0b", 
        "SELL": "#f87171",
        "STRONG_SELL": "#ef4444"
    }
    return mapping.get(rec_type, "#94a3b8")

def render_recommendation_badge(rec_type, size="normal"):
    badge_class = get_rec_badge_class(rec_type)
    text = get_rec_text(rec_type)
    if size == "small":
        return f'<span class="rec-badge {badge_class}" style="font-size:10px;padding:2px 8px;">{text}</span>'
    return f'<span class="rec-badge {badge_class}">{text}</span>'

def render_mini_recommendation_card(rec):
    """Render a compact recommendation card for embedding in other tabs"""
    if not rec:
        return ""
    color = rec['rec_color']
    return f"""
    <div style="padding: 10px 14px; background: {color}10; border: 1px solid {color}30; border-radius: 10px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">{rec['rec_icon']}</span>
                <div>
                    <span style="font-weight: 700; color: {color}; font-size: 13px;">{rec['rec_action']}</span>
                    <span style="color: #64748b; font-size: 11px; margin-right: 6px;">{rec['symbol']}</span>
                </div>
            </div>
            <div style="text-align: left;">
                <span style="font-size: 16px; font-weight: 800; color: {color};">{rec['eod_score']}</span>
                <span style="color: #64748b; font-size: 10px;">/100</span>
            </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 6px;">
            <span style="color: #94a3b8; font-size: 10px;">🎯 دخول: {rec['entry']}</span>
            <span style="color: #94a3b8; font-size: 10px;">🛑 SL: {rec['stop_loss']}</span>
            <span style="color: #94a3b8; font-size: 10px;">🎯 TP1: {rec['target1']}</span>
        </div>
    </div>
    """

# ==================== SIDEBAR NAVIGATION ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 28px; padding: 20px; background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08)); border-radius: 16px; border: 1px solid rgba(99,102,241,0.25);">
        <div style="width: 56px; height: 56px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 14px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 4px 20px rgba(99,102,241,0.3);">⚡</div>
        <h2 style="margin-top: 14px; font-size: 20px; font-weight: 800;">EGX Pro Terminal</h2>
        <p style="color: #64748b; font-size: 12px; margin-top: 6px;">v24.0 | نظام التوصيات الذكي</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh recommendations in sidebar
    st.markdown("<p style='color: #64748b; font-size: 11px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em;'>🗺️ خارطة التنقل</p>", unsafe_allow_html=True)

    # Check for cached recommendations
    cached_recs = rec_engine.get_cached_recommendations()
    buy_count = 0
    if cached_recs:
        stats = rec_engine.get_recommendation_stats(cached_recs['recommendations'])
        buy_count = stats.get('strong_buy', 0) + stats.get('buy', 0)

    nav_items = [
        ("market", "📈", "رادار السوق", None),
        ("stocks", "📋", "قائمة الأسهم", None),
        ("analysis", "🔮", "التحليل المفصل", None),
        ("fundamental", "📊", "التحليل المالي", None),
        ("funds", "💰", "صناديق الاستثمار", None),
        ("dividends", "🎁", "التوزيعات النقدية", None),
        ("eod_recommendations", "🎯", "توصيات نهاية الجلسة", buy_count if buy_count > 0 else None),
        ("ai_scan", "🤖", "الماسح الآلي", None),
        ("backtest", "📉", "Backtesting", None),
        ("tasks", "✅", "المهام الذكية", None),
    ]

    for section, icon, label, badge in nav_items:
        is_active = st.session_state.active_section == section
        active_class = "active" if is_active else ""
        badge_html = f'<span class="nav-badge">{badge}</span>' if badge else ''
        if st.button(f"{icon} {label}", key=f"nav_{section}", use_container_width=True, 
                     type="secondary" if not is_active else "primary"):
            set_section(section)
            st.rerun()

    st.divider()

    # Quick Recommendation Panel in Sidebar
    st.markdown("<p style='color: #64748b; font-size: 11px; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em;'>🎯 التوصيات السريعة</p>", unsafe_allow_html=True)

    if cached_recs and cached_recs.get('recommendations'):
        top_buy = next((r for r in cached_recs['recommendations'] if r['rec_type'] in ['STRONG_BUY', 'BUY']), None)
        top_sell = next((r for r in cached_recs['recommendations'] if r['rec_type'] in ['STRONG_SELL', 'SELL']), None)

        if top_buy:
            st.markdown(f"""
            <div style="padding: 10px; background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); border-radius: 10px; margin-bottom: 8px;">
                <p style="margin: 0; color: #10b981; font-size: 11px; font-weight: 600;">🟢 أفضل شراء</p>
                <p style="margin: 4px 0 0 0; color: #f1f5f9; font-size: 13px; font-weight: 700;">{top_buy['symbol']} @ {top_buy['price']:.2f}</p>
                <p style="margin: 2px 0 0 0; color: #64748b; font-size: 10px;">درجة: {top_buy['eod_score']} | R/R ممتاز</p>
            </div>
            """, unsafe_allow_html=True)

        if top_sell:
            st.markdown(f"""
            <div style="padding: 10px; background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); border-radius: 10px; margin-bottom: 8px;">
                <p style="margin: 0; color: #ef4444; font-size: 11px; font-weight: 600;">🔴 أفضل بيع</p>
                <p style="margin: 4px 0 0 0; color: #f1f5f9; font-size: 13px; font-weight: 700;">{top_sell['symbol']} @ {top_sell['price']:.2f}</p>
                <p style="margin: 2px 0 0 0; color: #64748b; font-size: 10px;">درجة: {top_sell['eod_score']} | تجنب</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 12px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; text-align: center;">
            <p style="color: #64748b; font-size: 12px; margin: 0;">اضغط 🔄 لتحديث التوصيات</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Risk Settings
    st.header("🛡️ إعدادات المخاطرة")
    st.session_state.risk_settings['max_risk_pct'] = st.slider("المخاطرة/صفقة %", 0.5, 5.0, 2.0, 0.5)
    st.session_state.risk_settings['max_portfolio_heat'] = st.slider("سخونة المحفظة %", 10.0, 50.0, 25.0, 5.0)
    st.session_state.risk_settings['min_rr'] = st.slider("الحد الأدنى R/R", 1.0, 3.0, 1.5, 0.5)

    st.divider()

    # Global Refresh Button
    if st.button("🔄 تحديث البيانات والتوصيات", use_container_width=True, type="primary"):
        st.session_state.market_data_cache = {}
        st.session_state.alerts_cache = None
        st.session_state.price_history_sim = {}
        st.session_state.global_recommendations = None
        # Generate new recommendations
        prices = data_engine.get_live_prices()
        recs = rec_engine.generate_all_recommendations(prices)
        st.session_state.global_recommendations = recs
        st.session_state.last_scan_time = datetime.now()
        st.toast("✅ تم تحديث البيانات والتوصيات في جميع التبويبات!")
        st.rerun()

    st.divider()

    # Quick Stats
    st.header("📊 إحصائيات سريعة")
    total_tasks = len(st.session_state.tasks)
    completed = sum(1 for t in st.session_state.tasks if t["completed"])
    pending = total_tasks - completed
    high_priority = sum(1 for t in st.session_state.tasks if t["priority"] == "high" and not t["completed"])

    c1, c2 = st.columns(2)
    c1.metric("المهام", total_tasks)
    c2.metric("مكتمل", completed)
    c1.metric("قيد التنفيذ", pending)
    c2.metric("عالية الأولوية", high_priority, delta_color="inverse")

    if st.session_state.get('last_scan_time'):
        st.caption(f"آخر تحديث: {st.session_state.last_scan_time.strftime('%H:%M:%S')}")

# ==================== HEADER ====================
best_stock = {"symbol": "N/A", "change_pct": 0}
worst_stock = {"symbol": "N/A", "change_pct": 0}

stocks_live = data_engine.get_live_prices()
df_live = pd.DataFrame(stocks_live)

if not df_live.empty:
    best_stock = max(stocks_live, key=lambda x: x["change_pct"])
    worst_stock = min(stocks_live, key=lambda x: x["change_pct"])

# Market session status
session_status = rec_engine.get_market_session_status()

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding: 20px; background: linear-gradient(90deg, rgba(99,102,241,0.1), rgba(139,92,246,0.06)); border-radius: 16px; border: 1px solid rgba(99,102,241,0.15);">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ EGX Pro Terminal v24
        </h1>
        <p style="color: #64748b; margin-top: 6px; font-size: 14px;">
            <span class="live-pulse"></span> {session_status['phase']} | تحديث لحظي | {datetime.now().strftime("%H:%M:%S")}
        </p>
    </div>
    <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
        <div style="padding: 12px 18px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px;">
            <span style="color: #64748b; font-size: 11px;">EGX30</span>
            <span style="color: #10b981; margin-right: 8px; font-size: 20px; font-weight: 800;">24,850</span>
            <span class="badge badge-green">+1.24%</span>
        </div>
        <div style="padding: 12px 18px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px;">
            <span style="color: #64748b; font-size: 11px;">الأقوى</span>
            <span style="color: #fbbf24; margin-right: 8px; font-size: 18px; font-weight: 700;">{best_stock['symbol']}</span>
            <span class="badge badge-green">+{best_stock['change_pct']:.2f}%</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SECTION: MARKET RADAR ====================
if st.session_state.active_section == 'market':
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
                <p style="color: #64748b; font-size: 11px; margin: 0; text-transform: uppercase; font-weight: 600;">{idx['name']}</p>
                <p style="font-size: 22px; font-weight: 800; margin: 6px 0; color: {change_color};">{idx['value']:,.2f}</p>
                <div style="display: flex; justify-content: center; gap: 8px;">
                    <span style="color: {change_color}; font-size: 13px; font-weight: 700;">{arrow} {abs(idx['change']):.2f}%</span>
                    <span style="color: #64748b; font-size: 11px;">{idx['vol']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recommendation Banner in Market Radar
    cached_recs = rec_engine.get_cached_recommendations()
    if cached_recs and cached_recs.get('recommendations'):
        stats = rec_engine.get_recommendation_stats(cached_recs['recommendations'])
        market_sum = cached_recs.get('market_summary', {})

        st.markdown(f"""
        <div class="rec-panel">
            <div class="rec-header">
                <div class="rec-title">🎯 توصيات السوق الحالية</div>
                <div style="display: flex; gap: 8px;">
                    <span class="rec-count">{stats.get('strong_buy', 0) + stats.get('buy', 0)} شراء</span>
                    <span class="rec-count" style="background: rgba(239,68,68,0.15); color: #f87171; border-color: rgba(239,68,68,0.3);">{stats.get('strong_sell', 0) + stats.get('sell', 0)} بيع</span>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; gap: 16px; align-items: center;">
                    <span style="color: {market_sum.get('sentiment_color', '#94a3b8')}; font-size: 14px; font-weight: 600;">
                        {market_sum.get('sentiment_icon', '⚪')} مزاج السوق: {market_sum.get('sentiment', 'محايد')}
                    </span>
                    <span style="color: #64748b; font-size: 13px;">
                        📈 {market_sum.get('advancers', 0)} صاعد | 📉 {market_sum.get('decliners', 0)} هابط
                    </span>
                </div>
                <span style="color: #64748b; font-size: 12px;">آخر تحديث: {cached_recs.get('timestamp', datetime.now()).strftime('%H:%M:%S')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Top 3 recommendations quick view
        top_recs = cached_recs['recommendations'][:3]
        rec_cols = st.columns(3)
        for i, rec in enumerate(top_recs):
            with rec_cols[i]:
                st.markdown(render_mini_recommendation_card(rec), unsafe_allow_html=True)

    if not df_live.empty:
        row2_col1, row2_col2 = st.columns([2, 1])
        with row2_col1:
            st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🗺️ خريطة السوق التفاعلية</span></div>', unsafe_allow_html=True)
            try:
                fig_treemap = px.treemap(
                    df_live, path=[px.Constant("EGX"), 'sector', 'symbol'],
                    values='volume', color='change_pct',
                    color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
                    color_continuous_midpoint=0,
                )
                fig_treemap.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", color="#94a3b8", size=11),
                    height=400, margin=dict(t=0, b=0, l=0, r=0),
                )
                st.plotly_chart(fig_treemap, use_container_width=True)
            except Exception as e:
                st.error(f"خطأ في خريطة السوق: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_col2:
            st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🚀 الأكثر نشاطاً</span></div>', unsafe_allow_html=True)
            try:
                top_movers = df_live.nlargest(8, 'change_pct')
                for _, stock in top_movers.iterrows():
                    change_class = "status-up" if stock['change_pct'] >= 0 else "status-down"
                    change_sign = "+" if stock['change_pct'] >= 0 else ""
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
                        <div>
                            <span style="color: #fbbf24; font-weight: 700; font-size: 14px;">{stock['symbol']}</span>
                            <span style="color: #64748b; font-size: 12px; margin-right: 6px;">{stock['name'][:15]}</span>
                        </div>
                        <div style="text-align: left;">
                            <span style="font-size: 14px; font-weight: 700;">{stock['price']:.2f}</span>
                            <span class="{change_class}" style="font-size: 12px; margin-right: 4px; font-weight: 600;">{change_sign}{stock['change_pct']:.2f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass
            st.markdown('</div>', unsafe_allow_html=True)

        # Sector Performance
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 أداء القطاعات</span></div>', unsafe_allow_html=True)
        try:
            sector_perf = df_live.groupby('sector').agg({'change_pct': 'mean', 'volume': 'sum', 'market_cap': 'sum'}).reset_index()
            sector_perf.columns = ['القطاع', 'التغيير %', 'الحجم', 'القيمة السوقية']
            fig_sector = px.bar(sector_perf, x='القطاع', y='التغيير %', color='التغيير %',
                               color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'], text='التغيير %')
            fig_sector.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_sector.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#94a3b8"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                height=320, margin=dict(t=20, b=40)
            )
            st.plotly_chart(fig_sector, use_container_width=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)

    # Market Heatmap (if recommendations available)
    if cached_recs and cached_recs.get('recommendations'):
        st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🌡️ خريطة حرارية للتوصيات</span></div>', unsafe_allow_html=True)

        recs = cached_recs['recommendations']
        heatmap_data = []
        for r in recs[:30]:
            heatmap_data.append({
                'السهم': r['symbol'],
                'القطاع': r['sector'],
                'الدرجة': r['eod_score'],
                'التوصية': r['rec_action'],
                'السعر': r['price']
            })

        heatmap_df = pd.DataFrame(heatmap_data)
        if not heatmap_df.empty:
            fig_heat = px.density_heatmap(
                heatmap_df, x='القطاع', y='السهم', z='الدرجة',
                color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                title="توزيع درجات التوصيات بالقطاعات"
            )
            fig_heat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#94a3b8"),
                height=350
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: STOCKS LIST ====================
elif st.session_state.active_section == 'stocks':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📋 جميع الأسهم المتداولة - مع التوصيات الذكية</span></div>', unsafe_allow_html=True)

    # Get cached recommendations for stock cards
    cached_recs = rec_engine.get_cached_recommendations()
    rec_map = {}
    if cached_recs and cached_recs.get('recommendations'):
        for r in cached_recs['recommendations']:
            rec_map[r['symbol']] = r

    f_col1, f_col2, f_col3 = st.columns([3, 1, 1])
    with f_col1:
        search_term = st.text_input("🔍 البحث", placeholder="ابحث بالرمز أو اسم الشركة...", key="stocks_search", label_visibility="collapsed")
    with f_col2:
        sectors = ["الكل"] + sorted(df_live['sector'].unique().tolist()) if 'sector' in df_live.columns else ["الكل"]
        sector_filter = st.selectbox("القطاع", sectors, key="stocks_sector", label_visibility="collapsed")
    with f_col3:
        rec_filter = st.selectbox("التوصية", ["الكل", "شراء", "بيع", "انتظار"], key="rec_filter", label_visibility="collapsed")

    display_stocks = df_live.copy()
    if search_term:
        mask = display_stocks['symbol'].str.contains(search_term, case=False, na=False) | display_stocks['name'].str.contains(search_term, case=False, na=False)
        display_stocks = display_stocks[mask]
    if sector_filter != "الكل":
        display_stocks = display_stocks[display_stocks['sector'] == sector_filter]

    stock_list = display_stocks.to_dict('records')

    # Quick signals cache
    quick_signals = {}
    for stock in stock_list[:30]:
        try:
            df_q = data_engine.get_stock_history(stock['symbol'], "1mo")
            if df_q is not None and len(df_q) > 20:
                df_q = ta_engine.calculate_all(df_q)
                if df_q is not None:
                    sigs = ta_engine.generate_signals(df_q)
                    overall, _, text, trend, _ = ta_engine.calculate_overall(sigs)
                    quick_signals[stock['symbol']] = {"signal": overall, "trend": trend, "text": text}
        except:
            quick_signals[stock['symbol']] = {"signal": "HOLD", "trend": "neutral", "text": "محايد"}

    # Filter by recommendation if selected
    filtered_stocks = []
    for stock in stock_list:
        rec_data = rec_map.get(stock['symbol'])
        if rec_filter == "الكل":
            filtered_stocks.append(stock)
        elif rec_filter == "شراء" and rec_data and rec_data['rec_type'] in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
            filtered_stocks.append(stock)
        elif rec_filter == "بيع" and rec_data and rec_data['rec_type'] in ['STRONG_SELL', 'SELL', 'WEAK_SELL']:
            filtered_stocks.append(stock)
        elif rec_filter == "انتظار" and rec_data and rec_data['rec_type'] == 'HOLD':
            filtered_stocks.append(stock)
        elif not rec_data and rec_filter == "الكل":
            filtered_stocks.append(stock)

    # Show recommendation summary bar
    if rec_map:
        buy_count = sum(1 for s in filtered_stocks if rec_map.get(s['symbol'], {}).get('rec_type') in ['STRONG_BUY', 'BUY'])
        sell_count = sum(1 for s in filtered_stocks if rec_map.get(s['symbol'], {}).get('rec_type') in ['STRONG_SELL', 'SELL'])
        hold_count = len(filtered_stocks) - buy_count - sell_count

        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 16px; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #10b981; font-size: 13px; font-weight: 600;">🟢 {buy_count} شراء</span>
            <span style="color: #94a3b8; font-size: 13px; font-weight: 600;">⚪ {hold_count} انتظار</span>
            <span style="color: #ef4444; font-size: 13px; font-weight: 600;">🔴 {sell_count} بيع</span>
            <span style="color: #64748b; font-size: 13px; margin-right: auto;">من {len(stock_list)} سهم</span>
        </div>
        """, unsafe_allow_html=True)

    for stock in filtered_stocks:
        signal_info = quick_signals.get(stock['symbol'], {"signal": "HOLD", "trend": "neutral", "text": "محايد"})
        signal_class = "buy-signal" if signal_info['signal'] in ['BUY', 'STRONG_BUY'] else "sell-signal" if signal_info['signal'] in ['SELL', 'STRONG_SELL'] else "hold-signal" if signal_info['trend'] in ['weak_bullish', 'weak_bearish'] else "neutral-signal"
        change_class = "up" if stock['change_pct'] >= 0 else "down"
        change_sign = "+" if stock['change_pct'] >= 0 else ""

        # Add recommendation badge if available
        rec_badge_html = ""
        rec_data = rec_map.get(stock['symbol'])
        if rec_data:
            rec_badge_html = render_recommendation_badge(rec_data['rec_type'], size="small")

        st.markdown(f"""
        <div class="stock-card-rect {signal_class}">
            <div class="stock-rect-info">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span class="stock-rect-symbol">{stock['symbol']}</span>
                    <span class="badge {'badge-green' if signal_info['signal'] in ['BUY', 'STRONG_BUY'] else 'badge-red' if signal_info['signal'] in ['SELL', 'STRONG_SELL'] else 'badge-yellow'}">{signal_info['text']}</span>
                    <span class="badge badge-blue">{stock['sector']}</span>
                    {rec_badge_html}
                </div>
                <span class="stock-rect-name">{stock['name']}</span>
            </div>
            <div class="stock-rect-price-section">
                <span class="stock-rect-price">{stock['price']:.2f}</span>
                <span class="stock-rect-change {change_class}">{change_sign}{stock['change_pct']:.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show mini recommendation details if available
        if rec_data:
            st.markdown(f"""
            <div style="margin: -8px 0 12px 0; padding: 8px 16px; background: {rec_data['rec_color']}08; border-radius: 0 0 12px 12px; border: 1px solid {rec_data['rec_color']}15; border-top: none;">
                <div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
                    <span style="color: {rec_data['rec_color']}; font-size: 11px; font-weight: 600;">🎯 {rec_data['rec_action']} (درجة: {rec_data['eod_score']})</span>
                    <span style="color: #64748b; font-size: 11px;">دخول: {rec_data['entry']:.2f} | SL: {rec_data['stop_loss']:.2f} | TP: {rec_data['target1']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Compact buttons inside card area
        btn_cols = st.columns([1, 1, 1, 1])
        with btn_cols[0]:
            st.button("🔮 تحليل فني", key=f"analyze_{stock['symbol']}", on_click=select_stock_callback, args=(stock['symbol'],), use_container_width=True)
        with btn_cols[1]:
            st.button("📊 مالي", key=f"fund_{stock['symbol']}", on_click=edit_company_callback, args=(stock['symbol'],), use_container_width=True)
        with btn_cols[2]:
            st.button("📈 بيانات", key=f"data_{stock['symbol']}", on_click=edit_company_callback, args=(stock['symbol'],), use_container_width=True)
        with btn_cols[3]:
            st.button("🎁 توزيعات", key=f"div_{stock['symbol']}", on_click=lambda sym=stock['symbol']: [set_section('dividends'), setattr(st.session_state, 'div_filter_sym', sym)], use_container_width=True)
        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: INVESTMENT FUNDS ====================
elif st.session_state.active_section == 'funds':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">💰 صناديق الاستثمار وصناديق الأسهم المصرية</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 14px; background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 10px; margin-bottom: 20px;">
        <p style="color: #818cf8; font-weight: 700; margin: 0; font-size: 14px;">📌 صناديق الاستثمار المصرية</p>
        <p style="color: #a5b4fc; font-size: 13px; margin-top: 6px;">بيانات محاكاة واقعية للصناديق المتداولة في البورصة المصرية مع التوصيات المقترحة.</p>
    </div>
    """, unsafe_allow_html=True)

    # Fund Type Filter
    fund_types = ["الكل", "أسهم", "ETF", "دخل ثابت", "نقد", "عقاري", "قطاعي", "إسلامي"]
    selected_fund_type = st.selectbox("نوع الصندوق", fund_types, key="fund_type_filter")

    all_funds = funds_engine.get_all_funds()
    if selected_fund_type != "الكل":
        filtered_funds = [f for f in all_funds if f['type'] == selected_fund_type]
    else:
        filtered_funds = all_funds

    # Fund Metrics Summary
    if filtered_funds:
        total_aum = sum(f['aum'] for f in filtered_funds)
        avg_ytd = sum(f['ytd'] for f in filtered_funds) / len(filtered_funds)
        best_fund = max(filtered_funds, key=lambda x: x['ytd'])

        met_cols = st.columns(4)
        met_cols[0].metric("عدد الصناديق", len(filtered_funds))
        met_cols[1].metric("إجمالي الأصول", f"{total_aum/1e9:.1f}B ج.م")
        met_cols[2].metric("متوسط YTD", f"{avg_ytd:.1f}%")
        met_cols[3].metric("الأفضل YTD", f"{best_fund['name'][:15]}...", f"+{best_fund['ytd']:.1f}%")

    st.subheader("📋 قائمة الصناديق")
    for fund in filtered_funds:
        change_color = "#10b981" if fund['change'] >= 0 else "#ef4444"
        change_sign = "+" if fund['change'] >= 0 else ""
        risk_color = "#10b981" if fund['risk'] == "منخفض" else "#f59e0b" if fund['risk'] == "متوسط" else "#ef4444"

        st.markdown(f"""
        <div class="fund-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div>
                    <h3 style="margin: 0; font-size: 17px; color: #f1f5f9; font-weight: 700;">{fund['name']}</h3>
                    <div style="display: flex; gap: 8px; margin-top: 6px;">
                        <span class="badge badge-blue">{fund['type']}</span>
                        <span class="badge" style="background: {risk_color}15; color: {risk_color};">مخاطرة: {fund['risk']}</span>
                    </div>
                </div>
                <div style="text-align: left;">
                    <p style="margin: 0; font-size: 22px; font-weight: 800; color: {change_color};">{fund['nav']:.2f}</p>
                    <p style="margin: 0; font-size: 13px; color: {change_color}; font-weight: 600;">{change_sign}{fund['change']:.2f}%</p>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05);">
                <div style="text-align: center;">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">YTD</p>
                    <p style="color: #fbbf24; font-size: 16px; font-weight: 700; margin: 4px 0;">+{fund['ytd']:.1f}%</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">الأصول (AUM)</p>
                    <p style="color: #e2e8f0; font-size: 16px; font-weight: 700; margin: 4px 0;">{fund['aum']/1e6:.0f}M ج.م</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">أهم القابضات</p>
                    <p style="color: #94a3b8; font-size: 12px; margin: 4px 0;">{', '.join(fund['top_holdings'][:3]) if fund['top_holdings'] else 'متنوع'}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Fund Comparison Chart
    st.subheader("📊 مقارنة أداء الصناديق")
    fund_df = pd.DataFrame(filtered_funds)
    if not fund_df.empty:
        fig_funds = px.bar(fund_df, x='name', y='ytd', color='ytd',
                          color_continuous_scale=['#ef4444', '#1e1b4b', '#10b981'],
                          text='ytd', title="عائد الصناديق من بداية العام (YTD %)")
        fig_funds.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_funds.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#94a3b8"),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            height=350, margin=dict(t=40, b=80)
        )
        st.plotly_chart(fig_funds, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: DIVIDENDS ====================
elif st.session_state.active_section == 'dividends':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🎁 التوزيعات النقدية للشركات المصرية</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 14px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 10px; margin-bottom: 20px;">
        <p style="color: #34d399; font-weight: 700; margin: 0; font-size: 14px;">📌 توزيعات الأرباح النقدية</p>
        <p style="color: #6ee7b7; font-size: 13px; margin-top: 6px;">متابعة مواعيد التوزيعات النقدية للشركات المدرجة في البورصة المصرية.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sub-navigation for dividends
    div_sub = st.columns(3)
    with div_sub[0]:
        if st.button("📅 القادمة", use_container_width=True, type="primary" if st.session_state.get('div_sub', 'upcoming') == 'upcoming' else "secondary"):
            st.session_state.div_sub = 'upcoming'
    with div_sub[1]:
        if st.button("📊 الكل", use_container_width=True, type="primary" if st.session_state.get('div_sub', 'upcoming') == 'all' else "secondary"):
            st.session_state.div_sub = 'all'
    with div_sub[2]:
        if st.button("📈 مقارنة القطاعات", use_container_width=True, type="primary" if st.session_state.get('div_sub', 'upcoming') == 'sectors' else "secondary"):
            st.session_state.div_sub = 'sectors'

    div_sub_view = st.session_state.get('div_sub', 'upcoming')

    if div_sub_view == 'upcoming':
        st.subheader("📅 التوزيعات القادبة")
        upcoming = dividends_engine.get_upcoming_dividends()
        if upcoming:
            for div in upcoming:
                days_until = (datetime.strptime(div['dividend_date'], "%Y-%m-%d") - datetime.now()).days
                status_color = "#f59e0b" if days_until <= 7 else "#10b981"
                st.markdown(f"""
                <div class="dividend-card">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                            <span style="font-size: 18px; font-weight: 800; color: #fbbf24;">{div['symbol']}</span>
                            <span style="font-size: 14px; color: #e2e8f0; font-weight: 600;">{div['name']}</span>
                            <span class="badge badge-blue">{div['sector']}</span>
                        </div>
                        <div style="display: flex; gap: 14px;">
                            <span style="font-size: 13px; color: #94a3b8;">📅 {div['dividend_date']}</span>
                            <span style="font-size: 13px; color: {status_color}; font-weight: 600;">⏳ {days_until} يوم</span>
                            <span style="font-size: 13px; color: #94a3b8;">🔁 {div['frequency']}</span>
                        </div>
                    </div>
                    <div style="text-align: left;">
                        <p style="margin: 0; font-size: 22px; font-weight: 800; color: #10b981;">{div['amount']:.2f} ج.م</p>
                        <p style="margin: 0; font-size: 13px; color: #fbbf24; font-weight: 600;">عائد: {div['yield']:.2f}%</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد توزيعات قريبة في الفترة الحالية")

    elif div_sub_view == 'all':
        st.subheader("📊 جميع التوزيعات")
        all_divs = dividends_engine.get_all_dividends()
        div_df = pd.DataFrame(all_divs)
        if not div_df.empty:
            st.dataframe(div_df[['symbol', 'name', 'sector', 'dividend_date', 'amount', 'yield', 'frequency', 'status']].rename(columns={
                'symbol': 'الرمز', 'name': 'الشركة', 'sector': 'القطاع', 'dividend_date': 'التاريخ',
                'amount': 'القيمة', 'yield': 'العائد %', 'frequency': 'التكرار'
            }), use_container_width=True, hide_index=True)

    elif div_sub_view == 'sectors':
        st.subheader("📈 مقارنة عائد التوزيعات بالقطاع")
        sector_yields = dividends_engine.get_sector_yields()
        if sector_yields:
            sec_df = pd.DataFrame(list(sector_yields.items()), columns=['القطاع', 'متوسط العائد %'])
            fig_sec = px.bar(sec_df, x='القطاع', y='متوسط العائد %', color='متوسط العائد %',
                            color_continuous_scale=['#10b981', '#fbbf24', '#ef4444'],
                            text='متوسط العائد %')
            fig_sec.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_sec.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", color="#94a3b8"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickangle=-45),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                height=350, margin=dict(t=40, b=80)
            )
            st.plotly_chart(fig_sec, use_container_width=True)

    # Dividend yield leaders
    st.subheader("🏆 أعلى عائد توزيعات")
    all_divs = dividends_engine.get_all_dividends()
    top_yields = sorted(all_divs, key=lambda x: x['yield'], reverse=True)[:10]
    for div in top_yields:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.03);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #fbbf24; font-weight: 700; font-size: 15px;">{div['symbol']}</span>
                <span style="color: #94a3b8; font-size: 13px;">{div['name']}</span>
            </div>
            <div style="display: flex; gap: 18px;">
                <span style="color: #10b981; font-size: 15px; font-weight: 700;">{div['yield']:.2f}%</span>
                <span style="color: #64748b; font-size: 13px;">{div['amount']:.2f} ج.م</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: AI SCANNER ====================
elif st.session_state.active_section == 'ai_scan':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🤖 الماسح الآلي الذكي - مع التوصيات الموحدة</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 14px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 10px; margin-bottom: 20px;">
        <p style="color: #f87171; font-weight: 700; margin: 0; font-size: 14px;">⚠️ تحذير المخاطر</p>
        <p style="color: #fca5a5; font-size: 13px; margin-top: 6px;">التحليل الآلي يعتمد على البيانات التاريخية والمحاكاة. استخدم Stop Loss لحماية رأس مالك.</p>
    </div>
    """, unsafe_allow_html=True)

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1])
    with ctrl_col1: min_score = st.slider("الحد الأدنى للدرجة", 0, 100, 55, key="ai_min_score")
    with ctrl_col2: max_risk = st.slider("الحد الأقصى للمخاطرة %", 0.5, 10.0, 5.0, 0.5, key="ai_max_risk")
    with ctrl_col3: min_rr = st.slider("الحد الأدنى R/R", 1.0, 5.0, 1.5, 0.5, key="ai_min_rr")

    if st.button("🚀 تشغيل الماسح الآلي", type="primary", use_container_width=True, on_click=run_analysis_callback):
        pass

    # Also show unified recommendations if available
    cached_recs = rec_engine.get_cached_recommendations()
    if cached_recs and cached_recs.get('recommendations'):
        st.markdown("""
        <div class="rec-panel" style="margin-top: 16px;">
            <div class="rec-header">
                <div class="rec-title">🎯 التوصيات الموحدة المتاحة</div>
            </div>
            <p style="color: #94a3b8; font-size: 13px;">تم تحديث التوصيات لجميع الأسهم. استخدم "تشغيل الماسح الآلي" للحصول على تحليل تفصيلي إضافي.</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.alerts_cache is not None:
        alerts = st.session_state.alerts_cache

        st.subheader("📊 ملخص الفرص")
        sum_cols = st.columns(4)
        buy_count = len([a for a in alerts if a['signal'] in ['BUY', 'STRONG_BUY']])
        sell_count = len([a for a in alerts if a['signal'] in ['SELL', 'STRONG_SELL']])
        avg_score = sum(a['score'] for a in alerts) / len(alerts) if alerts else 0

        sum_cols[0].metric("الفرص الشرائية", buy_count)
        sum_cols[1].metric("إشارات البيع", sell_count)
        sum_cols[2].metric("متوسط الدرجة", f"{avg_score:.1f}")
        sum_cols[3].metric("المحللة", len(alerts))

        # Buy Opportunities
        buy_ops = [a for a in alerts if a['score'] >= min_score and a['signal'] in ['BUY', 'STRONG_BUY'] and a['risk_pct'] <= max_risk and a['rr_ratio'] >= min_rr]
        if buy_ops:
            st.subheader("🔥 أفضل فرص الشراء المؤكدة")
            for i, alert in enumerate(buy_ops[:8]):
                with st.expander(f"{i+1}. {alert['name']} ({alert['symbol']}) - درجة: {alert['score']} | R/R: {alert['rr_ratio']}", expanded=i < 2):
                    sig_cols = st.columns([1, 3, 1])
                    with sig_cols[0]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 14px; background: {alert['alert_color']}15; border: 1px solid {alert['alert_color']}40; border-radius: 10px;">
                            <p style="margin: 0; color: {alert['alert_color']}; font-size: 32px; font-weight: 800;">{alert['score']}</p>
                            <p style="margin: 6px 0 0 0; color: {alert['alert_color']}; font-size: 12px; font-weight: 600;">درجة الفرصة</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with sig_cols[1]:
                        st.markdown(f"""
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 17px;">{alert['name']} | {alert['sector']}</p>
                            <p style="color: #64748b; font-size: 14px; margin: 6px 0;">
                                السعر: <b>{alert['price']}</b> | RSI: <b>{alert['rsi']}</b> | MACD: <b>{alert['macd']}</b>
                            </p>
                            <p style="color: #10b981; font-size: 12px; margin: 6px 0;">{' | '.join(alert.get('reasons', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with sig_cols[2]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background: {alert['risk_color']}15; border: 1px solid {alert['risk_color']}40; border-radius: 10px;">
                            <p style="margin: 0; color: {alert['risk_color']}; font-size: 12px; font-weight: 700;">{alert['risk_class']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    risk_cols = st.columns(4)
                    risk_data = [
                        ("🛑 Stop Loss", alert['stop_loss'], alert['risk_pct'], "#ef4444"),
                        ("📍 السعر", alert['price'], 0, "#6366f1"),
                        ("🎯 الهدف 1", alert['take_profit_1'], alert['reward_pct'], "#10b981"),
                        ("🎯🎯 الهدف 2", round(alert['price'] + (alert['price'] - alert['stop_loss']) * 3.5, 2), 0, "#fbbf24")
                    ]
                    for j, (label, value, pct, color) in enumerate(risk_data):
                        with risk_cols[j]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid {color}30;">
                                <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{label}</p>
                                <p style="font-size: 20px; font-weight: 700; color: {color}; margin: 6px 0;">{value:.2f}</p>
                                {f'<p style="font-size: 11px; color: {color}; margin: 0;">{pct:.1f}%</p>' if pct else ''}
                            </div>
                            """, unsafe_allow_html=True)

                    st.button(f"🔮 تحليل مفصل لـ {alert['symbol']}", key=f"detail_{alert['symbol']}", on_click=select_stock_callback, args=(alert['symbol'],), use_container_width=True, type="primary")

        # Full Table
        st.subheader("📋 الجدول التحليلي الكامل")
        table_data = []
        for alert in alerts:
            table_data.append({
                "الرمز": alert['symbol'], "الشركة": alert['name'], "القطاع": alert['sector'],
                "السعر": alert['price'], "الإشارة": alert['signal_text'], "الدرجة": alert['score'],
                "RSI": alert['rsi'], "MACD": alert['macd'], "R/R": alert['rr_ratio'],
                "المخاطرة%": alert['risk_pct'], "التقلب%": alert['volatility'],
                "Stop Loss": alert['stop_loss'], "الهدف": alert['take_profit_1']
            })
        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 تصدير التحليل CSV",
            data=df_table.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"egx_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True
        )
    else:
        st.info("👈 اضغط 'تشغيل الماسح الآلي' لبدء المسح الشامل")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: BACKTESTING ====================
elif st.session_state.active_section == 'backtest':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">📊 محرك Backtesting متقدم</span></div>', unsafe_allow_html=True)

    bt_col1, bt_col2 = st.columns([1, 3])
    with bt_col1:
        symbols = df_live['symbol'].tolist() if not df_live.empty else ["COMI"]
        bt_ticker = st.selectbox("السهم", symbols, key="bt_ticker")
        strategy = st.selectbox("الاستراتيجية", [
            "RSI_MACD - تقاطع الزخم", "MA_Crossover - تقاطع المتوسطات",
            "Bollinger - نطاقات بولينجر", "Mean_Reversion - العودة للمتوسط",
            "ADX_Trend - اتباع الاتجاه"
        ], key="bt_strategy")
        period = st.selectbox("الفترة", ["3mo", "6mo", "1y", "2y"], index=2, key="bt_period")
        initial_capital = st.number_input("رأس المال", value=100000, step=10000, key="bt_capital")
        run_bt = st.button("🚀 تشغيل الاختبار", type="primary", use_container_width=True)

    with bt_col2:
        if run_bt:
            with st.spinner("جاري التحليل..."):
                df_bt = data_engine.get_stock_history(bt_ticker, period)
                if df_bt is None or df_bt.empty:
                    st.error("❌ تعذر جلب البيانات")
                else:
                    try:
                        df_bt = df_bt[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                        df_bt['Returns'] = df_bt['Close'].pct_change()
                        strategy_key = strategy.split(" - ")[0]

                        if strategy_key == "RSI_MACD":
                            delta = df_bt['Close'].diff()
                            gain = delta.clip(lower=0).rolling(14).mean()
                            loss = (-delta.clip(upper=0)).rolling(14).mean()
                            rs = gain / loss.replace(0, np.nan)
                            rsi = 100 - (100 / (1 + rs))
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
                            df_bt['Deviation'] = (df_bt['Close'] - df_bt['MA20']) / df_bt['MA20'].replace(0, np.nan)
                            df_bt['Signal'] = np.where(df_bt['Deviation'] < -0.03, 1, np.where(df_bt['Deviation'] > 0.03, -1, 0))
                        else:
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

                        m1, m2, m3, m4, m5 = st.columns(5)
                        m1.metric("عائد الاستراتيجية", f"{total_return:+.2f}%")
                        m2.metric("Buy & Hold", f"{buy_hold:+.2f}%")
                        m3.metric("Sharpe", f"{sharpe:.2f}")
                        m4.metric("Win Rate", f"{win_rate:.1f}%")
                        m5.metric("Max DD", f"{max_dd:.2f}%")

                        fig_equity = go.Figure()
                        fig_equity.add_trace(go.Scatter(x=df_bt.index, y=df_bt['Equity'].values, mode='lines', name='رأس المال', line=dict(color='#6366f1', width=2), fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.1)'))
                        bh_curve = initial_capital * (1 + df_bt['Returns'].fillna(0)).cumprod()
                        fig_equity.add_trace(go.Scatter(x=df_bt.index, y=bh_curve.values, mode='lines', name='Buy & Hold', line=dict(color='#fbbf24', width=2, dash='dash')))
                        fig_equity.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", color="#94a3b8"), height=350)
                        st.plotly_chart(fig_equity, use_container_width=True)
                    except Exception as e:
                        st.error(f"خطأ في الاختبار: {str(e)}")
        else:
            st.info("👈 اختر السهم والاستراتيجية واضغط 'تشغيل الاختبار'")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: SMART TASKS ====================
elif st.session_state.active_section == 'tasks':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">✅ المهام الذكية وإدارة المحفظة</span></div>', unsafe_allow_html=True)

    with st.expander("➕ إضافة مهمة جديدة", expanded=False):
        t_col1, t_col2, t_col3 = st.columns([3, 1, 1])
        with t_col1: st.text_input("عنوان المهمة", placeholder="مثال: مراجعة أداء سهم CIB", key="new_task_title")
        with t_col2:
            st.selectbox("الأولوية", ["high", "medium", "low"], 
                        format_func=lambda x: {"high": "🔴 عالية", "medium": "🟡 متوسطة", "low": "🟢 منخفضة"}[x],
                        key="new_task_priority")
        with t_col3:
            st.selectbox("التصنيف", ["work", "personal", "learning", "urgent"],
                        format_func=lambda x: {"work": "💼 عمل", "personal": "👤 شخصي", "learning": "📚 تعلم", "urgent": "🚨 عاجل"}[x],
                        key="new_task_category")
        t_col4, t_col5 = st.columns([2, 1])
        with t_col4: st.date_input("تاريخ الاستحقاق", datetime.now() + timedelta(days=3), key="new_task_due")
        with t_col5: st.button("💾 حفظ", on_click=add_task_callback, use_container_width=True)

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1: task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...", key="task_search")
    with f_col2:
        filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"],
                                       format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x],
                                       key="filter_priority")
    with f_col3:
        filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"], key="filter_status")

    filtered = st.session_state.tasks.copy()
    if task_search: filtered = [t for t in filtered if task_search.lower() in t["title"].lower()]
    if filter_priority != "الكل": filtered = [t for t in filtered if t["priority"] == filter_priority]
    if filter_status == "مكتمل": filtered = [t for t in filtered if t["completed"]]
    elif filter_status == "قيد التنفيذ": filtered = [t for t in filtered if not t["completed"]]

    priority_colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
    category_icons = {"work": "💼", "personal": "👤", "learning": "📚", "urgent": "🚨"}

    for task in filtered:
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
                        <div style="display: flex; gap: 8px; margin-top: 4px;">
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
            st.checkbox("تم", value=task["completed"], key=f"check_{task['id']}", on_change=toggle_task, args=(task['id'],), label_visibility="collapsed")
        with act_col2:
            st.button("🗑️", key=f"del_{task['id']}", on_click=delete_task, args=(task['id'],), help="حذف")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECTION: END OF SESSION RECOMMENDATIONS ====================
elif st.session_state.active_section == 'eod_recommendations':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pro-panel-header"><span class="pro-panel-title">🎯 توصيات نهاية الجلسة - End of Session Signals</span></div>', unsafe_allow_html=True)

    # Market session status
    session_status = rec_engine.get_market_session_status()
    st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.06)); border-radius: 16px; border: 1px solid rgba(99,102,241,0.25); margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; font-size: 22px; font-weight: 800;">{session_status['icon']} حالة السوق: {session_status['status']}</h2>
                <p style="color: {session_status['color']}; margin: 6px 0; font-size: 15px; font-weight: 700;">{session_status['phase']}</p>
            </div>
            <div style="text-align: center; padding: 14px 24px; background: rgba(255,255,255,0.05); border-radius: 12px;">
                <p style="margin: 0; color: #64748b; font-size: 12px; font-weight: 600;">الوقت الحالي</p>
                <p style="margin: 6px 0 0 0; font-size: 28px; font-weight: 800; color: #f1f5f9;">{datetime.now().strftime("%H:%M")}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Warning if market still open
    if not session_status['is_open'] and datetime.now().hour < 14:
        st.warning("⚠️ السوق ما زال مفتوحاً. التوصيات تُحسب بناءً على البيانات الحالية وقد تتغير عند الإغلاق.")
    elif session_status['status'] == "مغلق":
        st.success("✅ السوق مغلق. التوصيات نهائية للجلسة الحالية.")

    # Generate recommendations button
    col_gen1, col_gen2 = st.columns([3, 1])
    with col_gen1:
        st.markdown("<p style='color: #94a3b8; font-size: 14px;'>يحلل النظام جميع الأسهم ويولد توصيات شراء/بيع/انتظار بناءً على:</p>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
            <span class="badge badge-blue">📊 المؤشرات الفنية</span>
            <span class="badge badge-green">📈 أداء الجلسة</span>
            <span class="badge badge-yellow">📊 حجم التداول</span>
            <span class="badge badge-purple">🎯 الدعم والمقاومة</span>
            <span class="badge badge-blue">🕯️ نماذج الشموع</span>
            <span class="badge badge-green">🌍 مزاج السوق</span>
            <span class="badge badge-yellow">📊 التحليل المالي</span>
        </div>
        """, unsafe_allow_html=True)
    with col_gen2:
        if st.button("🎯 توليد التوصيات", type="primary", use_container_width=True):
            with st.spinner("جاري تحليل جميع الأسهم وإنشاء التوصيات..."):
                prices = data_engine.get_live_prices()
                recs = rec_engine.generate_all_recommendations(prices)
                st.session_state.global_recommendations = recs
                st.session_state.last_scan_time = datetime.now()
                st.toast("✅ تم إنشاء التوصيات بنجاح!")
                st.rerun()

    # Display recommendations
    recs = st.session_state.get('global_recommendations')
    if recs is None:
        # Try to get from unified engine cache
        cached = rec_engine.get_cached_recommendations()
        if cached and cached.get('recommendations'):
            recs = cached['recommendations']

    if recs:
        stats = rec_engine.get_recommendation_stats(recs)
        market_summary = rec_engine.RECOMMENDATION_CACHE.get('market_summary', {}) if rec_engine.RECOMMENDATION_CACHE else {}

        # Summary dashboard
        st.subheader("📊 ملخص توصيات الجلسة")
        sum_cols = st.columns(6)
        summary_items = [
            ("🟢 شراء قوي", stats.get('strong_buy', 0), "#10b981"),
            ("🟢 شراء", stats.get('buy', 0), "#34d399"),
            ("🟡 شراء ضعيف", stats.get('weak_buy', 0), "#fbbf24"),
            ("⚪ انتظار", stats.get('hold', 0), "#94a3b8"),
            ("🔴 بيع", stats.get('sell', 0), "#f87171"),
            ("🔴 بيع قوي", stats.get('strong_sell', 0), "#ef4444"),
        ]
        for i, (label, value, color) in enumerate(summary_items):
            with sum_cols[i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 14px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid {color}30;">
                    <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{label}</p>
                    <p style="font-size: 24px; font-weight: 800; color: {color}; margin: 6px 0;">{value}</p>
                </div>
                """, unsafe_allow_html=True)

        # Top sectors
        if stats.get('top_buy_sector') != "N/A" or stats.get('top_sell_sector') != "N/A":
            sec_cols = st.columns(2)
            with sec_cols[0]:
                st.markdown(f"""
                <div style="padding: 14px; background: rgba(16,185,129,0.05); border-radius: 10px; border: 1px solid rgba(16,185,129,0.25);">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">🏆 أفضل قطاع للشراء</p>
                    <p style="color: #10b981; font-size: 18px; font-weight: 800; margin: 6px 0;">{stats.get('top_buy_sector', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            with sec_cols[1]:
                st.markdown(f"""
                <div style="padding: 14px; background: rgba(239,68,68,0.05); border-radius: 10px; border: 1px solid rgba(239,68,68,0.25);">
                    <p style="color: #64748b; font-size: 12px; margin: 0; font-weight: 600;">⚠️ قطاع يحتاج بيع</p>
                    <p style="color: #ef4444; font-size: 18px; font-weight: 800; margin: 6px 0;">{stats.get('top_sell_sector', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

        # Top Buy Recommendations
        buy_recs = [r for r in recs if r['rec_type'] in ['STRONG_BUY', 'BUY']]
        if buy_recs:
            st.subheader("🟢 توصيات الشراء القوية")
            for i, rec in enumerate(buy_recs[:10]):
                with st.expander(f"{rec['rec_icon']} {rec['name']} ({rec['symbol']}) - درجة: {rec['eod_score']} | {rec['rec_action']}", expanded=i < 3):
                    rec_cols = st.columns([1, 2, 1])
                    with rec_cols[0]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 14px; background: {rec['rec_color']}15; border: 1px solid {rec['rec_color']}40; border-radius: 12px;">
                            <p style="margin: 0; color: {rec['rec_color']}; font-size: 36px; font-weight: 800;">{rec['eod_score']}</p>
                            <p style="margin: 6px 0 0 0; color: {rec['rec_color']}; font-size: 12px; font-weight: 700;">درجة التوصية</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with rec_cols[1]:
                        st.markdown(f"""
                        <div>
                            <p style="margin: 0; font-weight: 700; font-size: 17px;">{rec['name']} | {rec['sector']}</p>
                            <p style="color: #64748b; font-size: 14px; margin: 6px 0;">
                                السعر: <b style="color: #f1f5f9;">{rec['price']:.2f}</b> | 
                                تغيير اليوم: <b style="color: {'#10b981' if rec['change_pct'] >= 0 else '#ef4444'};">{rec['change_pct']:+.2f}%</b> |
                                RSI: <b>{rec['rsi']}</b>
                            </p>
                            <p style="color: #10b981; font-size: 13px; margin: 6px 0;">{' | '.join(rec.get('reasons', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with rec_cols[2]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.02); border-radius: 10px;">
                            <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">الإلحاح</p>
                            <p style="color: {rec['rec_color']}; font-size: 14px; font-weight: 700; margin: 4px 0;">{rec['urgency']}</p>
                            <p style="color: #64748b; font-size: 11px; margin: 6px 0 0 0; font-weight: 600;">مدة الاحتفاظ</p>
                            <p style="color: #818cf8; font-size: 13px; font-weight: 700; margin: 4px 0;">{rec['hold_period']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Trading levels
                    level_cols = st.columns(5)
                    levels = [
                        ("🎯 دخول", rec['entry'], "#6366f1"),
                        ("🛑 وقف الخسارة", rec['stop_loss'], "#ef4444"),
                        ("🎯 الهدف 1", rec['target1'], "#10b981"),
                        ("🎯🎯 الهدف 2", rec['target2'], "#fbbf24"),
                        ("📊 الدعم", rec['support'], "#94a3b8"),
                    ]
                    for j, (label, value, color) in enumerate(levels):
                        with level_cols[j]:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid {color}30;">
                                <p style="color: #64748b; font-size: 11px; margin: 0; font-weight: 600;">{label}</p>
                                <p style="font-size: 18px; font-weight: 700; color: {color}; margin: 6px 0;">{value:.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # Action buttons
                    btn_cols = st.columns([1, 1])
                    with btn_cols[0]:
                        st.button(f"🔮 تحليل فني تفصيلي", key=f"eod_tech_{rec['symbol']}", on_click=select_stock_callback, args=(rec['symbol'],), use_container_width=True)
                    with btn_cols[1]:
                        st.button(f"📊 التحليل المالي", key=f"eod_fund_{rec['symbol']}", on_click=edit_company_callback, args=(rec['symbol'],), use_container_width=True)

        # Sell Recommendations
        sell_recs = [r for r in recs if r['rec_type'] in ['STRONG_SELL', 'SELL']]
        if sell_recs:
            st.subheader("🔴 توصيات البيع")
            for rec in sell_recs[:8]:
                with st.expander(f"{rec['rec_icon']} {rec['name']} ({rec['symbol']}) - درجة: {rec['eod_score']} | {rec['rec_action']}"):
                    st.markdown(f"""
                    <div style="padding: 14px; background: rgba(239,68,68,0.05); border-radius: 10px; border: 1px solid rgba(239,68,68,0.2);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; font-weight: 700; color: #f1f5f9; font-size: 16px;">{rec['name']} | {rec['sector']}</p>
                                <p style="color: #64748b; font-size: 14px; margin: 6px 0;">
                                    السعر: <b>{rec['price']:.2f}</b> | تغيير: <b>{rec['change_pct']:+.2f}%</b> | RSI: <b>{rec['rsi']}</b>
                                </p>
                            </div>
                            <div style="text-align: center; padding: 10px 18px; background: {rec['rec_color']}15; border-radius: 10px;">
                                <p style="margin: 0; color: {rec['rec_color']}; font-size: 22px; font-weight: 800;">{rec['eod_score']}</p>
                            </div>
                        </div>
                        <div style="display: flex; gap: 14px; margin-top: 10px;">
                            <span style="color: #94a3b8; font-size: 13px;">🛑 SL: {rec['stop_loss']:.2f}</span>
                            <span style="color: #94a3b8; font-size: 13px;">📊 مقاومة: {rec['resistance']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Watch list
        watch_recs = [r for r in recs if r['rec_type'] in ['HOLD', 'WEAK_BUY', 'WEAK_SELL']]
        if watch_recs:
            st.subheader("👁️ قائمة المراقبة")
            watch_df = pd.DataFrame([{
                "الرمز": r['symbol'], "الشركة": r['name'], "القطاع": r['sector'],
                "السعر": r['price'], "التغيير %": f"{r['change_pct']:+.2f}%",
                "الدرجة": r['eod_score'], "التوصية": r['rec_action'],
                "الدعم": r['support'], "المقاومة": r['resistance']
            } for r in watch_recs[:15]])
            st.dataframe(watch_df, use_container_width=True, hide_index=True)

        # Export recommendations
        export_df = pd.DataFrame([{
            "الرمز": r['symbol'], "الشركة": r['name'], "القطاع": r['sector'],
            "السعر": r['price'], "التغيير %": r['change_pct'],
            "التوصية": r['rec_action'], "الدرجة": r['eod_score'],
            "الدخول": r['entry'], "وقف الخسارة": r['stop_loss'],
            "الهدف 1": r['target1'], "الهدف 2": r['target2'],
            "الإلحاح": r['urgency'], "مدة الاحتفاظ": r['hold_period']
        } for r in recs])

        st.download_button(
            label="📥 تصدير التوصيات CSV",
            data=export_df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"eod_recommendations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )
    else:
        st.info("👈 اضغط 'توليد التوصيات' لتحليل جميع الأسهم وإنشاء التوصيات لنهاية الجلسة")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[0]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #64748b; font-size: 13px; margin: 0; font-weight: 600;">⚡ EGX Pro Terminal v24.0</p>
        <p style="color: #475569; font-size: 12px; margin: 6px 0;">نظام تحليلي احترافي | البورصة المصرية</p>
    </div>
    """, unsafe_allow_html=True)
with footer_cols[1]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #fbbf24; font-size: 14px; margin: 0; font-weight: 700;">
            🏆 الأقوى: {best_stock['symbol']} +{best_stock['change_pct']:.2f}% | 📉 الأضعف: {worst_stock['symbol']} {worst_stock['change_pct']:.2f}%
        </p>
        <p style="color: #475569; font-size: 12px; margin: 6px 0;">آخر تحديث: {datetime.now().strftime("%H:%M:%S")}</p>
    </div>
    """, unsafe_allow_html=True)
with footer_cols[2]:
    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: #475569; font-size: 12px; margin: 0;">© 2026 | جميع البيانات للتوضيح | التوقعات للأغراض التعليمية فقط</p>
        <p style="color: #475569; font-size: 11px; margin: 6px 0;">صناديق استثمار | توزيعات | تحليل فني | إدارة مخاطر | توصيات ذكية</p>
    </div>
    """, unsafe_allow_html=True)
