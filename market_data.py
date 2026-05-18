"""
EGX Pro Terminal - Multi-Source Market Data Provider
Advanced data fetching with caching, fallback sources, and real-time simulation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import time
import requests
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

from data.egx_symbols import get_yahoo_symbol, get_all_symbols
from config.settings import app_config


class DataProvider(ABC):
    """Abstract base class for data providers"""

    @abstractmethod
    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class YahooFinanceProvider(DataProvider):
    """Yahoo Finance data provider with retry logic"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._last_request_time = 0
        self._min_request_interval = 0.5  # seconds between requests

    def is_available(self) -> bool:
        try:
            # Quick test with a well-known symbol
            test = yf.Ticker("AAPL")
            _ = test.info
            return True
        except:
            return False

    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch data with retry logic and rate limiting"""
        yahoo_sym = get_yahoo_symbol(symbol)

        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)

        for attempt in range(self.max_retries):
            try:
                self._last_request_time = time.time()
                ticker = yf.Ticker(yahoo_sym)
                df = ticker.history(period=period, interval=interval)

                if df.empty:
                    print(f"⚠️ Empty data for {symbol} (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    return None

                # Standardize column names
                df.columns = [c.lower().replace(' ', '_') for c in df.columns]
                df = df.reset_index()

                # Handle timezone
                if hasattr(df['date'], 'dt'):
                    df['date'] = df['date'].dt.tz_localize(None)

                # Add metadata
                df['symbol'] = symbol
                df['source'] = 'yahoo'
                df['fetched_at'] = datetime.now()

                return df

            except Exception as e:
                print(f"❌ Yahoo Finance error for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None

        return None


class LocalCacheProvider(DataProvider):
    """Local SQLite cache provider"""

    def __init__(self, db_path: str = None):
        from data.storage import LocalStorage
        self.storage = LocalStorage(db_path or app_config.DB_PATH)

    def is_available(self) -> bool:
        try:
            self.storage.conn.execute("SELECT 1")
            return True
        except:
            return False

    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        return self.storage.get_stock_data(symbol, period)

    def store(self, df: pd.DataFrame) -> bool:
        """Store data in local cache"""
        if df is None or df.empty:
            return False
        return self.storage.store_stock_data(df)


class SimulatedProvider(DataProvider):
    """Simulated data provider for testing and fallback"""

    def __init__(self):
        np.random.seed(42)

    def is_available(self) -> bool:
        return True

    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Generate realistic simulated OHLCV data"""
        # Parse period
        days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
        n_days = days_map.get(period, 365)

        # Generate dates (business days only)
        end_date = datetime.now()
        dates = pd.bdate_range(end=end_date, periods=n_days)

        # Base price around 10-100 EGP
        base_price = np.random.uniform(10, 100)

        # Generate random walk
        returns = np.random.normal(0.0002, 0.02, len(dates))
        prices = base_price * np.exp(np.cumsum(returns))

        # Generate OHLC from close
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
        })

        df['open'] = df['close'].shift(1) * (1 + np.random.normal(0, 0.005, len(df)))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.01, len(df))))
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.01, len(df))))
        df['volume'] = np.random.randint(100000, 5000000, len(df))

        df = df.fillna(method='bfill')
        df['symbol'] = symbol
        df['source'] = 'simulated'
        df['fetched_at'] = datetime.now()

        return df.reset_index(drop=True)


class MarketDataEngine:
    """Multi-source data engine with intelligent fallback"""

    def __init__(self):
        self.providers = {
            'yahoo': YahooFinanceProvider(),
            'cache': LocalCacheProvider(),
            'simulated': SimulatedProvider()
        }
        self.priority = ['yahoo', 'cache', 'simulated']
        self._cache = {}
        self._cache_timestamp = {}

    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d", 
              use_cache: bool = True, store_cache: bool = True) -> Optional[pd.DataFrame]:
        """
        Fetch stock data with multi-source fallback

        Args:
            symbol: EGX stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
            interval: Data interval (1d, 1wk, 1mo)
            use_cache: Whether to use local cache first
            store_cache: Whether to store fetched data in cache

        Returns:
            DataFrame with OHLCV data or None
        """
        cache_key = f"{symbol}_{period}_{interval}"

        # Check memory cache
        if use_cache and cache_key in self._cache:
            cached_time = self._cache_timestamp.get(cache_key, 0)
            if time.time() - cached_time < app_config.CACHE_TTL_DATA:
                print(f"📦 Memory cache hit for {symbol}")
                return self._cache[cache_key].copy()

        # Try providers in priority order
        df = None
        used_provider = None

        for provider_name in self.priority:
            provider = self.providers[provider_name]

            if not provider.is_available():
                continue

            print(f"🔍 Trying {provider_name} for {symbol}...")
            df = provider.fetch(symbol, period, interval)

            if df is not None and not df.empty:
                used_provider = provider_name
                break

        if df is None or df.empty:
            print(f"❌ Failed to fetch data for {symbol} from all sources")
            return None

        print(f"✅ Data fetched from {used_provider} for {symbol}: {len(df)} rows")

        # Store in cache
        if store_cache and used_provider != 'cache':
            self.providers['cache'].store(df)

        # Update memory cache
        self._cache[cache_key] = df.copy()
        self._cache_timestamp[cache_key] = time.time()

        return df

    def fetch_multiple(self, symbols: List[str], period: str = "1y", 
                       interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols"""
        results = {}
        for symbol in symbols:
            df = self.fetch(symbol, period, interval)
            if df is not None:
                results[symbol] = df
            time.sleep(0.5)  # Rate limiting
        return results

    def get_realtime_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote (simulated for EGX)"""
        df = self.fetch(symbol, period="5d", interval="1d")
        if df is None or df.empty:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        change = latest['close'] - prev['close']
        change_pct = (change / prev['close']) * 100 if prev['close'] != 0 else 0

        return {
            'symbol': symbol,
            'price': round(latest['close'], 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'volume': int(latest['volume']),
            'high': round(latest['high'], 2),
            'low': round(latest['low'], 2),
            'open': round(latest['open'], 2),
            'timestamp': latest['date'],
            'source': latest.get('source', 'unknown')
        }

    def get_market_overview(self) -> pd.DataFrame:
        """Get overview of all active stocks"""
        symbols = get_all_symbols()[:20]  # Limit to 20 for performance
        quotes = []

        for symbol in symbols:
            quote = self.get_realtime_quote(symbol)
            if quote:
                quotes.append(quote)

        return pd.DataFrame(quotes)


# Global instance
market_engine = MarketDataEngine()
