import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات المنصة المتكاملة
st.set_page_config(page_title="EGX Global Terminal 2026", layout="wide")
st_autorefresh(interval=180 * 1000, key="mega_terminal_final")

# قائمة الأسهم القيادية (EGX30)
EGX_TICKERS = [
    "COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "ESRS", "JUFO",
    "PHDC", "AMOC", "HELI", "MNHD", "MFOT", "SKPC", "EFIC", "CCAP", "CIEB"
]

# ============================================================
# 2. المحرك التحليلي (فني + مالي + توزيعات)
# ============================================================
@st.cache_data(ttl=600)
def fetch_market_intelligence():
    data_list = []
    for t in EGX_TICKERS:
        try:
            symbol = f"{t}.CA"
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            if hist.empty: continue
            
            # تنظيف البيانات
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            info = stock.info
            cp = hist['Close'].iloc[-1]
            chg = ((cp / hist['Close'].iloc[-2]) - 1) * 100
            
            # حساب RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss.replace(0, np.nan))
            rsi = 100 - (100 / (1 + rs.fillna(0)))
            
            # حساب جودة الاستثمار
            score = 0
            pe = info.get('trailingPE', 0)
            div = info.get('dividendYield', 0)
            if 0 < pe < 15: score += 5
            if div > 0.05: score += 5
            
            data_list.append({
                "الرمز": t, "السعر": round(cp, 2), "التغير%": round(chg, 2),
                "RSI": round(rsi.iloc[-1], 1), "P/E": round(pe, 1) if pe else "N/A",
                "توزيعات": f"{div*100:.2f}%", "الجودة": f"{score}/10",
                "القرار": "دخول 🟢" if rsi.iloc[-1] < 35 else "خروج 🔴" if rsi.iloc[-1] > 65 else "مراقبة 🟡",
                "history": hist, "info": info
            })
        except: continue
    return data_list

# ============================================================
# 3. الواجهة الرسومية وتوزيع الأقسام
# ============================================================
all_intel = fetch_market_intelligence()
df_market = pd.DataFrame(all_intel).drop(columns=['history', 'info'])

st.title("🏛️ منصة البورصة المصرية الشاملة | EGX Ultimate")

tab1, tab2, tab3 = st.tabs(["📈 رادار السوق", "🔍 فحص السهم", "🛡️ إدارة المحفظة"])

# --- التبويب الأول: الرادار الشامل ---
with tab1:
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.subheader("🌡️ خريطة سيولة السوق")
        fig_heat = px.treemap(df_market, path=['الرمز'], values='السعر', color='التغير%',
                             color_continuous_scale='RdYlGn', range_color=[-3, 3])
        st.plotly_chart(fig_heat, use_container_width=True)
    with col_h2:
        st.subheader("🔔 نبض الأخبار")
        for i in range(min(5, len(all_intel))):
            st.info(f"**{all_intel[i]['الرمز']}**: جودة الاستثمار {all_intel[i]['الجودة']} | السعر {all_intel[i]['السعر']}")

    st.subheader("📋 قائمة الأسعار والتوزيعات")
    st.dataframe(df_market, use_container_width=True, hide_index=True)

# --- التبويب الثاني: الفحص المجهري ---
with tab2:
    target = st.selectbox("اختر سهم للفحص العميق:", df_market['الرمز'].tolist())
    s = next(item for item in all_intel if item["الرمز"] == target)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_candle = go.Figure(data=[go.Candlestick(x=s['history'].index, open=s['history']['Open'], 
                        high=s['history']['High'], low=s['history']['Low'], close=s['history']['Close'])])
        fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_candle, use_container_width=True)
    with c2:
        st.subheader("📋 التقرير المالي")
        st.write(f"💵 **صافي الدخل:** {s['info'].get('netIncomeToCommon', 0):,.0f} ج.م")
        st.write(f"📊 **مكرر الربحية:** {s['P/E']}")
        st.write(f"💰 **توزيعات الأرباح:** {s['توزيعات']}")
        st.progress(int(s['الجودة'].split('/')[0])*10)

# --- التبويب الثالث: إدارة المخاطر ---
with tab3:
    st.sidebar.header("⚙️ إعدادات المحفظة")
    capital = st.sidebar.number_input("رأس المال:", value=500000)
    risk_pct = st.sidebar.slider("المخاطرة %", 0.5, 5.0, 2.0)
    
    st.subheader(f"🛡️ حاسبة الكمية الآمنة لـ {target}")
    sl = st.number_input("سعر وقف الخسارة المقترح:", value=s['السعر'] * 0.95)
    diff = s['السعر'] - sl
    if diff > 0:
        qty = int((capital * (risk_pct/100)) / diff)
        st.success(f"الكمية المقترحة للشراء: **{qty} سهم**")
        st.info(f"إجمالي القيمة: {qty * s['السعر']:,.2f} ج.م")

# شريط النبض السفلي
st.markdown(f"""
    <div style="position: fixed; bottom: 0; width: 100%; background-color: #111; color: #0f0; padding: 5px; text-align: center; border-top: 1px solid #444;">
        <marquee>🔥 نبض السوق: سهم {target} في حالة {s['القرار']} | RSI: {s['RSI']} | أفضل توزيعات حالية في القائمة: {df_market.sort_values('توزيعات', ascending=False).iloc[0]['الرمز']}</marquee>
    </div>
""", unsafe_allow_html=True)
