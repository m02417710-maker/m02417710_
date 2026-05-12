import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="EGX Master Terminal", layout="wide", page_icon="🏛️")

# ============================================================
# إعدادات وثوابت
# ============================================================
EGX_TICKERS = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO", "HELI"]

# ============================================================
# طبقة البيانات (Backend)
# ============================================================
@st.cache_data(ttl=180, show_spinner=False)
def fetch_market_intelligence():
    results = []
    for ticker in EGX_TICKERS:
        try:
            symbol = f"{ticker}.CA"
            stock = yf.Ticker(symbol)
            
            # جلب البيانات بطريقة أكثر موثوقية
            df = stock.history(period="1y", interval="1d")
            if df.empty or len(df) < 20:
                continue

            # تنظيف الأعمدة
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close']
            
            # === RSI محسن ===
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            rsi_val = rsi.iloc[-1]

            info = stock.info
            current_price = close.iloc[-1]
            prev_price = close.iloc[-2]
            change_pct = ((current_price / prev_price) - 1) * 100

            # نظام التقييم
            pe = info.get('trailingPE', np.nan)
            div_yield = info.get('dividendYield', 0) or 0
            score = 0
            if 0 < pe < 16: score += 5
            if div_yield > 0.04: score += 5

            decision = "دخول ذهبي 🟢" if rsi_val < 35 else \
                       "جني أرباح 🔴" if rsi_val > 65 else "مراقبة 🟡"

            results.append({
                "الرمز": ticker,
                "السعر": round(current_price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi_val, 1),
                "P/E": round(pe, 1) if not np.isnan(pe) else "N/A",
                "توزيعات": f"{div_yield*100:.2f}%",
                "الجودة": f"{score}/10",
                "القرار": decision,
                "history": df,
                "info": info
            })
        except Exception as e:
            st.warning(f"خطأ في جلب {ticker}: {str(e)}")
            continue
    return results


# ============================================================
# الواجهة
# ============================================================
data_pool = fetch_market_intelligence()

if not data_pool:
    st.error("تعذر جلب البيانات. تحقق من الاتصال بالإنترنت.")
    st.stop()

df_main = pd.DataFrame(data_pool).drop(columns=['history', 'info'])

st.title("🏛️ EGX Master Terminal")
st.caption("منصة تحليل البورصة المصرية | مبنية وفق أفضل ممارسات Full-Stack 2026")

tab_r, tab_d, tab_n, tab_s = st.tabs(["📈 رادار السوق", "🔍 تحليل معمق", "🗞️ نبض الأخبار", "🛡️ إدارة المخاطر"])

# ==================== تبويب الرادار ====================
with tab_r:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🌡️ خريطة سيولة السوق")
        fig = px.treemap(df_main, path=['الرمز'], values='السعر',
                        color='التغير%', color_continuous_scale='RdYlGn',
                        range_color=[-4, 4])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⭐ أفضل 5 أسهم جودة")
        top5 = df_main.sort_values('الجودة', ascending=False).head(5)
        st.dataframe(top5[['الرمز', 'الجودة', 'القرار', 'RSI']], use_container_width=True, hide_index=True)

    st.subheader("📋 جميع الأسهم")
    st.dataframe(df_main, use_container_width=True, hide_index=True)

# ==================== تبويب التحليل المعمق ====================
with tab_d:
    target = st.selectbox("اختر السهم:", df_main['الرمز'].tolist(), key="stock_select")
    
    # البحث عن السهم المختار
    selected_stock = next((item for item in data_pool if item["الرمز"] == target), None)
    if selected_stock:
        df_hist = selected_stock['history']
        
        c1, c2 = st.columns([3, 1])
        with c1:
            fig = go.Figure(data=[go.Candlestick(
                x=df_hist.index,
                open=df_hist['Open'],
                high=df_hist['High'],
                low=df_hist['Low'],
                close=df_hist['Close']
            )])
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("📊 التقرير المالي")
            st.metric("السعر الحالي", f"{selected_stock['السعر']} ج.م", f"{selected_stock['التغير%']}%")
            st.metric("جودة الاستثمار", selected_stock['الجودة'])
            st.metric("مكرر الربح", selected_stock['P/E'])
            st.metric("RSI (14)", selected_stock['RSI'])
            
            quality = int(selected_stock['الجودة'].split('/')[0])
            st.progress(quality * 10, text=f"مستوى الجودة: {quality}/10")

# ==================== تبويب الأخبار ====================
with tab_n:
    st.subheader("📰 نبض السوق اللحظي")
    for stock in data_pool:
        st.info(f"**{stock['الرمز']}** — {stock['القرار']} | RSI: {stock['RSI']} | توزيعات: {stock['توزيعات']}")
        st.divider()

# ==================== تبويب إدارة المخاطر ====================
with tab_s:
    st.sidebar.header("⚙️ إعدادات المحفظة")
    capital = st.sidebar.number_input("رأس المال (ج.م)", value=500_000, min_value=10_000)
    risk_pct = st.sidebar.slider("نسبة المخاطرة لكل صفقة (%)", 0.5, 5.0, 1.0)

    if 'stock_select' in st.session_state:
        target = st.session_state.stock_select
        s = next((item for item in data_pool if item["الرمز"] == target), None)
        
        if s:
            st.subheader(f"🛡️ حاسبة المخاطر - {target}")
            sl_price = st.number_input("سعر وقف الخسارة", value=float(s['السعر'] * 0.93))
            diff = s['السعر'] - sl_price
            
            if diff > 0:
                shares = int((capital * (risk_pct / 100)) / diff)
                position_value = shares * s['السعر']
                st.success(f"**الكمية الموصى بها: {shares:,} سهم**")
                st.info(f"قيمة المركز: {position_value:,.0f} ج.م")
                st.warning(f"الخسارة المحتملة إذا تم الوقف: {capital * (risk_pct/100):,.0f} ج.م")

# ==================== Footer ذكي ====================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #0f0; padding: 10px;">
    🔴 نبض السوق الآن • أفضل سهم جودة: <b>{df_main.sort_values('الجودة', ascending=False).iloc[0]['الرمز']}</b> 
    • آخر تحديث: {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)
