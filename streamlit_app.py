#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ EGX Pro Terminal v26 - نظام تحليلي احترافي للبورصة المصرية
التطبيق الرئيسي - محسّن لـ Streamlit Cloud

Version: 26.0.0
Last Updated: May 2026
Author: m02417710-maker
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================

# إعدادات الصفحة
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v26",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ==================== STYLING ====================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Cairo:wght@300;400;600;700;800&display=swap');
    
    * { 
        font-family: 'Inter', 'Cairo', sans-serif !important; 
        letter-spacing: -0.01em; 
    }
    
    .main { 
        background: linear-gradient(180deg, #07070d 0%, #0f0f1a 50%, #07070d 100%); 
        color: #e2e8f0; 
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(99,102,241,0.8), rgba(139,92,246,0.8));
        border: 1px solid rgba(99,102,241,0.5);
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99,102,241,0.3);
    }
    
    .metric-card {
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98));
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    
    h1, h2, h3 {
        color: #818cf8;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER CLASSES ====================

class AlertManager:
    """نظام التنبيهات الذكية"""
    def __init__(self):
        self.alerts = st.session_state.get('alerts', [])
    
    def add_alert(self, symbol: str, alert_type: str, condition: str, value: float):
        alert = {
            'id': len(self.alerts),
            'symbol': symbol,
            'type': alert_type,
            'condition': condition,
            'value': value,
            'created_at': datetime.now()
        }
        self.alerts.append(alert)
        st.session_state.alerts = self.alerts
        return alert
    
    def get_alerts(self):
        return self.alerts

class RiskManager:
    """إدارة المخاطر المتقدمة"""
    
    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return sorted_returns[index] if index < len(sorted_returns) else 0
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.05) -> float:
        if len(returns) < 2:
            return 0
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        return (mean_return - risk_free_rate) / std_return if std_return != 0 else 0
    
    @staticmethod
    def calculate_max_drawdown(returns: List[float]) -> float:
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown) if len(drawdown) > 0 else 0

class StockScreener:
    """مسح الأسهم الذكي"""
    
    def __init__(self, stocks_data: List[Dict]):
        self.stocks = stocks_data
    
    def filter_by_criteria(self, criteria: Dict) -> List[Dict]:
        results = self.stocks.copy()
        
        if 'price_min' in criteria:
            results = [s for s in results if s.get('price', 0) >= criteria['price_min']]
        if 'price_max' in criteria:
            results = [s for s in results if s.get('price', 0) <= criteria['price_max']]
        if 'change_min' in criteria:
            results = [s for s in results if s.get('change_pct', 0) >= criteria['change_min']]
        
        return results

class StrategyManager:
    """مدير الاستراتيجيات"""
    
    TEMPLATES = {
        'الدعم والمقاومة': {
            'description': 'تداول من مستويات الدعم والمقاومة',
            'entry_rule': 'ارتداد من الدعم',
            'exit_rule': 'كسر المستوى',
            'ratio': '1:2'
        },
        'الزخم': {
            'description': 'تتابع اتجاهات قوية',
            'entry_rule': 'كسر مستوى عالي',
            'exit_rule': 'انعكاس الاتجاه',
            'ratio': '1:3'
        },
        'المتوسط المتحرك': {
            'description': 'تتابع الاتجاه',
            'entry_rule': 'تقاطع السعر',
            'exit_rule': 'تقاطع معاكس',
            'ratio': '1:2.5'
        }
    }
    
    def get_templates(self):
        return self.TEMPLATES

# ==================== SAMPLE DATA ====================

def get_sample_stocks():
    """بيانات نموذجية للأسهم"""
    return [
        {'symbol': 'EBANK', 'name': 'البنك الأهلي المصري', 'price': 150.5, 'change_pct': 2.5, 'volume': 5000000, 'sector': 'البنوك'},
        {'symbol': 'EVCO', 'name': 'الكوك مصر', 'price': 200.0, 'change_pct': -1.2, 'volume': 3000000, 'sector': 'الغذائيات'},
        {'symbol': 'ORWA', 'name': 'أوراسكوم تليكوم', 'price': 75.25, 'change_pct': 3.8, 'volume': 2000000, 'sector': 'الاتصالات'},
        {'symbol': 'CRNT', 'name': 'ساينتيا', 'price': 120.0, 'change_pct': 0.5, 'volume': 1500000, 'sector': 'الدواء'},
        {'symbol': 'MOIL', 'name': 'جنرال بتروليوم', 'price': 180.75, 'change_pct': -2.1, 'volume': 4000000, 'sector': 'الطاقة'},
    ]

