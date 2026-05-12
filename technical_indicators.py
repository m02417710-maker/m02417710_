import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
st.set_page_config(page_title="⚡ EGX Super Analyst Pro", layout="wide", page_icon="⚡")

# Auto-refresh every 90 seconds
st_autorefresh(interval=90 * 1000, key="auto_refresh")

# Custom CSS for Glassmorphism styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');

    * { font-family: 'Cairo', sans-serif !important; }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .stock-up { color: #10b981; font-weight: bold; }
    .stock-down { color: #ef4444; font-weight: bold; }
    .gold-text { color: #fbbf24; font-weight: bold; }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #10b981;
        font-size: 12px;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .priority-high { border-right: 3px solid #ef4444; }
    .priority-medium { border-right: 3px solid #f59e0b; }
    .priority-low { border-right: 3px solid #10b981; }

    .tag-work { background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-personal { background: rgba(139, 92, 246, 0.2); color: #a78bfa; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-urgent { background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 8px; border-radius: 6px; font-size: 12px; }
    .tag-learning { background: rgba(6, 182, 212, 0.2); color: #22d3ee; padding: 2px 8px; border-radius: 6px; font-size: 12px; }

    .task-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s;
    }

    .task-item:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.2) !important;
        color: #818cf8 !important;
    }

    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; }
    div[data-testid="stMetricDelta"] { font-size: 14px !important; }

    .news-item {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: rgba(255, 255, 255, 0.03);
        border-right: 3px solid;
    }

    .news-positive { border-color: #10b981; }
    .news-negative { border-color: #ef4444; }
    .news-neutral { border-color: #6b7280; }

    .signal-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .signal-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .signal-hold {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.05));
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }

    .prediction-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
    }

    .indicator-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .warning-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "مراجعة أداء سهم CIB", "priority": "high", "category": "work", "due": "2026-05-15", "completed": False, "created": "2026-05-10"},
        {"id": 2, "title": "تحليل تقرير البورصة الأسبوعي", "priority": "medium", "category": "work", "due": "2026-05-16", "completed": True, "created": "2026-05-09"},
        {"id": 3, "title": "قراءة كتاب الاستثمار الذكي", "priority": "low", "category": "learning", "due": "2026-05-20", "completed": False, "created": "2026-05-08"},
        {"id": 4, "title": "متابعة اجتماع عمومية البنك التجاري", "priority": "high", "category": "urgent", "due": "2026-05-14", "completed": False, "created": "2026-05-12"},
        {"id": 5, "title": "تحديث بيانات المحفظة الاستثمارية", "priority": "medium", "category": "personal", "due": "2026-05-13", "completed": False, "created": "2026-05-11"},
    ]

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"symbol": "COMI", "name": "CIB", "quantity": 500, "buy_price": 47.50, "current_price": 50.25},
        {"symbol": "SWDY", "name": "السويدي", "quantity": 1200, "buy_price": 11.20, "current_price": 12.80},
        {"symbol": "ISPH", "name": "العاصمة", "quantity": 3000, "buy_price": 8.50, "current_price": 8.95},
        {"symbol": "EFIH", "name": "e-Finance", "quantity": 800, "buy_price": 20.10, "current_price": 22.30},
        {"symbol": "ORAS", "name": "أوراسكوم", "quantity": 1500, "buy_price": 9.10, "current_price": 9.75},
    ]

# ==================== DATA ====================
stocks_data = [
    {"symbol": "COMI", "name": "البنك التجاري الدولي - CIB", "sector": "بنوك", "price": 50.25, "change": 1.85, "change_pct": 3.82, "volume": 12500000, "high": 51.00, "low": 49.10},
    {"symbol": "FWRY", "name": "فوري لتكنولوجيا البنوك", "sector": "تكنولوجيا مالية", "price": 28.40, "change": 0.92, "change_pct": 3.35, "volume": 8900000, "high": 29.10, "low": 27.80},
    {"symbol": "TMGH", "name": "طلعت مصطفى", "sector": "عقارات", "price": 15.80, "change": 0.35, "change_pct": 2.26, "volume": 6700000, "high": 16.20, "low": 15.40},
    {"symbol": "ABUK", "name": "أبو قير للأسمدة", "sector": "صناعة", "price": 32.15, "change": -0.45, "change_pct": -1.38, "volume": 5400000, "high": 33.00, "low": 31.80},
    {"symbol": "SWDY", "name": "السويدي إلكتريك", "sector": "صناعة", "price": 12.80, "change": 0.45, "change_pct": 3.64, "volume": 6700000, "high": 13.15, "low": 12.40},
    {"symbol": "EKHO", "name": "العربية للخزف", "sector": "صناعة", "price": 5.65, "change": -0.15, "change_pct": -2.59, "volume": 3400000, "high": 5.90, "low": 5.50},
    {"symbol": "ETEL", "name": "Telecom Egypt", "sector": "اتصالات", "price": 22.30, "change": 0.55, "change_pct": 2.53, "volume": 7800000, "high": 22.85, "low": 21.90},
    {"symbol": "ORAS", "name": "أوراسكوم للإنشاءات", "sector": "مقاولات", "price": 9.75, "change": 0.22, "change_pct": 2.31, "volume": 7800000, "high": 10.00, "low": 9.50},
    {"symbol": "AMOC", "name": "Alexandria Oil", "sector": "بترول", "price": 18.90, "change": 0.68, "change_pct": 3.73, "volume": 4500000, "high": 19.40, "low": 18.30},
    {"symbol": "PHDC", "name": "القاهرة للاستثمار", "sector": "عقارات", "price": 8.25, "change": 0.12, "change_pct": 1.48, "volume": 3200000, "high": 8.50, "low": 8.10},
]

news_data = [
    {"time": "14:30", "title": "EGX30 يتجاوز 24800 نقطة للمرة الأولى منذ 2022", "type": "positive"},
    {"time": "14:15", "title": "CIB يعلن عن توزيع أرباح نقدية 2.5 جنيه للسهم", "type": "positive"},
    {"time": "13:45", "title": "تراجع طفيف في مؤشر EGX100 مع جني الأرباح", "type": "negative"},
    {"time": "13:20", "title": "المركزي: استقرار سعر الصرف عند 30.85 للدولار", "type": "neutral"},
    {"time": "12:50", "title": "e-Finance توقع اتفاقية رقمية مع الحكومة", "type": "positive"},
    {"time": "12:15", "title": "ارتفاع حجم التداولات إلى 1.8 مليار جنيه", "type": "positive"},
    {"time": "11:30", "title": "فوري تعلن عن نمو أرباح الربع الأول بنسبة 25%", "type": "positive"},
    {"time": "10:45", "title": "ضغوط بيعية على قطاع الأسمدة", "type": "negative"},
]

# ==================== ADVANCED TECHNICAL ANALYSIS ENGINE ====================
def calculate_technical_indicators(df):
    """Calculate comprehensive technical indicators"""
    df = df.copy()

    # RSI (14)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
    df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

    # Stochastic Oscillator
    low_14 = df['Low'].rolling(14).min()
    high_14 = df['High'].rolling(14).max()
    df['Stoch_K'] = 100 * (df['Close'] - low_14) / (high_14 - low_14)
    df['Stoch_D'] = df['Stoch_K'].rolling(3).mean()

    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['SMA_200'] = df['Close'].rolling(200).mean()
    df['EMA_20'] = df['Close'].ewm(span=20).mean()

    # Average True Range (ATR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()

    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

    # Price momentum
    df['Momentum'] = df['Close'] / df['Close'].shift(10) - 1
    df['ROC'] = (df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12) * 100

    return df

def generate_trading_signals(df):
    """Generate buy/sell/hold signals based on multiple indicators"""
    signals = []

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    # RSI signals
    if latest['RSI'] < 30:
        signals.append(("RSI", "شراء قوي", 2, "السهم في منطقة ذروة البيع"))
    elif latest['RSI'] > 70:
        signals.append(("RSI", "بيع قوي", -2, "السهم في منطقة ذروة الشراء"))
    elif latest['RSI'] < 45:
        signals.append(("RSI", "شراء ضعيف", 1, "إشارة شراء محتملة"))
    elif latest['RSI'] > 55:
        signals.append(("RSI", "بيع ضعيف", -1, "إشارة بيع محتملة"))
    else:
        signals.append(("RSI", "محايد", 0, "لا توجد إشارة واضحة"))

    # MACD signals
    if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
        signals.append(("MACD", "شراء", 2, "تقاطع صاعد للماكد"))
    elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
        signals.append(("MACD", "بيع", -2, "تقاطع هابط للماكد"))
    elif latest['MACD'] > latest['MACD_Signal']:
        signals.append(("MACD", "شراء ضعيف", 1, "المacd فوق خط الإشارة"))
    else:
        signals.append(("MACD", "بيع ضعيف", -1, "المacd تحت خط الإشارة"))

    # Bollinger Bands signals
    if latest['Close'] < latest['BB_Lower']:
        signals.append(("Bollinger", "شراء قوي", 2, "السعر تحت النطاق السفلي"))
    elif latest['Close'] > latest['BB_Upper']:
        signals.append(("Bollinger", "بيع قوي", -2, "السعر فوق النطاق العلوي"))
    elif latest['Close'] < latest['BB_Middle']:
        signals.append(("Bollinger", "شراء ضعيف", 0.5, "السعر في النصف السفلي"))
    else:
        signals.append(("Bollinger", "بيع ضعيف", -0.5, "السعر في النصف العلوي"))

    # Stochastic signals
    if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
        signals.append(("Stochastic", "شراء", 1.5, "مؤشر ستوكاستيك في منطقة ذروة البيع"))
    elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
        signals.append(("Stochastic", "بيع", -1.5, "مؤشر ستوكاستيك في منطقة ذروة الشراء"))
    else:
        signals.append(("Stochastic", "محايد", 0, "لا توجد إشارة"))

    # Moving Average signals
    if latest['Close'] > latest['SMA_20'] and latest['Close'] > latest['SMA_50']:
        signals.append(("MA", "شراء", 1, "السعر فوق المتوسطات المتحركة"))
    elif latest['Close'] < latest['SMA_20'] and latest['Close'] < latest['SMA_50']:
        signals.append(("MA", "بيع", -1, "السعر تحت المتوسطات المتحركة"))
    else:
        signals.append(("MA", "محايد", 0, "إشارات متضاربة من المتوسطات"))

    # Volume confirmation
    if latest['Volume_Ratio'] > 1.5:
        signals.append(("Volume", "تأكيد", 0.5, "حجم تداول أعلى من المتوسط"))
    elif latest['Volume_Ratio'] < 0.5:
        signals.append(("Volume", "ضعف", -0.5, "حجم تداول منخفض"))
    else:
        signals.append(("Volume", "محايد", 0, "حجم تداول طبيعي"))

    return signals

def calculate_overall_signal(signals):
    """Calculate overall trading signal from individual indicators"""
    total_score = sum([s[2] for s in signals])

    if total_score >= 3:
        return "STRONG_BUY", total_score, "إشارة شراء قوية"
    elif total_score >= 1.5:
        return "BUY", total_score, "إشارة شراء"
    elif total_score <= -3:
        return "STRONG_SELL", total_score, "إشارة بيع قوية"
    elif total_score <= -1.5:
        return "SELL", total_score, "إشارة بيع"
    else:
        return "HOLD", total_score, "انتظار/محايد"

def predict_future_prices(df, days=5):
    """Predict future prices using multiple methods"""
    predictions = {}

    try:
        # Method 1: Linear Regression with trend
        prices = df['Close'].dropna().values
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices

        # Polynomial features for better fit
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        # Predict next days
        future_X = np.arange(len(prices), len(prices) + days).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        linear_pred = model.predict(future_X_poly)

        # Method 2: Moving Average extrapolation
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]

        # Trend direction
        if ma20 > ma50:
            trend_factor = 1.002  # Slight upward adjustment
        elif ma20 < ma50:
            trend_factor = 0.998  # Slight downward adjustment
        else:
            trend_factor = 1.0

        ma_pred = [prices[-1] * (trend_factor ** i) for i in range(1, days + 1)]

        # Method 3: Average of methods with confidence intervals
        combined_pred = []
        for i in range(days):
            avg = (linear_pred[i] + ma_pred[i]) / 2
            volatility = df['Close'].pct_change().std() * prices[-1]
            combined_pred.append({
                'day': i + 1,
                'predicted': round(avg, 2),
                'lower_bound': round(avg - volatility * 1.5, 2),
                'upper_bound': round(avg + volatility * 1.5, 2),
                'confidence': max(0, min(100, 100 - (i * 15)))  # Confidence decreases with time
            })

        predictions['linear'] = linear_pred.tolist()
        predictions['moving_average'] = ma_pred
        predictions['combined'] = combined_pred

    except Exception as e:
        predictions['error'] = str(e)

    return predictions

