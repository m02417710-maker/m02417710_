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

st.set_page_config(page_title="EGX Super Analyst v13.1", layout="wide", page_icon="⚡")

st_autorefresh(interval=90 * 1000, key="super131")

# ====================== إدارة المفاتيح السرية ======================
if 'grok_api_key' not in st.session_state:
    st.session_state.grok_api_key = st.secrets.get("GROK_API_KEY", "")

def save_api_key(key):
    st.session_state.grok_api_key = key
    st.success("✅ تم حفظ مفتاح Grok API بنجاح")

# ====================== Grok AI ======================
def analyze_with_grok(text: str, ticker: str = "السوق"):
    api_key = st.session_state.grok_api_key
    if not api_key:
        return "⚠️ يرجى إدخال مفتاح Grok API أولاً من قسم الإعدادات"
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "grok-3",
                "messages": [{"role": "user", "content": f"أنت محلل مالي خبير. حلل وأعطِ توصية إدارية:\n{text}"}],
                "temperature": 0.6
            },
            timeout=12
        )
        return resp.json()['choices'][0]['message']['content']
    except:
        return "❌ تعذر الاتصال بـ Grok API"

# ====================== جلب البيانات ======================
@st.cache_data(ttl=90)
def get_super_analysis():
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
            if price > close.rolling(50).mean().iloc[-1] > close.rolling(200).mean().iloc[-1]: score += 35
            if rsi < 35: score += 25
            if macd_hist > 0: score += 22
            if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.8: score += 18

            signal_str = "STRONG BUY 🟢🟢" if score >= 80 else "BUY 🟢" if score >= 60 else "HOLD 🟡" if score >= 40 else "SELL 🔴" if score >= 20 else "STRONG SELL 🔴🔴"

            results.append({
                "الرمز": ticker,
                "السعر": round(price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi, 1),
                "MACD": round(macd_hist, 3),
                "الإشارة": signal_str,
                "الجودة": int(score),
                "history": df,
                "info": stock.info
            })
        except:
            continue
    return results

data = get_super_analysis()
df_main = pd.DataFrame([{k: v for k, v in item.items() if k not in ['history', 'info']} for item in data])

# ====================== Mubasher News ======================
def get_mubasher_news(ticker=None):
    news = []
    try:
        url = f"https://english.mubasher.info/markets/EGX/stocks/{ticker}/news/" if ticker else "https://english.mubasher.info/markets/EGX/news/"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.find_all(['h2', 'h3', 'a'])[:10]
        for item in items:
            title = item.get_text(strip=True)
            if len(title) > 20:
                news.append({"title": title[:130], "link": url, "source": "Mubasher"})
    except:
        news.append({"title": "تعذر جلب الأخبار", "link": "#", "source": "System"})
    return news

# ====================== Sidebar - إدارة المفاتيح ======================
with st.sidebar:
    st.header("🔑 إعدادات المفاتيح السرية")
    new_key = st.text_input("Grok API Key (xAI)", type="password", value=st.session_state.grok_api_key)
    if st.button("حفظ المفتاح"):
        save_api_key(new_key)
    
    st.divider()
    st.success("🟢 النظام يعمل")
    st.caption(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")

# ====================== الواجهة الرئيسية ======================
st.title("⚡ EGX Super Analyst v13.1")
st.caption("نظام تحليلي إداري ذكي | مع إدارة المفاتيح")

col1, col2, col3, col4 = st.columns(4)
best = df_main.nlargest(1, 'الجودة').iloc[0]
col1.metric("أقوى سهم", best['الرمز'], best['الإشارة'])
col2.metric("أعلى جودة", f"{best['الجودة']}/100")
col3.metric("متوسط RSI", f"{df_main['RSI'].mean():.1f}")
col4.metric("إشارات شراء", len(df_main[df_main['الجودة'] >= 70]))

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 رادار السوق", "🔍 تحليل معمق", "📊 مؤشرات الشركات",
    "📰 Mubasher News", "🤖 Grok AI", "💼 الملخص الإداري"
])

with tab1:
    st.subheader("📈 رادار السوق")
    fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_main.sort_values('الجودة', ascending=False), use_container_width=True, hide_index=True)

with tab2:
    ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist())
    stock = next(s for s in data if s["الرمز"] == ticker)
    fig = go.Figure(data=[go.Candlestick(x=stock['history'].index, open=stock['history']['Open'],
                    high=stock['history']['High'], low=stock['history']['Low'], close=stock['history']['Close'])])
    fig.update_layout(template="plotly_dark", height=650)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("📰 Mubasher News")
    mode = st.radio("نوع الأخبار", ["عامة", "لسهم محدد"])
    sel = st.selectbox("اختر السهم", df_main['الرمز'].tolist()) if mode == "لسهم محدد" else None
    news_list = get_mubasher_news(sel)
    for n in news_list:
        with st.expander(f"📰 {n['title']}"):
            st.markdown(f"[اقرأ الخبر]({n['link']})")
            if st.button("تحليل AI", key=n['title'][:50]):
                with st.spinner("جاري التحليل..."):
                    st.success(analyze_with_grok(n['title'], sel or "السوق"))

with tab5:
    st.subheader("🤖 Grok AI Analyzer")
    ai_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist(), key="ai")
    prompt = st.text_area("اكتب سؤالك أو الصق الخبر")
    if st.button("تحليل"):
        st.info(analyze_with_grok(prompt or "تحليل شامل", ai_ticker))

with tab6:
    st.subheader("💼 الملخص الإداري")
    for _, row in df_main.nlargest(8, 'الجودة').iterrows():
        st.success(f"**{row['الرمز']}** → {row['الإشارة']} | الجودة: {row['الجودة']}/100")

# Footer
best_stock = df_main.nlargest(1, 'الجودة').iloc[0]
st.markdown(f"""
<div style="text-align:center; padding:30px; background:linear-gradient(90deg,#0a0a0a,#1a1a2e); color:#00ffaa; border-top:7px solid #00ffaa;">
    ⚡ EGX Super Analyst v13.1 | مفتاح Grok API مفعل | 
    أقوى توصية: <b>{best_stock['الرمز']}</b> — {best_stock['الإشارة']}
</div>
""", unsafe_allow_html=True)
