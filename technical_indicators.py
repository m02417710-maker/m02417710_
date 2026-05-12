import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from bs4 import BeautifulSoup

st.set_page_config(page_title="EGX Super Analyst v13.4", layout="wide", page_icon="⚡")

st_autorefresh(interval=90 * 1000, key="v13_4")

# ====================== Grok AI Function ======================
def analyze_with_grok(text: str, ticker: str = "السوق"):
    api_key = st.secrets.get("GROK_API_KEY")
    if not api_key:
        return "Grok API غير مفعل"
    try:
        resp = requests.post("https://api.x.ai/v1/chat/completions", 
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "grok-3", "messages": [{"role": "user", "content": text}], "temperature": 0.6})
        return resp.json()['choices'][0]['message']['content']
    except:
        return "تعذر الاتصال بـ Grok"

# ====================== التحليل الفني المتقدم ======================
@st.cache_data(ttl=90)
def get_super_analysis():
    tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO", "HELI"]
    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(f"{ticker}.CA")
            df = stock.history(period="1y")
            if df.empty or len(df) < 100: continue

            close = df['Close']
            price = close.iloc[-1]
            change_pct = ((price / close.iloc[-2]) - 1) * 100

            # Indicators
            delta = close.diff()
            rsi = (100 - (100 / (1 + (delta.clip(lower=0).rolling(14).mean() / abs(delta.clip(upper=0).rolling(14).mean()))))).iloc[-1]
            macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
            macd_hist = (macd - macd.ewm(span=9).mean()).iloc[-1]

            score = 0
            if price > close.rolling(50).mean().iloc[-1] > close.rolling(200).mean().iloc[-1]: score += 35
            if rsi < 35: score += 25
            if macd_hist > 0: score += 22
            if df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().iloc[-1] * 1.8: score += 18

            signal = "STRONG BUY 🟢🟢" if score >= 80 else "BUY 🟢" if score >= 60 else "HOLD 🟡" if score >= 40 else "SELL 🔴" if score >= 20 else "STRONG SELL 🔴🔴"

            results.append({
                "الرمز": ticker,
                "السعر": round(price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi, 1),
                "MACD": round(macd_hist, 3),
                "الإشارة": signal,
                "الجودة": int(score),
                "history": df
            })
        except:
            continue
    return results

data = get_super_analysis()
df_main = pd.DataFrame([{k: v for k, v in item.items() if k not in ['history']} for item in data])

# ====================== Backtesting Function ======================
def run_backtest(ticker, period="6mo"):
    stock = yf.Ticker(f"{ticker}.CA")
    df = stock.history(period=period)
    if df.empty: return None

    df['Signal'] = 0
    df['Position'] = 0

    # Strategy: Buy when RSI < 35 and MACD positive
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rsi = 100 - (100 / (1 + gain / loss))

    macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    signal_line = macd.ewm(span=9).mean()

    df['Signal'] = np.where((rsi < 35) & (macd > signal_line), 1, 0)
    df['Position'] = df['Signal'].diff()

    # Calculate returns
    df['Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Position'].shift(1) * df['Returns']

    # Metrics
    total_return = (1 + df['Strategy_Returns']).cumprod().iloc[-1] - 1
    win_rate = len(df[df['Strategy_Returns'] > 0]) / len(df[df['Strategy_Returns'] != 0]) * 100 if len(df[df['Strategy_Returns'] != 0]) > 0 else 0
    max_drawdown = ((1 + df['Strategy_Returns']).cumprod() / (1 + df['Strategy_Returns']).cumprod().cummax() - 1).min() * 100

    return {
        "Total Return": f"{total_return*100:.2f}%",
        "Win Rate": f"{win_rate:.1f}%",
        "Max Drawdown": f"{max_drawdown:.2f}%",
        "Number of Trades": int(df['Position'].abs().sum() / 2),
        "Equity Curve": (1 + df['Strategy_Returns']).cumprod()
    }

# ====================== الواجهة ======================
st.title("⚡ EGX Super Analyst v13.4")
st.caption("نظام تحليلي إداري ذكي | Backtesting متقدم")

tabs = st.tabs(["📈 رادار السوق", "🔍 تحليل معمق", "📊 Backtesting", "📰 Mubasher News", "🤖 Grok AI"])

with tabs[0]:
    fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_main, use_container_width=True, hide_index=True)

with tabs[2]:  # ← Backtesting Tab
    st.title("📊 Backtesting (اختبار تاريخي)")
    
    ticker_bt = st.selectbox("اختر السهم للاختبار التاريخي", df_main['الرمز'].tolist())
    period_bt = st.selectbox("فترة الاختبار", ["3mo", "6mo", "1y", "2y"], index=1)
    
    if st.button("🚀 شغل الـ Backtest"):
        with st.spinner("جاري تشغيل الاختبار التاريخي..."):
            result = run_backtest(ticker_bt, period_bt)
            
            if result:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("العائد الإجمالي", result['Total Return'])
                col2.metric("نسبة الربح", result['Win Rate'])
                col3.metric("أقصى تراجع", result['Max Drawdown'])
                col4.metric("عدد الصفقات", result['Number of Trades'])
                
                st.subheader("منحنى الأداء (Equity Curve)")
                st.line_chart(result['Equity Curve'])
            else:
                st.error("تعذر تشغيل الـ Backtest")

# باقي التبويبات (يمكن نسخها من النسخ السابقة)

# Footer
best = df_main.nlargest(1, 'الجودة').iloc[0]
st.markdown(f"""
<div style="text-align:center; padding:35px; background:linear-gradient(90deg,#0a0a0a,#1a1a2e); color:#00ffaa; border-top:8px solid #00ffaa; margin-top:40px;">
    ⚡ EGX Super Analyst v13.4 | Backtesting + تحليل ذكي | 
    أقوى توصية: <b>{best['الرمز']}</b> — {best['الإشارة']}
</div>
""", unsafe_allow_html=True)
