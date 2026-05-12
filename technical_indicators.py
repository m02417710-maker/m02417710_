import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="EGX Master Terminal v12.1", layout="wide", page_icon="🏛️")

st_autorefresh(interval=120 * 1000, key="v12_mubasher")

# ====================== Grok AI ======================
def analyze_with_grok(text: str, ticker: str = ""):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "Grok API غير مفعل. أضف المفتاح في secrets.toml"
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "grok-3",
                "messages": [{"role": "user", "content": f"حلل هذا الخبر لسهم {ticker} في EGX وأعطِ توصية واضحة:\n{text}"}],
                "temperature": 0.6
            },
            timeout=12
        )
        return resp.json()['choices'][0]['message']['content']
    except:
        return "تعذر الاتصال بـ Grok API"

# ====================== جلب أخبار Mubasher (Scraping) ======================
@st.cache_data(ttl=300)
def get_mubasher_news(ticker=None, limit=8):
    news = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        if ticker:
            url = f"https://english.mubasher.info/markets/EGX/stocks/{ticker}/news/"
        else:
            url = "https://english.mubasher.info/markets/EGX/news/"
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن العناصر (حسب هيكل الموقع)
        items = soup.find_all(['div', 'article'], class_=lambda x: x and ('news' in x.lower() or 'item' in x.lower()))[:limit]
        
        for item in items:
            title_tag = item.find(['h2', 'h3', 'a'])
            title = title_tag.get_text(strip=True) if title_tag else "خبر من Mubasher"
            link = title_tag.get('href') if title_tag else url
            if not link.startswith('http'):
                link = "https://english.mubasher.info" + link
            
            news.append({
                "title": title[:120],
                "link": link,
                "source": "Mubasher Info",
                "time": "حديث"
            })
    except Exception as e:
        # Fallback
        news.append({"title": "تعذر جلب الأخبار مباشرة من Mubasher", "link": "#", "source": "System", "time": ""})
    
    return news

# ====================== البيانات الرئيسية ======================
@st.cache_data(ttl=150)
def get_market_data():
    # ... (نفس الكود السابق لجلب yfinance)
    # (يمكنك نسخه من الردود السابقة)
    pass  # اختصار للطول

data = get_market_data()
df_main = pd.DataFrame([{k:v for k,v in d.items() if k not in ['history','info']} for d in data])

# ====================== التبويب الرئيسي للأخبار ======================
st.title("📰 Mubasher News - الأخبار الحية")

col1, col2 = st.columns([1, 3])
with col1:
    news_mode = st.radio("نوع الأخبار", ["أخبار عامة", "أخبار سهم محدد"])
    selected_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist()) if news_mode == "أخبار سهم محدد" else None

with col2:
    if st.button("🔄 تحديث الأخبار من Mubasher"):
        st.cache_data.clear()

news_list = get_mubasher_news(selected_ticker)

for item in news_list:
    with st.expander(f"📰 {item['title']}"):
        st.caption(f"المصدر: {item['source']} | {item.get('time', '')}")
        st.markdown(f"[اقرأ الخبر كاملاً]({item['link']})")
        
        if st.button("🤖 تحليل الخبر بـ Grok AI", key=item['title'][:30]):
            with st.spinner("جاري التحليل الذكي..."):
                analysis = analyze_with_grok(item['title'], selected_ticker or "السوق")
                st.success(analysis)

st.divider()
st.caption("⚠️ يتم سحب الأخبار مباشرة من Mubasher Info عبر Scraping. المحتوى يخضع لحقوق الموقع.")

# Footer
best = max(data, key=lambda x: x.get('الجودة', 0))
st.markdown(f"""
<div style="text-align:center; padding:25px; background:linear-gradient(90deg,#0a0a0a,#1a1a2e); color:#00ffcc; border-top:5px solid #00ffcc;">
    v12.1 | Mubasher Live News + Grok AI | أقوى توصية: <b>{best['الرمز']}</b> — {best['الإشارة']}
</div>
""", unsafe_allow_html=True)
