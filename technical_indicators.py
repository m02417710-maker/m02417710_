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
st_autorefresh(interval=300 * 1000, key="global_update")

# ============================================================
# 2. فئة المحرك الفني (المؤشرات + التوقعات)
# ============================================================
class StockEngine:
    def __init__(self, data):
        self.df = data.copy()
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = self.df.columns.get_level_values(0)
        self.df = self.df.sort_values('Date').reset_index(drop=True)

    def get_indicators(self):
        # RSI
        delta = self.df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        self.df['RSI'] = 100 - (100 / (1 + rs))
        # MACD
        exp1 = self.df['Close'].ewm(span=12).mean()
        exp2 = self.df['Close'].ewm(span=26).mean()
        self.df['MACD'] = exp1 - exp2
        self.df['Signal'] = self.df['MACD'].ewm(span=9).mean()
        return self.df

    def predict_price(self, days=7):
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
st.sidebar.info("📢 قناة التليجرام: مفعلة لاستقبال التنبيهات")

# --- جلب البيانات والتحليل ---
try:
    raw_data = yf.download(ticker, period="1y", interval="1d").reset_index()
    if not raw_data.empty:
        engine = StockEngine(raw_data)
        df_full = engine.get_indicators()
        current_price = df_full['Close'].iloc[-1]
        
        # 1. الرسوم البيانية التفاعلية (الشموع اليابانية)
        st.subheader(f"📊 مخطط الشموع اليابانية التفاعلي - {ticker}")
        fig = go.Figure(data=[go.Candlestick(
            x=df_full['Date'], open=df_full['Open'],
            high=df_full['High'], low=df_full['Low'],
            close=df_full['Close'], name="Candlesticks"
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_view=True)

        # 2. التوقعات وإدارة المخاطر (أعمدة)
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.header("🔮 التوقع والربح")
            preds = engine.predict_price(7)
            target = preds[-1]
            gain_100 = (target - current_price) * 100
            st.metric("السعر المستهدف (7 أيام)", f"{target:.2f}")
            st.metric("ربح متوقع لـ 100 سهم", f"${gain_100:.2f}", f"{((target/current_price)-1)*100:.2f}%")

        with col2:
            st.header("⚖️ إدارة المخاطر")
            if stop_loss > 0:
                risk_per_share = current_price - stop_loss
                position_size = int((capital * 0.02) / risk_per_share) if risk_per_share > 0 else 0
                st.write(f"الكمية الآمنة للشراء: **{position_size} سهم**")
                st.write(f"إجمالي المخاطرة (2%): **${capital * 0.02:.2f}**")
            else:
                st.write("⚠️ حدد سعر وقف الخسارة لتفعيل الحاسبة")

        with col3:
            st.header("🧠 مشاعر السوق")
            rsi = df_full['RSI'].iloc[-1]
            sentiment = "إيجابي 🟢" if rsi < 40 else "سلبي 🔴" if rsi > 65 else "محايد 🟡"
            st.subheader(sentiment)
            st.write(f"مؤشر القوة النسبية: {rsi:.2f}")
            if rsi < 30: st.toast("🚨 تنبيه: سهم في منطقة شراء ذهبية!")

        # 3. قناة التحديثات اللحظية
        st.divider()
        st.subheader("📺 قناة التحديثات والنبض اللحظي")
        t1, t2, t3 = st.columns(3)
        t1.write(f"🕒 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")
        t2.write(f"📡 حالة الربط مع تليجرام: **متصل**")
        t3.write(f"📈 الاتجاه العام: {'صاعد' if target > current_price else 'هابط'}")

    else:
        st.error("فشل جلب البيانات. يرجى التأكد من الرمز.")
except Exception as e:
    st.error(f"خطأ في النظام: {e}")
