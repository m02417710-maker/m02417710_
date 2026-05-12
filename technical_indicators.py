import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات المنصة الشاملة
st.set_page_config(page_title="EGX Ultimate Terminal 2026", layout="wide")
st_autorefresh(interval=180 * 1000, key="mega_terminal_refresh")

# ============================================================
# 2. قاعدة بيانات الأسهم والمؤشرات (المسح الشامل)
# ============================================================
EGX_30_TICKERS = [
    "COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "ESRS", "JUFO",
    "PHDC", "AMOC", "HELI", "MNHD", "MFOT", "SKPC", "EFIC", "CCAP", "CIEB", "BTEL",
    "HRHO", "ORWE", "ISMA", "KABO", "RAMEDA", "CLHO", "AUTO", "MTIE", "BINV", "DSCW"
]

# ============================================================
# 3. المحرك التحليلي الخارق
# ============================================================
@st.cache_data(ttl=600)
def fetch_full_market():
    market_data = []
    for t in EGX_30_TICKERS:
        try:
            symbol = f"{t}.CA"
            s = yf.Ticker(symbol)
            hist = s.history(period="5d")
            if hist.empty: continue
            
            info = s.info
            cp = hist['Close'].iloc[-1]
            prev_cp = hist['Close'].iloc[-2]
            chg = ((cp / prev_cp) - 1) * 100
            
            # جلب التوزيعات والأخبار بشكل مبسط
            div = info.get('dividendYield', 0) * 100
            pe = info.get('trailingPE', 0)
            
            market_data.append({
                "الرمز": t,
                "السعر": round(cp, 2),
                "التغير%": round(chg, 2),
                "التوزيعات%": f"{div:.2f}%",
                "P/E": round(pe, 1) if pe else "N/A",
                "الحجم": info.get('volume', 0),
                "القيمة السوقية": info.get('marketCap', 0),
                "القرار": "شراء 🟢" if chg < -2 else "بيع 🔴" if chg > 3 else "مراقبة 🟡"
            })
        except: continue
    return pd.DataFrame(market_data)

# ============================================================
# 4. واجهة المستخدم المتعددة الأقسام (Tabs)
# ============================================================

st.title("🏛️ منصة البورصة المصرية المتكاملة (EGX Terminal)")

tab1, tab2, tab3, tab4 = st.tabs(["📈 رادار السوق", "🗞️ الأخبار والنبض", "📊 تحليل المؤشرات", "🛡️ محفظتي الذكية"])

# --- TAB 1: رادار السوق الشامل ---
with tab1:
    col_m1, col_m2 = st.columns([3, 1])
    df_m = fetch_full_market()
    
    with col_m1:
        st.subheader("🌡️ خريطة سيولة السوق (Heatmap)")
        fig_h = px.treemap(df_m, path=['الرمز'], values='السعر', color='التغير%',
                          color_continuous_scale='RdYlGn', range_color=[-4, 4])
        st.plotly_chart(fig_h, use_container_width=True)
    
    with col_m2:
        st.subheader("🔝 الأفضل أداءً")
        st.dataframe(df_m.sort_values('التغير%', ascending=False)[['الرمز', 'التغير%']].head(5))

    st.subheader("📋 قائمة الأسعار والتوزيعات الكاملة")
    st.dataframe(df_m, use_container_width=True, hide_index=True)

# --- TAB 2: الأخبار والنبض اللحظي ---
with tab2:
    st.subheader("📰 شريط أخبار الشركات والنبض")
    # محاكاة للأخبار اللحظية بناءً على أداء السوق
    for index, row in df_m.head(10).iterrows():
        status = "صعود قوي" if row['التغير%'] > 0 else "تراجع هادئ"
        st.write(f"🔔 **{row['الرمز']}**: {status} بسعر {row['السعر']} ج.م | توزيعات الأرباح الحالية: {row['التوزيعات%']}")
        st.divider()

# --- TAB 3: تحليل المؤشرات الرئيسية ---
with tab3:
    st.subheader("📉 أداء مؤشر EGX30")
    idx = yf.Ticker("^CASE30")
    idx_hist = idx.history(period="1mo")
    fig_idx = go.Figure(data=[go.Scatter(x=idx_hist.index, y=idx_hist['Close'], mode='lines', line=dict(color='#00ff00'))])
    fig_idx.update_layout(template="plotly_dark", title="مؤشر البورصة المصرية الرئيسي (30 يوم)")
    st.plotly_chart(fig_idx, use_container_width=True)

# --- TAB 4: محفظتي الذكية وغرفة الفحص ---
with tab4:
    with st.sidebar:
        st.header("⚙️ إعدادات المحفظة")
        cap = st.number_input("إجمالي رأس المال:", value=500000)
        risk = st.slider("المخاطرة %", 0.5, 5.0, 2.0)

    target = st.selectbox("اختر سهم للفحص العميق من المحفظة:", df_m['الرمز'].tolist())
    s_info = df_m[df_m['الرمز'] == target].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(f"سعر {target}", s_info['السعر'], s_info['التغير%'])
        st.write(f"💰 **توزيعات السهم:** {s_info['التوزيعات%']}")
        st.write(f"📊 **مكرر الربحية:** {s_info['P/E']}")
    
    with c2:
        st.subheader("🧮 حاسبة الكمية الآمنة")
        stop = st.number_input("حدد سعر وقف الخسارة:", value=s_info['السعر'] * 0.95)
        diff = s_info['السعر'] - stop
        if diff > 0:
            pos = int((cap * (risk/100)) / diff)
            st.success(f"الكمية المقترحة: {pos} سهم")
            st.info(f"إجمالي قيمة المركز: {pos * s_info['السعر']:,.2f} ج.م")

# --- شريط النبض السفلي الثابت ---
st.markdown(f"""
    <div style="position: fixed; bottom: 0; width: 100%; background-color: #111; color: #0f0; padding: 5px; text-align: center; border-top: 1px solid #444;">
        🔥 نبض البورصة المصرية: مؤشر EGX30 في حالة توازن | أكثر الأسهم توزيعاً للأرباح حالياً: {df_main.sort_values('التوزيعات%', ascending=False).iloc[0]['الرمز'] if 'df_main' in locals() else 'جاري التحميل...'}
    </div>
""", unsafe_allow_html=True)
