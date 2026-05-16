"""
EGX Pro Terminal v26 - Main Application
Professional Technical Analysis Platform for Egyptian Stock Exchange
Fixed for Streamlit Cloud deployment with comprehensive error handling
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# ============================================
# FIX: Ensure the app directory is in Python path
# ============================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Also add parent if needed (for Streamlit Cloud subfolder deployments)
PARENT_DIR = os.path.dirname(APP_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# Now import project modules
from config.settings import *
from data.egx_symbols import get_all_symbols, get_stock_info, search_stocks
from core.analysis import EGXAnalyzer
from core.alerts import AlertEngine, SignalType

# Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} {APP_VERSION}",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .bullish {
        color: #26a69a;
        font-weight: bold;
    }
    .bearish {
        color: #ef5350;
        font-weight: bold;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #ef5350;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 4px solid #66bb6a;
        padding: 10px;
        margin: 5px 0;
    }
    .error-card {
        background-color: #ffebee;
        border: 1px solid #ef5350;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .warning-card {
        background-color: #fff8e1;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown(f"<h1 style='text-align: center;'>{APP_NAME}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; color: gray;'>{APP_VERSION}</p>", unsafe_allow_html=True)
st.sidebar.divider()

# Navigation
page = st.sidebar.radio(
    "القائمة الرئيسية / Main Menu",
    ["🏠 الرئيسية", "📊 تحليل السهم", "📋 قائمة المتابعة", "🔔 التنبيهات", "ℹ️ عن التطبيق"]
)

# Initialize session state
if 'alert_engine' not in st.session_state:
    st.session_state.alert_engine = AlertEngine()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["COMI", "TMGH", "ETEL", "ESRS"]

# Load symbols
all_symbols = get_all_symbols()

# ============================================
# HELPER FUNCTIONS FOR SAFE DATA HANDLING
# ============================================

def safe_fetch_data(analyzer, symbol):
    """Safely fetch data with comprehensive error handling"""
    try:
        analyzer.fetch_data()

        # Check if data is empty
        if analyzer.data is None or analyzer.data.empty:
            return False, f"لا توجد بيانات متاحة للرمز {symbol}. قد يكون الرمز غير صحيح أو البيانات غير متوفرة من Yahoo Finance."

        # Check for required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [c for c in required_cols if c not in analyzer.data.columns]
        if missing_cols:
            return False, f"أعمدة مفقودة في البيانات: {missing_cols}. الأعمدة المتاحة: {list(analyzer.data.columns)}"

        # Check for valid Close prices
        close_data = analyzer.data['Close'].dropna()
        if len(close_data) == 0:
            return False, f"جميع بيانات الإغلاق فارغة (NaN) للرمز {symbol}"

        # Check minimum data points
        if len(analyzer.data) < 20:
            return False, f"عدد البيانات قليل جداً ({len(analyzer.data)} صف). يجب أن يكون على الأقل 20 صفاً لحساب المؤشرات."

        return True, None

    except Exception as e:
        error_msg = str(e)
        if "No data found" in error_msg:
            return False, f"لم يتم العثور على بيانات للرمز {symbol}. تأكد من صحة الرمز أو حاول لاحقاً."
        elif "Connection" in error_msg or "Timeout" in error_msg:
            return False, f"مشكلة في الاتصال بـ Yahoo Finance. تحقق من اتصالك بالإنترنت."
        else:
            return False, f"خطأ في جلب البيانات: {error_msg}"


def safe_get_last_price(data):
    """Safely get the last closing price"""
    try:
        if data is None or data.empty:
            return None, "البيانات فارغة"

        if 'Close' not in data.columns:
            return None, f"عمود الإغلاق غير موجود. الأعمدة المتاحة: {list(data.columns)}"

        close_series = data['Close'].dropna()
        if len(close_series) == 0:
            return None, "لا توجد قيم إغلاق صالحة"

        last_price = close_series.iloc[-1]
        prev_price = close_series.iloc[-2] if len(close_series) > 1 else last_price

        return {
            'last': last_price,
            'prev': prev_price,
            'change': ((last_price - prev_price) / prev_price * 100) if prev_price != 0 else 0
        }, None

    except Exception as e:
        return None, f"خطأ في قراءة السعر: {str(e)}"


def display_error_card(title, message, suggestion=""):
    """Display a styled error card"""
    st.markdown(f"""
    <div class="error-card">
        <h3>❌ {title}</h3>
        <p>{message}</p>
        {f"<p style='color: gray; margin-top: 10px;'>💡 {suggestion}</p>" if suggestion else ""}
    </div>
    """, unsafe_allow_html=True)


def display_warning_card(message):
    """Display a styled warning card"""
    st.markdown(f"""
    <div class="warning-card">
        <p>⚠️ {message}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# HOME PAGE
