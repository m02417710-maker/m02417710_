# 📈 EGX Pro Terminal v26

**Professional Technical Analysis Platform for Egyptian Stock Exchange (EGX)**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Advanced Technical Analysis** | RSI, MACD, Bollinger Bands, EMA, SMA, ATR, ADX, Stochastic |
| 🤖 **AI Predictions** | Ensemble rule-based prediction engine with confidence scoring |
| 🔔 **Smart Alerts** | Multi-condition alerts with severity levels and notification channels |
| 🔍 **Pattern Recognition** | 20+ candlestick patterns with confidence scoring |
| 📈 **Interactive Charts** | Plotly-powered charts with multiple overlays |
| 🧪 **Backtesting** | Historical strategy testing with full performance metrics |
| 📋 **Watchlist** | Track your favorite stocks with target prices |
| 🏢 **Market Overview** | Sector performance and stock comparison |
| 💾 **Local Storage** | SQLite database with backup and optimization |
| 🌐 **Multi-Source Data** | Yahoo Finance with fallback to local cache and simulation |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/m02417710-maker/egx-pro-terminal.git
cd egx-pro-terminal

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
egx-pro-terminal/
├── 📄 app.py                    # Main Streamlit application
├── 📁 core/
│   ├── 📄 __init__.py
│   ├── 📄 analysis.py           # Technical analysis engine
│   ├── 📄 alerts.py             # Smart alert system
│   ├── 📄 patterns.py           # Candlestick pattern recognition
│   ├── 📄 ai_engine.py          # AI prediction engine
│   ├── 📄 backtest.py           # Backtesting engine
│   └── 📄 charts.py             # Plotly charting engine
├── 📁 data/
│   ├── 📄 __init__.py
│   ├── 📄 egx_symbols.py        # 100+ EGX stock database
│   ├── 📄 market_data.py        # Multi-source data provider
│   └── 📄 storage.py            # SQLite storage engine
├── 📁 config/
│   ├── 📄 __init__.py
│   └── 📄 settings.py           # Configuration and constants
├── 📁 utils/
│   ├── 📄 __init__.py
│   └── 📄 helpers.py            # Utility functions and formatters
├── 📁 tests/
│   ├── 📄 __init__.py
│   └── 📄 test_analysis.py      # Unit tests
├── 📄 requirements.txt          # Python dependencies
├── 📄 LICENSE                   # MIT License
└── 📄 README.md                 # This file
```

---

## 🎯 Usage Guide

### 1. Dashboard
- Market overview with top gainers/losers
- Featured stock analysis
- AI prediction preview
- Recent alerts

### 2. Stock Analysis
- Detailed technical indicators
- Support/Resistance levels
- Fibonacci retracement
- Pattern detection
- Trend analysis

### 3. Charts
- Interactive candlestick charts
- RSI, ADX, Stochastic sub-charts
- Volume analysis
- Customizable indicators

### 4. Alerts
- Create price, RSI, MACD, EMA alerts
- Manage active alerts
- View alert history

### 5. AI Predictions
- Single stock prediction
- Market sentiment analysis
- Feature importance
- Risk/Reward calculation

### 6. Watchlist
- Track favorite stocks
- Set target prices and stop losses
- Monitor performance

### 7. Backtest
- Test strategies historically
- View equity curves
- Analyze drawdowns
- Compare strategies

### 8. Market Overview
- Full market summary
- Sector performance
- Stock comparison

---

## ⚙️ Configuration

Edit `config/settings.py` to customize:

```python
# Data settings
DEFAULT_PERIOD = "1y"
CACHE_TTL_DATA = 300  # seconds

# Alert settings
ALERT_CHECK_INTERVAL = 60
MAX_ALERTS_PER_SYMBOL = 10

# AI settings
AI_PREDICTION_HORIZON = 5  # days
AI_CONFIDENCE_THRESHOLD = 0.65

# Backtest settings
BACKTEST_INITIAL_CAPITAL = 100000.0
BACKTEST_COMMISSION = 0.0015
```

---

## 🧪 Running Tests

```bash
python -m unittest tests.test_analysis
```

---

## 🛠️ Development

### Adding a New Indicator

1. Add computation in `core/analysis.py`:
```python
def _compute_custom_indicator(self, df):
    df['custom'] = df['close'].rolling(10).mean()
    return df
```

2. Call it in `compute_all()`
3. Add to summary in `get_summary()`

### Adding a New Strategy

1. Add strategy function in `core/backtest.py`:
```python
def my_strategy(self, df, params):
    signals = pd.Series(0, index=df.index)
    signals[df['rsi'] < 30] = 1
    signals[df['rsi'] > 70] = -1
    return signals
```

2. Register in `get_strategy_list()`

---

## 📊 Supported Stocks

The platform supports **100+ Egyptian stocks** across all sectors:

- **Banking:** COMI, EGBE, CBKD, NSGB, HDBK, FAIT
- **Real Estate:** TMGH, MNHD, PHDC, HELL, ORAS
- **Food & Beverage:** EAST, DOMT, JUHO, UNIP, OLFI
- **Construction:** ORWE, SWDY, ESRS, AMOC, HELW
- **Telecom:** ETEL, EGTS
- **Energy:** TAQA, EDBM
- **Healthcare:** PHAR, RMDA, IDHC, CLHO
- **Chemicals:** EFIC, KZPC, NIPH, MICH
- **Technology:** FWRY, EGTS3, SWVL
- And many more...

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** This platform is for educational purposes only. Not financial advice. Always do your own research before investing.

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) - For the amazing web framework
- [Plotly](https://plotly.com) - For interactive charts
- [yfinance](https://github.com/ranaroussi/yfinance) - For market data
- [TA-Lib](https://mrjbq7.github.io/ta-lib/) - For technical indicators

---

<div align="center">

**🇪🇬 Made with ❤️ in Egypt**

[Report Bug](https://github.com/m02417710-maker/egx-pro-terminal/issues) · 
[Request Feature](https://github.com/m02417710-maker/egx-pro-terminal/issues)

</div>