def calculate_support_resistance(df, window=20):
    """Calculate dynamic support and resistance levels"""
    recent = df.tail(window)

    # Support levels (recent lows)
    lows = recent['Low'].nsmallest(3).values
    supports = [round(l, 2) for l in lows]

    # Resistance levels (recent highs)
    highs = recent['High'].nlargest(3).values
    resistances = [round(h, 2) for h in highs]

    # Fibonacci levels from recent swing
    swing_high = recent['High'].max()
    swing_low = recent['Low'].min()
    diff = swing_high - swing_low

    fib_levels = {
        '0%': round(swing_high, 2),
        '23.6%': round(swing_high - 0.236 * diff, 2),
        '38.2%': round(swing_high - 0.382 * diff, 2),
        '50%': round(swing_high - 0.5 * diff, 2),
        '61.8%': round(swing_high - 0.618 * diff, 2),
        '78.6%': round(swing_high - 0.786 * diff, 2),
        '100%': round(swing_low, 2)
    }

    return {
        'supports': supports,
        'resistances': resistances,
        'fibonacci': fib_levels,
        'current': round(df['Close'].iloc[-1], 2)
    }

# ==================== BACKTESTING ENGINE ====================
def run_advanced_backtest(ticker, strategy="RSI_MACD", period="1y", market_type="EGX"):
    try:
        suffix = ".CA" if market_type == "EGX" else ""
        df = yf.Ticker(f"{ticker}{suffix}").history(period=period)
        if df.empty:
            return None

        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        initial_capital = 100000
        df['Returns'] = df['Close'].pct_change()

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

        elif strategy == "Mean_Reversion":
            df['MA20'] = df['Close'].rolling(20).mean()
            df['Deviation'] = (df['Close'] - df['MA20']) / df['MA20']
            df['Signal'] = np.where(df['Deviation'] < -0.03, 1, np.where(df['Deviation'] > 0.03, -1, 0))

        df['Position'] = df['Signal'].diff().fillna(0)
        df['Strategy_Returns'] = df['Position'].shift(1) * df['Returns']
        df['Equity'] = initial_capital * (1 + df['Strategy_Returns']).cumprod()

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
            "Trades": int(df['Position'].abs().sum() / 2),
            "Data": df
        }
    except Exception as e:
        st.error(f"Error in backtesting: {str(e)}")
        return None


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 16px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 28px;">⚡</div>
        <h2 style="margin-top: 12px; font-size: 20px;">EGX Super Analyst</h2>
        <p style="color: #94a3b8; font-size: 12px;">Pro v15.0 - AI Powered</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("🌍 اختيار السوق")
    market = st.radio("", ["🇪🇬 السوق المصري", "🌍 الأسواق العالمية"], label_visibility="collapsed")
    is_egypt = "مصري" in market

    tickers = ["COMI", "FWRY", "TMGH", "ABUK", "SWDY", "EKHO", "ETEL", "ORAS", "AMOC", "PHDC"] if is_egypt else               ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "INTC", "NFLX"]

    st.divider()

    # Portfolio Summary in Sidebar
    st.header("💼 ملخص المحفظة")
    port_value = sum(p["quantity"] * p["current_price"] for p in st.session_state.portfolio)
    port_cost = sum(p["quantity"] * p["buy_price"] for p in st.session_state.portfolio)
    port_pl = port_value - port_cost
    port_pl_pct = (port_pl / port_cost) * 100 if port_cost > 0 else 0

    st.markdown(f"""
    <div class="metric-card">
        <p style="color: #94a3b8; font-size: 12px; margin-bottom: 4px;">القيمة الحالية</p>
        <p class="gold-text" style="font-size: 20px;">ج.م {port_value:,.0f}</p>
        <p style="color: {'#10b981' if port_pl >= 0 else '#ef4444'}; font-size: 14px; margin-top: 4px;">
            {'+' if port_pl >= 0 else ''}{port_pl:,.0f} ({port_pl_pct:+.2f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.header("📊 إحصائيات المهام")
    total_tasks = len(st.session_state.tasks)
    completed = sum(1 for t in st.session_state.tasks if t["completed"])
    pending = total_tasks - completed
    high_priority = sum(1 for t in st.session_state.tasks if t["priority"] == "high" and not t["completed"])

    col1, col2 = st.columns(2)
    col1.metric("الكل", total_tasks)
    col2.metric("مكتمل", completed)
    col1.metric("قيد التنفيذ", pending)
    col2.metric("عالية الأولوية", high_priority, delta_color="inverse")

# ==================== HEADER ====================
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
    <div>
        <h1 style="margin: 0; font-size: 32px; background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚡ EGX Super Analyst Pro</h1>
        <p style="color: #94a3b8; margin-top: 4px; font-size: 14px;">
            <span class="live-indicator"><span class="live-dot"></span> السوق مفتوح | آخر تحديث: {}</span>
        </p>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div class="glass-card" style="padding: 8px 16px;">
            <span style="color: #94a3b8; font-size: 12px;">EGX30</span>
            <span class="stock-up" style="margin-right: 8px; font-size: 18px;">24,850</span>
            <span class="stock-up" style="font-size: 12px;">+1.24%</span>
        </div>
    </div>
</div>
""".format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 رادار السوق", 
    "🔮 التحليل الذكي والتوقعات", 
    "📊 Backtesting متقدم", 
    "💼 محفظتي", 
    "✅ المهام الذكية", 
    "📰 الأخبار والتحليل"
])

