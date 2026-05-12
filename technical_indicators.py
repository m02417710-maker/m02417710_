import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات الصفحة
st.set_page_config(page_title="منصة التحليل الفني والمالي المتكاملة", layout="wide")
st_autorefresh(interval=300 * 1000, key="full_analysis_update")

# ============================================================
# 2. محرك التحليل (فني + مالي)
# ============================================================
class ComprehensiveEngine:
    def __init__(self, ticker):
        self.symbol = ticker if ".CA" in ticker or "-" in ticker else f"{ticker}.CA"
        self.stock = yf.Ticker(self.symbol)
        self.data = self.stock.history(period="1y")
        
    def get_fundamental_data(self):
        """جلب البيانات المالية الأساسية"""
        info = self.stock.info
        return {
            "مكرر الربحية (P/E)": info.get('trailingPE', 'N/A'),
            "ريع السهم (Yield)": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "لا يوجد",
            "القيمة الدفترية": info.get('bookValue', 'N/A'),
            "مضاعف القيمة الدفترية": info.get('priceToBook', 'N/A'),
            "صافي الدخل": f"{info.get('netIncomeToCommon', 0):,.0f}" if info.get('netIncomeToCommon') else "N/A",
            "العملة": info.get('currency', 'EGP')
        }

    def analyze_technical(self):
        if self.data.empty: return None
        df = self.data.copy()
        
        # حساب RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        
        current_price = df['Close'].iloc[-1]
        last_rsi = rsi.iloc[-1]
        
        # قرار دمج الفني مع المالي
        if last_rsi < 35: decision = "فرصة شراء (تشبع بيعي) 🟢"
        elif last_rsi > 65: decision = "جني أرباح (تشبع شرائي) 🔴"
        else: decision = "منطقة استقرار 🟡"

        return {
            "الرمز": self.symbol.replace(".CA", ""),
            "السعر الحالي": round(current_price, 2),
            "القرار الفني": decision,
            "RSI": round(last_rsi, 2),
            "history": df
        }

# ============================================================
# 3. واجهة المستخدم
# ============================================================

st.title("🏛️ الرادار المتكامل: تحليل فني + صحة مالية")

# قائمة الأسهم
watchlist = ["COMI", "FWRY", "ABUK", "TMGH", "SWDY", "ETEL", "EKHO", "ORAS", "ESRS"]

# --- الجزء الأول: المسح السريع ---
st.header("📊 نظرة عامة على السوق")
summary = []
for t in watchlist:
    try:
        engine = ComprehensiveEngine(t)
        tech = engine.analyze_technical()
        if tech:
            summary.append(tech)
    except: continue

st.table(pd.DataFrame(summary).drop(columns=['history']))

st.divider()

# --- الجزء الثاني: الفحص المجهري (فني + مالي) ---
st.header("🔍 الفحص المجهري للسهم")
target = st.selectbox("اختر السهم للتحليل المالي والفني المفصل:", watchlist)

if target:
    engine = ComprehensiveEngine(target)
    tech_res = engine.analyze_technical()
    fund_res = engine.get_fundamental_data()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 التحليل الفني (الشموع)")
        df_chart = tech_res['history']
        fig = go.Figure(data=[go.Candlestick(
            x=df_chart.index, open=df_chart['Open'],
            high=df_chart['High'], low=df_chart['Low'],
            close=df_chart['Close']
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📋 التحليل المالي (Fundamentals)")
        # عرض البيانات المالية في بطاقات أو جدول صغير
        for key, value in fund_res.items():
            st.write(f"**{key}:** {value}")
        
        st.divider()
        # تقييم سريع
        pe = fund_res["مكرر الربحية (P/E)"]
        if pe != 'N/A':
            if pe < 10: st.success("💎 السهم يعتبر 'رخيص' مالياً (P/E منخفض)")
            elif pe > 25: st.warning("⚠️ السهم قد يكون 'مبالغ في سعره' (P/E مرتفع)")

# --- الجزء الثالث: حاسبة الاستثمار المتطورة ---
st.divider()
st.header("💰 حاسبة العائد وإدارة المحفظة")
c1, c2, c3 = st.columns(3)

with c1:
    qty = st.number_input("كمية الأسهم", value=100)
with c2:
    price = tech_res['السعر الحالي']
    st.metric("إجمالي التكلفة", f"{price * qty:,.2f} ج.م")
with c3:
    target_gain = st.slider("الهدف الربحي %", 1, 50, 10)
    st.metric("الربح الصافي المستهدف", f"{(price * qty) * (target_gain/100):,.2f} ج.م")

st.info(f"آخر تحديث للبيانات المالية والفنية: {datetime.now().strftime('%H:%M:%S')}")
