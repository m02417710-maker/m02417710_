import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="رادار الأسهم والقرار الذكي", layout="wide")
st_autorefresh(interval=300 * 1000, key="global_update")

# ============================================================
# 2. محرك التحليل والقرار
# ============================================================
class StockEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = yf.download(ticker, period="1y", interval="1d", progress=False).reset_index()
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)

    def analyze(self):
        if self.data.empty: return None
        
        df = self.data.copy()
        # حساب RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        last_rsi = rsi.iloc[-1]

        # منطق اتخاذ القرار
        if last_rsi < 35:
            decision = "شراء قوي 🟢"
            reason = "تشبع بيعي واضح"
        elif last_rsi > 65:
            decision = "بيع / جني أرباح 🔴"
            reason = "تضخم في الشراء"
        else:
            decision = "انتظار / حياد 🟡"
            reason = "استقرار السعر"

        return {
            "السهم": self.ticker,
            "السعر": round(current_price, 2),
            "التغير %": f"{change:+.2f}%",
            "القرار": decision,
            "السبب": reason,
            "RSI": round(last_rsi, 2),
            "data": df
        }

# ============================================================
# 3. واجهة المستخدم
# ============================================================

st.title("🛡️ رادار فحص السوق واتخاذ القرار")

# قائمة الأسهم المتابعة (يمكنك زيادتها)
watchlist = ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "2222.SR", "BTC-USD"]

# --- القسم الأول: قائمة الأسهم والتحليل السريع ---
st.header("📋 ملخص حالة السوق والقرارات")

summary_data = []
for t in watchlist:
    with st.spinner(f'تحليل {t}...'):
        result = StockEngine(t).analyze()
        if result:
            summary_data.append(result)

# تحويل البيانات لجدول جذاب
df_summary = pd.DataFrame(summary_data).drop(columns=['data'])
st.table(df_summary)

st.divider()

# --- القسم الثاني: التحليل التفصيلي للسهم المختار ---
st.header("🎯 التحليل العميق لسهم محدد")
selected_stock = st.selectbox("اختر سهماً من القائمة لعرض الرسم البياني وإدارة المخاطر:", watchlist)

# جلب بيانات السهم المختار
detailed_result = next(item for item in summary_data if item["السهم"] == selected_stock)
df_detailed = detailed_result["data"]

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure(data=[go.Candlestick(
        x=df_detailed['Date'], open=df_detailed['Open'],
        high=df_detailed['High'], low=df_detailed['Low'],
        close=df_detailed['Close'], name=selected_stock
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("إدارة المخاطر (100 سهم)")
    curr_p = detailed_result["السعر"]
    st.write(f"السعر الحالي: **{curr_p}**")
    
    # حساب العائد المتوقع لـ 100 سهم بناءً على حركة 3%
    target_3pct = curr_p * 1.03
    expected_profit = (target_3pct - curr_p) * 100
    
    st.metric("الربح المتوقع لـ 100 سهم (+3%)", f"${expected_profit:.2f}")
    
    stop_loss = st.number_input("حدد سعر وقف الخسارة الخاص بك:", value=curr_p * 0.95)
    risk = (curr_p - stop_loss) * 100
    st.error(f"خسارة محتملة لـ 100 سهم: ${risk:.2f}")

# القسم الأخير للتنبيهات
st.divider()
st.info(f"🕒 آخر تحديث للسوق: {datetime.now().strftime('%H:%M:%S')}")