# ==================== MAIN APP ====================

def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1>⚡ EGX Pro Terminal v26</h1>
            <p style="color: #94a3b8; font-size: 14px;">نظام تحليلي احترافي للبورصة المصرية</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar Navigation
    st.sidebar.markdown("### 📍 القائمة الرئيسية")
    page = st.sidebar.radio(
        "اختر القسم:",
        ["📊 لوحة التحكم", "🔔 التنبيهات", "⚖️ إدارة المخاطر", "🔍 مسح الأسهم", "📚 الاستراتيجيات", "💼 المحفظة"],
        key="page_selector"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ معلومات")
    st.sidebar.markdown("""
    **الإصدار:** v26.0.0
    
    **آخر تحديث:** مايو 2026
    
    **الميزات:**
    - ✨ نظام تنبيهات ذكية
    - 📈 إدارة مخاطر متقدمة
    - 🔍 مسح أسهم ذكي
    - 📚 قوالب استراتيجيات
    """)
    
    # ==================== PAGE: DASHBOARD ====================
    if page == "📊 لوحة التحكم":
        st.markdown("## 📊 لوحة التحكم الرئيسية")
        
        stocks = get_sample_stocks()
        df = pd.DataFrame(stocks)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 إجمالي الأسهم", len(stocks), "نشطة")
        with col2:
            avg_change = df['change_pct'].mean()
            st.metric("📊 متوسط التغير", f"{avg_change:+.2f}%", "يومي")
        with col3:
            total_volume = df['volume'].sum() / 1_000_000
            st.metric("📉 الحجم الإجمالي", f"{total_volume:.1f}M", "دولار")
        with col4:
            sectors = df['sector'].nunique()
            st.metric("🏭 القطاعات", sectors, "قطاع")
        
        st.markdown("---")
        st.markdown("### 📋 أكبر الأسهم تداولاً")
        top_stocks = df.nlargest(5, 'volume')[['symbol', 'name', 'price', 'change_pct', 'volume']]
        st.dataframe(top_stocks, use_container_width=True, hide_index=True)
    
    # ==================== PAGE: ALERTS ====================
    elif page == "🔔 التنبيهات":
        st.markdown("## 🔔 نظام التنبيهات الذكية")
        
        alert_mgr = AlertManager()
        
        with st.expander("➕ إضافة تنبيه جديد", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                symbol = st.selectbox("السهم", [s['symbol'] for s in get_sample_stocks()])
            with col2:
                alert_type = st.selectbox("النوع", ["PRICE", "VOLUME", "MACD", "RSI"])
            with col3:
                condition = st.selectbox("الشرط", [">", "<", "="])
            with col4:
                value = st.number_input("القيمة", min_value=0.0, step=0.01)
            
            if st.button("✅ إضافة التنبيه"):
                alert_mgr.add_alert(symbol, alert_type, condition, value)
                st.success(f"✅ تم إضافة تنبيه على {symbol}")
        
        st.markdown("---")
        st.markdown("### 📋 التنبيهات النشطة")
        alerts = alert_mgr.get_alerts()
        if alerts:
            alerts_df = pd.DataFrame([
                {
                    'السهم': a['symbol'],
                    'النوع': a['type'],
                    'الشرط': f"{a['condition']} {a['value']}"
                } for a in alerts
            ])
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 لا توجد تنبيهات نشطة")
    
    # ==================== PAGE: RISK MANAGEMENT ====================
    elif page == "⚖️ إدارة المخاطر":
        st.markdown("## ⚖️ إدارة المخاطر المتقدمة")
        
        risk_mgr = RiskManager()
        
        # Generate sample returns
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, 100).tolist()
        
        var_95 = risk_mgr.calculate_var(returns, 0.95)
        sharpe = risk_mgr.calculate_sharpe_ratio(returns)
        max_dd = risk_mgr.calculate_max_drawdown(returns)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 VaR (95%)", f"{var_95:.2%}")
        with col2:
            st.metric("📈 Sharpe Ratio", f"{sharpe:.2f}")
        with col3:
            st.metric("📉 Max Drawdown", f"{max_dd:.2%}")
        with col4:
            st.metric("📐 Volatility", f"{np.std(returns):.2%}")
        
        # Chart
        cumulative_returns = np.cumprod(1 + np.array(returns))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=cumulative_returns,
            mode='lines',
            name='العائدات التراكمية',
            line=dict(color='#818cf8', width=2)
        ))
        fig.update_layout(
            title="العائدات التراكمية",
            xaxis_title="الفترة",
            yaxis_title="العائد",
            template="plotly_dark",
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== PAGE: STOCK SCREENER ====================
    elif page == "🔍 مسح الأسهم":
        st.markdown("## 🔍 مسح الأسهم الذكي")
        
        screener = StockScreener(get_sample_stocks())
        
        with st.expander("🎯 معايير البحث"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                price_min = st.number_input("السعر الأدنى", min_value=0.0, value=0.0)
            with col2:
                price_max = st.number_input("السعر الأقصى", min_value=0.0, value=500.0)
            with col3:
                change_min = st.number_input("التغير الأدنى %", value=-10.0)
            with col4:
                volume_min = st.number_input("الحجم الأدنى", value=0, step=100000)
        
        criteria = {
            'price_min': price_min,
            'price_max': price_max,
            'change_min': change_min
        }
        
        results = screener.filter_by_criteria(criteria)
        
        if results:
            results_df = pd.DataFrame([
                {
                    'السهم': s['symbol'],
                    'الاسم': s['name'],
                    'السعر': f"{s['price']:.2f}",
                    'التغير%': f"{s['change_pct']:+.2f}%",
                    'الحجم': f"{s['volume']:,}"
                } for s in results
            ])
            st.dataframe(results_df, use_container_width=True, hide_index=True)
        else:
            st.warning("❌ لا توجد نتائج تطابق المعايير")
    
    # ==================== PAGE: STRATEGIES ====================
    elif page == "📚 الاستراتيجيات":
        st.markdown("## 📚 قوالب الاستراتيجيات")
        
        strategy_mgr = StrategyManager()
        templates = strategy_mgr.get_templates()
        
        for strategy_name, config in templates.items():
            with st.expander(f"📌 {strategy_name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**الوصف:** {config['description']}")
                    st.markdown(f"**نسبة المخاطرة:** {config['ratio']}")
                with col2:
                    st.markdown(f"**الدخول:** {config['entry_rule']}")
                    st.markdown(f"**الخروج:** {config['exit_rule']}")
    
    # ==================== PAGE: PORTFOLIO ====================
    elif page == "💼 المحفظة":
        st.markdown("## 💼 محاكاة المحفظة")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 رأس المال", "100,000", "ج.م")
        with col2:
            st.metric("📈 الأرباح", "+5,250", "ج.م")
        with col3:
            st.metric("📊 العائد", "+5.25%", "نسبة")
        with col4:
            st.metric("⚖️ الأسهم", "12", "صفقة")
        
        st.markdown("---")
        
        with st.expander("➕ إضافة صفقة جديدة"):
            col1, col2 = st.columns(2)
            with col1:
                symbol = st.selectbox("السهم", [s['symbol'] for s in get_sample_stocks()])
                direction = st.radio("الاتجاه", ["شراء", "بيع"])
            with col2:
                quantity = st.number_input("الكمية", min_value=1, value=100)
                entry_price = st.number_input("سعر الدخول", min_value=0.0, step=0.01)
            
            if st.button("💾 إضافة الصفقة"):
                st.success(f"✅ تمت إضافة صفقة {direction} على {symbol}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 12px;">
        <p>© 2026 EGX Pro Terminal v26 | نظام تحليلي احترافي للبورصة المصرية</p>
        <p>للأغراض التعليمية فقط - ليست نصيحة استثمارية</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
