import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import json
import os

st.set_page_config(page_title="EGX Master Terminal v12.0", layout="wide", page_icon="🏛️")

st_autorefresh(interval=120 * 1000, key="v12_final")

# ====================== Session State ======================
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 'username': '', 'portfolio': {}, 
        'watchlist': [], 'alerts': [], 'chat_history': []
    })

USERS = {"admin": "123456", "trader": "123456", "demo": "123456"}

# ====================== Grok AI (xAI) ======================
def analyze_with_grok(text: str, ticker: str = "السوق"):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "⚠️ Grok API غير مفعل. أضف GROK_API_KEY في secrets.toml لتفعيل التحليل الذكي."
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "grok-3",
                "messages": [{"role": "user", "content": f"حلل الخبر التالي لسهم {ticker} في البورصة المصرية وأعطِ توصية واضحة مع أسباب:\n{text}"}],
                "temperature": 0.65
            },
            timeout=12
        )
        return response.json()['choices'][0]['message']['content']
    except:
        return "❌ تعذر الاتصال بـ Grok API"

# ====================== جلب البيانات ======================
@st.cache_data(ttl=150)
def get_full_market_data():
    tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO", "HELI"]
    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(f"{ticker}.CA")
            df = stock.history(period="1y")
            if df.empty or len(df) < 60: continue

            close = df['Close']
            price = close.iloc[-1]
            change_pct = ((price / close.iloc[-2]) - 1) * 100

            # RSI
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = (100 - (100 / (1 + gain / loss))).iloc[-1]

            # MACD
            macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
            signal = macd.ewm(span=9).mean()
            macd_hist = (macd - signal).iloc[-1]

            score = 0
            if price > close.rolling(50).mean().iloc[-1] > close.rolling(200).mean().iloc[-1]: score += 30
            if rsi < 40: score += 25
            if macd_hist > 0: score += 20
            if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.6: score += 15

            signal_str = "Strong Buy 🟢🟢" if score >= 75 else "Buy 🟢" if score >= 55 else "Hold 🟡" if score >= 35 else "Sell 🔴"

            results.append({
                "الرمز": ticker,
                "السعر": round(price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi, 1),
                "MACD": round(macd_hist, 3),
                "الإشارة": signal_str,
                "الجودة": int(score),
                "history": df,
                "info": stock.info,
                "news": stock.news[:3] if hasattr(stock, 'news') else []
            })
        except:
            continue
    return results

data = get_full_market_data()
df_main = pd.DataFrame([{k: v for k, v in item.items() if k not in ['history', 'info', 'news']} for item in data])

# ====================== Login ======================
if not st.session_state.logged_in:
    st.title("🏛️ EGX Master Terminal v12.0")
    st.subheader("المنصة الشاملة الذكية للبورصة المصرية")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", type="primary", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ تم تسجيل الدخول")
                st.rerun()
    st.stop()

# ====================== Sidebar ======================
with st.sidebar:
    st.success(f"👋 مرحباً {st.session_state.username}")
    capital = st.number_input("رأس المال (ج.م)", value=1000000, step=10000)
    if st.button("🚪 تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

# ====================== التبويبات ======================
tabs = st.tabs([
    "📈 رادار السوق", "🔍 تحليل معمق", "📊 مؤشرات الشركات",
    "📰 Mubasher & EGX News", "🤖 Grok AI Analyzer", "💼 المحفظة", "🛡️ إدارة المخاطر"
])

# Tab 1: رادار السوق
with tabs[0]:
    st.title("📈 رادار السوق المصري")
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("🔥 أفضل 5 أسهم")
        st.dataframe(df_main.nlargest(5, 'الجودة')[['الرمز', 'السعر', 'الإشارة', 'الجودة']], hide_index=True, use_container_width=True)
    st.dataframe(df_main, use_container_width=True, hide_index=True)

# Tab 2: تحليل معمق
with tabs[1]:
    ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist())
    stock = next(s for s in data if s["الرمز"] == ticker)
    df = stock['history']
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", height=650)
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: مؤشرات الشركات
with tabs[2]:
    st.title("📊 المؤشرات المالية للشركات")
    t = st.selectbox("اختر الشركة", df_main['الرمز'].tolist(), key="fund")
    info = next(s for s in data if s["الرمز"] == t)['info']
    col1, col2 = st.columns(2)
    with col1:
        st.metric("مكرر الربح", info.get('trailingPE', 'N/A'))
        st.metric("عائد التوزيعات", f"{info.get('dividendYield', 0)*100:.2f}%")
        st.metric("القيمة السوقية", f"{info.get('marketCap', 0):,}")
    with col2:
        st.write(f"**الاسم:** {info.get('longName', t)}")
        st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")

# Tab 4: الأخبار
with tabs[3]:
    st.title("📰 Mubasher & EGX News")
    mode = st.radio("نوع الأخبار", ["عامة", "لسهم محدد"])
    selected = st.selectbox("اختر السهم", df_main['الرمز'].tolist()) if mode == "لسهم محدد" else None
    # أخبار وهمية + روابط (يمكن تطويرها)
    news = [
        {"title": "إفصاح توزيع أرباح", "source": "Mubasher", "link": "#"},
        {"title": "نتائج أعمال قوية", "source": "EGX", "link": "#"}
    ]
    for n in news:
        with st.expander(n['title']):
            st.write(f"المصدر: {n['source']}")
            if st.button("تحليل بالذكاء الاصطناعي", key=n['title']):
                with st.spinner("Grok يحلل..."):
                    analysis = analyze_with_grok(n['title'], selected or "السوق")
                    st.success(analysis)

# Tab 5: Grok AI
with tabs[4]:
    st.title("🤖 Grok AI - محلل ذكي")
    ai_ticker = st.selectbox("السهم", df_main['الرمز'].tolist(), key="ai")
    user_input = st.text_area("اكتب الخبر أو سؤالك")
    if st.button("تحليل"):
        result = analyze_with_grok(user_input or "أعطني تحليلاً عاماً", ai_ticker)
        st.info(result)

# Tab 6 & 7: المحفظة وإدارة المخاطر (مختصر)
with tabs[5]:
    st.subheader("💼 محفظتي")
    st.info("يمكن توسيع هذا التبويب بإضافة/حذف الأسهم")

with tabs[6]:
    st.subheader("🛡️ إدارة المخاطر")
    st.info("حاسبة وقف الخسارة ونسبة المخاطرة")

# ====================== Footer ======================
best = max(data, key=lambda x: x['الجودة'])
st.markdown(f"""
<div style="text-align:center; padding:28px; background:linear-gradient(90deg, #0a0a0a, #1a1a2e); color:#00ffcc; 
            border-top:6px solid #00ffcc; margin-top:40px; font-size:20px;">
    🏛️ EGX Master Terminal v12.0 | Mubasher + Grok AI | 
    أقوى توصية: <b>{best['الرمز']}</b> — {best['الإشارة']} (Score: {best['الجودة']}/100)
</div>
""", unsafe_allow_html=True)
