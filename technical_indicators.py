import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# 1. إعدادات المنصة الأساسية
st.set_page_config(page_title="منصة الاستثمار المتكاملة - EGX", layout="wide")
st_autorefresh(interval=300 * 1000, key="mega_update") # تحديث كل 5 دقائق

# ============================================================
# 2. المحرك الذكي الشامل (الفني + المالي + التوقعات)
# ============================================================
class MegaStockEngine:
    def __init__(self, ticker):
        # إضافة لاحقة البورصة المصرية تلقائياً إذا لم تكن موجودة
        self.symbol = ticker if ".CA" in ticker or "-" in ticker else f"{ticker}.CA"
        self.stock = yf.Ticker(self.symbol)
        # جلب البيانات التاريخية
        self.df = self.stock.history(period="1y")
        if isinstance(self.df.columns, pd.MultiIndex):
            self.df.columns = self.df.columns.get_level_values(0)

    def get_analysis(self):
        if self.df.empty: return None
        
        # --- التحليل الفني ---
        df = self.df.copy()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
        
        current_price = df['Close'].iloc[-1]
        change = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        last_rsi = rsi.iloc[-1]

        # قرار فني مبني على RSI
        if last_rsi < 35: decision = "شراء قوي 🟢"
        elif last_rsi > 65: decision = "بيع / جني أرباح 🔴"
        else: decision = "حياد / انتظار 🟡"

        # --- التحليل المالي وتوزيعات الأرباح ---
        info = self.stock.info
        fundamentals = {
            "مكرر الربحية (P/E)": info.get('trailingPE', 'N/A'),
            "مضاعف القيمة الدفترية": info.get('priceToBook', 'N/A'),
            "توزيعات الأرباح (Yield)": f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "0.00%",
            "صافي الربح": f"{info.get('netIncomeToCommon', 0):,.0f}" if info.get('netIncomeToCommon') else "N/A"
        }

        # --- التوقع الرياضي لـ 7 أيام ---
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['Close'].values
        model = LinearRegression().fit(X, y)
        future_price = model.predict([[len(df) + 7]])[0]

        return {
            "الرمز": self.symbol.replace(".CA", ""),
            "السعر": round(current_price, 2),
            "التغير": f"{change:+.2f}%",
            "القرار": decision,
            "توزيعات": fundamentals["توزيعات الأرباح (Yield)"],
            "P/E": fundamentals["مكرر الربحية (P/E)"],
            "التوقع (7ي)": round(future_price, 2),
            "RSI": round(last_rsi, 2),
            "fundamentals": fundamentals,
            "history": df
        }

# ============================================================
# 3. واجهة المستخدم (The Dashboard)
# ============================================================

st.title("🏛️ منصة الرصد والتحليل المالي والفني الشاملة")

# --- قائمة المراقبة المحدثة (EGX 100+) ---
watchlist = ["COMI", "FWRY", "ABUK", "TMGH", "SWDY", "ETEL", "EKHO", "ORAS", "ESRS", "JUFO", "PHDC", "AMOC"]

# إضافة سهم مخصص من الجانب
custom = st.sidebar.text_input("🔍 إضافة سهم للرادار (مثال: MNHD):").upper()
if custom and custom not in watchlist: watchlist.append(custom)

# --- القسم الأول: رادار فحص السوق (المسح الشامل) ---
st.header("📋 رادار السوق: تحليل فني + مالي + توزيعات")
market_data = []
progress = st.progress(0)

for i, t in enumerate(watchlist):
    try:
        engine = MegaStockEngine(t)
        res = engine.get_analysis()
        if res: market_data.append(res)
    except: continue
    progress.progress((i + 1) / len(watchlist))

if market_data:
    # عرض الجدول الرئيسي (المختصر لاتخاذ القرار)
    df_display = pd.DataFrame(market_data).drop(columns=['fundamentals', 'history'])
    st.dataframe(df_display, use_container_width=True)

st.divider()

# --- القسم الثاني: الفحص المجهري للسهم المختار ---
st.header("🎯 نافذة الفحص التفصيلي للسهم")
target = st.selectbox("اختر سهماً لتحليله بعمق:", [r["الرمز"] for r in market_data])

if target:
    # استرجاع بيانات السهم المختار من القائمة
    selected = next(item for item in market_data if item["الرمز"] == target)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 1. الرسم البياني التفاعلي (الشموع اليابانية)
        fig = go.Figure(data=[go.Candlestick(
            x=selected['history'].index, 
            open=selected['history']['Open'],
            high=selected['history']['High'], 
            low=selected['history']['Low'],
            close=selected['history']['Close']
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, title=f"حركة سعر {target}")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # 2. بطاقة الصحة المالية وتوزيعات الأرباح
        st.subheader("📊 البيانات المالية الأساسية")
        f = selected['fundamentals']
        st.write(f"💰 **توزيعات الأرباح:** {f['توزيعات الأرباح (Yield)']}")
        st.write(f"📈 **مكرر الربحية (P/E):** {f['مكرر الربحية (P/E)']}")
        st.write(f"📗 **مضاعف القيمة الدفترية:** {f['مضاعف القيمة الدفترية']}")
        st.write(f"🏢 **صافي ربح الشركة:** {f['صافي الربح']} ج.م")
        
        st.divider()
        # 3. حاسبة الاستثمار (100 سهم)
        st.subheader("🧮 حاسبة المركز المالي")
        qty = st.number_input("الكمية:", value=100)
        curr_p = selected['السعر']
        st.write(f"التكلفة الإجمالية: **{qty * curr_p:,.2f} ج.م**")
        
        target_p = selected['التوقع (7ي)']
        expected_profit = (target_p - curr_p) * qty
        st.success(f"الربح/الخسارة المتوقعة (بناءً على التوقع): **{expected_profit:,.2f} ج.م**")

# --- القسم الثالث: التنبيهات وقناة المراقبة ---
st.divider()
st.subheader("🔔 التنبيهات اللحظية")
for r in market_data:
    if "شراء" in r["القرار"]:
        st.toast(f"فرصة شراء ذهبية: {r['الرمز']}")
    if float(r["توزيعات"].replace("%","")) > 5:
        st.sidebar.warning(f"💎 سهم عالي التوزيعات: {r['الرمز']} ({r['توزيعات']})")

st.info(f"🕒 آخر تحديث شامل للبيانات: {datetime.now().strftime('%H:%M:%S')}")
