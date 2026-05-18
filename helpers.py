"""
EGX Pro Terminal - Utility Helpers
Common utility functions and formatters
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with commas and specified decimals"""
    if num is None:
        return "N/A"
    return f"{num:,.{decimals}f}"


def format_currency(num: float, currency: str = "EGP") -> str:
    """Format as currency"""
    if num is None:
        return "N/A"
    return f"{format_number(num)} {currency}"


def format_percentage(num: float, decimals: int = 2) -> str:
    """Format as percentage with color indicator"""
    if num is None:
        return "N/A"
    sign = "+" if num > 0 else ""
    return f"{sign}{num:.{decimals}f}%"


def format_volume(num: int) -> str:
    """Format large volume numbers"""
    if num is None:
        return "N/A"
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def get_signal_color(signal: str) -> str:
    """Get color for signal type"""
    colors = {
        'STRONG_BUY': '#00e676',
        'BUY': '#4caf50',
        'HOLD': '#ff9800',
        'SELL': '#f44336',
        'STRONG_SELL': '#d50000',
        'NEUTRAL': '#9e9e9e',
        'UP': '#4caf50',
        'DOWN': '#f44336',
        'SIDEWAYS': '#ff9800'
    }
    return colors.get(signal, '#9e9e9e')


def get_trend_color(trend: str) -> str:
    """Get color for trend"""
    colors = {
        'Strong Up': '#00e676',
        'Up': '#4caf50',
        'Neutral': '#ff9800',
        'Down': '#f44336',
        'Strong Down': '#d50000'
    }
    return colors.get(trend, '#9e9e9e')


def get_severity_color(severity: str) -> str:
    """Get color for alert severity"""
    colors = {
        'info': '#2196F3',
        'warning': '#FF9800',
        'critical': '#f44336'
    }
    return colors.get(severity, '#9e9e9e')


def get_severity_emoji(severity: str) -> str:
    """Get emoji for alert severity"""
    emojis = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'critical': '🚨'
    }
    return emojis.get(severity, 'ℹ️')


def render_metric_card(label: str, value: str, delta: str = None, 
                       delta_color: str = None, help_text: str = None):
    """Render a styled metric card"""
    delta_html = ""
    if delta:
        color = delta_color or ("green" if "+" in str(delta) else "red")
        delta_html = f'<span style="color:{color};font-size:0.8em">{delta}</span>'

    help_html = f'<span title="{help_text}">❓</span>' if help_text else ""

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        ">
            <div style="color: #888; font-size: 0.85em; margin-bottom: 5px;">
                {label} {help_html}
            </div>
            <div style="color: white; font-size: 1.5em; font-weight: bold;">
                {value}
            </div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def render_signal_badge(signal: str, size: str = "normal"):
    """Render a signal badge"""
    color = get_signal_color(signal)
    font_size = "1em" if size == "normal" else "0.8em"
    padding = "8px 16px" if size == "normal" else "4px 8px"

    st.markdown(f"""
        <span style="
            background-color: {color}22;
            color: {color};
            border: 1px solid {color};
            border-radius: 20px;
            padding: {padding};
            font-size: {font_size};
            font-weight: bold;
        ">{signal}</span>
    """, unsafe_allow_html=True)


def render_progress_bar(value: float, max_value: float = 100, 
                        color: str = None, label: str = ""):
    """Render a styled progress bar"""
    if color is None:
        if value >= 70:
            color = "#4caf50"
        elif value >= 40:
            color = "#ff9800"
        else:
            color = "#f44336"

    percentage = min((value / max_value) * 100, 100)

    st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                <span style="color: #ccc; font-size: 0.85em;">{label}</span>
                <span style="color: {color}; font-size: 0.85em; font-weight: bold;">{value:.1f}</span>
            </div>
            <div style="
                background-color: rgba(255,255,255,0.1);
                border-radius: 5px;
                height: 8px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, {color}88, {color});
                    width: {percentage}%;
                    height: 100%;
                    border-radius: 5px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_alert_card(alert: Dict):
    """Render an alert card"""
    severity = alert.get('severity', 'info')
    color = get_severity_color(severity)
    emoji = get_severity_emoji(severity)

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 10px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {color}; font-weight: bold;">
                    {emoji} {alert.get('alert_type', 'Alert').upper()}
                </span>
                <span style="color: #888; font-size: 0.8em;">
                    {alert.get('timestamp', '')[:16]}
                </span>
            </div>
            <div style="color: white; margin-top: 5px; font-size: 0.95em;">
                {alert.get('message', '')}
            </div>
            <div style="color: #888; font-size: 0.8em; margin-top: 3px;">
                {alert.get('symbol', '')} @ {alert.get('price', 'N/A')} EGP
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_separator():
    """Render a visual separator"""
    st.markdown("""
        <hr style="
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 20px 0;
        ">
    """, unsafe_allow_html=True)


def get_arabic_number(num: float) -> str:
    """Convert number to Arabic numerals"""
    arabic_nums = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                   '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩', '.': '.'}
    return ''.join(arabic_nums.get(c, c) for c in str(num))


def time_ago(dt_str: str) -> str:
    """Convert datetime string to human-readable time ago"""
    try:
        dt = pd.to_datetime(dt_str)
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    except:
        return dt_str


def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol"""
    from data.egx_symbols import SYMBOL_MAP
    return symbol.upper() in SYMBOL_MAP


def get_sector_performance(quotes_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sector performance"""
    from data.egx_symbols import SECTOR_MAP

    sector_perf = []
    for sector, stocks in SECTOR_MAP.items():
        sector_symbols = [s.symbol for s in stocks]
        sector_data = quotes_df[quotes_df['symbol'].isin(sector_symbols)]

        if not sector_data.empty:
            avg_change = sector_data['change_pct'].mean()
            sector_perf.append({
                'sector': sector,
                'avg_change': avg_change,
                'stocks_count': len(sector_data),
                'top_gainer': sector_data.loc[sector_data['change_pct'].idxmax(), 'symbol'] if len(sector_data) > 0 else None
            })

    return pd.DataFrame(sector_perf).sort_values('avg_change', ascending=False)
