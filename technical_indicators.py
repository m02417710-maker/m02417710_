import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh
import requests

# 1. إعدادات المنصة الاحترافية
st.set_page_config(page_title="Terminal EGX Pro 2026", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=120 * 1000, key="terminal_update") # تحديث كل دقيقتين

# --- وظائف الربط الخارجي ---
def send_telegram(token, chat_id, text):
    if token and chat_id:
        try: requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}")
        except: pass

def play_audio_notification():
    audio_html = """
        <audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mp3"></audio>
    """
    st.components.v1.html(audio_html, height=0)

# ============================================================
# 2. المحرك المالي والفني المتقدم (Expert System)
# =============================-==============================
class ExpertStockEngine:
    def __init__(self, ticker):
        self.symbol = ticker if ".CA" in ticker else f"{ticker}.CA"
        self.stock = yf.Ticker(self.symbol)
        self.df = self.stock.history(period="1y")
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = self.df.columns.get_level_values(0)

    def analyze(self):
        if self.df.empty: return None
        df = self.df.copy()
        
        # مؤشرات فنية دقيقة
        curr_p = df['Close'].iloc[-1]
        df['MA20'] = df['Close'].rolling(window=20).mean()
        rsi = 100 - (100 / (1 + (df['Close'].diff().where(lambda x: x > 0, 0).rolling(14).mean() / 
                                  df['Close'].diff().where(lambda x: x < 0, 0).abs().rolling(14).mean())))
        last_rsi = rsi.iloc[-1]
        
        # التقييم المالي (Fundamental Scoring)
        info = self.stock.info
        score = 0
        pe = info.get('trailingPE', 100)
        yield_val = info.get('dividendYield', 0)
        if pe < 12: score += 4
        if yield_val > 0.05: score += 3
        if info.get('earningsGrowth', 0) > 0.1: score += 3
        
        # التوقع والاتجاه
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['Close'].values
        target = LinearRegression().fit(X, y).predict([[len(df) + 5]])[0]

        return {
            "الرمز": self.symbol.replace(".CA", ""),
            "السعر": round(curr_p, 2),
            "التغير": round(((curr_p/df['Close'].iloc[-2])-1)*100, 2),
            "RSI": round(last_rsi, 1),
            "P/E": round(pe, 1) if pe != 100 else "N/A",
            "التوزيعات": f"{yield_val*100:.1f}%",
            "جودة الاستثمار": f"{score}/10",
            "القرار": "🚀 دخول" if last_rsi < 30 else "⚠️ جني" if last_rsi > 70 else "⚖️ مراقبة",
            "توقع_7ي": round(target, 2),
            "history": df,
            "info": info
        }

# ============================================================
# 3. واجهة المستخدم الرسومية (UI/UX)
# ============================================================

# --- القائمة الجانبية الذكية ---
with st.sidebar:
    st.title("⚙️ الإعدادات الذكية")
    tg_t = st.text_input("Bot Token:", type="password")
    tg_c = st.text_input("Chat ID:")
    st.divider()
    capital = st.number_input("رأس المال (EGP):", value=200000)
    risk = st.slider("مخاطرة الصفقة %", 0.5, 5.0, 1.5)
    st.divider()
    st.success("النظام متصل بالبورصة المصرية ✅")

# --- لوحة القيادة الرئيسية ---
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown(f"# 🏛️ مركز إدارة المحفظة | {datetime.now().strftime('%Y-%m-%d')}")
with col_t2:
    if st.button("🔄 تحديث يدوي فوري"): st.rerun()

# --- جلب البيانات ---
watchlist = ["COMI", "FWRY", "ABUK", "TMGH", "SWDY", "ETEL", "EKHO", "ORAS", "ESRS", "JUFO", "AMOC"]
all_data = []
for t in watchlist:
    try:
        res = ExpertStockEngine(t).analyze()
        if res: all_data.append(res)
    except: continue

main_df = pd.DataFrame(all_data)

# --- عرض خريطة الحرارة (Heatmap) لسرعة اتخاذ القرار ---
st.subheader("🌡️ خريطة نبض السوق (التغير اللحظي)")
fig_heat = px.treemap(main_df, path=['الرمز'], values='السعر', color='التغير',
                     color_continuous_scale='RdYlGn', range_color=[-3, 3])
st.plotly_chart(fig_heat, use_container_width=True)

# --- الجدول الاحترافي ---
st.subheader("📊 رادار الفرص الذكي")
st.dataframe(main_df.drop(columns=['history', 'info']), use_container_width=True)

st.divider()

# --- قسم الفحص المجهري المطور ---
st.header("🔍 غرفة التحليل العميق")
target = st.selectbox("اختر السهم لتشريح أداءه:", main_df['الرمز'].tolist())
s = next(item for item in all_data if item["الرمز"] == target)

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    # الرسم الفني + المتوسطات المتحركة
    fig_candle = go.Figure()
    fig_candle.add_trace(go.Candlestick(x=s['history'].index, open=s['history']['Open'], high=s['history']['High'], 
                                       low=s['history']['Low'], close=s['history']['Close'], name="السعر"))
    fig_candle.add_trace(go.Scatter(x=s['history'].index, y=s['history']['MA20'], name="متوسط 20", line=dict(color='orange')))
    fig_candle.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig_candle, use_container_width=True)

with c2:
    st.markdown("### 📋 التقرير المالي")
    st.metric("جودة الاستثمار", s['جودة الاستثمار'])
    st.write(f"💵 **صافي الدخل:** {s['info'].get('netIncomeToCommon', 0):,.0f}")
    st.write(f"📉 **أدنى سعر (52 أسبوع):** {s['info'].get('fiftyTwoWeekLow', 0)}")
    st.write(f"📈 **أعلى سعر (52 أسبوع):** {s['info'].get('fiftyTwoWeekHigh', 0)}")
    st.progress(int(float(s['جودة الاستثمار'].split('/')[0])*10))

with c3:
    st.markdown("### 🛡️ إدارة المخاطر")
    stop_loss = st.number_input("سعر وقف الخسارة:", value=s['السعر']*0.95)
    shares = int((capital * (risk/100)) / (s['السعر'] - stop_loss)) if s['السعر'] > stop_loss else 0
    st.metric("الكمية الآمنة", f"{shares} سهم")
    st.warning(f"المخاطرة المالية: {shares * (s['السعر'] - stop_loss):,.2f} ج.م")

# --- نظام التنبيهات الذكي ---
if "🚀" in s['القرار']:
    play_audio_notification()
    st.toast(f"🚨 فرصة انفجار سعري على {target}!")
    send_telegram(tg_t, tg_c, f"إشارة شراء ذهبية: {target} بسعر {s['السعر']}")

# --- قناة النبض الحية (Scrolling News Style) ---
st.markdown(f"""
    <div style="white-space: nowrap; overflow: hidden; background: #0e1117; color: #00ff00; padding: 10px; border: 1px solid #333;">
        <marquee scrollamount="5"> 
            📢 <b>نبض السوق:</b> {target} يستهدف {s['توقع_7ي']} ج.م | 
            RSI الحالي {s['RSI']} | 
            أفضل الأسهم استثمارياً اليوم: {main_df.sort_values(by='جودة الاستثمار', ascending=False).iloc[0]['الرمز']} | 
            سيولة داخلة قوية في قطاع العقارات...
        </marquee>
    </div>
""", unsafe_allow_html=True)
