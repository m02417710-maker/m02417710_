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

st.set_page_config(page_title="EGX Super Analyst v13.2", layout="wide", page_icon="⚡")

st_autorefresh(interval=90 * 1000, key="v13_2")

# ====================== إدارة المفاتيح السرية ======================
if 'grok_key' not in st.session_state:
    st.session_state.grok_key = st.secrets.get("GROK_API_KEY", "")
if 'openai_key' not in st.session_state:
    st.session_state.openai_key = st.secrets.get("OPENAI_API_KEY", "")
if 'selected_api' not in st.session_state:
    st.session_state.selected_api = "Grok"

def save_keys(grok, openai, selected):
    st.session_state.grok_key = grok
    st.session_state.openai_key = openai
    st.session_state.selected_api = selected
    st.success("✅ تم حفظ المفاتيح بنجاح")

# ====================== دالة التحليل الموحدة (Grok + OpenAI) ======================
def analyze_with_ai(text: str, ticker: str = "السوق"):
    api_type = st.session_state.selected_api
    
    if api_type == "Grok":
        api_key = st.session_state.grok_key
        if not api_key:
            return "⚠️ مفتاح Grok API غير مفعل"
        try:
            resp = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "grok-3", "messages": [{"role": "user", "content": f"حلل: {text}"}], "temperature": 0.6},
                timeout=12
            )
            return resp.json()['choices'][0]['message']['content']
        except:
            return "❌ تعذر الاتصال بـ Grok API"
    
    else:  # OpenAI
        api_key = st.session_state.openai_key
        if not api_key:
            return "⚠️ مفتاح OpenAI API غير مفعل"
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"أنت محلل مالي خبير في البورصة المصرية. حلل وأعطِ توصية:\n{text}"}],
                    "temperature": 0.7
                },
                timeout=12
            )
            return resp.json()['choices'][0]['message']['content']
        except:
            return "❌ تعذر الاتصال بـ OpenAI API"

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

# ====================== Sidebar - إدارة المفاتيح ======================
with st.sidebar:
    st.header("🔑 إعدادات المفاتيح السرية")
    
    api_choice = st.radio("اختر خدمة الذكاء الاصطناعي", ["Grok", "OpenAI"], horizontal=True)
    
    if api_choice == "Grok":
        grok_key = st.text_input("Grok API Key (xAI)", type="password", value=st.session_state.grok_key)
        openai_key = st.session_state.openai_key
    else:
        openai_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_key)
        grok_key = st.session_state.grok_key
    
    if st.button("💾 حفظ المفاتيح"):
        save_keys(grok_key, openai_key, api_choice)

    st.divider()
    st.success(f"✅ الخدمة المفعلة: **{st.session_state.selected_api}**")

# ====================== الواجهة الرئيسية ======================
st.title("⚡ EGX Super Analyst v13.2")
st.caption("نظام تحليلي إداري ذكي | دعم Grok + OpenAI")

# ... (باقي الكود كما في النسخة السابقة مع استبدال analyze_with_grok بالدالة الجديدة)

# Footer
best_stock = df_main.nlargest(1, 'الجودة').iloc[0]
st.markdown(f"""
<div style="text-align:center; padding:30px; background:linear-gradient(90deg,#0a0a0a,#1a1a2e); color:#00ffaa; border-top:7px solid #00ffaa;">
    ⚡ EGX Super Analyst v13.2 | Grok + OpenAI | 
    أقوى توصية: <b>{best_stock['الرمز']}</b> — {best_stock['الإشارة']}
</div>
""", unsafe_allow_html=True)
