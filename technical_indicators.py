import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="رادار البورصة المصرية الشامل", layout="wide")
st_autorefresh(interval=300 * 1000, key="comprehensive_update")

# ============================================================
# 2. محرك التحليل الذكي
# ============================================================
class StockEngine:
    def __init__(self, ticker):
        self.ticker = ticker if ".CA" in ticker or "-" in ticker else f"{ticker}.CA"
        self.data = yf.download(self.ticker, period="1y", interval="1d", progress=False).reset_index()
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
        
        # قرار فني
        last_rsi = rsi.iloc[-1]
        if last_rsi < 30: decision = "شراء قوي 🟢"
        elif last_rsi < 45: decision = "منطقة تجميع 🔵"
        elif last_rsi > 70: decision = "بيع / جني أرباح 🔴"
        elif last_rsi > 60: decision = "منطقة تصريف 🟠"
        else: decision = "انتظار 🟡"

        return {
            "الرمز": self.ticker.replace(".CA", ""),
            "السعر": round(current_price, 2),
            "التغير": f"{change:+.2f}%",
            "القرار": decision,
            "RSI": round(last_rsi, 2),
            "data": df
        }

# ============================================================
# 3. واجهة المستخدم
# ============================================================

st.title("🇪🇬 منصة الرصد الشاملة للبورصة المصرية")

# --- لوحة التحكم الجانبية لإضافة أي سهم ---
st.sidebar.header("🔍 إضافة أسهم مخصصة")
custom_ticker = st.sidebar.text_input("أدخل رمز السهم (مثلاً: EKHO, ORAS, ESRS):").upper()
if custom_ticker:
    st.sidebar.write(f"سيتم إضافة {custom_ticker} للقائمة")

# قائمة الأسهم الافتراضية (تغطي معظم القطاعات النشطة)
default_list = [
    "COMI", "FWRY", "ABUK", "TMGH", "SWDY", "ETEL", "HELI", "MFOT", 
    "EKHO", "ESRS", "ORAS", "JUFO", "PHDC", "AMOC", "SKPC", "BTEL",
    "CIRA", "MNHD", "EAST", "ALCN", "ISPH", "PORT", "CCAP"
]

# دمج البحث مع القائمة الافتراضية
final_list = list(set(default_list + ([custom_ticker] if custom_ticker else [])))

# --- القسم الأول: جدول الرصد الشامل ---
st.header("📊 رادار القرارات اللحظي")
all_results = []
cols = st.columns(len(final_list) // 5 + 1) # تقسيم التحميل بصرياً

progress_bar = st.progress(0)
for i, ticker in enumerate(final_list):
    res = StockEngine(ticker).analyze()
    if res:
        all_results.append(res)
    progress_bar.progress((i + 1) / len(final_list))

if all_results:
    df_main = pd.DataFrame(all_results).drop(columns=['data'])
    st.dataframe(df_main, use_container_width=True)

# --- القسم الثاني: التحليل الفني العميق ---
st.divider()
st.header("🎯 نافذة الفحص التفصيلي")
target = st.selectbox("اختر السهم لعرض المخطط وحسابات الربح:", [r["الرمز"] for r in all_results])

# استخراج بيانات السهم المختار
selected_res = next(item for item in all_results if item["الرمز"] == target)
df_chart = selected_res["data"]

c1, c2 = st.columns([2, 1])

with c1:
    fig = go.Figure(data=[go.Candlestick(
        x=df_chart['Date'], open=df_chart['Open'],
        high=df_chart['High'], low=df_chart['Low'],
        close=df_chart['Close']
    )])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, title=f"حركة سعر {target}")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("💰 حاسبة الاستثمار")
    price = selected_res["السعر"]
    quantity = st.number_input("كمية الأسهم:", value=100, step=10)
    
    total_value = price * quantity
    st.write(f"إجمالي قيمة المركز: **{total_value:,.2f} ج.م**")
    
    st.divider()
    gain_target = st.slider("نسبة الربح المستهدفة %", 1, 20, 5)
    target_val = total_value * (gain_target/100)
    st.success(f"الربح المتوقع عند صعود {gain_target}%: **{target_val:,.2f} ج.م**")

st.info(f"💡 نصيحة: يمكنك إضافة أي سهم غير موجود في القائمة عبر كتابة رمزه في القائمة الجانبية.")
