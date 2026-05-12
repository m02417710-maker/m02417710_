import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="EGX Master Terminal Pro v2.0", layout="wide", page_icon="🏛️")

# تحديث تلقائي كل 3 دقائق
st_autorefresh(interval=180 * 1000, key="pro_v2_refresh")

EGX_TICKERS = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO", "HELI"]

# ============================================================
# محرك التحليل الآلي (Advanced Technical Analysis)
# ============================================================
@st.cache_data(ttl=240, show_spinner=False)
def fetch_and_analyze():
    results = []
    for ticker in EGX_TICKERS:
        try:
            stock = yf.Ticker(f"{ticker}.CA")
            df = stock.history(period="1y")
            if df.empty or len(df) < 50:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close']
            volume = df['Volume']
            high = df['High']
            low = df['Low']

            # === المؤشرات الفنية ===
            # Moving Averages
            df['SMA50'] = close.rolling(50).mean()
            df['SMA200'] = close.rolling(200).mean()
            df['EMA12'] = close.ewm(span=12).mean()
            df['EMA26'] = close.ewm(span=26).mean()

            # MACD
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['Signal'] = df['MACD'].ewm(span=9).mean()
            macd_hist = df['MACD'].iloc[-1] - df['Signal'].iloc[-1]

            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            rsi_val = rsi.iloc[-1]

            # Bollinger Bands
            bb_mid = close.rolling(20).mean()
            bb_std = close.rolling(20).std()
            bb_upper = bb_mid + 2 * bb_std
            bb_lower = bb_mid - 2 * bb_std

            # Signals
            price = close.iloc[-1]
            prev_price = close.iloc[-2]
            change_pct = ((price / prev_price) - 1) * 100

            # === نظام التسجيل الآلي (0-100) ===
            score = 0

            # Trend Score
            if price > df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
                score += 25  # Uptrend قوي
            elif price > df['SMA50'].iloc[-1]:
                score += 15

            # Momentum
            if rsi_val < 35:
                score += 20
            elif rsi_val > 65:
                score -= 15

            # MACD
            if macd_hist > 0 and df['MACD'].iloc[-2] < df['Signal'].iloc[-2]:
                score += 20  # Golden Cross

            # Bollinger
            if price < bb_lower.iloc[-1]:
                score += 15
            elif price > bb_upper.iloc[-1]:
                score -= 15

            # Volume Confirmation
            if volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]:
                score += 10 if change_pct > 0 else -5

            signal = "Strong Buy 🟢" if score >= 70 else \
                     "Buy 🟢" if score >= 50 else \
                     "Hold 🟡" if score >= 30 else \
                     "Sell 🔴" if score >= 10 else "Strong Sell 🔴🔴"

            info = stock.info
            pe = info.get('trailingPE', np.nan)
            div = info.get('dividendYield', 0) or 0

            results.append({
                "الرمز": ticker,
                "السعر": round(price, 2),
                "التغير%": round(change_pct, 2),
                "RSI": round(rsi_val, 1),
                "MACD": round(macd_hist, 3),
                "P/E": round(pe, 1) if not np.isnan(pe) else "N/A",
                "توزيعات": f"{div*100:.2f}%",
                "الجودة": f"{score}/100",
                "الإشارة": signal,
                "raw_score": score,
                "history": df,
                "info": info,
                "bb_upper": bb_upper.iloc[-1],
                "bb_lower": bb_lower.iloc[-1]
            })
        except:
            continue
    return results


# ============================================================
# الواجهة الرئيسية
# ============================================================
data = fetch_and_analyze()

if not data:
    st.error("تعذر جلب البيانات")
    st.stop()

df_display = pd.DataFrame(data).drop(columns=['history', 'info'])

st.title("🏛️ EGX Master Terminal Pro v2.0")
st.caption("نظام تحليل آلي + توصيات شراء/بيع فورية | Full-Stack Professional")

tab_radar, tab_deep, tab_signals, tab_risk, tab_news = st.tabs([
    "📈 رادار السوق", 
    "🔍 تحليل معمق", 
    "🚀 التوصيات الآلية",
    "🛡️ إدارة المخاطر",
    "🗞️ نبض السوق"
])

