import streamlit as st
import pandas as pd
from market_engine import get_stock_intelligence
from visual_tools import create_market_heatmap, create_candle_chart
from news_feed import show_news_feed

st.set_page_config(page_title="EGX Ultimate Terminal", layout="wide")

# قائمة الأسهم الشاملة
tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC", "JUFO"]

# جلب البيانات
market_results = []
for t in tickers:
    res = get_stock_intelligence(t)
    if res: market_results.append(res)

df_main = pd.DataFrame(market_results).drop(columns=['history', 'info'])

# عرض الواجهة
st.title("🏛️ منصة البورصة المصرية الكاملة")

col_a, col_b = st.columns([2, 1])
with col_a:
    st.subheader("🌡️ خريطة نبض السوق")
    st.plotly_chart(create_market_heatmap(df_main), use_container_width=True)

with col_b:
    st.subheader("📋 رادار التوزيعات")
    st.table(df_main[['الرمز', 'السعر', 'توزيعات', 'القرار']].head(6))

st.divider()
show_news_feed(market_results)

# شريط النبض السفلي
st.markdown(f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #000; color: #0f0; padding: 5px; text-align: center; z-index: 100;">
        <marquee scrollamount="5">🚀 نبض السوق: أفضل جودة استثمار حالياً في سهم {df_main.iloc[0]['الرمز']} | تم تحديث البيانات بنجاح</marquee>
    </div>
""", unsafe_allow_html=True)
import streamlit as st

def show_news_feed(all_stocks):
    st.subheader("🗞️ نبض أخبار الشركات")
    for stock in all_stocks[:10]:
        # تم استخدام مفتاح 'القرار' الموحد لتجنب KeyError
        st.write(f"📢 **{stock['الرمز']}**: يسجل RSI {stock['RSI']} وحالته الآن **{stock['القرار']}**. توزيعات الأرباح المتوقعة: {stock['توزيعات']}")
        st.divider()
        def calculate_position_size(capital, risk_pct, current_price, stop_loss):
    risk_amount = capital * (risk_pct / 100)
    price_diff = current_price - stop_loss
    
    if price_diff <= 0:
        return 0, "سعر الوقف يجب أن يكون أقل من السعر الحالي"
    
    quantity = int(risk_amount / price_diff)
    total_value = quantity * current_price
    
    return quantity, total_value
    
import plotly.graph_objects as go
import plotly.express as px

def create_market_heatmap(df):
    # إنشاء خريطة الحرارة بناءً على السعر والتغير
    fig = px.treemap(df, path=['الرمز'], values='السعر', color='التغير',
                     color_continuous_scale='RdYlGn', range_color=[-3, 3])
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=400)
    return fig

def create_candle_chart(df, ticker_name):
    # رسم الشموع اليابانية
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], 
                    high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, title=f"تحليل سهم {ticker_name}")
    return fig
import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_intelligence(ticker):
    symbol = f"{ticker}.CA"
    stock = yf.Ticker(symbol)
    df = stock.history(period="1y")
    
    if df.empty: return None
    
    # معالجة مشكلة Multi-Index لضمان استقرار الجداول
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # حساب مؤشر القوة النسبية RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs.fillna(0)))
    
    info = stock.info
    curr_p = df['Close'].iloc[-1]
    
    # تجميع البيانات المالية والفنية
    return {
        "الرمز": ticker,
        "السعر": round(curr_p, 2),
        "التغير": round(((curr_p / df['Close'].iloc[-2]) - 1) * 100, 2),
        "RSI": round(rsi.iloc[-1], 1),
        "توزيعات": f"{info.get('dividendYield', 0)*100:.2f}%",
        "القرار": "دخول ذهبي 🟢" if rsi.iloc[-1] < 35 else "جني أرباح 🔴" if rsi.iloc[-1] > 65 else "مراقبة 🟡",
        "history": df,
        "info": info
    }
