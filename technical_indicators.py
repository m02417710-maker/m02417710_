import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات المنصة
st.set_page_config(page_title="Terminal Pro - EGX", layout="wide")
st_autorefresh(interval=120 * 1000, key="final_stable_refresh")

# ============================================================
# 2. المحرك التحليلي المطور (Stable Engine)
# ============================================================
def analyze_stock(ticker):
    symbol = ticker if ".CA" in ticker else f"{ticker}.CA"
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")
        if df.empty: return None
        
        # تنظيف الأعمدة
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # حساب RSI بدقة (إصلاح مشكلة None)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss.replace(0, np.nan))
        df['RSI'] = 100 - (100 / (1 + rs.fillna(0)))
        
        info = stock.info
        curr_p = df['Close'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        # حساب جودة الاستثمار (Scoring)
        score = 0
        pe = info.get('trailingPE', 0)
        if 0 < pe < 15: score += 4
        elif 15 <= pe < 25: score += 2
        
        div_yield = info.get('dividendYield', 0)
        if div_yield > 0.04: score += 3
        elif div_yield > 0: score += 1
        
        growth = info.get('earningsGrowth', 0)
        if growth and growth > 0.1: score += 3
        
        # الحالة والقرار
        if last_rsi < 35: decision = "دخول ذهبي 🟢"
        elif last_rsi > 65: decision = "جني أرباح 🔴"
        else: decision = "مراقبة 🟡"

        return {
            "الرمز": ticker,
            "السعر": round(curr_p, 2),
            "التغير": round(((curr_p / df['Close'].iloc[-2]) - 1) * 100, 2),
            "RSI": round(last_rsi, 1),
            "P/E": round(pe, 1) if pe else "N/A",
            "توزيعات": f"{div_yield*100:.1f}%",
            "جودة الاستثمار": f"{score}/10",
            "القرار": decision,
            "history": df,
            "info": info
        }
    except:
        return None

# ============================================================
# 3. واجهة المستخدم النهائية (Dashboard)
# ============================================================

st.markdown(f"# 🏛️ مركز إدارة المحفظة الذكي | {datetime.now().strftime('%d-%m-%Y')}")

# القائمة الجانبية لإدارة المال
with st.sidebar:
    st.header("⚙️ إعدادات الحساب")
    total_capital = st.number_input("رأس المال المتاح (EGP):", value=200000)
    risk_level = st.slider("مخاطرة الصفقة الواحدة %", 0.5, 5.0, 1.5)
    st.divider()
    st.info("النظام يقوم بتحديث البيانات تلقائياً كل دقيقتين ⏱️")

# قائمة الأسهم
watchlist = ["COMI", "FWRY", "ABUK", "TMGH", "SWDY", "ETEL", "EKHO", "ORAS", "AMOC", "JUFO"]

# جمع البيانات
all_results = []
for t in watchlist:
    data = analyze_stock(t)
    if data: all_results.append(data)

if all_results:
    df_main = pd.DataFrame(all_results)
    
    # --- 1. خريطة نبض السوق ---
    st.subheader("🌡️ خريطة نبض السوق (التغير اللحظي)")
    fig_heat = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير',
                         color_continuous_scale='RdYlGn', range_color=[-3, 3])
    fig_heat.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

    # --- 2. رادار الفرص الذكي ---
    st.subheader("📊 رادار الفرص الذكي")
    display_cols = ["الرمز", "السعر", "التغير", "RSI", "P/E", "توزيعات", "جودة الاستثمار", "القرار"]
    st.dataframe(df_main[display_cols], use_container_width=True, hide_index=True)

    st.divider()

    # --- 3. غرفة التحليل العميق وإدارة المخاطر ---
    st.header("🔍 غرفة التحليل العميق")
    target = st.selectbox("اختر السهم لتشريح أداءه:", df_main['الرمز'].tolist())
    s = next(item for item in all_results if item["الرمز"] == target)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # شمعات يابانية + RSI
        fig_candle = go.Figure(data=[go.Candlestick(
            x=s['history'].index, open=s['history']['Open'], 
            high=s['history']['High'], low=s['history']['Low'], close=s['history']['Close']
        )])
        fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(t=30))
        st.plotly_chart(fig_candle, use_container_width=True)
        
    with col2:
        st.subheader("📋 التقرير المالي")
        st.metric("جودة الاستثمار", s['جودة الاستثمار'])
        st.write(f"💵 **صافي الدخل:** {s['info'].get('netIncomeToCommon', 0):,.0f} ج.م")
        st.write(f"📉 **أدنى سعر (52 أسبوع):** {s['info'].get('fiftyTwoWeekLow', 0)}")
        st.write(f"📈 **أعلى سعر (52 أسبوع):** {s['info'].get('fiftyTwoWeekHigh', 0)}")
        
    with col3:
        st.subheader("🛡️ إدارة المخاطر")
        sl_price = st.number_input("سعر وقف الخسارة:", value=s['السعر'] * 0.95)
        risk_amount = total_capital * (risk_level / 100)
        price_diff = s['السعر'] - sl_price
        
        if price_diff > 0:
            position_size = int(risk_amount / price_diff)
            st.metric("الكمية الآمنة", f"{position_size} سهم")
            st.warning(f"إجمالي المخاطرة: {position_size * price_diff:,.2f} ج.م")
        else:
            st.error("سعر الوقف يجب أن يكون أقل من السعر الحالي")

    # --- 4. شريط النبض السفلي ---
    st.markdown(f"""
        <div style="background-color: #0e1117; color: #00ff00; padding: 10px; border: 1px solid #333; border-radius: 5px; text-align: center;">
            <b>📺 قناة النبض:</b> سهم {target} يسجل RSI {s['RSI']} | القرار الحالي: {s['القرار']} | 
            توزيعات السهم {s['توزيعات']} | أفضل جودة استثمار حالياً: {df_main.sort_values(by='جودة الاستثمار', ascending=False).iloc[0]['الرمز']}
        </div>
    """, unsafe_allow_html=True)

else:
    st.warning("جاري جلب البيانات من البورصة المصرية... تأكد من استقرار الإنترنت.")
