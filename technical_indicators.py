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
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
st.set_page_config(page_title="⚡ EGX Super Analyst Pro", layout="wide", page_icon="⚡")

# Auto-refresh every 90 seconds
st_autorefresh(interval=90 * 1000, key="auto_refresh")

# Custom CSS for Glassmorphism styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');

    * { font-family: 'Cairo', sans-serif !important; }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .stock-up { color: #10b981; font-weight: bold; }
    .stock-down { color: #ef4444; font-weight: bold; }
    .gold-text { color: #fbbf24; font-weight: bold; }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #10b981;
        font-size: 12px;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .priority-high { border-right: 3px solid #ef4444; }
    .priority-medium { border-right: 3px solid #f59e0b; }
    .priority-low { border-right: 3px solid #10b981; }

    .tag-work { background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-personal { background: rgba(139, 92, 246, 0.2); color: #a78bfa; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-urgent { background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-learning { background: rgba(6, 182, 212, 0.2); color: #22d3ee; padding: 2px 8px; border-radius: 6px; font-size: 12px; }

    .task-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s;
    }

    .task-item:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #818cf8 !important;
    }

    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; }
    div[data-testid="stMetricDelta"] { font-size: 14px !important; }

    .news-item {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: rgba(255, 255, 255, 0.03);
        border-right: 3px solid;
    }

    .news-positive { border-color: #10b981; }
    .news-negative { border-color: #ef4444; }
    .news-neutral { border-color: #6b7280; }

    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .signal-hold {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.05));
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .prediction-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
    }

    .indicator-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .warning-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
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

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"symbol": "COMI", "name": "CIB", "quantity": 500, "buy_price": 47.50, "current_price": 50.25},
        {"symbol": "SWDY", "name": "السويدي", "quantity": 1200, "buy_price": 11.20, "current_price": 12.80},
        {"symbol": "ISPH", "name": "العاصمة", "quantity": 3000, "buy_price": 8.50, "current_price": 8.95},
        {"symbol": "EFIH", "name": "e-Finance", "quantity": 800, "buy_price": 20.10, "current_price": 22.30},
        {"symbol": "ORAS", "name": "أوراسكوم", "quantity": 1500, "buy_price": 9.10, "current_price": 9.75},
    ]

# ==================== DATA ====================
stocks_data = [
    {"symbol": "COMI", "name": "البنك التجاري الدولي - CIB", "sector": "بنوك", "price": 140.01, "change": -2.09, "change_pct": -1.47, "volume": 13263000000, "high": 142.81, "low": 137.21},
    {"symbol": "QNBE", "name": "QNB مصر", "sector": "بنوك", "price": 58.14, "change": -0.95, "change_pct": -1.61, "volume": 5550000000, "high": 59.3, "low": 56.98},
    {"symbol": "ADIB", "name": "أبوظبي الإسلامي - مصر", "sector": "بنوك", "price": 47.49, "change": -1.47, "change_pct": -3.0, "volume": 2413000000, "high": 48.44, "low": 46.54},
    {"symbol": "HDBK", "name": "بنك الإسكان والتعمير", "sector": "بنوك", "price": 147.26, "change": 0.03, "change_pct": 0.02, "volume": 3048000000, "high": 150.21, "low": 144.31},
    {"symbol": "CANA", "name": "بنك قناة السويس", "sector": "بنوك", "price": 33.88, "change": 1.86, "change_pct": 5.81, "volume": 1320000000, "high": 34.56, "low": 33.2},
    {"symbol": "CIEB", "name": "كريدي أجريكول مصر", "sector": "بنوك", "price": 23.73, "change": -0.29, "change_pct": -1.21, "volume": 1267000000, "high": 24.2, "low": 23.26},
    {"symbol": "FAIT", "name": "بنك فيصل الإسلامي", "sector": "بنوك", "price": 34.11, "change": 0.32, "change_pct": 0.95, "volume": 1202000000, "high": 34.79, "low": 33.43},
    {"symbol": "SAUD", "name": "البركة بنك مصر", "sector": "بنوك", "price": 24.7, "change": -0.36, "change_pct": -1.44, "volume": 809000000, "high": 25.19, "low": 24.21},
    {"symbol": "UBEE", "name": "المصرف المتحد", "sector": "بنوك", "price": 13.98, "change": 1.53, "change_pct": 12.29, "volume": 619000000, "high": 14.26, "low": 13.7},
    {"symbol": "EXPA", "name": "بنك التنمية الصادرات", "sector": "بنوك", "price": 18.68, "change": -0.05, "change_pct": -0.27, "volume": 1255000000, "high": 19.05, "low": 18.31},
    {"symbol": "EGBE", "name": "البنك المصري الخليجي", "sector": "بنوك", "price": 0.412, "change": -0.72, "change_pct": -63.6, "volume": 1076000000, "high": 0.42, "low": 0.4},
    {"symbol": "EFIH", "name": "e-Finance للاستثمارات الرقمية", "sector": "تكنولوجيا مالية", "price": 22.32, "change": -1.59, "change_pct": -6.65, "volume": 677000000, "high": 22.77, "low": 21.87},
    {"symbol": "FWRY", "name": "فوري لتكنولوجيا البنوك", "sector": "تكنولوجيا مالية", "price": 20.88, "change": -0.95, "change_pct": -4.35, "volume": 865000000, "high": 21.3, "low": 20.46},
    {"symbol": "SCTS", "name": "قناة السويس لتكنولوجيا المقاصة", "sector": "تكنولوجيا مالية", "price": 652.11, "change": -1.49, "change_pct": -0.23, "volume": 305000000, "high": 665.15, "low": 639.07},
    {"symbol": "VALU", "name": "U للتمويل الاستهلاكي", "sector": "تكنولوجيا مالية", "price": 12.6, "change": -2.25, "change_pct": -15.15, "volume": 115000000, "high": 12.85, "low": 12.35},
    {"symbol": "TMGH", "name": "طلعت مصطفى القابضة", "sector": "عقارات", "price": 98.25, "change": -1.75, "change_pct": -1.75, "volume": 6250000000, "high": 100.22, "low": 96.28},
    {"symbol": "EMFD", "name": "إعمار مصر للتنمية", "sector": "عقارات", "price": 11.1, "change": 0.64, "change_pct": 6.12, "volume": 1981000000, "high": 11.32, "low": 10.88},
    {"symbol": "PHDC", "name": "بالم هيلز للتطوير", "sector": "عقارات", "price": 14.0, "change": -2.44, "change_pct": -14.84, "volume": 3617000000, "high": 14.28, "low": 13.72},
    {"symbol": "ORHD", "name": "أوراسكوم للتنمية مصر", "sector": "عقارات", "price": 33.35, "change": -0.83, "change_pct": -2.43, "volume": 2495000000, "high": 34.02, "low": 32.68},
    {"symbol": "OCDI", "name": "سوديك", "sector": "عقارات", "price": 22.98, "change": 0.0, "change_pct": 0.0, "volume": 2126000000, "high": 23.44, "low": 22.52},
    {"symbol": "HELI", "name": "حلوان للإسكان", "sector": "عقارات", "price": 7.06, "change": -0.28, "change_pct": -3.81, "volume": 314000000, "high": 7.2, "low": 6.92},
    {"symbol": "MASR", "name": "مدينة نصر للإسكان", "sector": "عقارات", "price": 7.4, "change": 1.51, "change_pct": 25.64, "volume": 1171000000, "high": 7.55, "low": 7.25},
    {"symbol": "GPPL", "name": "الأهرام للاستثمارات", "sector": "عقارات", "price": 1.4, "change": 0.0, "change_pct": 0.0, "volume": 479000000, "high": 1.43, "low": 1.37},
    {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "price": 89.51, "change": -0.77, "change_pct": -0.85, "volume": 28105000000, "high": 91.3, "low": 87.72},
    {"symbol": "EGAL", "name": "مصر للألومنيوم", "sector": "صناعة", "price": 317.0, "change": 4.6, "change_pct": 1.47, "volume": 4588000000, "high": 323.34, "low": 310.66},
    {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "price": 87.19, "change": 1.38, "change_pct": 1.61, "volume": 2580000000, "high": 88.93, "low": 85.45},
    {"symbol": "MFPC", "name": "موبكو للأسمدة", "sector": "صناعة", "price": 45.15, "change": 3.15, "change_pct": 7.5, "volume": 2684000000, "high": 46.05, "low": 44.25},
    {"symbol": "ARCC", "name": "الأسمنت العربية", "sector": "صناعة", "price": 58.0, "change": 2.02, "change_pct": 3.61, "volume": 1245000000, "high": 59.16, "low": 56.84},
    {"symbol": "MCQE", "name": "مصر أسمنت قنا", "sector": "صناعة", "price": 196.0, "change": 1.6, "change_pct": 0.82, "volume": 955000000, "high": 199.92, "low": 192.08},
    {"symbol": "MBSC", "name": "مصر بني سويف للأسمنت", "sector": "صناعة", "price": 266.0, "change": 1.56, "change_pct": 0.59, "volume": 570000000, "high": 271.32, "low": 260.68},
    {"symbol": "SCEM", "name": "أسمنت سيناء", "sector": "صناعة", "price": 63.3, "change": 0.64, "change_pct": 1.02, "volume": 909000000, "high": 64.57, "low": 62.03},
    {"symbol": "SVCE", "name": "جنوب الوادي للأسمنت", "sector": "صناعة", "price": 8.44, "change": -2.32, "change_pct": -21.56, "volume": 276000000, "high": 8.61, "low": 8.27},
    {"symbol": "EGCH", "name": "الصناعات الكيماوية المصرية", "sector": "صناعة", "price": 13.55, "change": 5.86, "change_pct": 76.2, "volume": 831000000, "high": 13.82, "low": 13.28},
    {"symbol": "FERC", "name": "فيركيم مصر للأسمدة", "sector": "صناعة", "price": 80.77, "change": 0.47, "change_pct": 0.59, "volume": 1003000000, "high": 82.39, "low": 79.15},
    {"symbol": "MICH", "name": "الصناعات الكيماوية Misr", "sector": "صناعة", "price": 35.34, "change": 0.51, "change_pct": 1.46, "volume": 108000000, "high": 36.05, "low": 34.63},
    {"symbol": "ATQA", "name": "حديد عتاقة", "sector": "صناعة", "price": 9.93, "change": 1.22, "change_pct": 14.01, "volume": 633000000, "high": 10.13, "low": 9.73},
    {"symbol": "ISMQ", "name": "الحديد والصلب للمناجم", "sector": "صناعة", "price": 7.78, "change": 2.77, "change_pct": 55.29, "volume": 133000000, "high": 7.94, "low": 7.62},
    {"symbol": "IRON", "name": "الحديد والصلب المصرية", "sector": "صناعة", "price": 33.5, "change": 2.17, "change_pct": 6.93, "volume": 224000000, "high": 34.17, "low": 32.83},
    {"symbol": "ASCM", "name": "أسكوم", "sector": "صناعة", "price": 49.75, "change": 7.82, "change_pct": 18.65, "volume": 397000000, "high": 50.74, "low": 48.76},
    {"symbol": "ALCN", "name": "الإسكندرية للحاويات", "sector": "صناعة", "price": 30.09, "change": 1.15, "change_pct": 3.97, "volume": 820000000, "high": 30.69, "low": 29.49},
    {"symbol": "ALUM", "name": "الألومنيوم العربي", "sector": "صناعة", "price": 22.74, "change": 0.4, "change_pct": 1.79, "volume": 579000000, "high": 23.19, "low": 22.29},
    {"symbol": "ELEC", "name": "الكابلات الكهربائية", "sector": "صناعة", "price": 2.19, "change": -0.91, "change_pct": -29.35, "volume": 1082000000, "high": 2.23, "low": 2.15},
    {"symbol": "ENGC", "name": "ICON للهندسة", "sector": "صناعة", "price": 34.9, "change": -1.66, "change_pct": -4.54, "volume": 735000000, "high": 35.6, "low": 34.2},
    {"symbol": "ETEL", "name": "المصرية للاتصالات", "sector": "اتصالات", "price": 98.49, "change": -0.4, "change_pct": -0.4, "volume": 10667000000, "high": 100.46, "low": 96.52},
    {"symbol": "EGSA", "name": "النايل سات", "sector": "اتصالات", "price": 9.09, "change": 0.0, "change_pct": 0.0, "volume": 470000000, "high": 9.27, "low": 8.91},
    {"symbol": "OIH", "name": "أوراسكوم للاستثمار", "sector": "اتصالات", "price": 1.54, "change": 1.32, "change_pct": 600.0, "volume": 708000000, "high": 1.57, "low": 1.51},
    {"symbol": "EAST", "name": "الشرقية للدخان", "sector": "سلع استهلاكية", "price": 40.31, "change": 0.83, "change_pct": 2.1, "volume": 3989000000, "high": 41.12, "low": 39.5},
    {"symbol": "EFID", "name": "إيديتا للصناعات الغذائية", "sector": "سلع استهلاكية", "price": 28.6, "change": 1.65, "change_pct": 6.12, "volume": 2092000000, "high": 29.17, "low": 28.03},
    {"symbol": "JUFO", "name": "جهينة للصناعات الغذائية", "sector": "سلع استهلاكية", "price": 28.9, "change": 0.0, "change_pct": 0.0, "volume": 2998000000, "high": 29.48, "low": 28.32},
    {"symbol": "DOMT", "name": "دومتي للصناعات الغذائية", "sector": "سلع استهلاكية", "price": 26.0, "change": 2.93, "change_pct": 12.7, "volume": 939000000, "high": 26.52, "low": 25.48},
    {"symbol": "SUGR", "name": "دلتا للسكر", "sector": "سلع استهلاكية", "price": 48.81, "change": -0.35, "change_pct": -0.71, "volume": 883000000, "high": 49.79, "low": 47.83},
    {"symbol": "POUL", "name": "القاهرة للدواجن", "sector": "سلع استهلاكية", "price": 34.8, "change": -0.6, "change_pct": -1.69, "volume": 1582000000, "high": 35.5, "low": 34.1},
    {"symbol": "OLFI", "name": "أرض Obour للصناعات الغذائية", "sector": "سلع استهلاكية", "price": 22.72, "change": 1.43, "change_pct": 6.72, "volume": 1112000000, "high": 23.17, "low": 22.27},
    {"symbol": "GBCO", "name": "GB Corp", "sector": "سلع استهلاكية", "price": 29.3, "change": 2.09, "change_pct": 7.68, "volume": 8023000000, "high": 29.89, "low": 28.71},
    {"symbol": "ORWE", "name": "النساجون الشرقيون", "sector": "سلع استهلاكية", "price": 23.56, "change": -0.38, "change_pct": -1.59, "volume": 2662000000, "high": 24.03, "low": 23.09},
    {"symbol": "DSCW", "name": "دايس للملابس", "sector": "سلع استهلاكية", "price": 1.94, "change": -1.52, "change_pct": -43.93, "volume": 685000000, "high": 1.98, "low": 1.9},
    {"symbol": "AJWA", "name": "أجوا للصناعات الغذائية", "sector": "سلع استهلاكية", "price": 132.26, "change": -1.0, "change_pct": -0.75, "volume": 180000000, "high": 134.91, "low": 129.61},
    {"symbol": "COSG", "name": "القاهرة للزيوت والصابون", "sector": "سلع استهلاكية", "price": 1.45, "change": -0.69, "change_pct": -32.24, "volume": 769000000, "high": 1.48, "low": 1.42},
    {"symbol": "MOSC", "name": "مصر للزيوت والصابون", "sector": "سلع استهلاكية", "price": 312.34, "change": -0.43, "change_pct": -0.14, "volume": 327000000, "high": 318.59, "low": 306.09},
    {"symbol": "IFAP", "name": "المنتجات الزراعية", "sector": "سلع استهلاكية", "price": 21.42, "change": -1.34, "change_pct": -5.89, "volume": 244000000, "high": 21.85, "low": 20.99},
    {"symbol": "KABO", "name": "النصر للملابس والمنسوجات", "sector": "سلع استهلاكية", "price": 6.13, "change": -0.81, "change_pct": -11.67, "volume": 112000000, "high": 6.25, "low": 6.01},
    {"symbol": "GTWL", "name": "الذهبية للمنسوجات", "sector": "سلع استهلاكية", "price": 55.94, "change": 0.36, "change_pct": 0.65, "volume": 877000000, "high": 57.06, "low": 54.82},
    {"symbol": "ACGC", "name": "الأقطان", "sector": "سلع استهلاكية", "price": 8.71, "change": -1.58, "change_pct": -15.35, "volume": 263000000, "high": 8.88, "low": 8.54},
    {"symbol": "SPIN", "name": "الإسكندرية للغزل والنسيج", "sector": "سلع استهلاكية", "price": 14.44, "change": 0.21, "change_pct": 1.48, "volume": 714000000, "high": 14.73, "low": 14.15},
    {"symbol": "MFSC", "name": "مصر للأسواق الحرة", "sector": "سلع استهلاكية", "price": 48.14, "change": 19.99, "change_pct": 71.01, "volume": 135000000, "high": 49.1, "low": 47.18},
    {"symbol": "ZEOT", "name": "المستخلصات الزيتية", "sector": "سلع استهلاكية", "price": 9.5, "change": 1.93, "change_pct": 25.5, "volume": 416000000, "high": 9.69, "low": 9.31},
    {"symbol": "CLHO", "name": "مستشفيات كليوباترا", "sector": "صحة", "price": 14.94, "change": 0.74, "change_pct": 5.21, "volume": 723000000, "high": 15.24, "low": 14.64},
    {"symbol": "PHAR", "name": "أمون للصناعات الدوائية", "sector": "صحة", "price": 89.49, "change": -0.12, "change_pct": -0.13, "volume": 944000000, "high": 91.28, "low": 87.7},
    {"symbol": "ISPH", "name": "ابن سينا فارما", "sector": "صحة", "price": 11.96, "change": 0.25, "change_pct": 2.13, "volume": 7660000000, "high": 12.2, "low": 11.72},
    {"symbol": "MIPH", "name": "مينافارم", "sector": "صحة", "price": 687.72, "change": 0.37, "change_pct": 0.05, "volume": 692000000, "high": 701.47, "low": 673.97},
    {"symbol": "NIPH", "name": "النيل للأدوية", "sector": "صحة", "price": 173.2, "change": -1.59, "change_pct": -0.91, "volume": 197000000, "high": 176.66, "low": 169.74},
    {"symbol": "ADCI", "name": "العربية للأدوية", "sector": "صحة", "price": 216.63, "change": 1.77, "change_pct": 0.82, "volume": 123000000, "high": 220.96, "low": 212.3},
    {"symbol": "AXPH", "name": "الإسكندرية للأدوية", "sector": "صحة", "price": 1166.22, "change": 7.1, "change_pct": 0.61, "volume": 302000000, "high": 1189.54, "low": 1142.9},
    {"symbol": "CPCI", "name": "القاهرة للأدوية", "sector": "صحة", "price": 357.04, "change": 1.47, "change_pct": 0.41, "volume": 228000000, "high": 364.18, "low": 349.9},
    {"symbol": "RMDA", "name": "راميدا", "sector": "صحة", "price": 5.13, "change": 1.58, "change_pct": 44.51, "volume": 410000000, "high": 5.23, "low": 5.03},
    {"symbol": "OCPH", "name": "أكتوبر فارما", "sector": "صحة", "price": 394.0, "change": 1.77, "change_pct": 0.45, "volume": 146000000, "high": 401.88, "low": 386.12},
    {"symbol": "HRHO", "name": "EFG هيرمس", "sector": "استثمار", "price": 29.5, "change": -1.47, "change_pct": -4.75, "volume": 2657000000, "high": 30.09, "low": 28.91},
    {"symbol": "BTFH", "name": "بلتون القابضة", "sector": "استثمار", "price": 3.19, "change": 2.9, "change_pct": 1000.0, "volume": 696000000, "high": 3.25, "low": 3.13},
    {"symbol": "CCAP", "name": "قلعة للاستثمارات", "sector": "استثمار", "price": 4.67, "change": -1.06, "change_pct": -18.5, "volume": 13617000000, "high": 4.76, "low": 4.58},
    {"symbol": "CICH", "name": "سي آي كابيتال", "sector": "استثمار", "price": 12.9, "change": 5.31, "change_pct": 69.96, "volume": 451000000, "high": 13.16, "low": 12.64},
    {"symbol": "RAYA", "name": "راية القابضة", "sector": "استثمار", "price": 7.1, "change": -2.47, "change_pct": -25.81, "volume": 6383000000, "high": 7.24, "low": 6.96},
    {"symbol": "CNFN", "name": "كونتكت للتمويل", "sector": "استثمار", "price": 4.74, "change": 3.04, "change_pct": 178.82, "volume": 541000000, "high": 4.83, "low": 4.65},
    {"symbol": "BONY", "name": "بنيان للتنمية", "sector": "استثمار", "price": 4.37, "change": -0.68, "change_pct": -13.47, "volume": 758000000, "high": 4.46, "low": 4.28},
    {"symbol": "BINV", "name": "B للاستثمارات", "sector": "استثمار", "price": 41.19, "change": 0.39, "change_pct": 0.96, "volume": 948000000, "high": 42.01, "low": 40.37},
    {"symbol": "AMIA", "name": "الملتقى العربي للاستثمار", "sector": "استثمار", "price": 9.25, "change": -0.75, "change_pct": -7.5, "volume": 244000000, "high": 9.44, "low": 9.06},
    {"symbol": "ACAP", "name": "A كابيتال القابضة", "sector": "استثمار", "price": 7.61, "change": 0.13, "change_pct": 1.74, "volume": 315000000, "high": 7.76, "low": 7.46},
    {"symbol": "AMER", "name": "أمير القابضة", "sector": "استثمار", "price": 2.41, "change": 2.99, "change_pct": -515.52, "volume": 162000000, "high": 2.46, "low": 2.36},
    {"symbol": "ARAB", "name": "العربية للتطوير", "sector": "استثمار", "price": 0.204, "change": 0.49, "change_pct": -171.33, "volume": 142000000, "high": 0.21, "low": 0.2},
    {"symbol": "AIHC", "name": "عربية للاستثمارات", "sector": "استثمار", "price": 0.353, "change": -1.4, "change_pct": -79.86, "volume": 788000000, "high": 0.36, "low": 0.35},
    {"symbol": "ASPI", "name": "أسباير كابيتال", "sector": "استثمار", "price": 0.309, "change": 1.98, "change_pct": -118.49, "volume": 388000000, "high": 0.32, "low": 0.3},
    {"symbol": "PRMH", "name": "برايم القابضة", "sector": "استثمار", "price": 2.18, "change": 0.0, "change_pct": 0.0, "volume": 253000000, "high": 2.22, "low": 2.14},
    {"symbol": "GRCA", "name": "جراند كابيتال", "sector": "استثمار", "price": 54.09, "change": -0.63, "change_pct": -1.15, "volume": 62500000, "high": 55.17, "low": 53.01},
    {"symbol": "ATLC", "name": "التوفيق للتأجير", "sector": "استثمار", "price": 5.33, "change": 0.76, "change_pct": 16.63, "volume": 207000000, "high": 5.44, "low": 5.22},
    {"symbol": "DEIN", "name": "دلتا للتأمين", "sector": "استثمار", "price": 11.38, "change": 0.0, "change_pct": 0.0, "volume": 299000000, "high": 11.61, "low": 11.15},
    {"symbol": "MOIN", "name": "مهندس للتأمين", "sector": "استثمار", "price": 24.57, "change": 0.49, "change_pct": 2.03, "volume": 141000000, "high": 25.06, "low": 24.08},
    {"symbol": "ODIN", "name": "أودين للاستثمارات", "sector": "استثمار", "price": 2.01, "change": 2.55, "change_pct": -472.22, "volume": 214000000, "high": 2.05, "low": 1.97},
    {"symbol": "CRST", "name": "كريست مارك", "sector": "استثمار", "price": 0.832, "change": 2.09, "change_pct": -166.14, "volume": 281000000, "high": 0.85, "low": 0.82},
    {"symbol": "AALR", "name": "العربية لاستصلاح الأراضي", "sector": "استثمار", "price": 217.93, "change": -0.83, "change_pct": -0.38, "volume": 155000000, "high": 222.29, "low": 213.57},
    {"symbol": "TANM", "name": "تنمية للاستثمار العقاري", "sector": "استثمار", "price": 5.48, "change": 6.82, "change_pct": -508.96, "volume": 0, "high": 5.59, "low": 5.37},
    {"symbol": "PRDC", "name": "بايونيرز للتطوير", "sector": "استثمار", "price": 5.9, "change": 2.25, "change_pct": 61.64, "volume": 641000000, "high": 6.02, "low": 5.78},
    {"symbol": "ELSH", "name": "الشمس للإسكان", "sector": "استثمار", "price": 8.16, "change": 3.03, "change_pct": 59.06, "volume": 172000000, "high": 8.32, "low": 8.0},
    {"symbol": "EHDR", "name": "المصريين للإسكان", "sector": "استثمار", "price": 2.31, "change": 0.0, "change_pct": 0.0, "volume": 242000000, "high": 2.36, "low": 2.26},
    {"symbol": "OBRI", "name": "العبور للاستثمار العقاري", "sector": "استثمار", "price": 39.5, "change": -0.13, "change_pct": -0.33, "volume": 129000000, "high": 40.29, "low": 38.71},
    {"symbol": "GIHD", "name": "الغربية الإسلامية للإسكان", "sector": "استثمار", "price": 42.54, "change": 1.46, "change_pct": 3.55, "volume": 622000000, "high": 43.39, "low": 41.69},
    {"symbol": "ELKA", "name": "القاهرة للإسكان", "sector": "استثمار", "price": 1.2, "change": 3.45, "change_pct": -153.33, "volume": 554000000, "high": 1.22, "low": 1.18},
    {"symbol": "AMOC", "name": "Alexandria Mineral Oils", "sector": "طاقة", "price": 8.59, "change": 0.35, "change_pct": 4.25, "volume": 4011000000, "high": 8.76, "low": 8.42},
    {"symbol": "EGAS", "name": "مصر للغاز", "sector": "طاقة", "price": 49.12, "change": -0.41, "change_pct": -0.83, "volume": 900000000, "high": 50.1, "low": 48.14},
    {"symbol": "MOIL", "name": "ماري ديف للخدمات البترولية", "sector": "طاقة", "price": 0.458, "change": 2.46, "change_pct": -122.88, "volume": 1154000000, "high": 0.47, "low": 0.45},
    {"symbol": "NDRL", "name": "الحفر الوطنية", "sector": "طاقة", "price": 4.69, "change": 0.0, "change_pct": 0.0, "volume": 119000000, "high": 4.78, "low": 4.6},
    {"symbol": "MTIE", "name": "MM Group", "sector": "تعليم", "price": 9.42, "change": 1.29, "change_pct": 15.87, "volume": 2116000000, "high": 9.61, "low": 9.23},
    {"symbol": "MPRC", "name": "مدينة الإنتاج الإعلامي", "sector": "إعلام", "price": 31.75, "change": 0.16, "change_pct": 0.51, "volume": 127000000, "high": 32.38, "low": 31.11},
    {"symbol": "ETRS", "name": "النقل والخدمات التجارية", "sector": "نقل", "price": 7.78, "change": 0.26, "change_pct": 3.46, "volume": 1230000000, "high": 7.94, "low": 7.62},
    {"symbol": "SCFM", "name": "مطاحن جنوب القاهرة", "sector": "غذاء", "price": 282.14, "change": -0.96, "change_pct": -0.34, "volume": 304000000, "high": 287.78, "low": 276.5},
    {"symbol": "CEFM", "name": "مطاحن مصر الوسطى", "sector": "غذاء", "price": 109.44, "change": -1.56, "change_pct": -1.41, "volume": 912000000, "high": 111.63, "low": 107.25}
]

tickers_egypt = ['COMI', 'QNBE', 'ADIB', 'HDBK', 'CANA', 'CIEB', 'FAIT', 'SAUD', 'UBEE', 'EXPA', 'EGBE', 'EFIH', 'FWRY', 'SCTS', 'VALU', 'TMGH', 'EMFD', 'PHDC', 'ORHD', 'OCDI', 'HELI', 'MASR', 'GPPL', 'SWDY', 'EGAL', 'ABUK', 'MFPC', 'ARCC', 'MCQE', 'MBSC', 'SCEM', 'SVCE', 'EGCH', 'FERC', 'MICH', 'ATQA', 'ISMQ', 'IRON', 'ASCM', 'ALCN', 'ALUM', 'ELEC', 'ENGC', 'ETEL', 'EGSA', 'OIH', 'EAST', 'EFID', 'JUFO', 'DOMT', 'SUGR', 'POUL', 'OLFI', 'GBCO', 'ORWE', 'DSCW', 'AJWA', 'COSG', 'MOSC', 'IFAP', 'KABO', 'GTWL', 'ACGC', 'SPIN', 'MFSC', 'ZEOT', 'CLHO', 'PHAR', 'ISPH', 'MIPH', 'NIPH', 'ADCI', 'AXPH', 'CPCI', 'RMDA', 'OCPH', 'HRHO', 'BTFH', 'CCAP', 'CICH', 'RAYA', 'CNFN', 'BONY', 'BINV', 'AMIA', 'ACAP', 'AMER', 'ARAB', 'AIHC', 'ASPI', 'PRMH', 'GRCA', 'ATLC', 'DEIN', 'MOIN', 'ODIN', 'CRST', 'AALR', 'TANM', 'PRDC', 'ELSH', 'EHDR', 'OBRI', 'GIHD', 'ELKA', 'AMOC', 'EGAS', 'MOIL', 'NDRL', 'MTIE', 'MPRC', 'ETRS', 'SCFM', 'CEFM']

news_data = [
    {"time": "14:30", "title": "EGX30 يتجاوز 24800 نقطة للمرة الأولى منذ 2022", "type": "positive"},
    {"time": "14:15", "title": "CIB يعلن عن توزيع أرباح نقدية 2.5 جنيه للسهم", "type": "positive"},
    {"time": "13:45", "title": "تراجع طفيف في مؤشر EGX100 مع جني الأرباح", "type": "negative"},
    {"time": "13:20", "title": "المركزي: استقرار سعر الصرف عند 30.85 للدولار", "type": "neutral"},
    {"time": "12:50", "title": "e-Finance توقع اتفاقية رقمية مع الحكومة", "type": "positive"},
    {"time": "12:15", "title": "ارتفاع حجم التداولات إلى 1.8 مليار جنيه", "type": "positive"},
    {"time": "11:30", "title": "فوري تعلن عن نمو أرباح الربع الأول بنسبة 25%", "type": "positive"},
    {"time": "10:45", "title": "ضغوط بيعية على قطاع الأسمدة", "type": "negative"},
]

# ==================== ADVANCED TECHNICAL ANALYSIS ENGINE ====================
def calculate_technical_indicators(df):
    """Calculate comprehensive technical indicators"""
    df = df.copy()

    # RSI (14)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
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

    # Stochastic Oscillator
    low_14 = df['Low'].rolling(14).min()
    high_14 = df['High'].rolling(14).max()
    df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()
    df['EMA_20'] = df['Close'].ewm(span=20).mean()

    # Average True Range (ATR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()

    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

    # Price momentum
    df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
    df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100

    return df

def generate_trading_signals(df):
    """Generate buy/sell/hold signals based on multiple indicators"""
    signals = []

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    # RSI signals
    if latest['RSI'] < 30:
        signals.append(("RSI", "شراء قوي", 2, "السهم في منطقة ذروة البيع"))
    elif latest['RSI'] > 70:
        signals.append(("RSI", "بيع قوي", -2, "السهم في منطقة ذروة الشراء"))
    elif latest['RSI'] < 45:
        signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء محتملة"))
    elif latest['RSI'] > 55:
        signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع محتملة"))
    else:
        signals.append(("RSI", "محايد", 0, "لا توجد إشارة واضحة"))

    # MACD signals
    if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
        signals.append(("MACD", "شراء", 2, "تقاطع صاعد للماكد"))
    elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
        signals.append(("MACD", "بيع", -2, "تقاطع هابط للماكد"))
    elif latest['MACD'] > latest['MACD_Signal']:
        signals.append(("MACD", "شراء ضعيف", 1, "المacd فوق خط الإشارة"))
    else:
        signals.append(("MACD", "بيع ضعيف", -1, "المacd تحت خط الإشارة"))

    # Bollinger Bands signals
    if latest['Close'] < latest['BB_Lower']:
        signals.append(("Bollinger", "شراء قوي", 2, "السعر تحت النطاق السفلي"))
    elif latest['Close'] > latest['BB_Upper']:
        signals.append(("Bollinger", "بيع قوي", -2, "السعر فوق النطاق العلوي"))
    elif latest['Close'] < latest['BB_Middle']:
        signals.append(("Bollinger", "شراء ضعيف", 0.5, "السعر في النصف السفلي"))
    else:
        signals.append(("Bollinger", "بيع ضعيف", -0.5, "السعر في النصف العلوي"))

    # Stochastic signals
    if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
        signals.append(("Stochastic", "شراء", 1.5, "مؤشر ستوكاستيك في منطقة ذروة البيع"))
    elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
        signals.append(("Stochastic", "بيع", -1.5, "مؤشر ستوكاستيك في منطقة ذروة الشراء"))
    else:
        signals.append(("Stochastic", "محايد", 0, "لا توجد إشارة"))

    # Moving Average signals
    if latest['Close'] > latest['SMA_20'] and latest['Close'] > latest['SMA_50']:
        signals.append(("MA", "شراء", 1, "السعر فوق المتوسطات المتحركة"))
    elif latest['Close'] < latest['SMA_20'] and latest['Close'] < latest['SMA_50']:
        signals.append(("MA", "بيع", -1, "السعر تحت المتوسطات المتحركة"))
    else:
        signals.append(("MA", "محايد", 0, "إشارات متضاربة من المتوسطات"))

    # Volume confirmation
    if latest['Volume_Ratio'] > 1.5:
        signals.append(("Volume", "تأكيد", 0.5, "حجم تداول أعلى من المتوسط"))
    elif latest['Volume_Ratio'] < 0.5:
        signals.append(("Volume", "ضعف", -0.5, "حجم تداول منخفض"))
    else:
        signals.append(("Volume", "محايد", 0, "حجم تداول طبيعي"))

    return signals

def calculate_overall_signal(signals):
    """Calculate overall trading signal from individual indicators"""
    total_score = sum([s[2] for s in signals])

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

def predict_future_prices(df, days=5):
    """Predict future prices using multiple methods"""
    predictions = {}

    try:
        # Method 1: Linear Regression with trend
        prices = df['Close'].dropna().values
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        # Polynomial features for better fit
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        # Predict next days
        future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        linear_pred = model.predict(future_X_poly)

        # Method 2: Moving Average extrapolation
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]

        # Trend direction
        if ma20 > ma50:
            trend_factor = 1.002  # Slight upward adjustment
        elif ma20 < ma50:
            trend_factor = 0.998  # Slight downward adjustment
        else:
            trend_factor = 1.0

        ma_pred = [prices[-1] * (trend_factor ** i) for i in range(1, days + 1)]

        # Method 3: Average of methods with confidence intervals
        combined_pred = []
        for i in range(days):
            avg = (linear_pred[i] + ma_pred[i]) / 2
            volatility = df['Close'].pct_change().std() * prices[-1]
            combined_pred.append({
                'day': i + 1,
                'predicted': round(avg, 2),
                'lower_bound': round(avg - volatility * 1.5, 2),
                'upper_bound': round(avg + volatility * 1.5, 2),
                'confidence': max(0, min(100, 100 - (i * 15)))  # Confidence decreases with time
            })

        predictions['linear'] = linear_pred.tolist()
        predictions['moving_average'] = ma_pred
        predictions['combined'] = combined_pred

    except Exception as e:
        predictions['error'] = str(e)

    return predictions

def calculate_support_resistance(df, window=20):
    """Calculate dynamic support and resistance levels"""
    recent = df.tail(window)

    # Support levels (recent lows)
    lows = recent['Low'].nsmallest(3).values
    supports = [round(l, 2) for l in lows]

    # Resistance levels (recent highs)
    highs = recent['High'].nlargest(3).values
    resistances = [round(h, 2) for h in highs]

    # Fibonacci levels from recent swing
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

# ==================== BACKTESTING ENGINE ====================
def run_advanced_backtest(ticker, strategy="RSI_MACD", period="1y", market_type="EGX"):
    try:
        suffix = ".CA" if market_type == "EGX" else ""
        df = yf.Ticker(f"{ticker}{suffix}").history(period=period)
        if df.empty:
            return None

        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        initial_capital = 100000
        df['Returns'] = df['Close'].pct_change()

        if strategy == "RSI_MACD":
            delta = df['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = 100 - (100 / (1 + gain / loss))
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
        st.error(f"Error in backtesting: {str(e)}")
        return None


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 16px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 28px;">⚡</div>
        <h2 style="margin-top: 12px; font-size: 20px;">EGX Super Analyst</h2>
        <p style="color: #94a3b8; font-size: 12px;">Pro v15.0 - AI Powered</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("🌍 اختيار السوق")
    market = st.radio("", ["🇪🇬 السوق المصري", "🌍 الأسواق العالمية"], label_visibility="collapsed")
    is_egypt = "مصري" in market

    tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC"] if is_egypt else               ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "INTC", "NFLX"]

    st.divider()

    # Portfolio Summary in Sidebar
    st.header("💼 ملخص المحفظة")
    port_value = sum(p["quantity"] * p["current_price"] for p in st.session_state.portfolio)
    port_cost = sum(p["quantity"] * p["buy_price"] for p in st.session_state.portfolio)
    port_pl = port_value - port_cost
    port_pl_pct = (port_pl / port_cost) * 100 if port_cost > 0 else 0

    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 12px; margin-bottom: 4px;">القيمة الحالية</p>
        <p class="gold-text" style="font-size: 20px;">ج.م {port_value:,.0f}</p>
        <p style="color: {'#10b981' if port_pl >= 0 else '#ef4444'}; font-size: 14px; margin-top: 4px;">
            {'+' if port_pl >= 0 else ''}{port_pl:,.0f} ({port_pl_pct:+.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

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
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
    <div>
        <h1 style="margin: 0; font-size: 32px; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ EGX Super Analyst Pro</h1>
        <p style="color: #94a3b8; margin-top: 4px; font-size: 14px;">
            <span class="live-indicator"><span class="live-dot"></span> السوق مفتوح | آخر تحديث: {}</span>
        </p>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div class="glass-card" style="padding: 8px 16px;">
            <span style="color: #94a3b8; font-size: 12px;">EGX30</span>
            <span class="stock-up" style="margin-right: 8px; font-size: 18px;">24,850</span>
            <span class="stock-up" style="font-size: 12px;">+1.24%</span>
        </div>
    </div>
</div>
""".format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)


# ==================== DIVIDENDS & COUPONS DATABASE ====================
dividends_data = [
    # CIB - Commercial International Bank
    {"symbol": "COMI", "company": "البنك التجاري الدولي - CIB", 
     "dividends": [
         {"date": "2026-04-15", "type": "نقدي", "amount": 2.50, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-10-20", "type": "نقدي", "amount": 2.30, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-04-18", "type": "نقدي", "amount": 2.10, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2024-10-22", "type": "نقدي", "amount": 1.90, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-15", "yield": 3.57},

    # QNB Egypt
    {"symbol": "QNBE", "company": "QNB مصر",
     "dividends": [
         {"date": "2026-03-25", "type": "نقدي", "amount": 3.20, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-09-28", "type": "نقدي", "amount": 3.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-09-25", "yield": 5.50},

    # Abu Dhabi Islamic Bank
    {"symbol": "ADIB", "company": "أبوظبي الإسلامي - مصر",
     "dividends": [
         {"date": "2026-03-10", "type": "نقدي", "amount": 1.80, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-09-15", "type": "نقدي", "amount": 1.60, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-09-10", "yield": 3.79},

    # Housing & Development Bank
    {"symbol": "HDBK", "company": "بنك الإسكان والتعمير",
     "dividends": [
         {"date": "2026-04-05", "type": "نقدي", "amount": 5.50, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-10-10", "type": "نقدي", "amount": 5.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-05", "yield": 3.73},

    # Suez Canal Bank
    {"symbol": "CANA", "company": "بنك قناة السويس",
     "dividends": [
         {"date": "2026-03-20", "type": "نقدي", "amount": 1.20, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-09-25", "type": "نقدي", "amount": 1.10, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-09-20", "yield": 3.54},

    # Credit Agricole Egypt
    {"symbol": "CIEB", "company": "كريدي أجريكول مصر",
     "dividends": [
         {"date": "2026-04-12", "type": "نقدي", "amount": 1.50, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-12", "yield": 6.32},

    # Faisal Islamic Bank
    {"symbol": "FAIT", "company": "بنك فيصل الإسلامي",
     "dividends": [
         {"date": "2026-03-18", "type": "نقدي", "amount": 1.30, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-09-18", "yield": 3.81},

    # Al Baraka Bank
    {"symbol": "SAUD", "company": "البركة بنك مصر",
     "dividends": [
         {"date": "2026-03-22", "type": "نقدي", "amount": 1.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-09-22", "yield": 4.05},

    # e-Finance
    {"symbol": "EFIH", "company": "e-Finance للاستثمارات الرقمية",
     "dividends": [
         {"date": "2026-05-01", "type": "نقدي", "amount": 0.85, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-01", "yield": 3.81},

    # Fawry
    {"symbol": "FWRY", "company": "فوري لتكنولوجيا البنوك",
     "dividends": [
         {"date": "2026-04-20", "type": "نقدي", "amount": 0.65, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-20", "yield": 3.11},

    # Talaat Moustafa
    {"symbol": "TMGH", "company": "طلعت مصطفى القابضة",
     "dividends": [
         {"date": "2026-04-08", "type": "نقدي", "amount": 2.80, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-10-12", "type": "نقدي", "amount": 2.50, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-04-10", "type": "أسهم مجانية", "amount": 1, "currency": "سهم/10", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-08", "yield": 2.85},

    # Palm Hills
    {"symbol": "PHDC", "company": "بالم هيلز للتطوير",
     "dividends": [
         {"date": "2026-05-10", "type": "نقدي", "amount": 0.45, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-10", "yield": 3.21},

    # Emaar Misr
    {"symbol": "EMFD", "company": "إعمار مصر للتنمية",
     "dividends": [
         {"date": "2026-04-25", "type": "نقدي", "amount": 0.35, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-25", "yield": 3.15},

    # Orascom Development
    {"symbol": "ORHD", "company": "أوراسكوم للتنمية مصر",
     "dividends": [
         {"date": "2026-05-15", "type": "نقدي", "amount": 1.20, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-15", "yield": 3.60},

    # SODIC
    {"symbol": "OCDI", "company": "سوديك",
     "dividends": [
         {"date": "2026-04-18", "type": "نقدي", "amount": 0.90, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-18", "yield": 3.92},

    # El Sewedy Electric
    {"symbol": "SWDY", "company": "السويدي إلكتريك",
     "dividends": [
         {"date": "2026-05-05", "type": "نقدي", "amount": 3.50, "currency": "ج.م", "status": "معلن"},
         {"date": "2025-11-08", "type": "نقدي", "amount": 3.20, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-05-10", "type": "أسهم مجانية", "amount": 1, "currency": "سهم/5", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-11-05", "yield": 3.91},

    # Egypt Aluminum
    {"symbol": "EGAL", "company": "مصر للألومنيوم",
     "dividends": [
         {"date": "2026-04-22", "type": "نقدي", "amount": 12.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-22", "yield": 3.79},

    # Abu Qir Fertilizers
    {"symbol": "ABUK", "company": "أبو قير للأسمدة",
     "dividends": [
         {"date": "2026-05-12", "type": "نقدي", "amount": 4.50, "currency": "ج.م", "status": "معلن"},
         {"date": "2025-11-15", "type": "نقدي", "amount": 4.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-11-12", "yield": 5.16},

    # MOPCO
    {"symbol": "MFPC", "company": "موبكو للأسمدة",
     "dividends": [
         {"date": "2026-05-08", "type": "نقدي", "amount": 2.80, "currency": "ج.م", "status": "معلن"},
         {"date": "2025-11-10", "type": "نقدي", "amount": 2.50, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-11-08", "yield": 6.20},

    # Telecom Egypt
    {"symbol": "ETEL", "company": "المصرية للاتصالات",
     "dividends": [
         {"date": "2026-04-30", "type": "نقدي", "amount": 3.00, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-10-25", "type": "نقدي", "amount": 2.80, "currency": "ج.م", "status": "تم التوزيع"},
         {"date": "2025-04-28", "type": "أسهم مجانية", "amount": 1, "currency": "سهم/10", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-30", "yield": 3.05},

    # Eastern Tobacco
    {"symbol": "EAST", "company": "الشرقية للدخان",
     "dividends": [
         {"date": "2026-05-20", "type": "نقدي", "amount": 3.20, "currency": "ج.م", "status": "معلن"},
         {"date": "2025-11-22", "type": "نقدي", "amount": 3.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-11-20", "yield": 7.94},

    # Edita
    {"symbol": "EFID", "company": "إيديتا للصناعات الغذائية",
     "dividends": [
         {"date": "2026-05-18", "type": "نقدي", "amount": 1.10, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-18", "yield": 3.85},

    # Juhayna
    {"symbol": "JUFO", "company": "جهينة للصناعات الغذائية",
     "dividends": [
         {"date": "2026-05-22", "type": "نقدي", "amount": 1.00, "currency": "ج.م", "status": "معلن"},
         {"date": "2025-11-25", "type": "نقدي", "amount": 0.90, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-11-22", "yield": 3.46},

    # Delta Sugar
    {"symbol": "SUGR", "company": "دلتا للسكر",
     "dividends": [
         {"date": "2026-05-25", "type": "نقدي", "amount": 2.00, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-25", "yield": 4.10},

    # Cairo Poultry
    {"symbol": "POUL", "company": "القاهرة للدواجن",
     "dividends": [
         {"date": "2026-05-15", "type": "نقدي", "amount": 1.50, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-15", "yield": 4.31},

    # GB Corp
    {"symbol": "GBCO", "company": "GB Corp",
     "dividends": [
         {"date": "2026-04-28", "type": "نقدي", "amount": 1.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-28", "yield": 3.41},

    # Oriental Weavers
    {"symbol": "ORWE", "company": "النساجون الشرقيون",
     "dividends": [
         {"date": "2026-05-02", "type": "نقدي", "amount": 1.20, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-02", "yield": 5.09},

    # Cleopatra Hospitals
    {"symbol": "CLHO", "company": "مستشفيات كليوباترا",
     "dividends": [
         {"date": "2026-05-12", "type": "نقدي", "amount": 0.50, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-12", "yield": 3.35},

    # Amoun Pharma
    {"symbol": "PHAR", "company": "أمون للصناعات الدوائية",
     "dividends": [
         {"date": "2026-04-15", "type": "نقدي", "amount": 4.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-15", "yield": 4.47},

    # Ibnsina Pharma
    {"symbol": "ISPH", "company": "ابن سينا فارما",
     "dividends": [
         {"date": "2026-05-08", "type": "نقدي", "amount": 0.45, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-08", "yield": 3.76},

    # Minapharm
    {"symbol": "MIPH", "company": "مينافارم",
     "dividends": [
         {"date": "2026-04-20", "type": "نقدي", "amount": 15.00, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-20", "yield": 2.18},

    # EFG Hermes
    {"symbol": "HRHO", "company": "EFG هيرمس",
     "dividends": [
         {"date": "2026-04-25", "type": "نقدي", "amount": 1.20, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-25", "yield": 4.07},

    # Beltone
    {"symbol": "BTFH", "company": "بلتون القابضة",
     "dividends": [
         {"date": "2026-05-05", "type": "نقدي", "amount": 0.15, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-05", "yield": 4.70},

    # Qalaa Holdings
    {"symbol": "CCAP", "company": "قلعة للاستثمارات",
     "dividends": [
         {"date": "2026-04-18", "type": "نقدي", "amount": 0.20, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-18", "yield": 4.28},

    # Raya
    {"symbol": "RAYA", "company": "راية القابضة",
     "dividends": [
         {"date": "2026-05-10", "type": "نقدي", "amount": 0.35, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-10", "yield": 4.93},

    # Alexandria Container
    {"symbol": "ALCN", "company": "الإسكندرية للحاويات",
     "dividends": [
         {"date": "2026-05-15", "type": "نقدي", "amount": 1.80, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-15", "yield": 5.98},

    # TAQA Arabia
    {"symbol": "TAQA", "company": "طاقة عربية",
     "dividends": [
         {"date": "2026-05-20", "type": "نقدي", "amount": 0.70, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-20", "yield": 5.08},

    # Sidi Kerir Petrochemicals
    {"symbol": "SKPC", "company": "سيدي كرير للبتروكيماويات",
     "dividends": [
         {"date": "2026-05-18", "type": "نقدي", "amount": 1.20, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-18", "yield": 6.72},

    # Egypt Gas
    {"symbol": "EGAS", "company": "مصر للغاز",
     "dividends": [
         {"date": "2026-05-12", "type": "نقدي", "amount": 2.50, "currency": "ج.م", "status": "معلن"},
     ],
     "next_expected": "2026-11-12", "yield": 5.09},

    # Maridive Oil
    {"symbol": "MOIL", "company": "ماري ديف للخدمات البترولية",
     "dividends": [
         {"date": "2026-04-30", "type": "نقدي", "amount": 0.03, "currency": "ج.م", "status": "تم التوزيع"},
     ],
     "next_expected": "2026-10-30", "yield": 6.55},
]

# ==================== UPCOMING DIVIDENDS CALENDAR ====================
upcoming_dividends = [
    {"date": "2026-05-15", "symbol": "COMI", "company": "CIB", "type": "نقدي", "amount": 2.50, "status": "غداً"},
    {"date": "2026-05-18", "symbol": "EFID", "company": "إيديتا", "type": "نقدي", "amount": 1.10, "status": "بعد 3 أيام"},
    {"date": "2026-05-20", "symbol": "EAST", "company": "الشرقية للدخان", "type": "نقدي", "amount": 3.20, "status": "بعد 5 أيام"},
    {"date": "2026-05-22", "symbol": "JUFO", "company": "جهينة", "type": "نقدي", "amount": 1.00, "status": "بعد 7 أيام"},
    {"date": "2026-05-25", "symbol": "SUGR", "company": "دلتا للسكر", "type": "نقدي", "amount": 2.00, "status": "بعد 10 أيام"},
    {"date": "2026-06-01", "symbol": "TMGH", "company": "طلعت مصطفى", "type": "نقدي", "amount": 2.80, "status": "بعد 16 يوم"},
    {"date": "2026-06-05", "symbol": "SWDY", "company": "السويدي", "type": "نقدي", "amount": 3.50, "status": "بعد 20 يوم"},
    {"date": "2026-06-10", "symbol": "ABUK", "company": "أبو قير", "type": "نقدي", "amount": 4.50, "status": "بعد 25 يوم"},
]

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 رادار السوق", 
    "🔮 التحليل الذكي والتوقعات", 
    "📊 Backtesting متقدم", 
    "💼 محفظتي", 
    "✅ المهام الذكية", 
    "📰 الأخبار والتحليل",
    "💰 التوزيعات والكوبونات"
])

# ==================== TAB 1: MARKET RADAR ====================
with tab1:
    # Market Indices
    cols = st.columns(3)
    indices = [
        {"name": "EGX30", "value": 24850.32, "change": 1.24, "color": "#10b981"},
        {"name": "EGX70", "value": 3245.18, "change": 0.89, "color": "#10b981"},
        {"name": "EGX100", "value": 8932.45, "change": -0.34, "color": "#ef4444"},
    ]

    for i, idx in enumerate(indices):
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">{idx['name']}</p>
                <h2 style="font-size: 36px; margin: 0; color: {'#10b981' if idx['change'] >= 0 else '#ef4444'};">{idx['value']:,.2f}</h2>
                <p style="color: {'#10b981' if idx['change'] >= 0 else '#ef4444'}; font-size: 16px; margin-top: 8px;">
                    {'▲' if idx['change'] >= 0 else '▼'} {abs(idx['change']):.2f}%
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Treemap
    st.subheader("🗺️ خريطة السوق التفاعلية")
    df_main = pd.DataFrame(stocks_data)
    df_main['السعر'] = df_main['price']
    df_main['التغير%'] = df_main['change_pct']
    df_main['الرمز'] = df_main['symbol']
    df_main['الحجم'] = df_main['volume']

    fig_treemap = px.treemap(
        df_main,
        path=[px.Constant("EGX"), 'sector', 'symbol'],
        values='volume',
        color='change_pct',
        color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
        color_continuous_midpoint=0,
        title="حجم التداول والأداء حسب القطاع"
    )
    fig_treemap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Cairo", color="white"),
        height=500
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    # Stock Table
    st.subheader("📋 أسعار الأسهم الرئيسية")

    search_col, sector_col = st.columns([2, 1])
    with search_col:
        search = st.text_input("🔍 البحث في الأسهم", placeholder="ابحث بالرمز أو الاسم...")
    with sector_col:
        sector_filter = st.selectbox("القطاع", ["الكل"] + list(df_main['sector'].unique()))

    filtered_df = df_main.copy()
    if search:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search, case=False) | filtered_df['symbol'].str.contains(search, case=False)]
    if sector_filter != "الكل":
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    def make_styler(df):
        def color_change(val):
            if isinstance(val, (int, float)):
                color = '#10b981' if val >= 0 else '#ef4444'
                return f'color: {color}; font-weight: bold;'
            return ''

        styled = df.style
        for col in ['التغير', 'التغير %']:
            if col in df.columns:
                styled = styled.map(color_change, subset=[col])
        return styled

    display_df = filtered_df[['symbol', 'name', 'sector', 'price', 'change', 'change_pct', 'volume']].copy()
    display_df.columns = ['الرمز', 'الشركة', 'القطاع', 'السعر', 'التغير', 'التغير %', 'الحجم']
    display_df['الحجم'] = (display_df['الحجم'] / 1000000).round(2).astype(str) + 'M'

    st.dataframe(
        make_styler(display_df),
        use_container_width=True,
        hide_index=True,
        column_config={
            "السعر": st.column_config.NumberColumn(format="%.2f ج.م"),
            "التغير": st.column_config.NumberColumn(format="%.2f"),
            "التغير %": st.column_config.NumberColumn(format="%.2f%%"),
        }
    )

    # Top Movers
    st.subheader("🚀 الأكثر نشاطاً")
    movers_cols = st.columns(5)
    top_movers = df_main.nlargest(5, 'change_pct')

    for i, (_, stock) in enumerate(top_movers.iterrows()):
        with movers_cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <p style="color: #fbbf24; font-weight: bold; font-size: 14px;">{stock['symbol']}</p>
                <p style="font-size: 18px; font-weight: bold; margin: 4px 0;">{stock['price']:.2f}</p>
                <p style="color: #10b981; font-size: 14px;">+{stock['change_pct']:.2f}%</p>
                <p style="color: #94a3b8; font-size: 11px;">{(stock['volume']/1000000):.1f}M حجم</p>
            </div>
            """, unsafe_allow_html=True)


# ==================== TAB 2: AI ANALYSIS & PREDICTIONS ====================
with tab2:
    st.title("🔮 التحليل الذكي والتوقعات المستقبلية")

    # Warning
    st.markdown("""
    <div class="warning-box">
        <p style="color: #f87171; font-weight: bold; margin: 0;">⚠️ تحذير هام</p>
        <p style="color: #fca5a5; font-size: 13px; margin-top: 8px;">
        التوقعات والإشارات المعروضة هي نتائج تحليل رياضي للبيانات التاريخية فقط. 
        لا تعتبر توصية استثمارية. السوق يتأثر بعوامل لا يمكن التنبؤ بها. 
        استشر مستشار مالي قبل اتخاذ أي قرار استثماري.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stock Selection
    analysis_stock = st.selectbox("📌 اختر السهم للتحليل الذكي", tickers, key="ai_stock")
    analysis_period = st.selectbox("📅 الفترة التحليلية", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="ai_period")

    if st.button("🔮 تشغيل التحليل الذكي", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري تحليل البيانات وإنشاء التوقعات..."):
            try:
                suffix = ".CA" if is_egypt else ""
                df = yf.Ticker(f"{analysis_stock}{suffix}").history(period=analysis_period)

                if df.empty:
                    st.error("❌ تعذر جلب البيانات. تأكد من الرمز واتصال الإنترنت.")
                else:
                    # Calculate indicators
                    df = calculate_technical_indicators(df)

                    # Generate signals
                    signals = generate_trading_signals(df)
                    overall_signal, score, signal_text = calculate_overall_signal(signals)

                    # Predictions
                    predictions = predict_future_prices(df, days=5)

                    # Support/Resistance
                    sr_levels = calculate_support_resistance(df)

                    # ==================== SIGNAL DISPLAY ====================
                    st.subheader("🎯 إشارة التداول اللحظية")

                    signal_cols = st.columns([1, 2, 1])

                    with signal_cols[1]:
                        if overall_signal == "STRONG_BUY":
                            st.markdown(f"""
                            <div class="signal-buy">
                                <h2 style="margin: 0; color: #10b981; font-size: 36px;">🟢 شراء قوي</h2>
                                <p style="color: #10b981; font-size: 18px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "BUY":
                            st.markdown(f"""
                            <div class="signal-buy">
                                <h2 style="margin: 0; color: #34d399; font-size: 32px;">🟢 شراء</h2>
                                <p style="color: #34d399; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "STRONG_SELL":
                            st.markdown(f"""
                            <div class="signal-sell">
                                <h2 style="margin: 0; color: #ef4444; font-size: 36px;">🔴 بيع قوي</h2>
                                <p style="color: #ef4444; font-size: 18px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "SELL":
                            st.markdown(f"""
                            <div class="signal-sell">
                                <h2 style="margin: 0; color: #f87171; font-size: 32px;">🔴 بيع</h2>
                                <p style="color: #f87171; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="signal-hold">
                                <h2 style="margin: 0; color: #fbbf24; font-size: 32px;">🟡 انتظار</h2>
                                <p style="color: #fbbf24; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # ==================== TECHNICAL INDICATORS ====================
                    st.subheader("📊 المؤشرات الفنية الحية")

                    latest = df.iloc[-1]

                    ind_col1, ind_col2, ind_col3, ind_col4, ind_col5, ind_col6 = st.columns(6)

                    with ind_col1:
                        rsi_color = "#ef4444" if latest['RSI'] > 70 else "#10b981" if latest['RSI'] < 30 else "#fbbf24"
                        rsi_text = "ذروة شراء" if latest['RSI'] > 70 else "ذروة بيع" if latest['RSI'] < 30 else "محايد"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">RSI (14)</p>
                            <p style="font-size: 22px; font-weight: bold; color: {rsi_color}; margin: 4px 0;">{latest['RSI']:.1f}</p>
                            <p style="font-size: 10px; color: {rsi_color};">{rsi_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col2:
                        macd_color = "#10b981" if latest['MACD'] > latest['MACD_Signal'] else "#ef4444"
                        macd_text = "إيجابي" if latest['MACD'] > latest['MACD_Signal'] else "سلبي"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">MACD</p>
                            <p style="font-size: 22px; font-weight: bold; color: {macd_color}; margin: 4px 0;">{latest['MACD']:.2f}</p>
                            <p style="font-size: 10px; color: {macd_color};">{macd_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col3:
                        bb_pos = latest['BB_Position']
                        bb_color = "#10b981" if bb_pos < 0.2 else "#ef4444" if bb_pos > 0.8 else "#fbbf24"
                        bb_text = "منطقة شراء" if bb_pos < 0.2 else "منطقة بيع" if bb_pos > 0.8 else "النطاق الأوسط"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Bollinger</p>
                            <p style="font-size: 22px; font-weight: bold; color: {bb_color}; margin: 4px 0;">{bb_pos:.1%}</p>
                            <p style="font-size: 10px; color: {bb_color};">{bb_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col4:
                        stoch_color = "#10b981" if latest['Stoch_K'] < 20 else "#ef4444" if latest['Stoch_K'] > 80 else "#fbbf24"
                        stoch_text = "ذروة بيع" if latest['Stoch_K'] < 20 else "ذروة شراء" if latest['Stoch_K'] > 80 else "محايد"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Stochastic</p>
                            <p style="font-size: 22px; font-weight: bold; color: {stoch_color}; margin: 4px 0;">{latest['Stoch_K']:.1f}</p>
                            <p style="font-size: 10px; color: {stoch_color};">{stoch_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col5:
                        trend_color = "#10b981" if latest['Close'] > latest['SMA_20'] else "#ef4444"
                        trend_text = "صاعد" if latest['Close'] > latest['SMA_20'] else "هابط"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">SMA 20</p>
                            <p style="font-size: 22px; font-weight: bold; color: {trend_color}; margin: 4px 0;">{latest['SMA_20']:.2f}</p>
                            <p style="font-size: 10px; color: {trend_color};">{trend_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col6:
                        vol_color = "#10b981" if latest['Volume_Ratio'] > 1.5 else "#ef4444" if latest['Volume_Ratio'] < 0.5 else "#fbbf24"
                        vol_text = "نشط" if latest['Volume_Ratio'] > 1.5 else "ضعيف" if latest['Volume_Ratio'] < 0.5 else "طبيعي"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Volume</p>
                            <p style="font-size: 22px; font-weight: bold; color: {vol_color}; margin: 4px 0;">{latest['Volume_Ratio']:.1f}x</p>
                            <p style="font-size: 10px; color: {vol_color};">{vol_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # ==================== DETAILED SIGNALS TABLE ====================
                    st.subheader("📋 تفاصيل إشارات المؤشرات")

                    signals_df = pd.DataFrame(signals, columns=["المؤشر", "الإشارة", "الدرجة", "الوصف"])

                    def signal_color(val):
                        if "شراء" in str(val) and "قوي" in str(val):
                            return 'background-color: rgba(16, 185, 129, 0.3); color: #10b981; font-weight: bold;'
                        elif "شراء" in str(val):
                            return 'color: #10b981;'
                        elif "بيع" in str(val) and "قوي" in str(val):
                            return 'background-color: rgba(239, 68, 68, 0.3); color: #ef4444; font-weight: bold;'
                        elif "بيع" in str(val):
                            return 'color: #ef4444;'
                        return 'color: #fbbf24;'

                    styled_signals = signals_df.style.map(signal_color, subset=["الإشارة"])
                    st.dataframe(styled_signals, use_container_width=True, hide_index=True)

                    # ==================== PRICE PREDICTIONS ====================
                    st.subheader("🔮 توقعات الأسعار للأيام القادمة")

                    if 'combined' in predictions:
                        pred_df = pd.DataFrame(predictions['combined'])
                        pred_df['اليوم'] = pred_df['day'].apply(lambda x: f"يوم {x}")
                        pred_df['التوقع'] = pred_df['predicted']
                        pred_df['الحد الأدنى'] = pred_df['lower_bound']
                        pred_df['الحد الأقصى'] = pred_df['upper_bound']
                        pred_df['الثقة'] = pred_df['confidence'].apply(lambda x: f"{x:.0f}%")

                        display_pred = pred_df[['اليوم', 'التوقع', 'الحد الأدنى', 'الحد الأقصى', 'الثقة']].copy()

                        # Color code predictions
                        current_price = df['Close'].iloc[-1]
                        def pred_color(val):
                            if isinstance(val, (int, float)):
                                return 'color: #10b981;' if val > current_price else 'color: #ef4444;' if val < current_price else 'color: #fbbf24;'
                            return ''

                        styled_pred = display_pred.style.map(pred_color, subset=['التوقع'])
                        st.dataframe(styled_pred, use_container_width=True, hide_index=True)

                        # Prediction Chart
                        fig_pred = go.Figure()

                        # Historical prices
                        fig_pred.add_trace(go.Scatter(
                            x=df.index[-30:],
                            y=df['Close'].tail(30),
                            mode='lines',
                            name='السعر الفعلي',
                            line=dict(color='#6366f1', width=2)
                        ))

                        # Prediction line
                        last_date = df.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=5, freq='B')

                        fig_pred.add_trace(go.Scatter(
                            x=future_dates,
                            y=[p['predicted'] for p in predictions['combined']],
                            mode='lines+markers',
                            name='التوقع',
                            line=dict(color='#fbbf24', width=2, dash='dash'),
                            marker=dict(size=8)
                        ))

                        # Confidence interval
                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=[p['upper_bound'] for p in predictions['combined']] + [p['lower_bound'] for p in predictions['combined']][::-1],
                            fill='toself',
                            fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0)'),
                            name='نطاق الثقة'
                        ))

                        fig_pred.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Cairo", color="white"),
                            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="السعر"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=400
                        )

                        st.plotly_chart(fig_pred, use_container_width=True)

                    # ==================== SUPPORT & RESISTANCE ====================
                    st.subheader("🎯 مستويات الدعم والمقاومة الديناميكية")

                    sr_cols = st.columns(3)

                    with sr_cols[0]:
                        st.markdown("""
                        <div class="glass-card">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 12px;">🔴 مستويات المقاومة</p>
                        """, unsafe_allow_html=True)
                        for i, r in enumerate(sr_levels['resistances'][:3]):
                            st.markdown(f"""
                            <p style="color: #ef4444; font-size: 18px; font-weight: bold; margin: 8px 0;">
                                R{i+1}: {r:.2f}
                            </p>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with sr_cols[1]:
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center; border: 2px solid #6366f1;">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">السعر الحالي</p>
                            <p style="color: #6366f1; font-size: 32px; font-weight: bold; margin: 8px 0;">{sr_levels['current']:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with sr_cols[2]:
                        st.markdown("""
                        <div class="glass-card">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 12px;">🟢 مستويات الدعم</p>
                        """, unsafe_allow_html=True)
                        for i, s in enumerate(sr_levels['supports'][:3]):
                            st.markdown(f"""
                            <p style="color: #10b981; font-size: 18px; font-weight: bold; margin: 8px 0;">
                                S{i+1}: {s:.2f}
                            </p>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Fibonacci Levels
                    with st.expander("📐 مستويات فيبوناتشي", expanded=False):
                        fib_cols = st.columns(7)
                        for i, (level, value) in enumerate(sr_levels['fibonacci'].items()):
                            with fib_cols[i]:
                                fib_color = "#10b981" if value < sr_levels['current'] else "#ef4444" if value > sr_levels['current'] else "#fbbf24"
                                st.markdown(f"""
                                <div class="indicator-box">
                                    <p style="color: #94a3b8; font-size: 10px;">{level}</p>
                                    <p style="font-size: 16px; font-weight: bold; color: {fib_color};">{value:.2f}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    # ==================== CANDLESTICK CHART WITH INDICATORS ====================
                    st.subheader("📈 الرسم البياني التفاعلي مع المؤشرات")

                    fig = go.Figure()

                    # Candlestick
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='الشموع'
                    ))

                    # Moving Averages
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='#6366f1', width=1)
                    ))

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='#fbbf24', width=1)
                    ))

                    # Bollinger Bands
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['BB_Upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(16, 185, 129, 0.5)', width=1),
                        showlegend=False
                    ))

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(16, 185, 129, 0.5)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(16, 185, 129, 0.05)',
                        showlegend=False
                    ))

                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="السعر"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Volume Chart
                    fig_vol = go.Figure()
                    colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' for i in range(len(df))]

                    fig_vol.add_trace(go.Bar(
                        x=df.index,
                        y=df['Volume'],
                        marker_color=colors,
                        name='حجم التداول'
                    ))

                    fig_vol.add_trace(go.Scatter(
                        x=df.index,
                        y=df['Volume_SMA'],
                        mode='lines',
                        name='متوسط الحجم',
                        line=dict(color='#fbbf24', width=2)
                    ))

                    fig_vol.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="الحجم"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=250
                    )

                    st.plotly_chart(fig_vol, use_container_width=True)

            except Exception as e:
                st.error(f"❌ خطأ في التحليل: {str(e)}")
                st.info("💡 تأكد من وجود اتصال بالإنترنت وصحة رمز السهم")


