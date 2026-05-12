import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="EGX Super Analyst v13.6", layout="wide", page_icon="⚡")

st_autorefresh(interval=90 * 1000, key="v13_6")

st.title("⚡ EGX Super Analyst v13.6")
st.caption("نظام تحليلي ذكي | Backtesting متقدم")

# ====================== Sidebar - اختيار السوق ======================
with st.sidebar:
    st.header("🌍 اختر السوق")
    market = st.radio("السوق", ["🇪🇬 السوق المصري", "🌍 الأسواق العالمية"])
    tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC"] if "مصري" in market else \
              ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD"]

# ====================== Backtesting Engine ======================
def run_advanced_backtest(ticker, strategy="RSI_MACD", period="1y"):
    df = yf.Ticker(f"{ticker}{'.CA' if 'مصري' in market else ''}").history(period=period)
    if df.empty: return None

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    initial_capital = 100000
    df['Returns'] = df['Close'].pct_change()

    # --- استراتيجيات متعددة ---
    if strategy == "RSI_MACD":
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss))
        macd = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        signal = macd.ewm(span=9).mean()
        df['Signal'] = np.where((rsi < 35) & (macd > signal), 1, 0)

    elif strategy == "MA_Crossover":
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        df['Signal'] = np.where(df['MA50'] > df['MA200'], 1, 0)

    elif strategy == "Bollinger":
        bb_mid = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['Signal'] = np.where(df['Close'] < (bb_mid - 2*bb_std), 1, 0)

    df['Position'] = df['Signal'].diff()
    df['Strategy_Returns'] = df['Position'].shift(1) * df['Returns']
    df['Equity'] = initial_capital * (1 + df['Strategy_Returns']).cumprod()

    # Metrics
    total_return = (df['Equity'].iloc[-1] / initial_capital - 1) * 100
    buy_hold_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
    sharpe = (df['Strategy_Returns'].mean() / df['Strategy_Returns'].std() * np.sqrt(252)) if df['Strategy_Returns'].std() != 0 else 0
    max_dd = ((df['Equity'] / df['Equity'].cummax() - 1).min()) * 100
    win_rate = len(df[df['Strategy_Returns'] > 0]) / len(df[df['Strategy_Returns'] != 0]) * 100 if len(df[df['Strategy_Returns'] != 0]) > 0 else 0

    return {
        "Strategy_Return": round(total_return, 2),
        "Buy_Hold_Return": round(buy_hold_return, 2),
        "Sharpe_Ratio": round(sharpe, 2),
        "Max_Drawdown": round(max_dd, 2),
        "Win_Rate": round(win_rate, 1),
        "Equity_Curve": df['Equity'],
        "Trades": int(df['Position'].abs().sum() / 2)
    }

# ====================== التبويبات ======================
tab1, tab2, tab3, tab4 = st.tabs(["📈 رادار السوق", "📊 Backtesting متقدم", "📰 الأخبار", "🤖 AI Analyzer"])

with tab1:
    fig = px.treemap(df_main, path=['الرمز'], values='السعر', color='التغير%', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_main, use_container_width=True, hide_index=True)

with tab2:
    st.title("📊 Backtesting متقدم")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        bt_ticker = st.selectbox("اختر السهم", df_main['الرمز'].tolist())
        strategy = st.selectbox("الاستراتيجية", ["RSI_MACD", "MA_Crossover", "Bollinger"])
        period = st.selectbox("الفترة", ["3mo", "6mo", "1y", "2y"], index=2)
    
    with col2:
        if st.button("🚀 تشغيل Backtesting", type="primary"):
            with st.spinner("جاري تشغيل الاختبار التاريخي..."):
                result = run_advanced_backtest(bt_ticker, strategy, period)
                
                if result:
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("عائد الاستراتيجية", f"{result['Strategy_Return']}%")
                    c2.metric("عائد Buy & Hold", f"{result['Buy_Hold_Return']}%")
                    c3.metric("Sharpe Ratio", result['Sharpe_Ratio'])
                    c4.metric("Win Rate", f"{result['Win_Rate']}%")
                    c5.metric("Max Drawdown", f"{result['Max_Drawdown']}%")
                    
                    st.subheader("منحنى الأداء")
                    st.line_chart(result['Equity_Curve'])
                    
                    st.success(f"عدد الصفقات: {result['Trades']}")

# Footer
best = df_main.nlargest(1, 'الجودة').iloc[0]
st.markdown(f"""
<div style="text-align:center; padding:30px; background:linear-gradient(90deg,#0a0a0a,#1a1a2e); color:#00ffaa; border-top:7px solid #00ffaa;">
    ⚡ EGX Super Analyst v13.6 | Backtesting متقدم + دعم عالمي | 
    أقوى سهم: <b>{best['الرمز']}</b> — {best['الإشارة']}
</div>
""", unsafe_allow_html=True)
