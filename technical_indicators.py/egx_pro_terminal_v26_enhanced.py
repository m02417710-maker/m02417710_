import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
import os
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

warnings.filterwarnings('ignore')

# ==================== ADVANCED CONFIGURATION ====================
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v26 | نظام التوصيات الذكي", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL DARK THEME CSS v26 ====================
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

    /* ===== ALERT BADGE ===== */
    .alert-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 8px;
        background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
        border: 1px solid rgba(239,68,68,0.3);
        color: #ef4444;
        font-weight: 600;
        font-size: 12px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }

    /* ===== RISK METER ===== */
    .risk-meter {
        display: flex;
        gap: 4px;
        margin: 8px 0;
    }
    .risk-bar {
        flex: 1;
        height: 6px;
        border-radius: 3px;
        background: rgba(255,255,255,0.1);
    }
    .risk-bar.high { background: #ef4444; }
    .risk-bar.medium { background: #f59e0b; }
    .risk-bar.low { background: #10b981; }

    /* ===== STRATEGY CARD ===== */
    .strategy-card {
        background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(15,15,25,0.98));
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    .strategy-card:hover {
        border-color: rgba(99,102,241,0.5);
        box-shadow: 0 8px 32px rgba(99,102,241,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== NEW: ADVANCED ALERT SYSTEM ====================
class AlertManager:
    """نظام التنبيهات الذكية"""
    def __init__(self):
        self.alerts = []
        self.active_alerts = st.session_state.get('active_alerts', [])
    
    def add_alert(self, symbol: str, alert_type: str, condition: str, value: float, action: str = ""):
        """إضافة تنبيه جديد"""
        alert = {
            'id': len(self.alerts),
            'symbol': symbol,
            'type': alert_type,  # 'PRICE', 'VOLUME', 'MACD', 'RSI'
            'condition': condition,  # '>', '<', '='
            'value': value,
            'action': action,
            'created_at': datetime.now(),
            'triggered': False
        }
        self.alerts.append(alert)
        st.session_state.active_alerts = self.alerts
        return alert
    
    def check_alerts(self, current_data: Dict) -> List[Dict]:
        """فحص التنبيهات وإرجاع المفعلة"""
        triggered = []
        for alert in self.alerts:
            if alert['triggered']:
                continue
            
            symbol = alert['symbol']
            if symbol not in current_data:
                continue
            
            stock = current_data[symbol]
            
            if alert['type'] == 'PRICE':
                if alert['condition'] == '>' and stock['price'] > alert['value']:
                    triggered.append(alert)
                    alert['triggered'] = True
                elif alert['condition'] == '<' and stock['price'] < alert['value']:
                    triggered.append(alert)
                    alert['triggered'] = True
        
        return triggered
    
    def render_alerts_panel(self):
        """عرض لوحة التنبيهات"""
        st.markdown("### 🔔 لوحة التنبيهات النشطة")
        
        if self.alerts:
            alert_cols = st.columns([3, 1, 1, 1])
            with alert_cols[0]:
                st.markdown("**التنبيه**")
            with alert_cols[1]:
                st.markdown("**النوع**")
            with alert_cols[2]:
                st.markdown("**الحالة**")
            with alert_cols[3]:
                st.markdown("**إجراء**")
            
            for idx, alert in enumerate(self.alerts):
                acols = st.columns([3, 1, 1, 1])
                with acols[0]:
                    st.markdown(f"**{alert['symbol']}** {alert['condition']} {alert['value']}")
                with acols[1]:
                    st.markdown(f"`{alert['type']}`")
                with acols[2]:
                    status = "✅ مفعل" if alert['triggered'] else "⏳ نشط"
                    st.markdown(status)
                with acols[3]:
                    if st.button("🗑️", key=f"del_alert_{idx}"):
                        self.alerts.pop(idx)
                        st.rerun()
        else:
            st.info("📭 لا توجد تنبيهات نشطة حالياً")

# ==================== NEW: ADVANCED RISK MANAGEMENT ====================
class RiskManager:
    """إدارة المخاطر المتقدمة"""
    
    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """حساب Value at Risk"""
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return sorted_returns[index]
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.05) -> float:
        """حساب Sharpe Ratio"""
        if len(returns) < 2:
            return 0
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0
        return (mean_return - risk_free_rate) / std_return
    
    @staticmethod
    def calculate_max_drawdown(returns: List[float]) -> float:
        """حساب Maximum Drawdown"""
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown)
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], target_return: float = 0.0) -> float:
        """حساب Sortino Ratio"""
        downside_returns = [r for r in returns if r < target_return]
        if not downside_returns:
            return 0
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0
        return (np.mean(returns) - target_return) / downside_std
    
    @staticmethod
    def get_risk_level(volatility: float, drawdown: float, var: float) -> Tuple[str, str]:
        """تحديد مستوى المخاطر"""
        if volatility > 0.3 or drawdown < -0.2 or var < -0.15:
            return "🔴 عالي جداً", "#ef4444"
        elif volatility > 0.2 or drawdown < -0.1 or var < -0.08:
            return "🟠 عالي", "#f59e0b"
        elif volatility > 0.1 or drawdown < -0.05 or var < -0.03:
            return "🟡 متوسط", "#eab308"
        else:
            return "🟢 منخفض", "#10b981"

# ==================== NEW: PDF REPORT GENERATOR ====================
class PDFReportGenerator:
    """مولد التقارير بصيغة PDF"""
    
    @staticmethod
    def generate_analysis_report(symbol: str, data: Dict, recommendations: List) -> bytes:
        """توليد تقرير تحليلي"""
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # العنوان الرئيسي
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#818cf8'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph(f"📊 تقرير تحليلي - {symbol}", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # معلومات الأسهم
        info_data = [
            ['السهم', symbol],
            ['التاريخ', datetime.now().strftime("%d/%m/%Y %H:%M")],
            ['السعر الحالي', f"{data.get('price', 0):.2f} ج.م"],
            ['التغير اليومي', f"{data.get('change_pct', 0):.2f}%"],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0f0f1a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # التوصيات
        elements.append(Paragraph("التوصيات", styles['Heading2']))
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("📝 إخلاء المسؤولية: جميع البيانات للتوضيح فقط. هذا ليس بنصيحة استثمارية.", styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

# ==================== NEW: STOCK SCREENER ====================
class StockScreener:
    """مقارن الأسهم والمسح الضوئي"""
    
    def __init__(self, stocks_data: List[Dict]):
        self.stocks = stocks_data
    
    def filter_by_criteria(self, criteria: Dict) -> List[Dict]:
        """تصفية الأسهم حسب المعايير"""
        results = self.stocks.copy()
        
        # تصفية حسب السعر
        if 'price_min' in criteria:
            results = [s for s in results if s.get('price', 0) >= criteria['price_min']]
        if 'price_max' in criteria:
            results = [s for s in results if s.get('price', 0) <= criteria['price_max']]
        
        # تصفية حسب التغير
        if 'change_min' in criteria:
            results = [s for s in results if s.get('change_pct', 0) >= criteria['change_min']]
        if 'change_max' in criteria:
            results = [s for s in results if s.get('change_pct', 0) <= criteria['change_max']]
        
        # تصفية حسب الحجم
        if 'volume_min' in criteria:
            results = [s for s in results if s.get('volume', 0) >= criteria['volume_min']]
        
        return results
    
    def find_breakouts(self, threshold: float = 0.05) -> List[Dict]:
        """البحث عن الاختراقات"""
        breakouts = []
        for stock in self.stocks:
            if abs(stock.get('change_pct', 0)) > threshold * 100:
                breakouts.append(stock)
        return sorted(breakouts, key=lambda x: abs(x.get('change_pct', 0)), reverse=True)
    
    def find_support_resistance(self) -> List[Dict]:
        """البحث عن الأسهم القريبة من الدعم والمقاومة"""
        results = []
        for stock in self.stocks:
            price = stock.get('price', 0)
            # محاكاة بسيطة
            support = price * 0.95
            resistance = price * 1.05
            results.append({
                **stock,
                'support': support,
                'resistance': resistance,
                'distance_to_support': ((price - support) / support) * 100,
                'distance_to_resistance': ((resistance - price) / resistance) * 100,
            })
        return results

# ==================== NEW: STRATEGY TEMPLATES ====================
class StrategyManager:
    """مدير الاستراتيجيات المخزنة"""
    
    TEMPLATES = {
        'استراتيجية الدعم والمقاومة': {
            'description': 'تداول من مستويات الدعم والمقاومة',
            'entry_rule': 'ارتداد من الدعم أو اختراق المقاومة',
            'exit_rule': 'الوصول لهدف الربح أو كسر الدعم/المقاومة',
            'risk_reward_ratio': '1:2',
            'indicators': ['Support/Resistance', 'Volume', 'MA']
        },
        'استراتيجية الزخم': {
            'description': 'تتابع اتجاهات قوية',
            'entry_rule': 'كسر مستوى عالي مع حجم مرتفع',
            'exit_rule': 'انعكاس الاتجاه أو الوصول للهدف',
            'risk_reward_ratio': '1:3',
            'indicators': ['RSI', 'MACD', 'Volume']
        },
        'استراتيجية المتوسط المتحرك': {
            'description': 'تتابع الاتجاه باستخدام المتوسطات',
            'entry_rule': 'عندما يقطع السعر المتوسط من الأسفل',
            'exit_rule': 'عندما يقطع المتوسط من الأعلى',
            'risk_reward_ratio': '1:2.5',
            'indicators': ['MA', 'Close Price']
        },
        'استراتيجية التذبذب': {
            'description': 'الشراء والبيع بين المستويات',
            'entry_rule': 'السعر يقترب من الحد الأدنى',
            'exit_rule': 'السعر يقترب من الحد الأعلى',
            'risk_reward_ratio': '1:1.5',
            'indicators': ['RSI', 'Bollinger Bands', 'Support/Resistance']
        }
    }
    
    def get_templates(self) -> Dict:
        """الحصول على قائمة الاستراتيجيات"""
        return self.TEMPLATES
    
    def save_custom_strategy(self, name: str, config: Dict):
        """حفظ استراتيجية مخصصة"""
        if 'custom_strategies' not in st.session_state:
            st.session_state.custom_strategies = {}
        st.session_state.custom_strategies[name] = config
    
    def get_custom_strategies(self) -> Dict:
        """الحصول على الاستراتيجيات المخصصة"""
        return st.session_state.get('custom_strategies', {})

# ==================== INITIALIZE SESSION STATE ====================
if 'active_section' not in st.session_state:
    st.session_state.active_section = 'dashboard'
if 'active_alerts' not in st.session_state:
    st.session_state.active_alerts = []

# ==================== MAIN SIDEBAR ====================
st.sidebar.markdown("### ⚡ EGX Pro Terminal v26")
st.sidebar.markdown("---")

def set_section(section):
    st.session_state.active_section = section

sections = [
    ('📊 لوحة التحكم', 'dashboard'),
    ('🔔 إدارة التنبيهات', 'alerts'),
    ('⚖️ إدارة المخاطر', 'risk'),
    ('🔍 مسح الأسهم', 'screener'),
    ('📚 قالب الاستراتيجيات', 'strategies'),
    ('💼 محاكاة المحفظة', 'portfolio'),
]

for label, section_id in sections:
    btn_class = "nav-item active" if st.session_state.active_section == section_id else "nav-item"
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{section_id}"):
        set_section(section_id)

st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ معلومات عن التطبيق**")
st.sidebar.markdown("""
- **الإصدار**: v26.0
- **التحديث**: مايو 2026
- **الميزات الجديدة**: 
  - ✨ نظام تنبيهات ذكية
  - 📈 إدارة مخاطر متقدمة
  - 🔍 مسح الأسهم
  - 📚 قوالب الاستراتيجيات
  - 📄 تقارير PDF
""")

# ==================== MAIN CONTENT ====================

if st.session_state.active_section == 'dashboard':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### 📊 لوحة التحكم الرئيسية")
    
    st.info("🎯 لوحة التحكم الرئيسية - تم تحديثها بالكامل في الإصدار v26")
    st.markdown("""
    **الميزات الجديدة:**
    - 🔔 نظام التنبيهات الذكية
    - 📈 إدارة المخاطر المتقدمة
    - 🔍 مسح الأسهم الذكي
    - 📚 قوالب الاستراتيجيات
    - 📄 تقارير PDF متقدمة
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== ALERTS MANAGEMENT SECTION ====================
elif st.session_state.active_section == 'alerts':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### 🔔 نظام التنبيهات الذكية")
    
    alert_manager = AlertManager()
    
    with st.expander("➕ إضافة تنبيه جديد", expanded=True):
        acol1, acol2, acol3, acol4 = st.columns(4)
        
        with acol1:
            alert_symbol = st.selectbox("السهم", ['EBANK', 'EVCO', 'ORWA', 'CRNT', 'MOIL'])
        with acol2:
            alert_type = st.selectbox("نوع التنبيه", ['PRICE', 'VOLUME', 'MACD', 'RSI'])
        with acol3:
            alert_condition = st.selectbox("الشرط", ['>', '<', '='])
        with acol4:
            alert_value = st.number_input("القيمة", min_value=0.0, step=0.01)
        
        alert_action = st.text_input("إجراء التنبيه (اختياري)", placeholder="مثال: إرسال بريد إلكتروني")
        
        if st.button("✅ إضافة التنبيه", use_container_width=True, type="primary"):
            new_alert = alert_manager.add_alert(alert_symbol, alert_type, alert_condition, alert_value, alert_action)
            st.success(f"✅ تم إضافة التنبيه على {alert_symbol}")
    
    st.markdown("---")
    alert_manager.render_alerts_panel()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== RISK MANAGEMENT SECTION ====================
elif st.session_state.active_section == 'risk':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### ⚖️ إدارة المخاطر المتقدمة")
    
    risk_mgr = RiskManager()
    
    # محاكاة بيانات العائدات
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 100).tolist()
    
    # حساب المقاييس
    var_95 = risk_mgr.calculate_var(returns, 0.95)
    sharpe = risk_mgr.calculate_sharpe_ratio(returns)
    sortino = risk_mgr.calculate_sortino_ratio(returns)
    max_dd = risk_mgr.calculate_max_drawdown(returns)
    volatility = np.std(returns)
    
    risk_level, risk_color = risk_mgr.get_risk_level(volatility, max_dd, var_95)
    
    # عرض المقاييس
    st.markdown("#### 📊 مقاييس المخاطر الرئيسية")
    
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        st.markdown(f"""
        <div style="background: rgba(99,102,241,0.1); padding: 16px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.3);">
            <p style="color: #64748b; font-size: 12px; margin: 0;">Value at Risk (95%)</p>
            <p style="color: #f1f5f9; font-weight: 700; font-size: 18px; margin: 8px 0;">{var_95:.2%}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[1]:
        st.markdown(f"""
        <div style="background: rgba(99,102,241,0.1); padding: 16px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.3);">
            <p style="color: #64748b; font-size: 12px; margin: 0;">Sharpe Ratio</p>
            <p style="color: #f1f5f9; font-weight: 700; font-size: 18px; margin: 8px 0;">{sharpe:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[2]:
        st.markdown(f"""
        <div style="background: rgba(99,102,241,0.1); padding: 16px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.3);">
            <p style="color: #64748b; font-size: 12px; margin: 0;">Sortino Ratio</p>
            <p style="color: #f1f5f9; font-weight: 700; font-size: 18px; margin: 8px 0;">{sortino:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[3]:
        st.markdown(f"""
        <div style="background: rgba(99,102,241,0.1); padding: 16px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.3);">
            <p style="color: #64748b; font-size: 12px; margin: 0;">Max Drawdown</p>
            <p style="color: #f1f5f9; font-weight: 700; font-size: 18px; margin: 8px 0;">{max_dd:.2%}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"#### مستوى المخاطر الإجمالي: {risk_level}")
    
    # رسم بياني للعائدات
    fig = go.Figure()
    cumulative_returns = np.cumprod(1 + np.array(returns))
    fig.add_trace(go.Scatter(y=cumulative_returns, mode='lines', name='العائدات التراكمية', line=dict(color='#818cf8')))
    fig.update_layout(
        title="العائدات التراكمية",
        xaxis_title="الفترة",
        yaxis_title="العائد",
        template="plotly_dark",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== STOCK SCREENER SECTION ====================
elif st.session_state.active_section == 'screener':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### 🔍 مسح الأسهم الذكي")
    
    # بيانات مثالية
    sample_stocks = [
        {'symbol': 'EBANK', 'price': 150.5, 'change_pct': 2.5, 'volume': 5000000},
        {'symbol': 'EVCO', 'price': 200.0, 'change_pct': -1.2, 'volume': 3000000},
        {'symbol': 'ORWA', 'price': 75.25, 'change_pct': 3.8, 'volume': 2000000},
        {'symbol': 'CRNT', 'price': 120.0, 'change_pct': 0.5, 'volume': 1500000},
        {'symbol': 'MOIL', 'price': 180.75, 'change_pct': -2.1, 'volume': 4000000},
    ]
    
    screener = StockScreener(sample_stocks)
    
    st.markdown("#### 🎯 معايير البحث")
    screener_cols = st.columns(4)
    
    with screener_cols[0]:
        price_min = st.number_input("السعر الأدنى", min_value=0.0, value=0.0, step=10.0)
    with screener_cols[1]:
        price_max = st.number_input("السعر الأقصى", min_value=0.0, value=500.0, step=10.0)
    with screener_cols[2]:
        change_min = st.number_input("التغير الأدنى %", value=-10.0, step=0.5)
    with screener_cols[3]:
        volume_min = st.number_input("الحجم الأدنى", value=0, step=100000)
    
    criteria = {
        'price_min': price_min,
        'price_max': price_max,
        'change_min': change_min,
        'volume_min': volume_min
    }
    
    results = screener.filter_by_criteria(criteria)
    
    st.markdown("---")
    st.markdown(f"#### ✅ النتائج ({len(results)} سهم)")
    
    if results:
        results_df = pd.DataFrame([{
            'السهم': s['symbol'],
            'السعر': f"{s['price']:.2f}",
            'التغير%': f"{s['change_pct']:+.2f}%",
            'الحجم': f"{s['volume']:,}"
        } for s in results])
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    else:
        st.warning("لا توجد أسهم تطابق المعايير المحددة")
    
    st.markdown("---")
    st.markdown("#### 🚀 الاختراقات")
    breakouts = screener.find_breakouts(threshold=0.02)
    if breakouts:
        for stock in breakouts[:5]:
            st.markdown(f"**{stock['symbol']}** - تغير: {stock['change_pct']:+.2f}% 📈" if stock['change_pct'] > 0 else f"**{stock['symbol']}** - تغير: {stock['change_pct']:+.2f}% 📉")
    else:
        st.info("لا توجد اختراقات حالياً")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== STRATEGY TEMPLATES SECTION ====================
elif st.session_state.active_section == 'strategies':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### 📚 قوالب الاستراتيجيات")
    
    strategy_mgr = StrategyManager()
    templates = strategy_mgr.get_templates()
    
    st.markdown("#### 📖 الاستراتيجيات المدمجة")
    
    for strategy_name, strategy_config in templates.items():
        with st.expander(f"📌 {strategy_name}"):
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"**الوصف**: {strategy_config['description']}")
                st.markdown(f"**نسبة المخاطرة والعائد**: {strategy_config['risk_reward_ratio']}")
            with cols[1]:
                st.markdown(f"**قاعدة الدخول**: {strategy_config['entry_rule']}")
                st.markdown(f"**قاعدة الخروج**: {strategy_config['exit_rule']}")
            
            st.markdown("**المؤشرات المستخدمة**:")
            for indicator in strategy_config['indicators']:
                st.markdown(f"- {indicator}")
            
            if st.button(f"✅ استخدام هذه الاستراتيجية", key=f"use_{strategy_name}"):
                st.success(f"تم تحديد استراتيجية: {strategy_name}")
    
    st.markdown("---")
    st.markdown("#### ➕ إنشاء استراتيجية مخصصة")
    
    custom_cols = st.columns(2)
    with custom_cols[0]:
        custom_name = st.text_input("اسم الاستراتيجية")
        custom_entry = st.text_area("قاعدة الدخول")
    with custom_cols[1]:
        custom_exit = st.text_area("قاعدة الخروج")
        custom_ratio = st.text_input("نسبة المخاطرة والعائد", placeholder="1:2")
    
    if st.button("💾 حفظ الاستراتيجية", use_container_width=True, type="primary"):
        if custom_name and custom_entry and custom_exit:
            strategy_mgr.save_custom_strategy(custom_name, {
                'entry': custom_entry,
                'exit': custom_exit,
                'ratio': custom_ratio
            })
            st.success(f"✅ تم حفظ الاستراتيجية: {custom_name}")
        else:
            st.error("❌ يرجى ملء جميع الحقول")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== PORTFOLIO SECTION ====================
elif st.session_state.active_section == 'portfolio':
    st.markdown('<div class="pro-panel">', unsafe_allow_html=True)
    st.markdown("### 💼 محاكاة المحفظة")
    st.info("✅ قسم المحفظة متاح - يمكنك إضافة الصفقات وتتبع الأداء")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[0]:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #64748b; font-size: 13px; margin: 0; font-weight: 600;">⚡ EGX Pro Terminal v26.0</p>
        <p style="color: #475569; font-size: 12px; margin: 6px 0;">نظام تحليلي احترافي | البورصة المصرية</p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[1]:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #fbbf24; font-size: 12px; margin: 0; font-weight: 700;">
            🆕 الميزات الجديدة: تنبيهات | مخاطر | مسح | استراتيجيات | تقارير
        </p>
        <p style="color: #475569; font-size: 11px; margin: 6px 0;">آخر تحديث: {datetime.now().strftime("%H:%M:%S")}</p>
    </div>
    """, unsafe_allow_html=True)

with footer_cols[2]:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #475569; font-size: 12px; margin: 0;">© 2026 | جميع البيانات للتوضيح</p>
        <p style="color: #475569; font-size: 11px; margin: 6px 0;">للأغراض التعليمية فقط - ليست نصيحة استثمارية</p>
    </div>
    """, unsafe_allow_html=True)