# ==================== TAB 1: MARKET RADAR ====================
with tab1:
    # Market Indices
    cols = st.columns(3)
    indices = [
        {"name": "EGX30", "value": 24850.32, "change": 1.24, "color": "#10b981"},
        {"name": "EGX70", "value": 3245.18, "change": 0.89, "color": "#10b981"},
        {"name": "EGX100", "value": 8932.45, "change": -0.34, "color": "#ef4444"},
    ]

    for i, idx in enumerate(indices):
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">{idx['name']}</p>
                <h2 style="font-size: 36px; margin: 0; color: {'#10b981' if idx['change'] >= 0 else '#ef4444'};">{idx['value']:,.2f}</h2>
                <p style="color: {'#10b981' if idx['change'] >= 0 else '#ef4444'}; font-size: 16px; margin-top: 8px;">
                    {'▲' if idx['change'] >= 0 else '▼'} {abs(idx['change']):.2f}%
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Treemap
    st.subheader("🗺️ خريطة السوق التفاعلية")
    df_main = pd.DataFrame(stocks_data)
    df_main['السعر'] = df_main['price']
    df_main['التغير%'] = df_main['change_pct']
    df_main['الرمز'] = df_main['symbol']
    df_main['الحجم'] = df_main['volume']

    fig_treemap = px.treemap(
        df_main,
        path=[px.Constant("EGX"), 'sector', 'symbol'],
        values='volume',
        color='change_pct',
        color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
        color_continuous_midpoint=0,
        title="حجم التداول والأداء حسب القطاع"
    )
    fig_treemap.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Cairo", color="white"),
        height=500
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    # Stock Table
    st.subheader("📋 أسعار الأسهم الرئيسية")

    search_col, sector_col = st.columns([2, 1])
    with search_col:
        search = st.text_input("🔍 البحث في الأسهم", placeholder="ابحث بالرمز أو الاسم...")
    with sector_col:
        sector_filter = st.selectbox("القطاع", ["الكل"] + list(df_main['sector'].unique()))

    filtered_df = df_main.copy()
    if search:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search, case=False) | filtered_df['symbol'].str.contains(search, case=False)]
    if sector_filter != "الكل":
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    def make_styler(df):
        def color_change(val):
            if isinstance(val, (int, float)):
                color = '#10b981' if val >= 0 else '#ef4444'
                return f'color: {color}; font-weight: bold;'
            return ''

        styled = df.style
        for col in ['التغير', 'التغير %']:
            if col in df.columns:
                styled = styled.map(color_change, subset=[col])
        return styled

    display_df = filtered_df[['symbol', 'name', 'sector', 'price', 'change', 'change_pct', 'volume']].copy()
    display_df.columns = ['الرمز', 'الشركة', 'القطاع', 'السعر', 'التغير', 'التغير %', 'الحجم']
    display_df['الحجم'] = (display_df['الحجم'] / 1000000).round(2).astype(str) + 'M'

    st.dataframe(
        make_styler(display_df),
        use_container_width=True,
        hide_index=True,
        column_config={
            "السعر": st.column_config.NumberColumn(format="%.2f ج.م"),
            "التغير": st.column_config.NumberColumn(format="%.2f"),
            "التغير %": st.column_config.NumberColumn(format="%.2f%%"),
        }
    )

    # Top Movers
    st.subheader("🚀 الأكثر نشاطاً")
    movers_cols = st.columns(5)
    top_movers = df_main.nlargest(5, 'change_pct')

    for i, (_, stock) in enumerate(top_movers.iterrows()):
        with movers_cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <p style="color: #fbbf24; font-weight: bold; font-size: 14px;">{stock['symbol']}</p>
                <p style="font-size: 18px; font-weight: bold; margin: 4px 0;">{stock['price']:.2f}</p>
                <p style="color: #10b981; font-size: 14px;">+{stock['change_pct']:.2f}%</p>
                <p style="color: #94a3b8; font-size: 11px;">{(stock['volume']/1000000):.1f}M حجم</p>
            </div>
            """, unsafe_allow_html=True)


# ==================== TAB 2: AI ANALYSIS & PREDICTIONS ====================
with tab2:
    st.title("🔮 التحليل الذكي والتوقعات المستقبلية")

    # Warning
    st.markdown("""
    <div class="warning-box">
        <p style="color: #f87171; font-weight: bold; margin: 0;">⚠️ تحذير هام</p>
        <p style="color: #fca5a5; font-size: 13px; margin-top: 8px;">
        التوقعات والإشارات المعروضة هي نتائج تحليل رياضي للبيانات التاريخية فقط. 
        لا تعتبر توصية استثمارية. السوق يتأثر بعوامل لا يمكن التنبؤ بها. 
        استشر مستشار مالي قبل اتخاذ أي قرار استثماري.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stock Selection
    analysis_stock = st.selectbox("📌 اختر السهم للتحليل الذكي", tickers, key="ai_stock")
    analysis_period = st.selectbox("📅 الفترة التحليلية", ["1mo", "3mo", "6mo", "1y", "2y"], index=2, key="ai_period")

    if st.button("🔮 تشغيل التحليل الذكي", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري تحليل البيانات وإنشاء التوقعات..."):
            try:
                suffix = ".CA" if is_egypt else ""
                df = yf.Ticker(f"{analysis_stock}{suffix}").history(period=analysis_period)

                if df.empty:
                    st.error("❌ تعذر جلب البيانات. تأكد من الرمز واتصال الإنترنت.")
                else:
                    # Calculate indicators
                    df = calculate_technical_indicators(df)

                    # Generate signals
                    signals = generate_trading_signals(df)
                    overall_signal, score, signal_text = calculate_overall_signal(signals)

                    # Predictions
                    predictions = predict_future_prices(df, days=5)

                    # Support/Resistance
                    sr_levels = calculate_support_resistance(df)

                    # ==================== SIGNAL DISPLAY ====================
                    st.subheader("🎯 إشارة التداول اللحظية")

                    signal_cols = st.columns([1, 2, 1])

                    with signal_cols[1]:
                        if overall_signal == "STRONG_BUY":
                            st.markdown(f"""
                            <div class="signal-buy">
                                <h2 style="margin: 0; color: #10b981; font-size: 36px;">🟢 شراء قوي</h2>
                                <p style="color: #10b981; font-size: 18px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "BUY":
                            st.markdown(f"""
                            <div class="signal-buy">
                                <h2 style="margin: 0; color: #34d399; font-size: 32px;">🟢 شراء</h2>
                                <p style="color: #34d399; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "STRONG_SELL":
                            st.markdown(f"""
                            <div class="signal-sell">
                                <h2 style="margin: 0; color: #ef4444; font-size: 36px;">🔴 بيع قوي</h2>
                                <p style="color: #ef4444; font-size: 18px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif overall_signal == "SELL":
                            st.markdown(f"""
                            <div class="signal-sell">
                                <h2 style="margin: 0; color: #f87171; font-size: 32px;">🔴 بيع</h2>
                                <p style="color: #f87171; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="signal-hold">
                                <h2 style="margin: 0; color: #fbbf24; font-size: 32px;">🟡 انتظار</h2>
                                <p style="color: #fbbf24; font-size: 16px; margin-top: 8px;">{signal_text}</p>
                                <p style="color: #94a3b8; font-size: 14px;">درجة الثقة: {abs(score):.1f}/5</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # ==================== TECHNICAL INDICATORS ====================
                    st.subheader("📊 المؤشرات الفنية الحية")

                    latest = df.iloc[-1]

                    ind_col1, ind_col2, ind_col3, ind_col4, ind_col5, ind_col6 = st.columns(6)

                    with ind_col1:
                        rsi_color = "#ef4444" if latest['RSI'] > 70 else "#10b981" if latest['RSI'] < 30 else "#fbbf24"
                        rsi_text = "ذروة شراء" if latest['RSI'] > 70 else "ذروة بيع" if latest['RSI'] < 30 else "محايد"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">RSI (14)</p>
                            <p style="font-size: 22px; font-weight: bold; color: {rsi_color}; margin: 4px 0;">{latest['RSI']:.1f}</p>
                            <p style="font-size: 10px; color: {rsi_color};">{rsi_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col2:
                        macd_color = "#10b981" if latest['MACD'] > latest['MACD_Signal'] else "#ef4444"
                        macd_text = "إيجابي" if latest['MACD'] > latest['MACD_Signal'] else "سلبي"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">MACD</p>
                            <p style="font-size: 22px; font-weight: bold; color: {macd_color}; margin: 4px 0;">{latest['MACD']:.2f}</p>
                            <p style="font-size: 10px; color: {macd_color};">{macd_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col3:
                        bb_pos = latest['BB_Position']
                        bb_color = "#10b981" if bb_pos < 0.2 else "#ef4444" if bb_pos > 0.8 else "#fbbf24"
                        bb_text = "منطقة شراء" if bb_pos < 0.2 else "منطقة بيع" if bb_pos > 0.8 else "النطاق الأوسط"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Bollinger</p>
                            <p style="font-size: 22px; font-weight: bold; color: {bb_color}; margin: 4px 0;">{bb_pos:.1%}</p>
                            <p style="font-size: 10px; color: {bb_color};">{bb_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col4:
                        stoch_color = "#10b981" if latest['Stoch_K'] < 20 else "#ef4444" if latest['Stoch_K'] > 80 else "#fbbf24"
                        stoch_text = "ذروة بيع" if latest['Stoch_K'] < 20 else "ذروة شراء" if latest['Stoch_K'] > 80 else "محايد"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Stochastic</p>
                            <p style="font-size: 22px; font-weight: bold; color: {stoch_color}; margin: 4px 0;">{latest['Stoch_K']:.1f}</p>
                            <p style="font-size: 10px; color: {stoch_color};">{stoch_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col5:
                        trend_color = "#10b981" if latest['Close'] > latest['SMA_20'] else "#ef4444"
                        trend_text = "صاعد" if latest['Close'] > latest['SMA_20'] else "هابط"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">SMA 20</p>
                            <p style="font-size: 22px; font-weight: bold; color: {trend_color}; margin: 4px 0;">{latest['SMA_20']:.2f}</p>
                            <p style="font-size: 10px; color: {trend_color};">{trend_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with ind_col6:
                        vol_color = "#10b981" if latest['Volume_Ratio'] > 1.5 else "#ef4444" if latest['Volume_Ratio'] < 0.5 else "#fbbf24"
                        vol_text = "نشط" if latest['Volume_Ratio'] > 1.5 else "ضعيف" if latest['Volume_Ratio'] < 0.5 else "طبيعي"
                        st.markdown(f"""
                        <div class="indicator-box">
                            <p style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">Volume</p>
                            <p style="font-size: 22px; font-weight: bold; color: {vol_color}; margin: 4px 0;">{latest['Volume_Ratio']:.1f}x</p>
                            <p style="font-size: 10px; color: {vol_color};">{vol_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # ==================== DETAILED SIGNALS TABLE ====================
                    st.subheader("📋 تفاصيل إشارات المؤشرات")

                    signals_df = pd.DataFrame(signals, columns=["المؤشر", "الإشارة", "الدرجة", "الوصف"])

                    def signal_color(val):
                        if "شراء" in str(val) and "قوي" in str(val):
                            return 'background-color: rgba(16, 185, 129, 0.3); color: #10b981; font-weight: bold;'
                        elif "شراء" in str(val):
                            return 'color: #10b981;'
                        elif "بيع" in str(val) and "قوي" in str(val):
                            return 'background-color: rgba(239, 68, 68, 0.3); color: #ef4444; font-weight: bold;'
                        elif "بيع" in str(val):
                            return 'color: #ef4444;'
                        return 'color: #fbbf24;'

                    styled_signals = signals_df.style.map(signal_color, subset=["الإشارة"])
                    st.dataframe(styled_signals, use_container_width=True, hide_index=True)

                    # ==================== PRICE PREDICTIONS ====================
                    st.subheader("🔮 توقعات الأسعار للأيام القادمة")

                    if 'combined' in predictions:
                        pred_df = pd.DataFrame(predictions['combined'])
                        pred_df['اليوم'] = pred_df['day'].apply(lambda x: f"يوم {x}")
                        pred_df['التوقع'] = pred_df['predicted']
                        pred_df['الحد الأدنى'] = pred_df['lower_bound']
                        pred_df['الحد الأقصى'] = pred_df['upper_bound']
                        pred_df['الثقة'] = pred_df['confidence'].apply(lambda x: f"{x:.0f}%")

                        display_pred = pred_df[['اليوم', 'التوقع', 'الحد الأدنى', 'الحد الأقصى', 'الثقة']].copy()

                        # Color code predictions
                        current_price = df['Close'].iloc[-1]
                        def pred_color(val):
                            if isinstance(val, (int, float)):
                                return 'color: #10b981;' if val > current_price else 'color: #ef4444;' if val < current_price else 'color: #fbbf24;'
                            return ''

                        styled_pred = display_pred.style.map(pred_color, subset=['التوقع'])
                        st.dataframe(styled_pred, use_container_width=True, hide_index=True)

                        # Prediction Chart
                        fig_pred = go.Figure()

                        # Historical prices
                        fig_pred.add_trace(go.Scatter(
                            x=df.index[-30:],
                            y=df['Close'].tail(30),
                            mode='lines',
                            name='السعر الفعلي',
                            line=dict(color='#6366f1', width=2)
                        ))

                        # Prediction line
                        last_date = df.index[-1]
                        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=5, freq='B')

                        fig_pred.add_trace(go.Scatter(
                            x=future_dates,
                            y=[p['predicted'] for p in predictions['combined']],
                            mode='lines+markers',
                            name='التوقع',
                            line=dict(color='#fbbf24', width=2, dash='dash'),
                            marker=dict(size=8)
                        ))

                        # Confidence interval
                        fig_pred.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=[p['upper_bound'] for p in predictions['combined']] + [p['lower_bound'] for p in predictions['combined']][::-1],
                            fill='toself',
                            fillcolor='rgba(251, 191, 36, 0.1)',
                            line=dict(color='rgba(251, 191, 36, 0)'),
                            name='نطاق الثقة'
                        ))

                        fig_pred.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Cairo", color="white"),
                            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="السعر"),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            height=400
                        )

                        st.plotly_chart(fig_pred, use_container_width=True)

                    # ==================== SUPPORT & RESISTANCE ====================
                    st.subheader("🎯 مستويات الدعم والمقاومة الديناميكية")

                    sr_cols = st.columns(3)

                    with sr_cols[0]:
                        st.markdown("""
                        <div class="glass-card">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 12px;">🔴 مستويات المقاومة</p>
                        """, unsafe_allow_html=True)
                        for i, r in enumerate(sr_levels['resistances'][:3]):
                            st.markdown(f"""
                            <p style="color: #ef4444; font-size: 18px; font-weight: bold; margin: 8px 0;">
                                R{i+1}: {r:.2f}
                            </p>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with sr_cols[1]:
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center; border: 2px solid #6366f1;">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 8px;">السعر الحالي</p>
                            <p style="color: #6366f1; font-size: 32px; font-weight: bold; margin: 8px 0;">{sr_levels['current']:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with sr_cols[2]:
                        st.markdown("""
                        <div class="glass-card">
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 12px;">🟢 مستويات الدعم</p>
                        """, unsafe_allow_html=True)
                        for i, s in enumerate(sr_levels['supports'][:3]):
                            st.markdown(f"""
                            <p style="color: #10b981; font-size: 18px; font-weight: bold; margin: 8px 0;">
                                S{i+1}: {s:.2f}
                            </p>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Fibonacci Levels
                    with st.expander("📐 مستويات فيبوناتشي", expanded=False):
                        fib_cols = st.columns(7)
                        for i, (level, value) in enumerate(sr_levels['fibonacci'].items()):
                            with fib_cols[i]:
                                fib_color = "#10b981" if value < sr_levels['current'] else "#ef4444" if value > sr_levels['current'] else "#fbbf24"
                                st.markdown(f"""
                                <div class="indicator-box">
                                    <p style="color: #94a3b8; font-size: 10px;">{level}</p>
                                    <p style="font-size: 16px; font-weight: bold; color: {fib_color};">{value:.2f}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    # ==================== CANDLESTICK CHART WITH INDICATORS ====================
                    st.subheader("📈 الرسم البياني التفاعلي مع المؤشرات")

                    fig = go.Figure()

                    # Candlestick
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='الشموع'
                    ))

                    # Moving Averages
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='#6366f1', width=1)
                    ))

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='#fbbf24', width=1)
                    ))

                    # Bollinger Bands
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['BB_Upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(16, 185, 129, 0.5)', width=1),
                        showlegend=False
                    ))

                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(16, 185, 129, 0.5)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(16, 185, 129, 0.05)',
                        showlegend=False
                    ))

                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="السعر"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=500
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Volume Chart
                    fig_vol = go.Figure()
                    colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' for i in range(len(df))]

                    fig_vol.add_trace(go.Bar(
                        x=df.index,
                        y=df['Volume'],
                        marker_color=colors,
                        name='حجم التداول'
                    ))

                    fig_vol.add_trace(go.Scatter(
                        x=df.index,
                        y=df['Volume_SMA'],
                        mode='lines',
                        name='متوسط الحجم',
                        line=dict(color='#fbbf24', width=2)
                    ))

                    fig_vol.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="الحجم"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=250
                    )

                    st.plotly_chart(fig_vol, use_container_width=True)

            except Exception as e:
                st.error(f"❌ خطأ في التحليل: {str(e)}")
                st.info("💡 تأكد من وجود اتصال بالإنترنت وصحة رمز السهم")


