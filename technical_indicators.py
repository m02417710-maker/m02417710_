import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة والتحديث التلقائي (كل 5 دقائق)
st.set_page_config(page_title="المنصة المتكاملة للمستثمر", layout="wide")
# تحديث تلقائي للصفحة بالكامل لضمان تحديث الأسعار والمؤشرات
st_autorefresh(interval=300 * 1000, key="global_update")

# ============================================================
# 2. فئة المحرك الفني (المؤشرات + التوقعات)
# ============================================================
class StockEngine:
    def __init__(self, data):
        self.df = data.copy()
        # التعامل مع هيكل البيانات من ياهو فاينانس (إزالة الـ MultiIndex إن وجد)
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = self.df.columns.get_level_values(0)
        self.df = self.df.sort_values('Date').reset_index(drop=True)

    def get_indicators(self):
        # حساب مؤشر القوة النسبية (RSI)
        delta = self.df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        # حساب مؤشر الماكد (MACD)
        exp1 = self.df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['Close'].ewm(span=26, adjust=False).mean()
        self.df['MACD'] = exp1 - exp2
        self.df['Signal'] = self.df['MACD'].ewm(span=9, adjust=False).mean()
        return self.df

    def predict_price(self, days=7):
        """توقع السعر القادم باستخدام الانحدار الخطي"""
        model_df = self.df.dropna(subset=['Close'])
        X = np.arange(len(model_df)).reshape(-1, 1)
        y = model_df['Close'].values
        model = LinearRegression().fit(X, y)
        
        future_X = np.array([len(model_df) + i for i in range(days)]).reshape(-1, 1)
        return model.predict(future_X)

# ============================================================
# 3. واجهة المستخدم الرسومية (Streamlit Dashboard)
# ============================================================

st.title("🛡️ منصة التحليل المتقدم وإدارة المخاطر")

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.header("⚙️ الإعدادات والتحكم")
ticker = st.sidebar.text_input("رمز السهم:", value="NVDA")
capital = st.sidebar.number_input("رأس المال المستثمر ($):", value=10000)
stop_loss = st.sidebar.number_input("سعر وقف الخسارة ($):", value=0.0)

st.sidebar.divider()
st.sidebar.info("📢 إشعارات التليجرام: مفعلة (محاكاة)")

# --- جلب البيانات والتحليل ---
try:
    # جلب بيانات سنة كاملة للتحليل الدقيق
    raw_data = yf.download(ticker, period="1y", interval="1d").reset_index()
    
    if not raw_data.empty:
        engine = StockEngine(raw_data)
        df_full = engine.get_indicators()
        current_price = df_full['Close'].iloc[-1]
        
        # 1. الرسوم البيانية التفاعلية (الشموع اليابانية) باستخدام Plotly
        st.subheader(f"📊 مخطط الشموع اليابانية التفاعلي - {ticker}")
        fig = go.Figure(data=[go.Candlestick(
            x=df_full['Date'], 
            open=df_full['Open'],
            high=df_full['High'], 
            low=df_full['Low'],
            close=df_full['Close'], 
            name="الشموع اليابانية"
        )])
        
        # تحسين المظهر: القالب الداكن وإخفاء منزلق النطاق الزمني لتبسيط الرؤية
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        
        # تم تصحيح المعامل هنا من use_container_view إلى use_container_width
        st.plotly_chart(fig, use_container_width=True)

        # 2. التوقعات وإدارة المخاطر (تقسيم الأعمدة)
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.header("🔮 توقعات AI")
            preds = engine.predict_price(7)
            target = preds[-1]
            # ميزة العائد على 100 سهم
            gain_100 = (target - current_price) * 100
            st.metric("السعر المستهدف (بعد 7 أيام)", f"{target:.2f}")
            st.metric("الربح المتوقع لـ 100 سهم", f"${gain_100:.2f}", f"{((target/current_price)-1)*100:.2f}%")

        with col2:
            st.header("⚖️ إدارة المخاطر")
            if stop_loss > 0:
                risk_per_share = current_price - stop_loss
                # قاعدة إدارة المخاطر: لا تخاطر بأكثر من 2% من رأس مالك
                if risk_per_share > 0:
                    position_size = int((capital * 0.02) / risk_per_share)
                else:
                    position_size = 0
                
                st.write(f"الكمية الآمنة للشراء: **{position_size} سهم**")
                st.write(f"إجمالي المخاطرة (2% من رأس المال): **${capital * 0.02:.2f}**")
            else:
                st.write("⚠️ حدد سعر وقف الخسارة من القائمة الجانبية لتفعيل الحاسبة")

        with col3:
            st.header("🧠 مشاعر السوق")
            rsi_value = df_full['RSI'].iloc[-1]
            # تحديد المشاعر بناءً على مؤشر RSI
            if rsi_value < 40: sentiment = "إيجابي 🟢" 
            elif rsi_value > 65: sentiment = "سلبي 🔴"
            else: sentiment = "محايد 🟡"
            
            st.subheader(sentiment)
            st.write(f"مؤشر القوة النسبية (RSI): {rsi_value:.2f}")
            
            # تنبيهات ذكية منبثقة (Toast Notifications)
            if rsi_value < 30: 
                st.toast("🚨 تنبيه: السهم في منطقة شراء ذهبية (Oversold)!")

        # 3. قسم القناة والتحديثات اللحظية
        st.divider()
        st.subheader("📺 قناة التحديثات والنبض اللحظي")
        t1, t2, t3 = st.columns(3)
        t1.write(f"🕒 توقيت آخر فحص: {datetime.now().strftime('%H:%M:%S')}")
        t2.write(f"📡 حالة التوصيل: **متصل بالخادم السحابي**")
        trend_status = "صاعد 📈" if target > current_price else "هابط 📉"
        t3.write(f"📈 المسار المتوقع: **{trend_status}**")

    else:
        st.error("فشل في العثور على بيانات لهذا الرمز. يرجى التأكد من كتابة الرمز بشكل صحيح (مثل AAPL).")

except Exception as e:
    st.error(f"حدث خطأ غير متوقع في النظام: {e}")

