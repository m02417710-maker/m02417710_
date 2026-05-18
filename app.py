"""
EGX Pro Terminal v26
Professional Technical Analysis Platform for Egyptian Stock Exchange
===============================================================
The most advanced EGX analysis platform ever built.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Set page config FIRST
st.set_page_config(
    page_title="EGX Pro Terminal v26",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/m02417710-maker/egx-pro-terminal',
        'Report a bug': 'https://github.com/m02417710-maker/egx-pro-terminal/issues',
        'About': '# EGX Pro Terminal v26\nProfessional Technical Analysis Platform for Egyptian Stock Exchange'
    }
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
    }

    /* Headers */
    h1 {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    h2, h3 {
        color: #e0e0e0 !important;
    }

    /* Tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(26,26,46,0.8);
        border-radius: 10px 10px 0 0;
        color: #aaa;
        border: none;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* Alerts */
    .alert-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 4px solid;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        animation: slideIn 0.5s ease;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Progress bars */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
    }
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(26,26,46,0.8);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Imports
from config.settings import app_config, indicator_config, egx_config
from data.egx_symbols import (
    EGX_STOCKS, EGX_INDICES, ALL_SYMBOLS, SYMBOL_MAP, SECTOR_MAP,
    get_stock_info, get_stocks_by_sector, get_all_symbols, get_yahoo_symbol
)
from data.market_data import market_engine
from data.storage import local_storage
from core.analysis import analysis_engine
from core.alerts import alert_engine, AlertSeverity, AlertType
from core.patterns import pattern_engine
from core.ai_engine import ai_engine
from core.backtest import backtest_engine
from core.charts import chart_engine
from utils.helpers import (
    format_number, format_currency, format_percentage, format_volume,
    get_signal_color, get_trend_color, get_severity_color, get_severity_emoji,
    render_metric_card, render_signal_badge, render_progress_bar,
    render_alert_card, render_separator, get_arabic_number, time_ago,
    validate_symbol, get_sector_performance
)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'selected_symbol': 'COMI',
        'selected_period': '1y',
        'selected_interval': '1d',
        'analysis_data': None,
        'watchlist': [],
        'alerts': [],
        'last_update': None,
        'page': 'Dashboard',
        'language': 'ar',
        'theme': 'dark',
        'show_indicators': ['ema_9', 'ema_21', 'ema_50'],
        'backtest_results': None,
        'ai_predictions': {},
        'market_overview': None,
        'notifications_enabled': True,
        'auto_refresh': False,
        'refresh_interval': 60,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
def render_sidebar():
    """Render professional sidebar"""

    # Logo and Title
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 3em; margin-bottom: 10px;">📈</div>
            <div style="font-size: 1.5em; font-weight: 800; 
                        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;">
                EGX Pro
            </div>
            <div style="font-size: 0.8em; color: #888; margin-top: 5px;">
                Terminal v26
            </div>
            <div style="font-size: 0.7em; color: #667eea; margin-top: 3px;">
                ⚡ Professional Analysis
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.markdown("### 🧭 Navigation")

    pages = {
        '📊 Dashboard': 'Dashboard',
        '🔍 Stock Analysis': 'Analysis',
        '📈 Charts': 'Charts',
        '🔔 Alerts': 'Alerts',
        '🤖 AI Predictions': 'AI',
        '📋 Watchlist': 'Watchlist',
        '🧪 Backtest': 'Backtest',
        '🏢 Market Overview': 'Market',
        '⚙️ Settings': 'Settings'
    }

    for label, page_name in pages.items():
        if st.sidebar.button(label, use_container_width=True,
                            type="primary" if st.session_state.page == page_name else "secondary"):
            st.session_state.page = page_name
            st.rerun()

    st.sidebar.markdown("---")

    # Quick Stock Selector
    st.sidebar.markdown("### 🎯 Quick Select")

    # Search box
    search = st.sidebar.text_input("🔍 Search Symbol", 
                                  value=st.session_state.selected_symbol,
                                  placeholder="e.g., COMI, TMGH...")

    if search.upper() in SYMBOL_MAP:
        st.session_state.selected_symbol = search.upper()

    # Popular stocks
    popular = ['COMI', 'TMGH', 'EAST', 'SWDY', 'ORWE', 'MNHD', 'ETEL', 'FWRY']
    st.sidebar.markdown("**Popular:**")
    cols = st.sidebar.columns(4)
    for i, sym in enumerate(popular):
        with cols[i % 4]:
            if st.button(sym, key=f"pop_{sym}", use_container_width=True):
                st.session_state.selected_symbol = sym
                st.rerun()

    st.sidebar.markdown("---")

    # Time Period
    st.sidebar.markdown("### ⏱️ Time Period")
    period_options = {
        '1 Day': '1d', '5 Days': '5d', '1 Month': '1mo',
        '3 Months': '3mo', '6 Months': '6mo', '1 Year': '1y',
        '2 Years': '2y', '5 Years': '5y'
    }
    selected_period = st.sidebar.selectbox(
        "Period",
        list(period_options.keys()),
        index=list(period_options.values()).index(st.session_state.selected_period)
        if st.session_state.selected_period in period_options.values() else 5
    )
    st.session_state.selected_period = period_options[selected_period]

    # Auto Refresh
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Auto Refresh")
    st.session_state.auto_refresh = st.sidebar.toggle("Enable", 
                                                       value=st.session_state.auto_refresh)
    if st.session_state.auto_refresh:
        st.session_state.refresh_interval = st.sidebar.slider(
            "Interval (seconds)", 30, 300, st.session_state.refresh_interval, 30
        )
        time.sleep(st.session_state.refresh_interval)
        st.rerun()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.75em;">
            <div>🇪🇬 Made in Egypt</div>
            <div style="margin-top: 5px;">Data for educational purposes only</div>
            <div style="margin-top: 3px; color: #667eea;">Not investment advice</div>
        </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_stock_data(symbol: str, period: str, interval: str):
    """Load and cache stock data"""
    with st.spinner(f"📡 Fetching data for {symbol}..."):
        df = market_engine.fetch(symbol, period=period, interval=interval)
        if df is not None and not df.empty:
            df = analysis_engine.compute_all(df)
        return df


def get_current_data():
    """Get current stock data with analysis"""
    symbol = st.session_state.selected_symbol
    period = st.session_state.selected_period
    interval = st.session_state.selected_interval

    df = load_stock_data(symbol, period, interval)

    if df is not None and not df.empty:
        st.session_state.analysis_data = df
        st.session_state.last_update = datetime.now()

    return df


# ═══════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════
def render_dashboard():
    """Render main dashboard page"""

    # Hero Section
    st.markdown("""
        <div style="text-align: center; padding: 30px 0;">
            <h1 style="font-size: 3em; margin-bottom: 10px;">
                📈 EGX Pro Terminal
            </h1>
            <p style="font-size: 1.2em; color: #aaa;">
                Professional Technical Analysis Platform for Egyptian Stock Exchange
            </p>
            <p style="font-size: 0.9em; color: #667eea;">
                ⚡ 100+ Stocks | Advanced Indicators | AI Predictions | Real-time Alerts
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Market Overview Cards
    st.markdown("### 🌍 Market Overview")

    try:
        quotes = market_engine.get_market_overview()
        if not quotes.empty:
            cols = st.columns(4)

            # Top Gainer
            top_gainer = quotes.loc[quotes['change_pct'].idxmax()]
            with cols[0]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #4caf50; font-size: 0.85em;">📈 Top Gainer</div>
                        <div style="color: white; font-size: 1.8em; font-weight: bold;">
                            {top_gainer['symbol']}
                        </div>
                        <div style="color: #4caf50; font-size: 1.2em;">
                            +{top_gainer['change_pct']:.2f}%
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            {top_gainer['price']:.2f} EGP
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Top Loser
            top_loser = quotes.loc[quotes['change_pct'].idxmin()]
            with cols[1]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #f44336; font-size: 0.85em;">📉 Top Loser</div>
                        <div style="color: white; font-size: 1.8em; font-weight: bold;">
                            {top_loser['symbol']}
                        </div>
                        <div style="color: #f44336; font-size: 1.2em;">
                            {top_loser['change_pct']:.2f}%
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            {top_loser['price']:.2f} EGP
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Most Active
            most_active = quotes.loc[quotes['volume'].idxmax()]
            with cols[2]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #ff9800; font-size: 0.85em;">🔥 Most Active</div>
                        <div style="color: white; font-size: 1.8em; font-weight: bold;">
                            {most_active['symbol']}
                        </div>
                        <div style="color: #ff9800; font-size: 1.2em;">
                            {format_volume(most_active['volume'])}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            {most_active['change_pct']:.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Market Sentiment
            avg_change = quotes['change_pct'].mean()
            sentiment_color = "#4caf50" if avg_change > 0 else "#f44336" if avg_change < 0 else "#ff9800"
            sentiment_emoji = "🟢" if avg_change > 0 else "🔴" if avg_change < 0 else "🟡"
            with cols[3]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: {sentiment_color}; font-size: 0.85em;">
                            {sentiment_emoji} Market Sentiment
                        </div>
                        <div style="color: white; font-size: 1.8em; font-weight: bold;">
                            {avg_change:+.2f}%
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            Avg. Change ({len(quotes)} stocks)
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Market overview temporarily unavailable: {e}")

    render_separator()

    # Featured Stock Analysis
    st.markdown("### ⭐ Featured Analysis")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is not None and not df.empty:
        summary = analysis_engine.get_summary(df)

        cols = st.columns(5)
        metrics = [
            ("💰 Price", f"{summary['price']:.2f} EGP", 
             f"{summary['change']:+.2f} ({summary['change_pct']:+.2f}%)",
             "green" if summary['change'] >= 0 else "red"),
            ("📊 RSI", f"{summary['rsi']:.1f}", summary['rsi_signal'],
             "green" if summary['rsi'] < 30 else "red" if summary['rsi'] > 70 else "orange"),
            ("📈 MACD", f"{summary['macd']:.4f}", summary['macd_signal'],
             "green" if summary['macd'] > 0 else "red"),
            ("📉 ADX", f"{summary['adx']:.1f}", summary.get('adx_trend', 'N/A'),
             "green" if summary['adx'] > 25 else "orange"),
            ("🎯 Signal", summary['final_signal'], f"Strength: {summary['signal_strength']:.0%}",
             get_signal_color(summary['final_signal']))
        ]

        for i, (label, value, delta, color) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 0.85em;">{label}</div>
                        <div style="color: white; font-size: 1.5em; font-weight: bold;">
                            {value}
                        </div>
                        <div style="color: {color}; font-size: 0.9em;">
                            {delta}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Quick Chart
        st.markdown("### 📊 Quick Chart")
        fig = chart_engine.create_main_chart(df, symbol, 
                                             st.session_state.show_indicators)
        st.plotly_chart(fig, use_container_width=True, key="dashboard_chart")

        # AI Prediction Preview
        st.markdown("### 🤖 AI Prediction Preview")
        try:
            prediction = ai_engine.predict(df, symbol)
            if prediction:
                pred_color = get_signal_color(prediction.predicted_direction)
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Predicted Direction</div>
                            <div style="color: {pred_color}; font-size: 2em; font-weight: bold;">
                                {prediction.predicted_direction}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                Confidence: {prediction.confidence:.0%}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Target Price</div>
                            <div style="color: #4caf50; font-size: 2em; font-weight: bold;">
                                {prediction.target_price:.2f}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                EGP ({((prediction.target_price/prediction.current_price-1)*100):+.1f}%)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Stop Loss</div>
                            <div style="color: #f44336; font-size: 2em; font-weight: bold;">
                                {prediction.stop_loss:.2f}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                EGP ({((prediction.stop_loss/prediction.current_price-1)*100):+.1f}%)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.info("AI predictions loading...")

    # Recent Alerts
    st.markdown("### 🔔 Recent Alerts")
    try:
        alerts_df = local_storage.get_alerts(limit=5)
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                render_alert_card(alert.to_dict())
        else:
            st.info("No alerts yet. Set up alerts in the Alerts tab.")
    except Exception as e:
        st.info("Alerts system initializing...")


def render_analysis():
    """Render detailed analysis page"""
    st.markdown("## 🔍 Detailed Stock Analysis")

    symbol = st.session_state.selected_symbol
    stock_info = get_stock_info(symbol)

    # Stock Header
    if stock_info:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        border-radius: 15px; padding: 20px; margin-bottom: 20px;
                        border: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 2em; font-weight: bold; color: white;">
                            {symbol}
                        </div>
                        <div style="color: #888; font-size: 1em;">
                            {stock_info.name} | {stock_info.sector}
                        </div>
                        <div style="color: #667eea; font-size: 0.9em;">
                            {stock_info.name_ar}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.85em; color: #888;">Market Cap</div>
                        <div style="font-size: 1.2em; color: white; font-weight: bold;">
                            {format_currency(stock_info.market_cap, 'M EGP') if stock_info.market_cap else 'N/A'}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    df = get_current_data()

    if df is None or df.empty:
        st.error("❌ Unable to fetch data. Please try another symbol or check your connection.")
        return

    summary = analysis_engine.get_summary(df)

    # Key Metrics
    st.markdown("### 📊 Key Metrics")
    cols = st.columns(6)

    metrics_data = [
        ("💰 Price", f"{summary['price']:.2f}", "EGP"),
        ("📈 Change", f"{summary['change']:+.2f}", f"({summary['change_pct']:+.2f}%)"),
        ("📊 RSI", f"{summary['rsi']:.1f}", "14-period"),
        ("📉 MACD", f"{summary['macd']:.4f}", summary['macd_signal']),
        ("📉 ADX", f"{summary['adx']:.1f}", "Trend Strength"),
        ("📊 ATR", f"{summary['atr']:.2f}", "Volatility")
    ]

    for i, (label, value, sub) in enumerate(metrics_data):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888; font-size: 0.8em;">{label}</div>
                    <div style="color: white; font-size: 1.3em; font-weight: bold;">{value}</div>
                    <div style="color: #667eea; font-size: 0.75em;">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

    # Signal Badge
    signal_color = get_signal_color(summary['final_signal'])
    st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <span style="
                background-color: {signal_color}22;
                color: {signal_color};
                border: 2px solid {signal_color};
                border-radius: 25px;
                padding: 10px 30px;
                font-size: 1.3em;
                font-weight: bold;
            ">{summary['final_signal']}</span>
            <div style="color: #888; font-size: 0.85em; margin-top: 8px;">
                Signal Strength: {summary['signal_strength']:.0%}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Trend Analysis
    st.markdown("### 📈 Trend Analysis")
    cols = st.columns(2)

    with cols[0]:
        trend_color = get_trend_color(summary['trend'])
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: #888; font-size: 0.9em; margin-bottom: 10px;">Current Trend</div>
                <div style="color: {trend_color}; font-size: 1.5em; font-weight: bold;">
                    {summary['trend']}
                </div>
                <div style="margin-top: 10px;">
        """, unsafe_allow_html=True)
        render_progress_bar(summary['trend_strength'], 100, label="Trend Strength")
        st.markdown("</div></div>", unsafe_allow_html=True)

    with cols[1]:
        sr = summary['support_resistance']
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: #888; font-size: 0.9em; margin-bottom: 10px;">Support & Resistance</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #4caf50;">Support: {sr.get('nearest_support', 'N/A'):.2f}</span>
                    <span style="color: #f44336;">Resistance: {sr.get('nearest_resistance', 'N/A'):.2f}</span>
                </div>
                <div style="color: #667eea; font-size: 0.85em;">
                    Pivot: {sr.get('pivot_point', 'N/A'):.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Moving Averages
    st.markdown("### 📊 Moving Averages")
    ma_data = {
        'EMA 9': summary.get('ema_9', 0),
        'EMA 21': summary.get('ema_21', 0),
        'EMA 50': summary.get('ema_50', 0),
        'EMA 200': summary.get('ema_200', 0)
    }

    cols = st.columns(4)
    for i, (name, value) in enumerate(ma_data.items()):
        distance = ((summary['price'] - value) / value * 100) if value else 0
        color = "#4caf50" if distance > 0 else "#f44336"
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888; font-size: 0.85em;">{name}</div>
                    <div style="color: white; font-size: 1.3em; font-weight: bold;">
                        {value:.2f}
                    </div>
                    <div style="color: {color}; font-size: 0.85em;">
                        {distance:+.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Fibonacci Levels
    st.markdown("### 📐 Fibonacci Retracement Levels")
    fib = summary['fibonacci']
    if fib:
        fib_df = pd.DataFrame([
            {'Level': k, 'Price': v, 'Distance %': ((v/summary['price']-1)*100) if k != 'current' else 0}
            for k, v in fib.items() if k != 'current'
        ])

        # Color code rows
        def color_fib(val):
            if val > 0:
                return 'color: #4caf50'
            elif val < 0:
                return 'color: #f44336'
            return 'color: #ff9800'

        styled = fib_df.style.applymap(color_fib, subset=['Distance %'])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # Pattern Detection
    st.markdown("### 🔍 Pattern Detection")
    try:
        patterns = pattern_engine.get_pattern_summary(df)
        if patterns['total'] > 0:
            latest = patterns['latest']
            pattern_color = "#4caf50" if latest['bullish'] else "#f44336" if latest['bullish'] is False else "#ff9800"

            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 0.85em;">Latest Pattern</div>
                        <div style="color: {pattern_color}; font-size: 1.3em; font-weight: bold;">
                            {latest['name']}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            {latest['type']} | {latest['strength']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with cols[1]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 0.85em;">Pattern Confidence</div>
                        <div style="color: white; font-size: 1.3em; font-weight: bold;">
                            {latest['confidence']:.0%}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            Position: {latest['position']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with cols[2]:
                bull_count = patterns['bullish_count']
                bear_count = patterns['bearish_count']
                total = patterns['total']

                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 0.85em;">Pattern Summary</div>
                        <div style="display: flex; justify-content: space-around; margin-top: 5px;">
                            <span style="color: #4caf50;">🟢 {bull_count}</span>
                            <span style="color: #f44336;">🔴 {bear_count}</span>
                            <span style="color: #ff9800;">⚪ {patterns['neutral_count']}</span>
                        </div>
                        <div style="color: #888; font-size: 0.8em; margin-top: 5px;">
                            Total: {total} patterns detected
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.info(f"💡 **{latest['name']}**: {latest['description']}")
        else:
            st.info("No significant patterns detected in the current period.")
    except Exception as e:
        st.info("Pattern analysis loading...")


def render_charts():
    """Render charts page"""
    st.markdown("## 📈 Advanced Charts")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.error("No data available for charts.")
        return

    # Chart Controls
    st.markdown("### 🎛️ Chart Controls")
    cols = st.columns(4)

    with cols[0]:
        show_ema = st.toggle("EMA", True)
    with cols[1]:
        show_sma = st.toggle("SMA", False)
    with cols[2]:
        show_bb = st.toggle("Bollinger Bands", True)
    with cols[3]:
        show_volume = st.toggle("Volume", True)

    indicators = []
    if show_ema:
        indicators.extend(['ema_9', 'ema_21', 'ema_50'])
    if show_sma:
        indicators.extend(['sma_20', 'sma_50'])

    st.session_state.show_indicators = indicators

    # Main Chart
    st.markdown("### 📊 Price Chart")
    fig = chart_engine.create_main_chart(df, symbol, indicators)
    st.plotly_chart(fig, use_container_width=True, key="main_chart")

    # Additional Charts
    tabs = st.tabs(["RSI", "ADX", "Stochastic", "Volume Analysis"])

    with tabs[0]:
        fig_rsi = chart_engine.create_rsi_chart(df)
        st.plotly_chart(fig_rsi, use_container_width=True, key="rsi_chart")

    with tabs[1]:
        fig_adx = chart_engine.create_adx_chart(df)
        st.plotly_chart(fig_adx, use_container_width=True, key="adx_chart")

    with tabs[2]:
        fig_stoch = chart_engine.create_stochastic_chart(df)
        st.plotly_chart(fig_stoch, use_container_width=True, key="stoch_chart")

    with tabs[3]:
        st.markdown("### 📊 Volume Analysis")

        vol_df = df[['date', 'volume', 'volume_ma', 'volume_ratio', 'volume_spike']].tail(30)

        fig_vol = go.Figure()

        colors = ['#26a69a' if df['close'].iloc[i] >= df['open'].iloc[i] 
                  else '#ef5350' for i in range(-30, 0)]

        fig_vol.add_trace(go.Bar(
            x=vol_df['date'],
            y=vol_df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ))

        fig_vol.add_trace(go.Scatter(
            x=vol_df['date'],
            y=vol_df['volume_ma'],
            mode='lines',
            name='Volume MA',
            line=dict(color='#FF9800', width=2)
        ))

        fig_vol.update_layout(
            title='Volume Analysis (Last 30 Days)',
            template='plotly_dark',
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_vol, use_container_width=True, key="volume_chart")

        # Volume spikes
        spikes = df[df['volume_spike'] == True].tail(10)
        if not spikes.empty:
            st.markdown("### ⚡ Recent Volume Spikes")
            spike_df = spikes[['date', 'volume', 'volume_ratio', 'close']].copy()
            spike_df['date'] = spike_df['date'].dt.strftime('%Y-%m-%d')
            spike_df.columns = ['Date', 'Volume', 'Ratio', 'Close Price']
            st.dataframe(spike_df, use_container_width=True, hide_index=True)


def render_alerts():
    """Render alerts management page"""
    st.markdown("## 🔔 Alert Management")

    symbol = st.session_state.selected_symbol

    # Create Alert Section
    st.markdown("### ➕ Create New Alert")

    alert_types = {
        "💰 Price Target": "price",
        "📉 RSI Oversold (<30)": "rsi_oversold",
        "📈 RSI Overbought (>70)": "rsi_overbought",
        "⚡ MACD Bullish Cross": "macd_bullish",
        "⚡ MACD Bearish Cross": "macd_bearish",
        "📊 EMA Crossover": "ema_cross",
        "💥 BB Breakout": "bb_breakout",
        "🔥 Volume Spike": "volume_spike",
        "🔄 Trend Change": "trend_change"
    }

    cols = st.columns(2)
    with cols[0]:
        selected_alert = st.selectbox("Alert Type", list(alert_types.keys()))
    with cols[1]:
        alert_symbol = st.text_input("Symbol", value=symbol)

    # Alert-specific parameters
    alert_type = alert_types[selected_alert]

    if alert_type == "price":
        target_price = st.number_input("Target Price (EGP)", min_value=0.0, value=10.0, step=0.1)
        direction = st.radio("Direction", ["Above", "Below"], horizontal=True)

    if st.button("🚀 Create Alert", use_container_width=True):
        try:
            if alert_type == "price":
                alert_engine.add_price_alert(
                    alert_symbol, target_price, 
                    'above' if direction == "Above" else 'below',
                    AlertSeverity.WARNING
                )
            elif alert_type == "rsi_oversold":
                alert_engine.add_rsi_alert(alert_symbol, 30, 'below')
            elif alert_type == "rsi_overbought":
                alert_engine.add_rsi_alert(alert_symbol, 70, 'above')
            elif alert_type == "macd_bullish":
                alert_engine.add_macd_alert(alert_symbol, 'bullish')
            elif alert_type == "macd_bearish":
                alert_engine.add_macd_alert(alert_symbol, 'bearish')
            elif alert_type == "ema_cross":
                alert_engine.add_ema_alert(alert_symbol, 9, 21, 'bullish')
            elif alert_type == "bb_breakout":
                alert_engine.add_bb_alert(alert_symbol, 'upper')
            elif alert_type == "volume_spike":
                alert_engine.add_volume_alert(alert_symbol, 2.0)
            elif alert_type == "trend_change":
                alert_engine.add_trend_change_alert(alert_symbol)

            st.success(f"✅ Alert created for {alert_symbol}!")
        except Exception as e:
            st.error(f"❌ Error creating alert: {e}")

    render_separator()

    # Active Alerts
    st.markdown("### 📋 Active Alerts")
    try:
        conditions = alert_engine.get_conditions(symbol)
        if conditions:
            alert_data = []
            for c in conditions:
                alert_data.append({
                    'Name': c.name,
                    'Type': c.alert_type.value,
                    'Symbol': c.symbol,
                    'Severity': c.severity.value,
                    'Status': '✅ Active' if c.enabled else '⏸️ Paused',
                    'Triggers': c.trigger_count
                })

            st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        else:
            st.info("No active alerts. Create one above!")
    except Exception as e:
        st.info("Alert system initializing...")

    # Alert History
    st.markdown("### 📜 Alert History")
    try:
        alerts_df = local_storage.get_alerts(symbol, limit=20)
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                render_alert_card(alert.to_dict())
        else:
            st.info("No alert history yet.")
    except Exception as e:
        st.info("Alert history loading...")


def render_ai():
    """Render AI predictions page"""
    st.markdown("## 🤖 AI Predictions")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.error("No data available for AI analysis.")
        return

    # Single Stock Prediction
    st.markdown("### 🔮 Stock Prediction")

    with st.spinner("🧠 Analyzing with AI models..."):
        try:
            prediction = ai_engine.predict(df, symbol)

            if prediction:
                pred_color = get_signal_color(prediction.predicted_direction)

                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Direction</div>
                            <div style="color: {pred_color}; font-size: 2em; font-weight: bold;">
                                {prediction.predicted_direction}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                Confidence: {prediction.confidence:.0%}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with cols[1]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Target ({prediction.horizon_days} days)</div>
                            <div style="color: #4caf50; font-size: 2em; font-weight: bold;">
                                {prediction.target_price:.2f}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                EGP ({((prediction.target_price/prediction.current_price-1)*100):+.1f}%)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with cols[2]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">Stop Loss</div>
                            <div style="color: #f44336; font-size: 2em; font-weight: bold;">
                                {prediction.stop_loss:.2f}
                            </div>
                            <div style="color: #888; font-size: 0.8em;">
                                EGP ({((prediction.stop_loss/prediction.current_price-1)*100):+.1f}%)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # Feature Importance
                st.markdown("### 🧠 Feature Importance")

                features = prediction.features_importance
                feature_df = pd.DataFrame([
                    {'Feature': k, 'Importance': v, 'Weight %': f"{v*100:.0f}%"}
                    for k, v in features.items()
                ])

                fig = go.Figure(go.Bar(
                    x=list(features.values()),
                    y=list(features.keys()),
                    orientation='h',
                    marker_color='#667eea',
                    text=[f"{v*100:.0f}%" for v in features.values()],
                    textposition='outside'
                ))

                fig.update_layout(
                    template='plotly_dark',
                    height=300,
                    showlegend=False,
                    xaxis_title='Importance',
                    yaxis_title='Feature'
                )

                st.plotly_chart(fig, use_container_width=True, key="feature_importance")

                # Risk/Reward
                reward = abs(prediction.target_price - prediction.current_price)
                risk = abs(prediction.stop_loss - prediction.current_price)
                rr_ratio = reward / risk if risk > 0 else 0

                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                                border-radius: 15px; padding: 20px; margin-top: 20px;">
                        <div style="display: flex; justify-content: space-around; text-align: center;">
                            <div>
                                <div style="color: #888; font-size: 0.85em;">Risk/Reward</div>
                                <div style="color: {'#4caf50' if rr_ratio > 1 else '#f44336'}; 
                                            font-size: 2em; font-weight: bold;">
                                    1:{rr_ratio:.1f}
                                </div>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.85em;">Potential Reward</div>
                                <div style="color: #4caf50; font-size: 2em; font-weight: bold;">
                                    +{((prediction.target_price/prediction.current_price-1)*100):.1f}%
                                </div>
                            </div>
                            <div>
                                <div style="color: #888; font-size: 0.85em;">Max Risk</div>
                                <div style="color: #f44336; font-size: 2em; font-weight: bold;">
                                    {((prediction.stop_loss/prediction.current_price-1)*100):.1f}%
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"AI prediction error: {e}")

    # Market Sentiment
    st.markdown("### 🌍 Market Sentiment")
    try:
        # Get predictions for multiple stocks
        symbols = ['COMI', 'TMGH', 'EAST', 'SWDY', 'ORWE', 'MNHD', 'ETEL', 'FWRY']
        predictions = {}

        for sym in symbols:
            sym_df = market_engine.fetch(sym, period='1y', interval='1d')
            if sym_df is not None and not sym_df.empty:
                sym_df = analysis_engine.compute_all(sym_df)
                pred = ai_engine.predict(sym_df, sym)
                if pred:
                    predictions[sym] = pred

        if predictions:
            sentiment = ai_engine.get_market_sentiment(predictions)

            cols = st.columns(4)
            with cols[0]:
                sent_color = get_signal_color(sentiment['sentiment'])
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #888; font-size: 0.85em;">Overall Sentiment</div>
                        <div style="color: {sent_color}; font-size: 1.8em; font-weight: bold;">
                            {sentiment['sentiment']}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">
                            Score: {sentiment['score']}/100
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with cols[1]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #4caf50; font-size: 0.85em;">🟢 Bullish</div>
                        <div style="color: #4caf50; font-size: 1.8em; font-weight: bold;">
                            {sentiment['bullish']}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">stocks</div>
                    </div>
                """, unsafe_allow_html=True)

            with cols[2]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #f44336; font-size: 0.85em;">🔴 Bearish</div>
                        <div style="color: #f44336; font-size: 1.8em; font-weight: bold;">
                            {sentiment['bearish']}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">stocks</div>
                    </div>
                """, unsafe_allow_html=True)

            with cols[3]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #ff9800; font-size: 0.85em;">🟡 Neutral</div>
                        <div style="color: #ff9800; font-size: 1.8em; font-weight: bold;">
                            {sentiment['neutral']}
                        </div>
                        <div style="color: #888; font-size: 0.8em;">stocks</div>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Market sentiment analysis loading...")


def render_watchlist():
    """Render watchlist page"""
    st.markdown("## 📋 My Watchlist")

    # Add to watchlist
    st.markdown("### ➕ Add Stock")
    cols = st.columns([3, 1, 1, 1])
    with cols[0]:
        new_symbol = st.text_input("Symbol", key="watchlist_symbol")
    with cols[1]:
        target = st.number_input("Target", min_value=0.0, value=0.0, step=0.1)
    with cols[2]:
        stop = st.number_input("Stop Loss", min_value=0.0, value=0.0, step=0.1)
    with cols[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", use_container_width=True):
            if new_symbol and validate_symbol(new_symbol):
                local_storage.add_to_watchlist(
                    new_symbol.upper(), 
                    target_price=target if target > 0 else None,
                    stop_loss=stop if stop > 0 else None
                )
                st.success(f"Added {new_symbol.upper()} to watchlist!")
                st.rerun()
            else:
                st.error("Invalid symbol!")

    render_separator()

    # Watchlist Table
    st.markdown("### 📊 Watchlist")
    try:
        watchlist = local_storage.get_watchlist()
        if not watchlist.empty:
            # Enrich with current data
            enriched_data = []
            for _, row in watchlist.iterrows():
                sym = row['symbol']
                quote = market_engine.get_realtime_quote(sym)
                if quote:
                    enriched_data.append({
                        'Symbol': sym,
                        'Price': quote['price'],
                        'Change %': f"{quote['change_pct']:+.2f}%",
                        'Volume': format_volume(quote['volume']),
                        'Target': row['target_price'] if pd.notna(row['target_price']) else 'N/A',
                        'Stop Loss': row['stop_loss'] if pd.notna(row['stop_loss']) else 'N/A',
                        'Distance to Target': f"{((quote['price']/row['target_price']-1)*100):+.1f}%" if pd.notna(row['target_price']) and row['target_price'] > 0 else 'N/A',
                        'Added': time_ago(row['added_at'])
                    })

            if enriched_data:
                st.dataframe(pd.DataFrame(enriched_data), use_container_width=True, hide_index=True)
        else:
            st.info("Your watchlist is empty. Add stocks above!")
    except Exception as e:
        st.info("Watchlist loading...")


def render_backtest():
    """Render backtesting page"""
    st.markdown("## 🧪 Strategy Backtest")

    symbol = st.session_state.selected_symbol
    df = get_current_data()

    if df is None or df.empty:
        st.error("No data available for backtesting.")
        return

    # Strategy Selection
    st.markdown("### 🎯 Select Strategy")

    strategies = backtest_engine.get_strategy_list()
    strategy_name = st.selectbox("Strategy", list(strategies.keys()))

    # Strategy Parameters
    st.markdown("### ⚙️ Parameters")

    params = {}
    if "RSI" in strategy_name:
        cols = st.columns(2)
        with cols[0]:
            params['oversold'] = st.slider("Oversold Level", 10, 40, 30)
        with cols[1]:
            params['overbought'] = st.slider("Overbought Level", 60, 90, 70)

    elif "EMA" in strategy_name:
        cols = st.columns(2)
        with cols[0]:
            params['fast'] = st.selectbox("Fast EMA", [5, 9, 12, 20], index=1)
        with cols[1]:
            params['slow'] = st.selectbox("Slow EMA", [21, 26, 50, 200], index=0)

    initial_capital = st.number_input("Initial Capital (EGP)", 
                                      value=100000.0, step=10000.0, min_value=1000.0)

    if st.button("🚀 Run Backtest", use_container_width=True, type="primary"):
        with st.spinner("📊 Running backtest..."):
            try:
                strategy_func = strategies[strategy_name]

                # Create engine with custom capital
                engine = backtest_engine.__class__(initial_capital=initial_capital)
                result = engine.run_strategy(
                    df, strategy_func, symbol, strategy_name, params
                )

                if result:
                    st.session_state.backtest_results = result

                    # Results Summary
                    st.markdown("### 📈 Backtest Results")

                    cols = st.columns(4)
                    metrics = [
                        ("💰 Final Capital", f"{result.final_capital:,.0f} EGP", 
                         f"Return: {result.total_return_pct:+.2f}%"),
                        ("📊 Win Rate", f"{result.win_rate:.1f}%", 
                         f"{result.winning_trades}/{result.total_trades} trades"),
                        ("📉 Max Drawdown", f"{result.max_drawdown_pct:.2f}%", 
                         "Peak to trough"),
                        ("📈 Sharpe Ratio", f"{result.sharpe_ratio:.2f}", 
                         "Risk-adjusted return")
                    ]

                    for i, (label, value, sub) in enumerate(metrics):
                        with cols[i]:
                            color = "#4caf50" if "Return" in sub and result.total_return_pct > 0 else "#f44336"
                            st.markdown(f"""
                                <div class="metric-card">
                                    <div style="color: #888; font-size: 0.85em;">{label}</div>
                                    <div style="color: white; font-size: 1.5em; font-weight: bold;">
                                        {value}
                                    </div>
                                    <div style="color: {color}; font-size: 0.8em;">{sub}</div>
                                </div>
                            """, unsafe_allow_html=True)

                    # Equity Curve
                    st.markdown("### 📊 Equity Curve")
                    fig_equity = chart_engine.create_equity_curve(result.equity_curve)
                    st.plotly_chart(fig_equity, use_container_width=True, key="equity_curve")

                    # Drawdown
                    st.markdown("### 📉 Drawdown Analysis")
                    fig_dd = chart_engine.create_drawdown_chart(result.equity_curve)
                    st.plotly_chart(fig_dd, use_container_width=True, key="drawdown_chart")

                    # Trade History
                    if result.trades:
                        st.markdown("### 📋 Trade History")
                        trade_data = []
                        for trade in result.trades:
                            trade_data.append({
                                'Entry Date': trade.entry_date[:10],
                                'Exit Date': trade.exit_date[:10] if trade.exit_date else 'Open',
                                'Entry': f"{trade.entry_price:.2f}",
                                'Exit': f"{trade.exit_price:.2f}" if trade.exit_price else 'N/A',
                                'P&L': f"{trade.pnl:,.0f}" if trade.pnl else 'N/A',
                                'Return %': f"{trade.pnl_pct:.2f}%" if trade.pnl_pct else 'N/A',
                                'Days': trade.holding_days,
                                'Reason': trade.exit_reason
                            })

                        st.dataframe(pd.DataFrame(trade_data), use_container_width=True, hide_index=True)
                else:
                    st.error("Backtest failed. Check your data and parameters.")
            except Exception as e:
                st.error(f"Backtest error: {e}")

    # Previous Results
    st.markdown("### 📜 Previous Backtests")
    try:
        history = local_storage.get_backtests(limit=10)
        if not history.empty:
            st.dataframe(history[['strategy_name', 'symbol', 'total_return', 'win_rate', 
                                  'max_drawdown', 'sharpe_ratio', 'total_trades', 'created_at']],
                        use_container_width=True, hide_index=True)
        else:
            st.info("No backtest history yet.")
    except Exception as e:
        st.info("Backtest history loading...")


def render_market():
    """Render market overview page"""
    st.markdown("## 🏢 Market Overview")

    # Market Summary
    st.markdown("### 📊 Market Summary")
    try:
        quotes = market_engine.get_market_overview()
        if not quotes.empty:
            # Sortable table
            st.dataframe(
                quotes[['symbol', 'price', 'change', 'change_pct', 'volume', 'high', 'low']]
                .rename(columns={
                    'symbol': 'Symbol',
                    'price': 'Price',
                    'change': 'Change',
                    'change_pct': 'Change %',
                    'volume': 'Volume',
                    'high': 'High',
                    'low': 'Low'
                })
                .style.apply(lambda x: ['color: #4caf50' if v > 0 else 'color: #f44336' 
                                         for v in x], subset=['Change', 'Change %']),
                use_container_width=True,
                hide_index=True
            )

            # Sector Performance
            st.markdown("### 🏭 Sector Performance")
            sector_perf = get_sector_performance(quotes)
            if not sector_perf.empty:
                fig = go.Figure(go.Bar(
                    x=sector_perf['sector'],
                    y=sector_perf['avg_change'],
                    marker_color=['#4caf50' if v > 0 else '#f44336' for v in sector_perf['avg_change']],
                    text=[f"{v:+.2f}%" for v in sector_perf['avg_change']],
                    textposition='outside'
                ))

                fig.update_layout(
                    template='plotly_dark',
                    height=400,
                    showlegend=False,
                    xaxis_title='Sector',
                    yaxis_title='Average Change %'
                )

                st.plotly_chart(fig, use_container_width=True, key="sector_perf")
    except Exception as e:
        st.warning(f"Market data temporarily unavailable: {e}")

    # Stock Comparison
    st.markdown("### 📈 Stock Comparison")

    comparison_symbols = st.multiselect(
        "Select stocks to compare",
        get_all_symbols()[:50],
        default=['COMI', 'TMGH', 'EAST', 'SWDY'],
        max_selections=5
    )

    if comparison_symbols:
        try:
            data_dict = {}
            for sym in comparison_symbols:
                sym_df = market_engine.fetch(sym, period='1y', interval='1d')
                if sym_df is not None and not sym_df.empty:
                    data_dict[sym] = sym_df

            if data_dict:
                fig = chart_engine.create_comparison_chart(data_dict, normalize=True)
                st.plotly_chart(fig, use_container_width=True, key="comparison_chart")
        except Exception as e:
            st.error(f"Comparison error: {e}")


def render_settings():
    """Render settings page"""
    st.markdown("## ⚙️ Settings")

    # Appearance
    st.markdown("### 🎨 Appearance")

    theme = st.radio("Theme", ["Dark (Default)", "Light"], horizontal=True)
    language = st.selectbox("Language", ["English", "العربية"])

    # Notifications
    st.markdown("### 🔔 Notifications")

    st.session_state.notifications_enabled = st.toggle(
        "Enable Notifications",
        value=st.session_state.notifications_enabled
    )

    if st.session_state.notifications_enabled:
        st.checkbox("Email Alerts")
        st.checkbox("Telegram Alerts")
        st.checkbox("Webhook Alerts")

    # Data
    st.markdown("### 💾 Data Management")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")
    with col2:
        if st.button("💾 Backup Database", use_container_width=True):
            try:
                backup_path = local_storage.backup()
                if backup_path:
                    st.success(f"Backup created: {backup_path}")
                else:
                    st.error("Backup failed")
            except Exception as e:
                st.error(f"Backup error: {e}")

    # Database Stats
    st.markdown("### 📊 Database Statistics")
    try:
        stats = local_storage.get_stats()
        if stats:
            cols = st.columns(3)
            stats_display = [
                ("Stock Records", stats.get('stock_data', 0)),
                ("Alerts", stats.get('alerts', 0)),
                ("Watchlist", stats.get('watchlist', 0)),
                ("Analysis Cache", stats.get('analysis_cache', 0)),
                ("Backtests", stats.get('backtest_results', 0)),
                ("Size", f"{stats.get('size_bytes', 0)/1024/1024:.1f} MB")
            ]

            for i, (label, value) in enumerate(stats_display):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #888; font-size: 0.85em;">{label}</div>
                            <div style="color: white; font-size: 1.5em; font-weight: bold;">
                                {value}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Database statistics loading...")

    # About
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(f"""
        **EGX Pro Terminal v{app_config.VERSION}**

        - **Author:** {app_config.AUTHOR}
        - **License:** MIT
        - **Stocks:** 100+ EGX symbols
        - **Indicators:** RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX, Stochastic
        - **Features:** AI Predictions, Pattern Recognition, Backtesting, Alerts

        **Disclaimer:** This platform is for educational purposes only. 
        Not financial advice. Always do your own research before investing.
    """)


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════
def main():
    """Main application entry point"""

    # Render sidebar
    render_sidebar()

    # Render current page
    page = st.session_state.page

    if page == 'Dashboard':
        render_dashboard()
    elif page == 'Analysis':
        render_analysis()
    elif page == 'Charts':
        render_charts()
    elif page == 'Alerts':
        render_alerts()
    elif page == 'AI':
        render_ai()
    elif page == 'Watchlist':
        render_watchlist()
    elif page == 'Backtest':
        render_backtest()
    elif page == 'Market':
        render_market()
    elif page == 'Settings':
        render_settings()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