# ==================== TAB 3: BACKTESTING ====================
with tab3:
    st.title("📊 محرك Backtesting متقدم")

    bt_col1, bt_col2 = st.columns([1, 3])

    with bt_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        bt_ticker = st.selectbox("📌 اختر السهم", tickers)
        strategy = st.selectbox("🧠 الاستراتيجية", [
            "RSI_MACD - تقاطع الزخم",
            "MA_Crossover - تقاطع المتوسطات",
            "Bollinger - نطاقات بولينجر",
            "Mean_Reversion - العودة للمتوسط"
        ])
        period = st.selectbox("📅 الفترة", ["3mo", "6mo", "1y", "2y"], index=2)
        initial_capital = st.number_input("💰 رأس المال", value=100000, step=10000)
        st.markdown('</div>', unsafe_allow_html=True)

        run_bt = st.button("🚀 تشغيل الاختبار", type="primary", use_container_width=True)

    with bt_col2:
        if run_bt:
            with st.spinner("⏳ جاري تحليل البيانات التاريخية..."):
                strategy_key = strategy.split(" - ")[0]
                result = run_advanced_backtest(bt_ticker, strategy_key, period, "EGX" if is_egypt else "GLOBAL")

                if result:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    m1, m2, m3, m4, m5 = st.columns(5)

                    strat_color = "normal" if result['Strategy_Return'] >= 0 else "inverse"
                    bh_color = "normal" if result['Buy_Hold_Return'] >= 0 else "inverse"

                    m1.metric("📈 عائد الاستراتيجية", f"{result['Strategy_Return']:+.2f}%", delta_color=strat_color)
                    m2.metric("📊 Buy & Hold", f"{result['Buy_Hold_Return']:+.2f}%", delta_color=bh_color)
                    m3.metric("⚡ Sharpe Ratio", f"{result['Sharpe_Ratio']:.2f}")
                    m4.metric("🎯 Win Rate", f"{result['Win_Rate']:.1f}%")
                    m5.metric("📉 Max Drawdown", f"{result['Max_Drawdown']:.2f}%")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Equity Curve
                    st.subheader("📈 منحنى الأداء")
                    fig_equity = go.Figure()
                    fig_equity.add_trace(go.Scatter(
                        x=result['Equity_Curve'].index,
                        y=result['Equity_Curve'].values,
                        mode='lines',
                        name='رأس المال',
                        line=dict(color='#6366f1', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(99, 102, 241, 0.1)'
                    ))

                    bh_curve = 100000 * (1 + result['Data']['Returns']).cumprod()
                    fig_equity.add_trace(go.Scatter(
                        x=bh_curve.index,
                        y=bh_curve.values,
                        mode='lines',
                        name='Buy & Hold',
                        line=dict(color='#fbbf24', width=2, dash='dash')
                    ))

                    fig_equity.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Cairo", color="white"),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="التاريخ"),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title="رأس المال (ج.م)"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=400
                    )
                    st.plotly_chart(fig_equity, use_container_width=True)

                    # Trade Signals
                    st.subheader("🎯 إشارات التداول")
                    signals = result['Data'][result['Data']['Position'] != 0].copy()
                    if not signals.empty:
                        signals['النوع'] = signals['Position'].apply(lambda x: '🟢 شراء' if x > 0 else '🔴 بيع')
                        signals['السعر'] = signals['Close'].round(2)
                        signals['التاريخ'] = signals.index.strftime('%Y-%m-%d')
                        st.dataframe(signals[['التاريخ', 'النوع', 'السعر']].head(10), use_container_width=True, hide_index=True)

                    st.success(f"✅ عدد الصفقات المنفذة: {result['Trades']}")

                    # Strategy Comparison
                    st.subheader("🏆 مقارنة الاستراتيجيات")
                    strategies_to_test = ["RSI_MACD", "MA_Crossover", "Bollinger", "Mean_Reversion"]
                    comparison_results = []

                    for strat in strategies_to_test:
                        res = run_advanced_backtest(bt_ticker, strat, period, "EGX" if is_egypt else "GLOBAL")
                        if res:
                            comparison_results.append({
                                "الاستراتيجية": strat,
                                "العائد %": res['Strategy_Return'],
                                "Sharpe": res['Sharpe_Ratio'],
                                "Win Rate %": res['Win_Rate'],
                                "Max DD %": res['Max_Drawdown'],
                                "الصفقات": res['Trades']
                            })

                    if comparison_results:
                        comp_df = pd.DataFrame(comparison_results)

                        def highlight_best(val, col):
                            if col in ['العائد %', 'Sharpe', 'Win Rate %']:
                                return 'background-color: rgba(16, 185, 129, 0.3)' if val == comp_df[col].max() else ''
                            elif col == 'Max DD %':
                                return 'background-color: rgba(16, 185, 129, 0.3)' if val == comp_df[col].min() else ''
                            return ''

                        styled_comp = comp_df.style
                        for col in ['العائد %', 'Sharpe', 'Win Rate %', 'Max DD %']:
                            styled_comp = styled_comp.apply(lambda x, c=col: [highlight_best(v, c) for v in x], subset=[col])

                        st.dataframe(styled_comp, use_container_width=True, hide_index=True)
                else:
                    st.error("❌ تعذر جلب البيانات. تأكد من الرمز واتصال الإنترنت.")
        else:
            st.info("👈 اختر السهم والاستراتيجية واضغط 'تشغيل الاختبار'")