# --- رادار السوق ---
with tab_radar:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.treemap(df_display, path=['الرمز'], values='السعر',
                        color='التغير%', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("⭐ أقوى 5 توصيات")
        top = df_display.nlargest(5, 'raw_score')
        st.dataframe(top[['الرمز', 'السعر', 'الإشارة', 'الجودة']], hide_index=True, use_container_width=True)

    st.dataframe(df_display, use_container_width=True, hide_index=True)

# --- التحليل المعمق ---
with tab_deep:
    ticker = st.selectbox("اختر السهم", df_display['الرمز'].tolist(), key="deep_select")
    stock = next(s for s in data if s["الرمز"] == ticker)
    df = stock['history']

    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="OHLC"))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="SMA50", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name="SMA200", line=dict(color='blue')))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("السعر", f"{stock['السعر']} ج.م", f"{stock['التغير%']}%")
        st.metric("الإشارة الآلية", stock['الإشارة'])
        st.metric("Score", stock['الجودة'])
        st.metric("RSI", stock['RSI'])
        st.metric("MACD Histogram", stock['MACD'])

# --- التوصيات الآلية (الجديد كلياً) ---
with tab_signals:
    st.subheader("🚀 التوصيات الآلية والأوامر الفورية")
    sorted_data = sorted(data, key=lambda x: x['raw_score'], reverse=True)
    
    for s in sorted_data[:8]:
        col_a, col_b = st.columns([1, 3])
        with col_a:
            st.subheader(s['الرمز'])
            st.success(s['الإشارة']) if "Buy" in s['الإشارة'] else st.error(s['الإشارة'])
        with col_b:
            st.write(f"**السعر:** {s['السعر']} | **Score:** {s['الجودة']} | RSI: {s['RSI']} | MACD: {s['MACD']}")
            if "Strong Buy" in s['الإشارة']:
                st.success("**أمر شراء قوي** - فرصة ممتازة للدخول")
            elif "Buy" in s['الإشارة']:
                st.info("**أمر شراء** - السهم في منطقة إيجابية")
            elif "Strong Sell" in s['الإشارة']:
                st.error("**أمر بيع قوي** - يُفضل الخروج أو البيع على المكشوف")
        st.divider()

# --- إدارة المخاطر والمحفظة ---
with tab_risk:
    st.sidebar.header("⚙️ إعدادات المحفظة")
    capital = st.sidebar.number_input("رأس المال (ج.م)", value=500000, step=10000)
    risk_per_trade = st.sidebar.slider("مخاطرة لكل صفقة (%)", 0.5, 5.0, 1.0)

    ticker_risk = st.selectbox("اختر السهم لحساب المركز", df_display['الرمز'].tolist(), key="risk_select")
    s = next(item for item in data if item["الرمز"] == ticker_risk)

    sl = st.number_input("وقف الخسارة", value=float(s['السعر'] * 0.93))
    diff = s['السعر'] - sl
    if diff > 0:
        shares = int((capital * risk_per_trade / 100) / diff)
        st.success(f"**الكمية الموصى بها: {shares:,} سهم**")
        st.info(f"قيمة المركز: {shares * s['السعر']:,.0f} ج.م")
        st.warning(f"الخسارة المحتملة: {capital * risk_per_trade / 100:,.0f} ج.م")

# --- نبض السوق ---
with tab_news:
    st.subheader("📰 نبض السوق والتوصيات اللحظية")
    for s in sorted_data:
        st.info(f"**{s['الرمز']}** → {s['الإشارة']} | Score: {s['الجودة']} | RSI: {s['RSI']} | تغير: {s['التغير%']}%")
        st.divider()

# Footer
best = max(data, key=lambda x: x['raw_score'])
st.markdown(f"""
<div style="text-align:center; padding:15px; background:#111; color:#0f0; border-top:3px solid #0f0;">
    🔥 أقوى توصية الآن: <b>{best['الرمز']}</b> — {best['الإشارة']} (Score: {best['الجودة']}) 
    • آخر تحديث: {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)
