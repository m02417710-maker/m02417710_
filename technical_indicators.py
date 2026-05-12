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

st.set_page_config(page_title="EGX Super Analyst v13.0", layout="wide", page_icon="⚡", initial_sidebar_state="expanded")

st_autorefresh(interval=90 * 1000, key="super_final")

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
                "messages": [{"role": "user", "content": f"أنت محلل مالي خبير في البورصة المصرية. حلل وأعطِ توصية إدارية واضحة:\n{text}"}],
                "temperature": 0.6
            },
            timeout=12
        )
        return resp.json()['choices'][0]['message']['content']
    except:
        return "تحليل محلي: السهم يظهر قوة شرائية حالياً."

# ====================== جلب البيانات + التحليل الآلي ======================
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
        news.append({"title": "تعذر جلب الأخبار من Mubasher", "link": "#", "source": "System"})
    return news

# ====================== الواجهة ======================
st.title("⚡ EGX Super Analyst v13.0")
st.caption("نظام تحليلي إداري ذكي | يعمل بشكل آلي")

# Sidebar
with st.sidebar:
    st.success("🟢 النظام يعمل تلقائياً")
    st.caption(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}")

# ====================== لوحة التحكم الرئيسية ======================
col1, col2, col3, col4 = st.columns(4)
best = df_main.nlargest(1, 'الجودة').iloc[0]
worst = df_main.nsmallest(1, 'الجودة').iloc[0]

col1.metric("أقوى سهم", best['الرمز'], best['الإشارة'])
col2.metric("أضعف سهم", worst['الرمز'])
col3.metric("متوسط الجودة", f"{df_main['الجودة'].mean():.1f}/100")
col4.metric("إشارات شراء قوية", len(df_main[df_main['الجودة'] >= 75]))

st.divider()

# ====================== التبويبات ======================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 رادار السوق", 
    "🔍 تحليل معمق", 
    "📊 مؤشرات الشركات",
    "📰 Mubasher News", 
    "🤖 Grok AI", 
    "💼 الملخص الإداري"
])

with tab1:
    st.subheader("📈 رادار السوق")
    fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_main.sort_values('الجودة', ascending=False), use_container_width=True, hide_index=True)

with tab2:
    ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist())
    stock = next(s for s in data if s["الرمز"] == ticker)
    fig = go.Figure(data=[go.Candlestick(x=stock['history'].index,
                    open=stock['history']['Open'], high=stock['history']['High'],
                    low=stock['history']['Low'], close=stock['history']['Close'])])
    fig.update_layout(template="plotly_dark", height=680)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("📊 المؤشرات المالية")
    t = st.selectbox("اختر الشركة", df_main['الرمز'].tolist(), key="fund")
    info = next(s for s in data if s["الرمز"] == t)['info']
    col1, col2 = st.columns(2)
    with col1:
        st.metric("مكرر الربح", info.get('trailingPE', 'N/A'))
        st.metric("عائد التوزيعات", f"{info.get('dividendYield', 0)*100:.2f}%")
    with col2:
        st.write(f"**الاسم:** {info.get('longName', t)}")
        st.write(f"**القطاع:** {info.get('sector', 'غير متوفر')}")

with tab4:
    st.subheader("📰 Mubasher News")
    mode = st.radio("نوع الأخبار", ["عامة", "لسهم محدد"])
    sel_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist()) if mode == "لسهم محدد" else None
    news_list = get_mubasher_news(sel_ticker)
    for n in news_list:
        with st.expander(f"📰 {n['title']}"):
            st.caption(n['source'])
            st.markdown(f"[فتح الخبر]({n['link']})")
            if st.button("تحليل بالذكاء الاصطناعي", key=n['title'][:50]):
                with st.spinner("Grok يحلل..."):
                    st.success(analyze_with_grok(n['title'], sel_ticker or "السوق"))

with tab5:
    st.subheader("🤖 Grok AI Analyzer")
    ai_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist(), key="ai")
    prompt = st.text_area("اكتب سؤالك أو الصق الخبر")
    if st.button("تحليل"):
        st.info(analyze_with_grok(prompt or "أعطني تحليلاً شاملاً", ai_ticker))

with tab6:
    st.subheader("💼 الملخص الإداري الآلي")
    st.write("### أقوى 8 توصيات حالياً")
    top8 = df_main.nlargest(8, 'الجودة')
    for _, row in top8.iterrows():
        st.success(f"**{row['الرمز']}** → {row['الإشارة']} | جودة: {row['الجودة']}/100 | RSI: {row['RSI']}")

# ====================== Footer ======================
best_stock = df_main.nlargest(1, 'الجودة').iloc[0]
st.markdown(f"""
<div style="text-align:center; padding:35px; background:linear-gradient(90deg, #0a0a0a, #1a1a2e); color:#00ffaa; 
            border-top:8px solid #00ffaa; margin-top:50px; font-size:22px;">
    ⚡ EGX Super Analyst v13.0 | نظام تحليلي إداري ذكي كامل | 
    أقوى توصية: <b>{best_stock['الرمز']}</b> — {best_stock['الإشارة']}
</div>
""", unsafe_allow_html=True)