# ==================== TAB 4: PORTFOLIO ====================
with tab4:
    st.title("💼 محفظتي الاستثمارية")

    # Portfolio Metrics
    port_value = sum(p["quantity"] * p["current_price"] for p in st.session_state.portfolio)
    port_cost = sum(p["quantity"] * p["buy_price"] for p in st.session_state.portfolio)
    port_pl = port_value - port_cost
    port_pl_pct = (port_pl / port_cost) * 100 if port_cost > 0 else 0

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("💰 القيمة الحالية", f"ج.م {port_value:,.0f}")
    p2.metric("📈 إجمالي الربح/الخسارة", f"ج.م {port_pl:+,.0f}", f"{port_pl_pct:+.2f}%")
    p3.metric("📊 عدد الأسهم", len(st.session_state.portfolio))
    p4.metric("💵 رأس المال المستثمر", f"ج.م {port_cost:,.0f}")

    # Portfolio Chart & Table
    pt_col1, pt_col2 = st.columns([2, 3])

    with pt_col1:
        st.subheader("📊 توزيع المحفظة")
        fig_pie = px.pie(
            names=[p["symbol"] for p in st.session_state.portfolio],
            values=[p["quantity"] * p["current_price"] for p in st.session_state.portfolio],
            color_discrete_sequence=['#6366f1', '#8b5cf6', '#06b6d4', '#fbbf24', '#10b981'],
            hole=0.6
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Cairo", color="white"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1)
        )
        fig_pie.update_traces(textinfo='label+percent', textfont_size=12)
        st.plotly_chart(fig_pie, use_container_width=True)

    with pt_col2:
        st.subheader("📋 تفاصيل الأسهم")
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        portfolio_df['القيمة'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['التكلفة'] = portfolio_df['quantity'] * portfolio_df['buy_price']
        portfolio_df['الربح'] = portfolio_df['القيمة'] - portfolio_df['التكلفة']
        portfolio_df['العائد %'] = (portfolio_df['الربح'] / portfolio_df['التكلفة']) * 100

        display_df = portfolio_df[['symbol', 'name', 'quantity', 'buy_price', 'current_price', 'القيمة', 'الربح', 'العائد %']].copy()
        display_df.columns = ['الرمز', 'السهم', 'الكمية', 'سعر الشراء', 'السعر الحالي', 'القيمة', 'الربح/خسارة', 'العائد %']

        def highlight_profit(val):
            if isinstance(val, (int, float)):
                color = '#10b981' if val >= 0 else '#ef4444'
                return f'color: {color}; font-weight: bold;'
            return ''

        styled_port = display_df.style
        for col in ['الربح/خسارة', 'العائد %']:
            styled_port = styled_port.map(highlight_profit, subset=[col])

        st.dataframe(
            styled_port,
            use_container_width=True,
            hide_index=True,
            column_config={
                "سعر الشراء": st.column_config.NumberColumn(format="%.2f ج.م"),
                "السعر الحالي": st.column_config.NumberColumn(format="%.2f ج.م"),
                "القيمة": st.column_config.NumberColumn(format="%,.0f ج.م"),
                "الربح/خسارة": st.column_config.NumberColumn(format="%,.0f ج.م"),
                "العائد %": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    # Add Stock to Portfolio
    st.subheader("➕ إضافة سهم للمحفظة")
    ap_col1, ap_col2, ap_col3, ap_col4 = st.columns([2, 1, 1, 1])
    with ap_col1:
        new_stock = st.selectbox("السهم", [s["symbol"] + " - " + s["name"] for s in stocks_data])
    with ap_col2:
        new_qty = st.number_input("الكمية", min_value=1, value=100)
    with ap_col3:
        new_price = st.number_input("سعر الشراء", min_value=0.01, value=10.0, step=0.5)
    with ap_col4:
        st.write("")
        st.write("")
        if st.button("✅ إضافة", use_container_width=True):
            symbol = new_stock.split(" - ")[0]
            name = new_stock.split(" - ")[1]
            st.session_state.portfolio.append({
                "symbol": symbol, "name": name, "quantity": new_qty,
                "buy_price": new_price, "current_price": new_price
            })
            st.success(f"تمت إضافة {symbol}")
            st.rerun()

# ==================== TAB 5: SMART TASKS ====================
with tab5:
    st.title("✅ المهام الذكية")

    # Add Task
    with st.expander("➕ إضافة مهمة جديدة", expanded=False):
        t_col1, t_col2, t_col3 = st.columns([3, 1, 1])
        with t_col1:
            task_title = st.text_input("عنوان المهمة", placeholder="مثال: مراجعة أداء سهم CIB")
        with t_col2:
            task_priority = st.selectbox("الأولوية", ["high", "medium", "low"], format_func=lambda x: {"high": "🔴 عالية", "medium": "🟡 متوسطة", "low": "🟢 منخفضة"}[x])
        with t_col3:
            task_category = st.selectbox("التصنيف", ["work", "personal", "learning", "urgent"], format_func=lambda x: {"work": "💼 عمل", "personal": "👤 شخصي", "learning": "📚 تعلم", "urgent": "🚨 عاجل"}[x])

        t_col4, t_col5 = st.columns([2, 1])
        with t_col4:
            task_due = st.date_input("تاريخ الاستحقاق", datetime.now() + timedelta(days=3))
        with t_col5:
            st.write("")
            st.write("")
            if st.button("💾 حفظ المهمة", use_container_width=True):
                if task_title:
                    st.session_state.tasks.append({
                        "id": len(st.session_state.tasks) + 1,
                        "title": task_title,
                        "priority": task_priority,
                        "category": task_category,
                        "due": task_due.strftime("%Y-%m-%d"),
                        "completed": False,
                        "created": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success("✅ تمت الإضافة!")
                    st.rerun()
                else:
                    st.warning("⚠️ أدخل عنوان المهمة")

    # Filter Tasks
    st.subheader("📋 قائمة المهام")
    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        task_search = st.text_input("🔍 بحث", placeholder="ابحث في المهام...")
    with f_col2:
        filter_priority = st.selectbox("الأولوية", ["الكل", "high", "medium", "low"], format_func=lambda x: {"الكل": "الكل", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}[x])
    with f_col3:
        filter_status = st.selectbox("الحالة", ["الكل", "مكتمل", "قيد التنفيذ"])

    # Display Tasks
    filtered_tasks = st.session_state.tasks.copy()
    if task_search:
        filtered_tasks = [t for t in filtered_tasks if task_search.lower() in t["title"].lower()]
    if filter_priority != "الكل":
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == filter_priority]
    if filter_status == "مكتمل":
        filtered_tasks = [t for t in filtered_tasks if t["completed"]]
    elif filter_status == "قيد التنفيذ":
        filtered_tasks = [t for t in filtered_tasks if not t["completed"]]

    priority_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    category_icons = {"work": "💼", "personal": "👤", "learning": "📚", "urgent": "🚨"}

    for task in filtered_tasks:
        priority_class = f"priority-{task['priority']}"
        status_icon = "✅" if task["completed"] else "⬜"
        status_style = "text-decoration: line-through; opacity: 0.5;" if task["completed"] else ""

        st.markdown(f"""
        <div class="task-item {priority_class}" style="{status_style}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 20px;">{status_icon}</span>
                    <div>
                        <p style="margin: 0; font-weight: 600; font-size: 15px;">{task['title']}</p>
                        <div style="display: flex; gap: 8px; margin-top: 4px;">
                            <span class="tag-{task['category']}">{category_icons[task['category']]} {task['category']}</span>
                            <span style="color: #94a3b8; font-size: 12px;">📅 {task['due']}</span>
                            <span style="color: {'#ef4444' if task['priority'] == 'high' else '#f59e0b' if task['priority'] == 'medium' else '#10b981'}; font-size: 12px;">
                                {priority_colors[task['priority']]} {task['priority']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Hidden checkbox for actual interaction
        col_check, col_del = st.columns([20, 1])
        with col_check:
            new_status = st.checkbox("تم", value=task["completed"], key=f"task_{task['id']}", label_visibility="collapsed")
            if new_status != task["completed"]:
                task["completed"] = new_status
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{task['id']}", help="حذف"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task["id"]]
                st.rerun()

# ==================== TAB 6: NEWS & ANALYSIS ====================
with tab6:
    st.title("📰 أخبار السوق والتحليلات")

    # News Feed
    st.subheader("🔥 آخر الأخبار")
    for news in news_data:
        news_class = f"news-{news['type']}"
        icon = "📈" if news['type'] == 'positive' else "📉" if news['type'] == 'negative' else "📊"

        st.markdown(f"""
        <div class="news-item {news_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <span style="color: #fbbf24; font-size: 12px; font-weight: bold;">{news['time']}</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px;">{icon} {news['title']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Technical Analysis Section
    st.subheader("📊 التحليل الفني")

    ta_col1, ta_col2 = st.columns([1, 2])
    with ta_col1:
        ta_stock = st.selectbox("السهم للتحليل", [s["symbol"] for s in stocks_data])
        ta_period = st.selectbox("الفترة التحليلية", ["1mo", "3mo", "6mo", "1y"], index=2)

    with ta_col2:
        st.markdown("""
        <div class="glass-card">
            <h4>مؤشرات الزخم</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 12px;">
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">RSI (14)</p>
                    <p style="font-size: 24px; font-weight: bold; color: #fbbf24;">62.4</p>
                    <p style="font-size: 11px; color: #10b981;">محايد ➡️</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">MACD</p>
                    <p style="font-size: 24px; font-weight: bold; color: #10b981;">+0.45</p>
                    <p style="font-size: 11px; color: #10b981;">إيجابي 📈</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #94a3b8; font-size: 12px;">Bollinger</p>
                    <p style="font-size: 24px; font-weight: bold; color: #6366f1;">الوسط</p>
                    <p style="font-size: 11px; color: #f59e0b;">انتظار ⏸️</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Support/Resistance
    st.subheader("🎯 مستويات الدعم والمقاومة")
    sr_col1, sr_col2, sr_col3, sr_col4, sr_col5 = st.columns(5)

    current_price = next(s["price"] for s in stocks_data if s["symbol"] == ta_stock)
    support_levels = [current_price * 0.95, current_price * 0.90, current_price * 0.85]
    resistance_levels = [current_price * 1.05, current_price * 1.10]

    sr_col1.metric("الدعم 1", f"{support_levels[0]:.2f}")
    sr_col2.metric("الدعم 2", f"{support_levels[1]:.2f}")
    sr_col3.metric("السعر الحالي", f"{current_price:.2f}")
    sr_col4.metric("المقاومة 1", f"{resistance_levels[0]:.2f}")
    sr_col5.metric("المقاومة 2", f"{resistance_levels[1]:.2f}")

# ==================== FOOTER ====================
best_stock = max(stocks_data, key=lambda x: x["change_pct"])
st.markdown(f"""
<div style="text-align: center; padding: 30px; margin-top: 40px; background: linear-gradient(90deg, #0a0a0a, #1a1a2e); color: #00ffaa; border-top: 3px solid #6366f1; border-radius: 16px;">
    <p style="font-size: 18px; margin-bottom: 8px;">⚡ EGX Super Analyst Pro v15.0</p>
    <p style="color: #94a3b8; font-size: 14px;">
        نظام تحليلي ذكي متكامل | Backtesting متقدم | توقعات AI | إدارة المهام والمحافظ
    </p>
    <p style="color: #fbbf24; font-size: 14px; margin-top: 8px;">
        🏆 أقوى سهم اليوم: <b>{best_stock['symbol']}</b> ({best_stock['name']}) — +{best_stock['change_pct']:.2f}%
    </p>
    <p style="color: #6b7280; font-size: 12px; margin-top: 12px;">
        © 2026 | جميع البيانات تأتي من مصادر تجريبية للتوضيح | التوقعات للأغراض التعليمية فقط
    </p>
</div>
""", unsafe_allow_html=True)
