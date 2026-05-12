"""
محلل الأسهم المتقدم - تطبيق Streamlit
Advanced Stock Analyzer - Streamlit App
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Tuple
import logging

# ============================================================
# الإعدادات والتسجيل (Logging)
# ============================================================

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إعدادات Streamlit
st.set_page_config(
    page_title="محلل الأسهم المتقدم",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# دالات المساعدة (Helper Functions)
# ============================================================

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    جلب بيانات السهم من Yahoo Finance مع معالجة الأخطاء
    
    Args:
        ticker: رمز السهم (مثل AAPL, MSFT)
        start_date: تاريخ البداية (YYYY-MM-DD)
        end_date: تاريخ النهاية (YYYY-MM-DD)
    
    Returns:
        DataFrame يحتوي على البيانات أو None في حالة الخطأ
    """
    try:
        logger.info(f"جاري جلب البيانات للسهم: {ticker}")
        
        # التحقق من صحة المدخلات
        if not ticker or len(ticker.strip()) == 0:
            logger.error("رمز السهم فارغ")
            return None
        
        # جلب البيانات
        data = yf.download(
            ticker.upper(),
            start=start_date,
            end=end_date,
            progress=False  # تعطيل شريط التقدم في Streamlit
        )
        
        # التحقق من أن البيانات غير فارغة
        if data.empty:
            logger.error(f"لم يتم العثور على بيانات للسهم: {ticker}")
            return None
        
        logger.info(f"تم جلب {len(data)} صف من البيانات")
        
        # تنظيف البيانات
        data = data.dropna()
        
        if data.empty:
            logger.error("البيانات فارغة بعد التنظيف")
            return None
        
        return data
    
    except Exception as e:
        logger.error(f"خطأ في جلب البيانات: {str(e)}")
        return None


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    حساب المؤشرات الفنية
    """
    try:
        df = data.copy()
        
        # المتوسطات المتحركة
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # مؤشر القوة النسبية (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal']
        
        # Bollinger Bands
        bb_middle = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = bb_middle + (bb_std * 2)
        df['BB_Lower'] = bb_middle - (bb_std * 2)
        
        return df.dropna()
    
    except Exception as e:
        logger.error(f"خطأ في حساب المؤشرات: {str(e)}")
        return data


def get_stock_info(ticker: str) -> dict:
    """الحصول على معلومات السهم الأساسية"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
        }
    except Exception as e:
        logger.error(f"خطأ في جلب معلومات السهم: {str(e)}")
        return {}


# ============================================================
# واجهة المستخدم (UI)
# ============================================================

# الرأس
st.markdown("""
<h1 style='text-align: center; color: #1F4E78;'>
    📊 محلل الأسهم المتقدم
</h1>
<p style='text-align: center; color: #666;'>
    منصة تحليل أسهم احترافية مع مؤشرات فنية متقدمة
</p>
""", unsafe_allow_html=True)

st.divider()

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    # إدخال رمز السهم
    ticker = st.text_input(
        "رمز السهم",
        value="AAPL",
        placeholder="أدخل رمز السهم (مثل AAPL, MSFT)",
        help="رمز السهم من Yahoo Finance"
    ).upper()
    
    # اختيار نطاق التاريخ
    col1, col2 = st.columns(2)
    with col1:
        days_back = st.slider(
            "عدد الأيام",
            min_value=30,
            max_value=730,
            value=180,
            help="عدد الأيام التاريخية للتحليل"
        )
    
    # التواريخ
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    st.write(f"📅 من: {start_date.strftime('%Y-%m-%d')}")
    st.write(f"📅 إلى: {end_date.strftime('%Y-%m-%d')}")

# ============================================================
# المحتوى الرئيسي
# ============================================================

# رسالة اختبار
st.info("✅ إذا رأيت هذه الرسالة، فالتطبيق يعمل برمجياً!")