# ============================================
if page == "🏠 الرئيسية":
    st.markdown("<h1 class='main-header'>📈 EGX Pro Terminal</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>منصة تحليل فني احترافية للبورصة المصرية</h3>", unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 عدد الأسهم المتاحة", len(all_symbols))
    with col2:
        st.metric("🔔 عدد التنبيهات النشطة", len(st.session_state.alert_engine.get_recent_alerts(24)))
    with col3:
        st.metric("📈 مؤشر EGX30", "قيد التطوير")

    st.divider()

    st.subheader("🚀 نظرة سريعة على السوق")
    st.info("جاري جلب بيانات الأسهم الرئيسية من Yahoo Finance...")

    # Quick analysis of top stocks
    top_stocks = ["COMI", "TMGH", "ETEL", "ESRS", "JUHO"]
    cols = st.columns(len(top_stocks))

    for i, symbol in enumerate(top_stocks):
        with cols[i]:
            try:
                analyzer = EGXAnalyzer(symbol, period="5d")
                success, error_msg = safe_fetch_data(analyzer, symbol)

                if not success:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{get_stock_info(symbol)['name_ar']}</h4>
                        <h3>{symbol}</h3>
                        <p style="color: gray;">⚠️ {error_msg[:50]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    continue

                price_info, price_error = safe_get_last_price(analyzer.data)

                if price_error:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{get_stock_info(symbol)['name_ar']}</h4>
                        <h3>{symbol}</h3>
                        <p style="color: gray;">⚠️ {price_error}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    continue

                info = get_stock_info(symbol)
                color = "bullish" if price_info['change'] >= 0 else "bearish"
                arrow = "▲" if price_info['change'] >= 0 else "▼"

                st.markdown(f"""
                <div class="metric-card">
                    <h4>{info['name_ar']}</h4>
                    <h3>{symbol}</h3>
                    <p style="font-size: 1.2rem;">{price_info['last']:.2f} EGP</p>
                    <p class="{color}">{arrow} {abs(price_info['change']):.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"خطأ في عرض {symbol}: {str(e)}")

# ============================================
# STOCK ANALYSIS PAGE
# ============================================
elif page == "📊 تحليل السهم":
    st.header("📊 تحليل السهم الفني")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input("ابحث عن سهم (بالاسم/الرمز):", placeholder="مثال: البنك التجاري أو COMI")

        if search_query:
            results = search_stocks(search_query)
            if results:
                selected = st.selectbox("اختر السهم:", [f"{s} - {i['name_ar']}" for s, i in results])
                symbol = selected.split(" - ")[0]
            else:
                display_warning_card("لم يتم العثور على نتائج. جرب اسم أو رمز آخر.")
                symbol = None
        else:
            symbol = st.selectbox("اختر السهم من القائمة:", all_symbols, format_func=lambda x: f"{x} - {get_stock_info(x)['name_ar']}")

    with col2:
        period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        interval = st.selectbox("الفاصل الزمني", ["1d", "1wk", "1mo"], index=0)

    if symbol and st.button("🚀 تحليل السهم", type="primary"):
        with st.spinner("جاري جلب البيانات وتحليل المؤشرات الفنية..."):
            try:
                analyzer = EGXAnalyzer(symbol, period=period, interval=interval)
                success, error_msg = safe_fetch_data(analyzer, symbol)

                if not success:
                    display_error_card(
                        "فشل في جلب البيانات",
                        error_msg,
                        "تأكد من صحة رمز السهم أو حاول فترة زمنية أخرى."
                    )
                    st.stop()

                analyzer.calculate_all_indicators()

                info = get_stock_info(symbol)
                summary = analyzer.get_summary()
                trend = analyzer.get_trend_analysis()

                # Header Info
                st.subheader(f"{info['name_ar']} ({symbol})")
                st.caption(f"القطاع: {info['sector']} | آخر تحديث: {summary['date']}")

                # Price Info with SAFE handling
                price_info, price_error = safe_get_last_price(analyzer.data)

                if price_error:
                    display_warning_card(f"⚠️ {price_error}")
                    st.stop()

                # Metrics Row
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1:
                    delta_color = "normal" if price_info['change'] >= 0 else "inverse"
                    st.metric("السعر الحالي", f"{price_info['last']:.2f} EGP", f"{price_info['change']:+.2f}%", delta_color=delta_color)
                with m2:
                    st.metric("حجم التداول", f"{summary['volume']:,}")
                with m3:
                    st.metric("RSI", f"{summary['rsi']:.1f}")
                with m4:
                    st.metric("ADX", f"{summary['adx']:.1f}")
                with m5:
                    st.metric("ATR", f"{summary['atr']:.2f}")

                st.divider()

                # Main Chart
                fig = make_subplots(
                    rows=3, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.6, 0.2, 0.2],
                    subplot_titles=(f"{symbol} - Price Action", "Volume", "RSI / MACD")
                )

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=analyzer.data.index,
                    open=analyzer.data['Open'],
                    high=analyzer.data['High'],
                    low=analyzer.data['Low'],
                    close=analyzer.data['Close'],
                    name="Price",
                    increasing_line_color=THEME_BULLISH,
                    decreasing_line_color=THEME_BEARISH
                ), row=1, col=1)

                # EMAs
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_9'],  
                                           name="EMA 9", line=dict(color="yellow", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_20'],  
                                           name="EMA 20", line=dict(color="orange", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_50'], 
                                           name="EMA 50", line=dict(color="blue", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['EMA_200'], 
                                           name="EMA 200", line=dict(color="red", width=2)), row=1, col=1)

                # Bollinger Bands
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['BB_Upper'], 
                                           name="BB Upper", line=dict(color="gray", width=0.5, dash="dash")), row=1, col=1)
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['BB_Lower'], 
                                           name="BB Lower", line=dict(color="gray", width=0.5, dash="dash")), row=1, col=1)

                # Volume
                colors = [THEME_BULLISH if c >= o else THEME_BEARISH 
                          for c, o in zip(analyzer.data['Close'], analyzer.data['Open'])]
                fig.add_trace(go.Bar(x=analyzer.data.index, y=analyzer.data['Volume'], 
                                     name="Volume", marker_color=colors), row=2, col=1)

                # RSI
                fig.add_trace(go.Scatter(x=analyzer.data.index, y=analyzer.indicators['RSI'], 
                                         name="RSI", line=dict(color="purple", width=1.5)), row=3, col=1)
                fig.add_hline(y=RSI_OVERBOUGHT, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=RSI_OVERSOLD, line_dash="dash", line_color="green", row=3, col=1)

                fig.update_layout(
                    height=CHART_HEIGHT,
                    showlegend=True,
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    title_text=f"Technical Analysis - {info['name_ar']}",
                    hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Trend Analysis
                st.subheader("📊 تحليل الاتجاه")
                trend_col1, trend_col2 = st.columns(2)

                with trend_col1:
                    st.markdown(f"**الاتجاه:** {trend['direction']}")
                    st.markdown(f"**القوة:** {trend['strength']}")
                    st.markdown(f"**النقاط:** {trend['score']}")

                with trend_col2:
                    for signal in trend['signals']:
                        st.markdown(f"- {signal}")

                # Support/Resistance
                levels = summary['levels']
                st.subheader("🎯 مستويات الدعم والمقاومة")
                l1, l2, l3 = st.columns(3)
                with l1:
                    st.metric("الدعم", f"{levels['support']:.2f}")
                with l2:
                    st.metric("المحور", f"{levels['pivot']:.2f}")
                with l3:
                    st.metric("المقاومة", f"{levels['resistance']:.2f}")

                st.caption(f"نطاق التداول: {levels['range_pct']:.2f}%")

                # Add to Watchlist
                if st.button("➕ إضافة إلى قائمة المتابعة"):
                    if symbol not in st.session_state.watchlist:
                        st.session_state.watchlist.append(symbol)
                    st.success(f"تمت إضافة {symbol} إلى قائمة المتابعة!")

            except Exception as e:
                display_error_card(
                    "خطأ غير متوقع",
                    str(e),
                    "يرجى التحقق من الاتصال بالإنترنت أو المحاولة لاحقاً."
                )

# ============================================
# WATCHLIST PAGE
# ============================================
elif page == "📋 قائمة المتابعة":
    st.header("📋 قائمة المتابعة")

    if not st.session_state.watchlist:
        st.info("قائمة المتابعة فارغة. أضف أسهماً من صفحة التحليل.")
    else:
        for symbol in st.session_state.watchlist:
            try:
                analyzer = EGXAnalyzer(symbol, period="1mo")
                success, error_msg = safe_fetch_data(analyzer, symbol)

                if not success:
                    st.warning(f"⚠️ {symbol}: {error_msg}")
                    continue

                analyzer.calculate_all_indicators()
                summary = analyzer.get_summary()
                info = get_stock_info(symbol)

                change_color = "bullish" if summary['change_pct'] >= 0 else "bearish"

                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{info['name_ar']}** ({symbol})")
                    with col2:
                        st.markdown(f"<span class='{change_color}'>{summary['price']:.2f} ({summary['change_pct']:+.2f}%)</span>", 
                                   unsafe_allow_html=True)
                    with col3:
                        st.caption(f"RSI: {summary['rsi']:.1f}")
                    with col4:
                        st.caption(f"ADX: {summary['adx']:.1f}")
                    with col5:
                        if st.button("🗑️", key=f"remove_{symbol}"):
                            st.session_state.watchlist.remove(symbol)
                            st.rerun()
                    st.divider()
            except Exception as e:
                st.warning(f"⚠️ خطأ في عرض {symbol}: {str(e)}")

# ============================================
# ALERTS PAGE
# ============================================
elif page == "🔔 التنبيهات":
    st.header("🔔 نظام التنبيهات الذكي")

    alert_engine = st.session_state.alert_engine

    # Update alerts for watchlist
    if st.button("🔄 تحديث التنبيهات", type="primary"):
        with st.spinner("جاري فحص الأسهم والبحث عن إشارات..."):
            for symbol in st.session_state.watchlist:
                alert_engine.add_to_watchlist(symbol)
            results = alert_engine.scan_watchlist()

            total = sum(len(v) for v in results.values())
            st.success(f"تم فحص {len(st.session_state.watchlist)} سهم وتم العثور على {total} إشارة!")

    # Display alerts
    recent = alert_engine.get_recent_alerts(24)

    if recent:
        st.subheader(f"التنبيهات الأخيرة ({len(recent)})")

        for alert in sorted(recent, key=lambda x: x.priority.value, reverse=True):
            priority_class = "alert-high" if "عالية" in alert.priority.value else "alert-medium" if "متوسطة" in alert.priority.value else "alert-low"

            with st.container():
                st.markdown(f"""
                <div class="{priority_class}">
                      <strong>{alert.symbol}</strong> - {alert.signal.value} | {alert.priority.value}<br>
                    <small>{alert.timestamp} | السعر: {alert.price:.2f}</small><br>
                    {alert.message}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("لا توجد تنبيهات حالياً. أضف أسهماً إلى قائمة المتابعة واضغط تحديث.")

    # Summary
    summary = alert_engine.get_alert_summary()
    if summary['total'] > 0:
        st.divider()
        st.subheader("📊 ملخص التنبيهات")
        c1, c2 = st.columns(2)
        with c1:
            st.json(summary['by_signal'])
        with c2:
            st.json(summary['by_priority'])

# ============================================
# ABOUT PAGE
# ============================================
elif page == "ℹ️ عن التطبيق":
    st.header("ℹ️ عن التطبيق")

    st.markdown(f"""
    ### {APP_NAME} {APP_VERSION}

    **EGX Pro Terminal** هو منصة تحليل فني احترافية للبورصة المصرية، 
    تتيح للمستثمرين والمحللين متابعة الأسهم وتحليل المؤشرات الفنية بسهولة.

    #### المميزات:
    - تحليل فني شامل لأكثر من 100 سهم مصري
    - مؤشرات فنية متقدمة (RSI, MACD, Bollinger Bands, EMA)
    - نظام تنبيهات ذكي
    - رسم بياني تفاعلي
    - دعم كامل للغة العربية

    #### التقنيات المستخدمة:
    - Python 3.10+
    - Streamlit
    - Plotly
    - TA-Lib (Technical Analysis)
    - Yahoo Finance API

    #### تحذير:
    > **هذا التطبيق للأغراض التعليمية فقط. لا يُعتبر توصية استثمارية.**
    > **جميع البيانات من Yahoo Finance وقد تكون متأخرة أو غير دقيقة.**

    ---
    **المطور:** {APP_AUTHOR}  
    **الترخيص:** MIT License  
    **آخر تحديث:** 2026
    """)

# Footer
st.sidebar.divider()
st.sidebar.caption(f"© 2026 {APP_NAME} | MIT License")
st.sidebar.caption("البيانات من Yahoo Finance - للأغراض التعليمية فقط")
