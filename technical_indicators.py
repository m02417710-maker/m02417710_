import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ============================================================
# 1. مكتبة المؤشرات الفنية (Logic)
# ============================================================
class TechnicalIndicators:
    def __init__(self, historical_data: pd.DataFrame):
        self.data = historical_data.copy()
        # تنظيف البيانات لضمان عدم وجود قيم فارغة تؤدي لتوقف التطبيق
        self.data = self.data.sort_values('Date').reset_index(drop=True)
        self.indicators = {}

    def calculate_sma(self, period: int = 20):
        sma = self.data['Close'].rolling(window=period).mean()
        self.indicators[f'SMA_{period}'] = sma
        return sma

    def calculate_rsi(self, period: int = 14):
        delta = self.data['Close'].diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        self.indicators['RSI'] = rsi
        return rsi

    def calculate_macd(self, fast=12, slow=26, signal=9):
        ema_fast = self.data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.data['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        self.indicators['MACD'] = macd_line
        self.indicators['MACD_Signal'] = signal_line
        return macd_line, signal_line

    def generate_signals(self):
        signals = {'strength': 0, 'recommendation': 'HOLD', 'confidence': 50, 'details': []}
        
        if 'RSI' in self.indicators:
            last_rsi = self.indicators['RSI'].iloc[-1]
            if last_rsi < 35:
                signals['strength'] += 2
                signals['details'].append("RSI: تشبع بيعي (فرصة شراء)")
            elif last_rsi > 65:
                signals['strength'] -= 2
                signals['details'].append("RSI: تشبع شرائي (فرصة بيع)")

        if 'MACD' in self.indicators:
            if self.indicators['MACD'].iloc[-1] > self.indicators['MACD_Signal'].iloc[-1]:
                signals['strength'] += 1
                signals['details'].append("MACD: اتجاه صاعد")
            else:
                signals['strength'] -= 1
                signals['details'].append("MACD: اتجاه هابط")

        if signals['strength'] >= 2: signals['recommendation'] = "BUY"
        elif signals['strength'] <= -2: signals['recommendation'] = "SELL"
        
        signals['confidence'] = min(100, 50 + abs(signals['strength'] * 15))
        return signals

# ============================================================
# 2. واجهة التطبيق (Streamlit Interface)
# ============================================================
st.set_page_config(page_title="محلل الأسهم الذكي", layout="wide")

# تنسيق CSS بسيط لتحسين المظهر
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 محلل الأسهم المتقدم - المؤشرات الفنية")
st.sidebar.header("إعدادات البحث")

# مدخلات المستخدم
ticker = st.sidebar.text_input("رمز السهم (مثلاً AAPL أو 2222.SR):", value="AAPL")
time_period = st.sidebar.selectbox("الفترة الزمنية:", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

if st.sidebar.button("تحليل الآن"):
    try:
        with st.spinner('جاري جلب البيانات من Yahoo Finance...'):
            data = yf.download(ticker, period=time_period)
            
        if data.empty:
            st.error("لم يتم العثور على بيانات. تأكد من رمز السهم.")
        else:
            df = data.reset_index()
            # استدعاء الكلاس الخاص بك
            analyzer = TechnicalIndicators(df)
            analyzer.calculate_sma(20)
            analyzer.calculate_sma(50)
            analyzer.calculate_rsi()
            analyzer.calculate_macd()
            
            signals = analyzer.generate_signals()

            # --- عرض النتائج ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("السعر الحالي", f"{df['Close'].iloc[-1]:.2f}")
            with col2:
                color = "green" if signals['recommendation'] == "BUY" else "red" if signals['recommendation'] == "SELL" else "orange"
                st.markdown(f"### التوصية: :{color}[{signals['recommendation']}]")
            with col3:
                st.metric("درجة الثقة", f"{signals['confidence']}%")

            # الرسوم البيانية
            st.subheader("📈 حركة السعر والمؤشرات")
            chart_data = pd.DataFrame({
                'السعر': df['Close'],
                'SMA 20': analyzer.indicators['SMA_20']
            }, index=df['Date'])
            st.line_chart(chart_data)

            # تفاصيل الإشارات
            with st.expander("🔍 تفاصيل التحليل الفني"):
                for detail in signals['details']:
                    st.write(f"- {detail}")
                st.write(f"RSI الحالي: {analyzer.indicators['RSI'].iloc[-1]:.2f}")

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("أدخل رمز السهم في القائمة الجانبية واضغط على 'تحليل الآن' للبدء.")

