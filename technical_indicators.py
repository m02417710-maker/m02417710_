import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="EGX Ultimate Terminal", layout="wide")
st_autorefresh(interval=120 * 1000, key="final_mega_refresh")

# قائمة الأسهم القيادية الشاملة
EGX_FULL_LIST = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO", "HELI", "MNHD"]

# ============================================================
# 2. المحرك الذكي (تحليل مالي + فني + توزيعات)
# ============================================================
@st.cache_data(ttl=300)
def get_market_data():
    results = []
    for t in EGX_FULL_LIST:
        try:
            symbol = f"{t}.CA"
            s = yf.Ticker(symbol)
            df = s.history(period="1y")
            if df.empty: continue
            
            # إصلاح مشكلة الأعمدة المزدوجة (Multi-Index)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # حساب RSI بدقة
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss.replace(0, np.nan))
            rsi = 100 - (100 / (1 + rs.fillna(0)))
            
            info = s.info
            curr_p = df['Close'].iloc[-1]
            chg = ((curr_p / df['Close'].iloc[-2]) - 1) * 100
            
            # نظام التقييم (Score)
            score = 0
            pe = info.get('trailingPE', 0)
            div = info.get('dividendYield', 0)
            if 0 < pe < 15: score += 5
            if div > 0.04: score += 5

            results.append({
                "الرمز": t, "السعر": round(curr_p, 2), "التغير%": round(chg, 2),
                "RSI": round(rsi.iloc[-1], 1), "P/E": round(pe, 1) if pe else "N/A",
                "توزيعات": f"{div*100:.2f}%", "الجودة": f"{score}/10",
                "القرار": "دخول ذهبي 🟢" if rsi.iloc[-1] < 35 else "جني أرباح 🔴" if rsi.iloc[-1] > 65 else "مراقبة 🟡",
                "history": df, "info": info, "div_val": div
            })
        except: continue
    return results

# ============================================================
# 3. واجهة المستخدم النهائية (الدمج الكامل)
# ============================================================
all_stocks = get_market_data()
df_final = pd.DataFrame(all_stocks).drop(columns=['history', 'info', 'div_val'])

st.title("🏛️ منصة البورصة المصرية المتكاملة | EGX Terminal")

# نظام التبويبات الشامل
tab_radar, tab_analysis, tab_news, tab_portfolio = st.tabs(["📈 رادار السوق", "🔍 تحليل معمق", "🗞️ الأخبار والنبض", "🛡️ إدارة المخاطر"])

with tab_radar:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🌡️ خريطة الحرارة (Heatmap)")
        fig_heat = px.treemap(df_final, path=['الرمز'], values='السعر', color='التغير%',
                             color_continuous_scale='RdYlGn', range_color=[-3, 3])
        st.plotly_chart(fig_heat, use_container_width=True)
    with col2:
        st.subheader("🔝 الأفضل توزيعاً للأرباح")
        top_div = pd.DataFrame(all_stocks).sort_values('div_val', ascending=False).head(5)
        st.table(top_div[['الرمز', 'توزيعات']])

    st.subheader("📋 رادار الفرص الذكي")
    st.dataframe(df_final, use_container_width=True, hide_index=True)

with tab_analysis:
    selected = st.selectbox("اختر السهم للفحص:", df_final['الرمز'].tolist())
    s = next(item for item in all_stocks if item["الرمز"] == selected)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_candle = go.Figure(data=[go.Candlestick(x=s['history'].index, open=s['history']['Open'], 
                        high=s['history']['High'], low=s['history']['Low'], close=s['history']['Close'])])
        fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_candle, use_container_width=True)
    with c2:
        st.subheader("📋 التقرير المالي")
        st.metric("السعر الحالي", s['السعر'], f"{s['التغير%']}%")
        st.write(f"📊 **مكرر الربحية:** {s['P/E']}")
        st.write(f"💰 **صافي الربح:** {s['info'].get('netIncomeToCommon', 0):,.0f} ج.م")
        st.progress(int(s['الجودة'].split('/')[0])*10)

with tab_news:
    st.subheader("📰 نبض أخبار الشركات (تلقائي)")
    for stock in all_stocks[:8]:
        st.write(f"📌 **{stock['الرمز']}**: القرار الحالي هو **{stock['قرار']}** بناءً على RSI ({stock['RSI']}). الشركة توزع أرباحاً بنسبة {stock['توزيعات']}.")
        st.divider()

with tab_portfolio:
    st.sidebar.header("⚙️ إعدادات المحفظة")
    cap = st.sidebar.number_input("رأس المال الكلي:", value=200000)
    risk = st.sidebar.slider("المخاطرة %", 0.5, 5.0, 1.5)
    
    st.subheader(f"🛡️ حاسبة إدارة المخاطر لـ {selected}")
    sl = st.number_input("سعر وقف الخسارة:", value=s['السعر'] * 0.95)
    diff = s['السعر'] - sl
    if diff > 0:
        qty = int((cap * (risk/100)) / diff)
        st.success(f"الكمية المقترحة: **{qty} سهم**")
        st.info(f"إجمالي قيمة المركز: {qty * s['السعر']:,.2f} ج.م")

# شريط النبض السفلي
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #111; color: #0f0; padding: 5px; text-align: center; border-top: 1px solid #444; z-index: 100;">
        <marquee scrollamount="5">🔥 نبض السوق: سهم {selected} يستهدف مناطق جديدة | RSI حالي: {s['RSI']} | أفضل جودة استثمار الآن: {df_final.sort_values('الجودة', ascending=False).iloc[0]['الرمز']}</marquee>
    </div>
""", unsafe_allow_html=True)
