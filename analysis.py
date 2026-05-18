"""
EGX Pro Terminal - Technical Analysis Engine
Advanced indicator computation with caching and signal generation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from config.settings import indicator_config, app_config
from data.storage import local_storage


class TrendDirection(Enum):
    STRONG_UP = "Strong Up"
    UP = "Up"
    NEUTRAL = "Neutral"
    DOWN = "Down"
    STRONG_DOWN = "Strong Down"


@dataclass
class Signal:
    """Trading signal container"""
    indicator: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    price: float
    message: str
    timestamp: str


class TechnicalAnalysisEngine:
    """Professional technical analysis engine"""

    def __init__(self):
        self.config = indicator_config
        self.signals: List[Signal] = []

    def compute_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute all technical indicators"""
        if df is None or len(df) < 50:
            return df

        df = df.copy()

        # Trend Indicators
        df = self._compute_ema(df)
        df = self._compute_sma(df)

        # Momentum Indicators
        df = self._compute_rsi(df)
        df = self._compute_macd(df)
        df = self._compute_stochastic(df)

        # Volatility Indicators
        df = self._compute_bollinger(df)
        df = self._compute_atr(df)

        # Trend Strength
        df = self._compute_adx(df)

        # Volume Analysis
        df = self._compute_volume_indicators(df)

        # Generate signals
        df = self._generate_signals(df)

        # Determine trend
        df = self._determine_trend(df)

        return df

    def _compute_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Exponential Moving Averages"""
        for period in self.config.EMA_PERIODS:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    def _compute_sma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Simple Moving Averages"""
        for period in self.config.SMA_PERIODS:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        return df

    def _compute_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Relative Strength Index"""
        period = self.config.RSI_PERIOD
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi_signal'] = np.where(df['rsi'] < self.config.RSI_OVERSOLD, 'OVERSOLD',
                             np.where(df['rsi'] > self.config.RSI_OVERBOUGHT, 'OVERBOUGHT', 'NEUTRAL'))
        return df

    def _compute_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD Indicator"""
        fast = self.config.MACD_FAST
        slow = self.config.MACD_SLOW
        signal = self.config.MACD_SIGNAL

        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        df['macd_cross'] = np.where(
            (df['macd'].shift(1) < df['macd_signal'].shift(1)) & (df['macd'] > df['macd_signal']), 'BULLISH_CROSS',
            np.where(
                (df['macd'].shift(1) > df['macd_signal'].shift(1)) & (df['macd'] < df['macd_signal']), 'BEARISH_CROSS', 'NONE'
            )
        )
        return df

    def _compute_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Stochastic Oscillator"""
        k_period = self.config.STOCHASTIC_K
        d_period = self.config.STOCHASTIC_D

        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        df['stochastic_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
        df['stochastic_d'] = df['stochastic_k'].rolling(window=d_period).mean()
        return df

    def _compute_bollinger(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bollinger Bands"""
        period = self.config.BOLLINGER_PERIOD
        std_dev = self.config.BOLLINGER_STD

        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        df['bb_squeeze'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        return df

    def _compute_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Average True Range"""
        period = self.config.ATR_PERIOD
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=period).mean()
        df['atr_pct'] = (df['atr'] / df['close']) * 100
        return df

    def _compute_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Average Directional Index"""
        period = self.config.ADX_PERIOD

        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
        minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)

        tr = pd.concat([
            df['high'] - df['low'],
            np.abs(df['high'] - df['close'].shift()),
            np.abs(df['low'] - df['close'].shift())
        ], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(window=period).mean()
        df['plus_di'] = plus_di
        df['minus_di'] = minus_di
        df['adx_trend'] = np.where(df['adx'] > self.config.ADX_STRONG_TREND, 'STRONG', 'WEAK')
        return df

    def _compute_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volume-based indicators"""
        period = self.config.VOLUME_MA_PERIOD
        df['volume_ma'] = df['volume'].rolling(window=period).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        df['volume_spike'] = df['volume_ratio'] > self.config.VOLUME_SPIKE_THRESHOLD

        # On-Balance Volume
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv
        df['obv_ema'] = df['obv'].ewm(span=20, adjust=False).mean()
        return df

    def _generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals from indicators"""
        df['signal_rsi'] = np.where(df['rsi'] < self.config.RSI_OVERSOLD, 1,
                             np.where(df['rsi'] > self.config.RSI_OVERBOUGHT, -1, 0))

        df['signal_macd'] = np.where(df['macd_hist'] > 0, 1, -1)

        df['signal_bb'] = np.where(df['close'] < df['bb_lower'], 1,
                          np.where(df['close'] > df['bb_upper'], -1, 0))

        df['signal_ema'] = np.where(df['ema_9'] > df['ema_21'], 1, -1)

        df['signal_volume'] = np.where(df['volume_spike'] & (df['close'] > df['close'].shift(1)), 1,
                              np.where(df['volume_spike'] & (df['close'] < df['close'].shift(1)), -1, 0))

        # Composite signal
        signals = ['signal_rsi', 'signal_macd', 'signal_bb', 'signal_ema', 'signal_volume']
        df['composite_signal'] = df[signals].sum(axis=1)
        df['signal_strength'] = np.abs(df['composite_signal']) / len(signals)

        df['final_signal'] = np.where(df['composite_signal'] >= 3, 'STRONG_BUY',
                             np.where(df['composite_signal'] >= 1, 'BUY',
                             np.where(df['composite_signal'] <= -3, 'STRONG_SELL',
                             np.where(df['composite_signal'] <= -1, 'SELL', 'HOLD'))))

        return df

    def _determine_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Determine overall trend direction and strength"""
        conditions = [
            (df['adx'] > 25) & (df['plus_di'] > df['minus_di']) & (df['close'] > df['ema_50']),
            (df['adx'] > 25) & (df['plus_di'] > df['minus_di']),
            (df['adx'] > 25) & (df['minus_di'] > df['plus_di']) & (df['close'] < df['ema_50']),
            (df['adx'] > 25) & (df['minus_di'] > df['plus_di']),
        ]
        choices = [
            TrendDirection.STRONG_UP.value,
            TrendDirection.UP.value,
            TrendDirection.STRONG_DOWN.value,
            TrendDirection.DOWN.value,
        ]
        df['trend'] = np.select(conditions, choices, default=TrendDirection.NEUTRAL.value)

        # Trend strength score (0-100)
        df['trend_strength'] = (
            (df['adx'].fillna(0) / 100 * 30) +
            (np.where(df['close'] > df['ema_50'], 20, -20).fillna(0)) +
            (np.where(df['close'] > df['ema_200'], 15, -15).fillna(0)) +
            (np.where(df['macd'] > 0, 15, -15).fillna(0)) +
            (np.where(df['rsi'] > 50, 10, -10).fillna(0)) +
            (np.where(df['volume'] > df['volume_ma'], 10, 0).fillna(0))
        )
        df['trend_strength'] = np.clip(df['trend_strength'], 0, 100)

        return df

    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels"""
        if len(df) < window * 2:
            return {}

        recent = df.tail(window * 2)

        # Local minima and maxima
        local_min = recent['low'].rolling(window=5, center=True).min()
        local_max = recent['high'].rolling(window=5, center=True).max()

        supports = recent[recent['low'] == local_min]['low'].tail(3).tolist()
        resistances = recent[recent['high'] == local_max]['high'].tail(3).tolist()

        current_price = df['close'].iloc[-1]

        nearest_support = max([s for s in supports if s < current_price], default=current_price * 0.95)
        nearest_resistance = min([r for r in resistances if r > current_price], default=current_price * 1.05)

        return {
            'supports': supports,
            'resistances': resistances,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'pivot_point': (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
        }

    def get_fibonacci_levels(self, df: pd.DataFrame) -> Dict:
        """Calculate Fibonacci retracement levels"""
        high = df['high'].max()
        low = df['low'].min()
        diff = high - low

        levels = {
            '0.0%': high,
            '23.6%': high - 0.236 * diff,
            '38.2%': high - 0.382 * diff,
            '50.0%': high - 0.5 * diff,
            '61.8%': high - 0.618 * diff,
            '78.6%': high - 0.786 * diff,
            '100.0%': low
        }

        current = df['close'].iloc[-1]
        levels['current'] = current

        # Find nearest levels
        for level_name, level_price in levels.items():
            if level_name not in ['current'] and level_price > current:
                levels['nearest_resistance_fib'] = level_price
                break

        for level_name, level_price in reversed(list(levels.items())):
            if level_name not in ['current', 'nearest_resistance_fib'] and level_price < current:
                levels['nearest_support_fib'] = level_price
                break

        return levels

    def get_summary(self, df: pd.DataFrame) -> Dict:
        """Get analysis summary for latest data point"""
        if df is None or df.empty:
            return {}

        latest = df.iloc[-1]

        sr = self.get_support_resistance(df)
        fib = self.get_fibonacci_levels(df)

        return {
            'price': round(latest['close'], 2),
            'change': round(latest['close'] - df['close'].iloc[-2], 2) if len(df) > 1 else 0,
            'change_pct': round((latest['close'] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100, 2) if len(df) > 1 else 0,
            'volume': int(latest['volume']),
            'rsi': round(latest.get('rsi', 0), 2),
            'macd': round(latest.get('macd', 0), 4),
            'macd_signal': latest.get('macd_cross', 'NONE'),
            'bb_position': round(latest.get('bb_position', 0.5), 2),
            'adx': round(latest.get('adx', 0), 2),
            'trend': latest.get('trend', 'Unknown'),
            'trend_strength': round(latest.get('trend_strength', 0), 1),
            'final_signal': latest.get('final_signal', 'HOLD'),
            'signal_strength': round(latest.get('signal_strength', 0), 2),
            'atr': round(latest.get('atr', 0), 2),
            'support_resistance': sr,
            'fibonacci': fib,
            'ema_9': round(latest.get('ema_9', 0), 2),
            'ema_21': round(latest.get('ema_21', 0), 2),
            'ema_50': round(latest.get('ema_50', 0), 2),
            'ema_200': round(latest.get('ema_200', 0), 2),
        }


# Global instance
analysis_engine = TechnicalAnalysisEngine()
