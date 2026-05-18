"""
EGX Pro Terminal - Configuration & Settings
Advanced Technical Analysis Platform for Egyptian Stock Exchange
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import timedelta


@dataclass
class AppConfig:
    """Main application configuration"""
    # App Info
    APP_NAME: str = "EGX Pro Terminal"
    VERSION: str = "26.0.0"
    AUTHOR: str = "EGX Pro Team"

    # Streamlit
    PAGE_TITLE: str = "EGX Pro Terminal v26"
    PAGE_ICON: str = "📈"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"

    # Data
    DEFAULT_PERIOD: str = "1y"
    DEFAULT_INTERVAL: str = "1d"
    CACHE_TTL_DATA: int = 300  # 5 minutes
    CACHE_TTL_INDICATORS: int = 60  # 1 minute

    # Database
    DB_PATH: str = "data/egx_database.db"
    DB_BACKUP_INTERVAL: int = 86400  # 24 hours

    # Alerts
    ALERT_CHECK_INTERVAL: int = 60  # seconds
    MAX_ALERTS_PER_SYMBOL: int = 10
    ALERT_COOLDOWN_MINUTES: int = 30

    # AI/ML
    AI_MODEL_PATH: str = "models/"
    AI_PREDICTION_HORIZON: int = 5  # days
    AI_CONFIDENCE_THRESHOLD: float = 0.65

    # Backtesting
    BACKTEST_INITIAL_CAPITAL: float = 100000.0  # EGP
    BACKTEST_COMMISSION: float = 0.0015  # 0.15%

    # Notifications
    ENABLE_EMAIL_ALERTS: bool = False
    ENABLE_TELEGRAM_ALERTS: bool = False
    ENABLE_WEBHOOK_ALERTS: bool = False

    # UI
    THEME_PRIMARY_COLOR: str = "#1f77b4"
    THEME_SECONDARY_COLOR: str = "#ff7f0e"
    CHART_HEIGHT: int = 600
    MAX_CHART_POINTS: int = 500


@dataclass
class IndicatorConfig:
    """Technical indicator default parameters"""
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0

    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9

    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: float = 2.0

    EMA_PERIODS: List[int] = field(default_factory=lambda: [9, 21, 50, 200])
    SMA_PERIODS: List[int] = field(default_factory=lambda: [20, 50, 200])

    ATR_PERIOD: int = 14
    ADX_PERIOD: int = 14
    ADX_STRONG_TREND: float = 25.0

    STOCHASTIC_K: int = 14
    STOCHASTIC_D: int = 3

    VOLUME_MA_PERIOD: int = 20
    VOLUME_SPIKE_THRESHOLD: float = 2.0


@dataclass
class EGXConfig:
    """Egyptian Exchange specific settings"""
    MARKET_OPEN: str = "10:00"
    MARKET_CLOSE: str = "14:30"
    TRADING_DAYS: List[str] = field(default_factory=lambda: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"])

    # Symbol suffix for Yahoo Finance
    YAHOO_SUFFIX: str = ".CA"  # Cairo Exchange suffix

    # Sector mapping
    SECTORS: Dict[str, List[str]] = field(default_factory=lambda: {
        "Banking": ["COMI", "HRHO", "EGBE", "CBKD", "ABUK"],
        "Real Estate": ["MNHD", "PHDC", "HELl", "TMGH", "ORAS"],
        "Food & Beverage": ["EAST", "DOMT", "JUHO", "MPCI", "SKPC"],
        "Construction": ["ORWE", "SWDY", "ESRS", "AMOC", "HELW"],
        "Telecom": ["ETEL", "EGTS"],
        "Energy": ["CEFM", "SPIN", "APPC"],
        "Healthcare": ["PHAR", "MPCI", "POUL"],
        "Chemicals": ["EFIC", "KZPC", "NIPH"],
        "Tourism": ["HRHO", "TRTO"],
        "Industry": ["SIPC", "MISR", "MCRO"]
    })


# Global instances
app_config = AppConfig()
indicator_config = IndicatorConfig()
egx_config = EGXConfig()
