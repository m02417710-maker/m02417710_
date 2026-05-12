import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from bs4 import BeautifulSoup

st.set_page_config(page_title="EGX Master Terminal v12.2", layout="wide", page_icon="🏛️")

st_autorefresh(interval=120 * 1000, key="full_app")

# ====================== Session State ======================
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 'username': '', 'portfolio': {},
        'watchlist': [], 'alerts': [], 'chat_history': []
    })

USERS = {"admin": "123456", "trader": "123456", "demo": "123456"}

# ====================== Grok AI ======================
def analyze_with_grok(text: str, ticker: str = "السوق"):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "⚠️ Grok API غير مفعل. أضف المفتاح في secrets.toml"
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "grok-3",
                "messages": [{"role": "user", "content": f"حلل الخبر التالي لسهم {ticker} في EGX:\n{text}"}],
                "temperature": 0.65
            },
            timeout=12
        )
        return resp.json()['choices'][0]['message']['content']
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

            delta = close.diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()
            rsi = (100 - (100 / (1 + gain / loss))).iloc[-1]

            macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
            signal = macd.ewm(span=9).mean()
            macd_hist = (macd - signal).iloc[-1]

            score = 0
            if price > close.rolling(50).mean().iloc[-1] > close.rolling(200).mean().iloc[-1]: score += 30
            if rsi < 40: score += 25
            if macd_hist > 0: score += 20

            results.append({
                "الرمز": ticker,
                "السعر": round(price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi, 1),
                "MACD": round(macd_hist, 3),
                "الإشارة": "Strong Buy 🟢🟢" if score >= 75 else "Buy 🟢" if score >= 55 else "Hold 🟡" if score >= 35 else "Sell 🔴",
                "الجودة": int(score),
                "history": df,
                "info": stock.info
            })
        except:
            continue
    return results

data = get_full_market_data()
df_main = pd.DataFrame([{k: v for k, v in item.items() if k not in ['history', 'info']} for item in data])

# ====================== Mubasher News ======================
def get_mubasher_news(ticker=None):
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://english.mubasher.info/markets/EGX/stocks/{ticker}/news/" if ticker else "https://english.mubasher.info/markets/EGX/news/"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all(['h2', 'h3', 'a'])[:8]
        for item in items:
            text = item.get_text(strip=True)
            if len(text) > 20:
                news.append({"title": text[:100], "link": url, "source": "Mubasher"})
    except:
        news.append({"title": "تعذر جلب الأخبار من Mubasher", "link": "#", "source": "System"})
    return news

# ====================== Login ======================
if not st.session_state.logged_in:
    st.title("🏛️ EGX Master Terminal v12.2")
    st.subheader("المنصة الشاملة للبورصة المصرية")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        if st.button("دخول", type="primary", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
    st.stop()

# ====================== Sidebar ======================
with st.sidebar:
    st.success(f"👋 {st.session_state.username}")
    st.caption("v12.2 - Mubasher + Grok AI")

# ====================== التبويبات ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 رادار السوق", "🔍 تحليل معمق", "📊 مؤشرات الشركات",
    "📰 Mubasher News", "🤖 Grok AI", "💼 المحفظة"
])

with tab1:
    st.title("📈 رادار السوق")
    c1, c2 = st.columns([2,1])
    with c1:
        fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_main, use_container_width=True, hide_index=True)

with tab2:
    ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist())
    stock = next(s for s in data if s["الرمز"] == ticker)
    fig = go.Figure(data=[go.Candlestick(x=stock['history'].index,
                    open=stock['history']['Open'], high=stock['history']['High'],
                    low=stock['history']['Low'], close=stock['history']['Close'])])
    fig.update_layout(template="plotly_dark", height=650)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.title("📊 مؤشرات الشركات")
    t = st.selectbox("اختر الشركة", df_main['الرمز'].tolist(), key="fund")
    info = next(s for s in data if s["الرمز"] == t)['info']
    st.metric("مكرر الربح (P/E)", info.get('trailingPE', 'N/A'))
    st.metric("عائد التوزيعات", f"{info.get('dividendYield',0)*100:.2f}%")

with tab4:
    st.title("📰 Mubasher News")
    mode = st.radio("نوع الأخبار", ["عامة", "لسهم محدد"])
    sel_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist()) if mode == "لسهم محدد" else None
    news_list = get_mubasher_news(sel_ticker)
    for n in news_list:
        with st.expander(n['title']):
            st.markdown(f"[اقرأ الخبر]({n['link']})")
            if st.button("تحليل بالذكاء الاصطناعي", key=n['title'][:40]):
                with st.spinner("Grok يحلل..."):
                    res = analyze_with_grok(n['title'], sel_ticker or "")
                    st.success(res)

with tab5:
    st.title("🤖 Grok AI Analyzer")
    ai_ticker = st.selectbox("السهم", df_main['الرمز'].tolist(), key="ai")
    prompt = st.text_area("اكتب الخبر أو السؤال")
    if st.button("تحليل"):
        result = analyze_with_grok(prompt or "أعطني تحليلاً", ai_ticker)
        st.info(result)

with tab6:
    st.title("💼 المحفظة")
    st.info("يمكنك توسيع هذا التبويب بإضافة أسهم من Sidebar")

# ====================== Footer ======================
best = max(data, key=lambda x: x['الجودة'])
st.markdown(f"""
<div style="text-align:center; padding:30px; background:linear-gradient(90deg,#0a0a0a,#16213e); color:#00ffcc; border-top:6px solid #00ffcc;">
    🏛️ EGX Master Terminal v12.2 | Mubasher + Grok AI | 
    أقوى توصية: <b>{best['الرمز']}</b> — {best['الإشارة']}
</div>
""", unsafe_allow_html=True)