# ==================== TAB 3: BACKTESTING ====================
with tab3:
    st.title("📊 محرك Backtesting متقدم")

    bt_col1, bt_col2 = st.columns([1, 3])

    with bt_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        bt_ticker = st.selectbox("📌 اختر السهم", tickers)
        strategy = st.selectbox("🧠 الاستراتيجية", [
            "RSI_MACD - تقاطع الزخم",
            "MA_Crossover - تقاطع المتوسطات",
            "Bollinger - نطاقات بولينجر",
            "Mean_Reversion - العودة للمتوسط"
        ])
        period = st.selectbox("📅 الفترة", ["3mo", "6mo", "1y", "2y"], index=2)
        initial_capital = st.number_input("💰 رأس المال", value=100000, step=10000)
        st.markdown('</div>', unsafe_allow_html=True)

        run_bt = st.button("🚀 تشغيل الاختبار", type="primary", use_container_width=True)

    with bt_col2:
        if run_bt:
            with st.spinner("⏳ جاري تحليل البيانات التاريخية..."):
                strategy_key = strategy.split(" - ")[0]
                result = run_advanced_backtest(bt_ticker, strategy_key, period, "EGX" if is_egypt else "GLOBAL")

                if result:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    m1, m2, m3, m4, m5 = st.columns(5)

                    strat_color = "normal" if result['Strategy_Return'] >= 0 else "inverse"
                    bh_color = "normal" if result['Buy_Hold_Return'] >= 0 else "inverse"

                    m1.metric("📈 عائد الاستراتيجية", f"{result['Strategy_Return']:+.2f}%", delta_color=strat_color)
                    m2.metric("📊 Buy & Hold", f"{result['Buy_Hold_Return']:+.2f}%", delta_color=bh_color)
                    m3.metric("⚡ Sharpe Ratio", f"{result['Sharpe_Ratio']:.2f}")
                    m4.metric("🎯 Win Rate", f"{result['Win_Rate']:.1f}%")
                    m5.metric("📉 Max Drawdown", f"{result['Max_Drawdown']:.2f}%")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Equity Curve
                    st.subheader("📈 منحنى الأداء")
                    fig_equity = go.Figure()
                    fig_equity.add_trace(go.Scatter(
                        x=result['Equity_Curve'].index,
                        y=result['Equity_Curve'].values,
                        mode='lines',
                        name='رأس المال',
                        line=dict(color='#6366f1', width=3),
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
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="رأس المال (ج.م)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=400
                    )
                    st.plotly_chart(fig_equity, use_container_width=True)

                    # Trade Signals
                    st.subheader("🎯 إشارات التداول")
                    signals = result['Data'][result['Data']['Position'] != 0].copy()
                    if not signals.empty:
                        signals['النوع'] = signals['Position'].apply(lambda x: '🟢 شراء' if x > 0 else '🔴 بيع')
                        signals['السعر'] = signals['Close'].round(2)
                        signals['التاريخ'] = signals.index.strftime('%Y-%m-%d')
                        st.dataframe(signals[['التاريخ', 'النوع', 'السعر']].head(10), use_container_width=True, hide_index=True)

                    st.success(f"✅ عدد الصفقات المنفذة: {result['Trades']}")

                    # Strategy Comparison
                    st.subheader("🏆 مقارنة الاستراتيجيات")
                    strategies_to_test = ["RSI_MACD", "MA_Crossover", "Bollinger", "Mean_Reversion"]
                    comparison_results = []

                    for strat in strategies_to_test:
                        res = run_advanced_backtest(bt_ticker, strat, period, "EGX" if is_egypt else "GLOBAL")
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

                        def highlight_best(val, col):
                            if col in ['العائد %', 'Sharpe', 'Win Rate %']:
                                return 'background-color: rgba(16, 185, 129, 0.3)' if val == comp_df[col].max() else ''
                            elif col == 'Max DD %':
                                return 'background-color: rgba(16, 185, 129, 0.3)' if val == comp_df[col].min() else ''
                            return ''

                        styled_comp = comp_df.style
                        for col in ['العائد %', 'Sharpe', 'Win Rate %', 'Max DD %']:
                            styled_comp = styled_comp.apply(lambda x, c=col: [highlight_best(v, c) for v in x], subset=[col])

                        st.dataframe(styled_comp, use_container_width=True, hide_index=True)
                else:
                    st.error("❌ تعذر جلب البيانات. تأكد من الرمز واتصال الإنترنت.")
        else:
            st.info("👈 اختر السهم والاستراتيجية واضغط 'تشغيل الاختبار'")

# ==================== TAB 4: PORTFOLIO ====================
with tab4:
    st.title("💼 محفظتي الاستثمارية")

    # Portfolio Metrics
    port_value = sum(p["quantity"] * p["current_price"] for p in st.session_state.portfolio)
    port_cost = sum(p["quantity"] * p["buy_price"] for p in st.session_state.portfolio)
    port_pl = port_value - port_cost
    port_pl_pct = (port_pl / port_cost) * 100 if port_cost > 0 else 0

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("💰 القيمة الحالية", f"ج.م {port_value:,.0f}")
    p2.metric("📈 إجمالي الربح/الخسارة", f"ج.م {port_pl:+,.0f}", f"{port_pl_pct:+.2f}%")
    p3.metric("📊 عدد الأسهم", len(st.session_state.portfolio))
    p4.metric("💵 رأس المال المستثمر", f"ج.م {port_cost:,.0f}")

    # Portfolio Chart & Table
    pt_col1, pt_col2 = st.columns([2, 3])

    with pt_col1:
        st.subheader("📊 توزيع المحفظة")
        fig_pie = px.pie(
            names=[p["symbol"] for p in st.session_state.portfolio],
            values=[p["quantity"] * p["current_price"] for p in st.session_state.portfolio],
            color_discrete_sequence=['#6366f1', '#8b5cf6', '#06b6d4', '#fbbf24', '#10b981'],
            hole=0.6
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Cairo", color="white"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1)
        )
        fig_pie.update_traces(textinfo='label+percent', textfont_size=12)
        st.plotly_chart(fig_pie, use_container_width=True)

    with pt_col2:
        st.subheader("📋 تفاصيل الأسهم")
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        portfolio_df['القيمة'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['التكلفة'] = portfolio_df['quantity'] * portfolio_df['buy_price']
        portfolio_df['الربح'] = portfolio_df['القيمة'] - portfolio_df['التكلفة']
        portfolio_df['العائد %'] = (portfolio_df['الربح'] / portfolio_df['التكلفة']) * 100

        display_df = portfolio_df[['symbol', 'name', 'quantity', 'buy_price', 'current_price', 'القيمة', 'الربح', 'العائد %']].copy()
        display_df.columns = ['الرمز', 'السهم', 'الكمية', 'سعر الشراء', 'السعر الحالي', 'القيمة', 'الربح/خسارة', 'العائد %']

        def highlight_profit(val):
            if isinstance(val, (int, float)):
                color = '#10b981' if val >= 0 else '#ef4444'
                return f'color: {color}; font-weight: bold;'
            return ''

        styled_port = display_df.style
        for col in ['الربح/خسارة', 'العائد %']:
            styled_port = styled_port.map(highlight_profit, subset=[col])

        st.dataframe(
            styled_port,
            use_container_width=True,
            hide_index=True,
            column_config={
                "سعر الشراء": st.column_config.NumberColumn(format="%.2f ج.م"),
                "السعر الحالي": st.column_config.NumberColumn(format="%.2f ج.م"),
                "القيمة": st.column_config.NumberColumn(format="%,.0f ج.م"),
                "الربح/خسارة": st.column_config.NumberColumn(format="%,.0f ج.م"),
                "العائد %": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    # Add Stock to Portfolio
    st.subheader("➕ إضافة سهم للمحفظة")
    ap_col1, ap_col2, ap_col3, ap_col4 = st.columns([2, 1, 1, 1])
    with ap_col1:
        new_stock = st.selectbox("السهم", [s["symbol"] + " - " + s["name"] for s in stocks_data])
    with ap_col2:
        new_qty = st.number_input("الكمية", min_value=1, value=100)
    with ap_col3:
        new_price = st.number_input("سعر الشراء", min_value=0.01, value=10.0, step=0.5)
    with ap_col4:
        st.write("")
        st.write("")
        if st.button("✅ إضافة", use_container_width=True):
            symbol = new_stock.split(" - ")[0]
            name = new_stock.split(" - ")[1]
            st.session_state.portfolio.append({
                "symbol": symbol, "name": name, "quantity": new_qty,
                "buy_price": new_price, "current_price": new_price
            })
            st.success(f"تمت إضافة {symbol}")
            st.rerun()

# ==================== TAB 5: SMART TASKS ====================
with tab5:
    st.title("✅ المهام الذكية")

    # Add Task
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
            st.write("")
            st.write("")
            if st.button("💾 حفظ المهمة", use_container_width=True):
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

    # Filter Tasks
    st.subheader("📋 قائمة المهام")
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...")
    with f_col2:
        filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"], format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x])
    with f_col3:
        filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"])

    # Display Tasks
    filtered_tasks = st.session_state.tasks.copy()
    if task_search:
        filtered_tasks = [t for t in filtered_tasks if task_search.lower() in t["title"].lower()]
    if filter_priority != "الكل":
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == filter_priority]
    if filter_status == "مكتمل":
        filtered_tasks = [t for t in filtered_tasks if t["completed"]]
    elif filter_status == "قيد التنفيذ":
        filtered_tasks = [t for t in filtered_tasks if not t["completed"]]

    priority_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    category_icons = {"work": "💼", "personal": "👤", "learning": "📚", "urgent": "🚨"}

    for task in filtered_tasks:
        priority_class = f"priority-{task['priority']}"
        status_icon = "✅" if task["completed"] else "⬜"
        status_style = "text-decoration: line-through; opacity: 0.5;" if task["completed"] else ""

        st.markdown(f"""
        <div class="task-item {priority_class}" style="{status_style}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 20px;">{status_icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 15px;">{task['title']}</p>
                        <div style="display: flex; gap: 8px; margin-top: 4px;">
                            <span class="tag-{task['category']}">{category_icons[task['category']]} {task['category']}</span>
                            <span style="color: #94a3b8; font-size: 12px;">📅 {task['due']}</span>
                            <span style="color: {'#ef4444' if task['priority'] == 'high' else '#f59e0b' if task['priority'] == 'medium' else '#10b981'}; font-size: 12px;">
                                {priority_colors[task['priority']]} {task['priority']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Hidden checkbox for actual interaction
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

# ==================== TAB 6: NEWS & ANALYSIS ====================
with tab6:
    st.title("📰 أخبار السوق والتحليلات")

    # News Feed
    st.subheader("🔥 آخر الأخبار")
    for news in news_data:
        news_class = f"news-{news['type']}"
        icon = "📈" if news['type'] == 'positive' else "📉" if news['type'] == 'negative' else "📊"

        st.markdown(f"""
        <div class="news-item {news_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <span style="color: #fbbf24; font-size: 12px; font-weight: bold;">{news['time']}</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px;">{icon} {news['title']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Technical Analysis Section
    st.subheader("📊 التحليل الفني")

    ta_col1, ta_col2 = st.columns([1, 2])
    with ta_col1:
        ta_stock = st.selectbox("السهم للتحليل", [s["symbol"] for s in stocks_data])
        ta_period = st.selectbox("الفترة التحليلية", ["1mo", "3mo", "6mo", "1y"], index=2)

    with ta_col2:
        st.markdown("""
        <div class="glass-card">
            <h4>مؤشرات الزخم</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 12px;">
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">RSI (14)</p>
                    <p style="font-size: 24px; font-weight: bold; color: #fbbf24;">62.4</p>
                    <p style="font-size: 11px; color: #10b981;">محايد ➡️</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">MACD</p>
                    <p style="font-size: 24px; font-weight: bold; color: #10b981;">+0.45</p>
                    <p style="font-size: 11px; color: #10b981;">إيجابي 📈</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">Bollinger</p>
                    <p style="font-size: 24px; font-weight: bold; color: #6366f1;">الوسط</p>
                    <p style="font-size: 11px; color: #f59e0b;">انتظار ⏸️</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Support/Resistance
    st.subheader("🎯 مستويات الدعم والمقاومة")
    sr_col1, sr_col2, sr_col3, sr_col4, sr_col5 = st.columns(5)

    current_price = next(s["price"] for s in stocks_data if s["symbol"] == ta_stock)
    support_levels = [current_price * 0.95, current_price * 0.90, current_price * 0.85]
    resistance_levels = [current_price * 1.05, current_price * 1.10]

    sr_col1.metric("الدعم 1", f"{support_levels[0]:.2f}")
    sr_col2.metric("الدعم 2", f"{support_levels[1]:.2f}")
    sr_col3.metric("السعر الحالي", f"{current_price:.2f}")
    sr_col4.metric("المقاومة 1", f"{resistance_levels[0]:.2f}")
    sr_col5.metric("المقاومة 2", f"{resistance_levels[1]:.2f}")


# ==================== TAB 7: DIVIDENDS & COUPONS ====================
with tab7:
    st.title("💰 توزيعات الشركات والكوبونات")

    # Warning
    st.markdown("""
    <div class="warning-box">
        <p style="color: #f87171; font-weight: bold; margin: 0;">⚠️ تنبيه</p>
        <p style="color: #fca5a5; font-size: 13px; margin-top: 8px;">
        البيانات المعروضة هي بيانات توضيحية للتجربة. التواريخ والمبالغ قد لا تكون دقيقة. 
        يرجى التحقق من البورصة المصرية الرسمية للحصول على أحدث البيانات.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Summary Cards
    st.subheader("📊 ملخص التوزيعات")

    total_companies = len(dividends_data)
    total_distributed = sum(sum(d["amount"] for d in comp["dividends"] if d["type"] == "نقدي" and d["status"] == "تم التوزيع") for comp in dividends_data)
    upcoming_count = len([d for d in upcoming_dividends if d["status"] in ["غداً", "بعد 3 أيام", "بعد 5 أيام"]])
    avg_yield = sum(comp["yield"] for comp in dividends_data) / len(dividends_data) if dividends_data else 0

    div_col1, div_col2, div_col3, div_col4 = st.columns(4)

    with div_col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <p style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">الشركات الموزعة</p>
            <h2 style="font-size: 32px; margin: 0; color: #10b981;">{total_companies}</h2>
            <p style="color: #10b981; font-size: 14px; margin-top: 8px;">شركة</p>
        </div>
        """, unsafe_allow_html=True)

    with div_col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <p style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">إجمالي التوزيعات</p>
            <h2 style="font-size: 32px; margin: 0; color: #fbbf24;">{total_distributed:.1f}</h2>
            <p style="color: #fbbf24; font-size: 14px; margin-top: 8px;">ج.م للسهم الواحد</p>
        </div>
        """, unsafe_allow_html=True)

    with div_col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <p style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">القادمة قريباً</p>
            <h2 style="font-size: 32px; margin: 0; color: #6366f1;">{upcoming_count}</h2>
            <p style="color: #6366f1; font-size: 14px; margin-top: 8px;">توزيع</p>
        </div>
        """, unsafe_allow_html=True)

    with div_col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <p style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">متوسط العائد</p>
            <h2 style="font-size: 32px; margin: 0; color: #8b5cf6;">{avg_yield:.2f}%</h2>
            <p style="color: #8b5cf6; font-size: 14px; margin-top: 8px;">سنوياً</p>
        </div>
        """, unsafe_allow_html=True)

    # Upcoming Dividends Calendar
    st.subheader("📅 التوزيعات القادمة")

    for div in upcoming_dividends:
        status_color = "#ef4444" if div["status"] == "غداً" else "#f59e0b" if "3" in div["status"] or "5" in div["status"] else "#10b981"

        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px;">💰</div>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 16px;">{div["company"]} ({div["symbol"]})</p>
                        <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">
                            📅 {div["date"]} | 🏷️ {div["type"]} | 💵 {div["amount"]} ج.م للسهم
                        </p>
                    </div>
                </div>
                <div style="text-align: center;">
                    <span style="background: {status_color}20; color: {status_color}; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                        {div["status"]}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Dividends by Company
    st.subheader("📋 سجل التوزيعات حسب الشركة")

    # Filter by company
    div_company = st.selectbox("🔍 اختر الشركة", [d["company"] + " - " + d["symbol"] for d in dividends_data], key="div_company")

    selected_symbol = div_company.split(" - ")[1]
    selected_company = next((d for d in dividends_data if d["symbol"] == selected_symbol), None)

    if selected_company:
        # Company dividend summary
        st.markdown(f"""
        <div class="prediction-card" style="margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #fbbf24;">{selected_company["company"]}</h3>
                    <p style="color: #94a3b8; margin: 4px 0 0 0;">الرمز: {selected_company["symbol"]} | العائد السنوي: {selected_company["yield"]:.2f}%</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">التوزيع القادم المتوقع</p>
                    <p style="color: #10b981; font-size: 18px; font-weight: bold; margin: 4px 0;">{selected_company["next_expected"]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Dividends history table
        div_history = selected_company["dividends"]
        div_df = pd.DataFrame(div_history)
        div_df['التاريخ'] = div_df['date']
        div_df['النوع'] = div_df['type']
        div_df['المبلغ'] = div_df['amount'].astype(str) + " " + div_df['currency']
        div_df['الحالة'] = div_df['status']

        display_div = div_df[['التاريخ', 'النوع', 'المبلغ', 'الحالة']].copy()

        def status_color(val):
            if "تم" in str(val):
                return 'color: #10b981; font-weight: bold;'
            elif "معلن" in str(val):
                return 'color: #fbbf24; font-weight: bold;'
            return 'color: #94a3b8;'

        styled_div = display_div.style.map(status_color, subset=['الحالة'])
        st.dataframe(styled_div, use_container_width=True, hide_index=True)

        # Dividend yield chart
        st.subheader("📈 تاريخ العائد السنوي")

        # Calculate cumulative dividends
        cash_divs = [d for d in div_history if d["type"] == "نقدي"]
        if cash_divs:
            years = sorted(set([d["date"][:4] for d in cash_divs]))
            yearly_totals = []
            for year in years:
                year_divs = [d["amount"] for d in cash_divs if d["date"].startswith(year)]
                yearly_totals.append(sum(year_divs))

            fig_yield = go.Figure()
            fig_yield.add_trace(go.Bar(
                x=years,
                y=yearly_totals,
                marker_color=['#6366f1', '#8b5cf6', '#06b6d4'],
                text=[f"{t:.2f}" for t in yearly_totals],
                textposition='outside',
                textfont=dict(color='white', size=14)
            ))

            fig_yield.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Cairo", color="white"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="السنة"),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="إجمالي التوزيع (ج.م)"),
                height=350
            )

            st.plotly_chart(fig_yield, use_container_width=True)

    # All Dividends Table
    st.subheader("📊 جدول شامل للتوزيعات")

    all_divs = []
    for comp in dividends_data:
        for div in comp["dividends"]:
            all_divs.append({
                "الشركة": comp["company"],
                "الرمز": comp["symbol"],
                "التاريخ": div["date"],
                "النوع": div["type"],
                "المبلغ": f"{div['amount']} {div['currency']}",
                "الحالة": div["status"],
                "العائد %": comp["yield"]
            })

    all_divs_df = pd.DataFrame(all_divs)

    # Filter options
    div_filter_col1, div_filter_col2 = st.columns([2, 1])
    with div_filter_col1:
        div_type_filter = st.selectbox("نوع التوزيع", ["الكل", "نقدي", "أسهم مجانية"], key="div_type")
    with div_filter_col2:
        div_status_filter = st.selectbox("الحالة", ["الكل", "تم التوزيع", "معلن"], key="div_status")

    filtered_divs = all_divs_df.copy()
    if div_type_filter != "الكل":
        filtered_divs = filtered_divs[filtered_divs["النوع"] == div_type_filter]
    if div_status_filter != "الكل":
        filtered_divs = filtered_divs[filtered_divs["الحالة"] == div_status_filter]

    def div_status_color(val):
        if "تم" in str(val):
            return 'color: #10b981; font-weight: bold;'
        elif "معلن" in str(val):
            return 'color: #fbbf24; font-weight: bold;'
        return 'color: #94a3b8;'

    styled_all_divs = filtered_divs.style.map(div_status_color, subset=["الحالة"])
    st.dataframe(styled_all_divs, use_container_width=True, hide_index=True)

    # Top Dividend Yielders
    st.subheader("🏆 أعلى الشركات عائداً")

    top_yielders = sorted(dividends_data, key=lambda x: x["yield"], reverse=True)[:10]

    yield_cols = st.columns(5)
    for i, comp in enumerate(top_yielders):
        with yield_cols[i % 5]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; margin-bottom: 12px;">
                <p style="color: #fbbf24; font-weight: bold; font-size: 14px;">{comp["symbol"]}</p>
                <p style="font-size: 16px; font-weight: bold; margin: 4px 0; color: #10b981;">{comp["yield"]:.2f}%</p>
                <p style="color: #94a3b8; font-size: 11px;">{comp["company"][:15]}...</p>
            </div>
            """, unsafe_allow_html=True)

    # Dividend Calculator
    st.subheader("🧮 حاسبة التوزيعات")

    calc_col1, calc_col2, calc_col3 = st.columns([2, 1, 1])
    with calc_col1:
        calc_stock = st.selectbox("السهم", [d["company"] + " - " + d["symbol"] for d in dividends_data], key="calc_stock")
    with calc_col2:
        calc_qty = st.number_input("الكمية", min_value=1, value=1000, step=100, key="calc_qty")
    with calc_col3:
        st.write("")
        st.write("")
        if st.button("🧮 احسب", use_container_width=True, key="calc_btn"):
            calc_symbol = calc_stock.split(" - ")[1]
            calc_comp = next((d for d in dividends_data if d["symbol"] == calc_symbol), None)
            if calc_comp:
                latest_div = calc_comp["dividends"][0] if calc_comp["dividends"] else None
                if latest_div and latest_div["type"] == "نقدي":
                    total_amount = latest_div["amount"] * calc_qty
                    st.success(f"💰 إجمالي التوزيع المتوقع: {total_amount:,.2f} ج.م")
                    st.info(f"📊 العائد السنوي: {calc_comp['yield']:.2f}% | التوزيع القادم: {calc_comp['next_expected']}")

# ==================== FOOTER ====================
best_stock = max(stocks_data, key=lambda x: x["change_pct"])
st.markdown(f"""
<div style="text-align: center; padding: 30px; margin-top: 40px; background: linear-gradient(90deg, #0a0a0a, #1a1a2e); color: #00ffaa; border-top: 3px solid #6366f1; border-radius: 16px;">
    <p style="font-size: 18px; margin-bottom: 8px;">⚡ EGX Super Analyst Pro v15.0</p>
    <p style="color: #94a3b8; font-size: 14px;">
        نظام تحليلي ذكي متكامل | Backtesting متقدم | توقعات AI | إدارة المهام والمحافظ
    </p>
    <p style="color: #fbbf24; font-size: 14px; margin-top: 8px;">
        🏆 أقوى سهم اليوم: <b>{best_stock['symbol']}</b> ({best_stock['name']}) — +{best_stock['change_pct']:.2f}%
    </p>
    <p style="color: #6b7280; font-size: 12px; margin-top: 12px;">
        © 2026 | جميع البيانات تأتي من مصادر تجريبية للتوضيح | التوقعات للأغراض التعليمية فقط
    </p>
</div>
""", unsafe_allow_html=True)