# جلب البيانات
with st.spinner(f"⏳ جاري جلب بيانات السهم {ticker}..."):
    data = fetch_stock_data(
        ticker,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

# التحقق من البيانات
if data is None or data.empty:
    st.error(f"""
    ❌ فشل في تحميل البيانات
    
    **الأسباب المحتملة:**
    1. رمز السهم غير صحيح: {ticker}
    2. لا توجد اتصال بالإنترنت
    3. Yahoo Finance غير متاح حالياً
    4. النطاق الزمني غير صحيح
    
    **الحل:**
    - تأكد من رمز السهم (مثل AAPL, MSFT, GOOGL)
    - تحقق من اتصال الإنترنت
    - جرب سهم آخر
    """)
    st.stop()

# معلومات السهم
st.subheader(f"📈 معلومات {ticker}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("السعر الحالي", f"${data['Close'].iloc[-1]:.2f}")

with col2:
    change = data['Close'].iloc[-1] - data['Close'].iloc[0]
    change_percent = (change / data['Close'].iloc[0]) * 100
    st.metric("التغير", f"${change:.2f}", f"{change_percent:.2f}%")

with col3:
    st.metric("أعلى سعر", f"${data['High'].max():.2f}")

with col4:
    st.metric("أقل سعر", f"${data['Low'].min():.2f}")

st.divider()

# حساب المؤشرات
st.subheader("📊 حساب المؤشرات الفنية")

with st.spinner("⏳ جاري حساب المؤشرات الفنية..."):
    data_with_indicators = calculate_technical_indicators(data)

if data_with_indicators.empty:
    st.error("❌ فشل في حساب المؤشرات الفنية")
    st.stop()

st.success("✅ تم حساب المؤشرات بنجاح")

st.divider()

# الرسوم البيانية
st.subheader("📉 الرسوم البيانية")

# رسم السعر والمتوسطات المتحركة
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=data_with_indicators.index,
    y=data_with_indicators['Close'],
    name='سعر الإغلاق',
    mode='lines'
))

fig1.add_trace(go.Scatter(
    x=data_with_indicators.index,
    y=data_with_indicators['SMA_20'],
    name='SMA 20',
    mode='lines'
))

fig1.add_trace(go.Scatter(
    x=data_with_indicators.index,
    y=data_with_indicators['SMA_50'],
    name='SMA 50',
    mode='lines'
))

fig1.update_layout(
    title=f"{ticker} - السعر والمتوسطات المتحركة",
    xaxis_title="التاريخ",
    yaxis_title="السعر ($)",
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig1, use_container_width=True)

# رسم RSI
col1, col2 = st.columns(2)

with col1:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=data_with_indicators.index,
        y=data_with_indicators['RSI'],
        name='RSI',
        fill='tozeroy'
    ))
    fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig2.update_layout(
        title="مؤشر القوة النسبية (RSI)",
        xaxis_title="التاريخ",
        yaxis_title="RSI",
        height=350
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=data_with_indicators.index,
        y=data_with_indicators['MACD'],
        name='MACD',
        mode='lines'
    ))
    fig3.add_trace(go.Scatter(
        x=data_with_indicators.index,
        y=data_with_indicators['Signal'],
        name='Signal',
        mode='lines'
    ))
    fig3.add_trace(go.Bar(
        x=data_with_indicators.index,
        y=data_with_indicators['MACD_Histogram'],
        name='Histogram'
    ))
    fig3.update_layout(
        title="مؤشر MACD",
        xaxis_title="التاريخ",
        yaxis_title="القيمة",
        height=350
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# جدول البيانات
st.subheader("📋 جدول البيانات")

# عرض آخر 10 صفوف
display_columns = [
    'Close', 'Volume', 'SMA_20', 'SMA_50', 'RSI', 'MACD'
]

# تصفية الأعمدة الموجودة
display_columns = [col for col in display_columns if col in data_with_indicators.columns]

st.dataframe(
    data_with_indicators[display_columns].tail(10),
    use_container_width=True
)

st.divider()

# زر التحميل
if st.button("📥 تحميل البيانات كـ CSV"):
    csv = data_with_indicators.to_csv()
    st.download_button(
        label="اضغط للتحميل",
        data=csv,
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )

# التذييل
st.markdown("""
---
<p style='text-align: center; color: #999; font-size: 12px;'>
    محلل الأسهم المتقدم | جميع الحقوق محفوظة © 2025
</p>
""", unsafe_allow_html=True)
