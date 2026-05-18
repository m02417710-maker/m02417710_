"""
EGX Pro Terminal - Candlestick Pattern Recognition Engine
Advanced pattern detection with confidence scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    REVERSAL = "reversal"
    CONTINUATION = "continuation"
    INDECISION = "indecision"


class PatternStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class Pattern:
    """Candlestick pattern detection result"""
    name: str
    type: PatternType
    strength: PatternStrength
    confidence: float  # 0.0 to 1.0
    position: str  # top, bottom, middle
    index: int
    description: str
    bullish: bool


class PatternEngine:
    """Advanced candlestick pattern recognition engine"""

    def __init__(self):
        self.patterns = {
            'single': self._single_candle_patterns,
            'double': self._double_candle_patterns,
            'triple': self._triple_candle_patterns,
        }

    def detect_all(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect all patterns in the dataframe"""
        if df is None or len(df) < 3:
            return []

        patterns = []

        # Single candle patterns
        patterns.extend(self._single_candle_patterns(df))

        # Double candle patterns
        patterns.extend(self._double_candle_patterns(df))

        # Triple candle patterns
        patterns.extend(self._triple_candle_patterns(df))

        # Sort by confidence
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        return patterns

    def _get_body(self, open_price: float, close_price: float) -> Tuple[float, float]:
        """Get candle body size and direction"""
        body = abs(close_price - open_price)
        direction = 1 if close_price > open_price else -1
        return body, direction

    def _get_shadows(self, high: float, low: float, open_price: float, close_price: float) -> Tuple[float, float]:
        """Get upper and lower shadows"""
        upper = high - max(open_price, close_price)
        lower = min(open_price, close_price) - low
        return upper, lower

    def _single_candle_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect single candlestick patterns"""
        patterns = []

        for i in range(len(df)):
            row = df.iloc[i]
            open_p = row['open']
            close = row['close']
            high = row['high']
            low = row['low']

            body, direction = self._get_body(open_p, close)
            upper, lower = self._get_shadows(high, low, open_p, close)
            total_range = high - low

            if total_range == 0:
                continue

            body_pct = body / total_range
            upper_pct = upper / total_range
            lower_pct = lower / total_range

            # Doji
            if body_pct < 0.05:
                confidence = 1 - (body_pct * 20)
                patterns.append(Pattern(
                    name="Doji",
                    type=PatternType.INDECISION,
                    strength=PatternStrength.MODERATE,
                    confidence=confidence,
                    position="middle",
                    index=i,
                    description="Indecision in the market. Potential reversal signal.",
                    bullish=None
                ))

            # Hammer
            if direction == 1 and lower_pct > 0.6 and upper_pct < 0.05 and body_pct > 0.1:
                confidence = lower_pct * 0.8
                patterns.append(Pattern(
                    name="Hammer",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Bullish reversal at support level.",
                    bullish=True
                ))

            # Inverted Hammer
            if direction == 1 and upper_pct > 0.6 and lower_pct < 0.05 and body_pct > 0.1:
                confidence = upper_pct * 0.7
                patterns.append(Pattern(
                    name="Inverted Hammer",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Potential bullish reversal.",
                    bullish=True
                ))

            # Shooting Star
            if direction == -1 and upper_pct > 0.6 and lower_pct < 0.05 and body_pct > 0.1:
                confidence = upper_pct * 0.8
                patterns.append(Pattern(
                    name="Shooting Star",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Bearish reversal at resistance level.",
                    bullish=False
                ))

            # Hanging Man
            if direction == -1 and lower_pct > 0.6 and upper_pct < 0.05 and body_pct > 0.1:
                confidence = lower_pct * 0.7
                patterns.append(Pattern(
                    name="Hanging Man",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Potential bearish reversal at top.",
                    bullish=False
                ))

            # Marubozu
            if body_pct > 0.95:
                confidence = body_pct
                patterns.append(Pattern(
                    name="Marubozu",
                    type=PatternType.CONTINUATION,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="middle",
                    index=i,
                    description=f"Strong {'bullish' if direction == 1 else 'bearish'} momentum.",
                    bullish=direction == 1
                ))

            # Spinning Top
            if body_pct < 0.3 and upper_pct > 0.3 and lower_pct > 0.3:
                confidence = 0.6
                patterns.append(Pattern(
                    name="Spinning Top",
                    type=PatternType.INDECISION,
                    strength=PatternStrength.WEAK,
                    confidence=confidence,
                    position="middle",
                    index=i,
                    description="Market indecision, potential reversal ahead.",
                    bullish=None
                ))

        return patterns

    def _double_candle_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect double candlestick patterns"""
        patterns = []

        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]

            prev_body, prev_dir = self._get_body(prev['open'], prev['close'])
            curr_body, curr_dir = self._get_body(curr['open'], curr['close'])

            prev_total = prev['high'] - prev['low']
            curr_total = curr['high'] - curr['low']

            if prev_total == 0 or curr_total == 0:
                continue

            # Engulfing Bullish
            if (prev_dir == -1 and curr_dir == 1 and 
                curr['open'] < prev['close'] and curr['close'] > prev['open'] and
                curr_body > prev_body * 1.2):
                confidence = min(curr_body / curr_total, 0.95)
                patterns.append(Pattern(
                    name="Bullish Engulfing",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Strong bullish reversal. Buyers took control.",
                    bullish=True
                ))

            # Engulfing Bearish
            if (prev_dir == 1 and curr_dir == -1 and 
                curr['open'] > prev['close'] and curr['close'] < prev['open'] and
                curr_body > prev_body * 1.2):
                confidence = min(curr_body / curr_total, 0.95)
                patterns.append(Pattern(
                    name="Bearish Engulfing",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Strong bearish reversal. Sellers took control.",
                    bullish=False
                ))

            # Bullish Harami
            if (prev_dir == -1 and curr_dir == 1 and 
                curr['open'] > prev['close'] and curr['close'] < prev['open'] and
                curr_body < prev_body * 0.6):
                confidence = 0.7
                patterns.append(Pattern(
                    name="Bullish Harami",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Potential bullish reversal. Momentum slowing down.",
                    bullish=True
                ))

            # Bearish Harami
            if (prev_dir == 1 and curr_dir == -1 and 
                curr['open'] < prev['close'] and curr['close'] > prev['open'] and
                curr_body < prev_body * 0.6):
                confidence = 0.7
                patterns.append(Pattern(
                    name="Bearish Harami",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.MODERATE,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Potential bearish reversal. Momentum slowing down.",
                    bullish=False
                ))

            # Tweezer Bottom
            if (prev_dir == -1 and curr_dir == 1 and 
                abs(prev['low'] - curr['low']) < prev_total * 0.01):
                confidence = 0.75
                patterns.append(Pattern(
                    name="Tweezer Bottom",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Double bottom pattern. Strong support level.",
                    bullish=True
                ))

            # Tweezer Top
            if (prev_dir == 1 and curr_dir == -1 and 
                abs(prev['high'] - curr['high']) < prev_total * 0.01):
                confidence = 0.75
                patterns.append(Pattern(
                    name="Tweezer Top",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Double top pattern. Strong resistance level.",
                    bullish=False
                ))

            # Piercing Line
            if (prev_dir == -1 and curr_dir == 1 and 
                curr['open'] < prev['low'] and 
                curr['close'] > prev['open'] + (prev_body * 0.5)):
                confidence = 0.8
                patterns.append(Pattern(
                    name="Piercing Line",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Bullish reversal. Buyers stepping in.",
                    bullish=True
                ))

            # Dark Cloud Cover
            if (prev_dir == 1 and curr_dir == -1 and 
                curr['open'] > prev['high'] and 
                curr['close'] < prev['open'] + (prev_body * 0.5)):
                confidence = 0.8
                patterns.append(Pattern(
                    name="Dark Cloud Cover",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Bearish reversal. Sellers stepping in.",
                    bullish=False
                ))

        return patterns

    def _triple_candle_patterns(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect triple candlestick patterns"""
        patterns = []

        for i in range(2, len(df)):
            first = df.iloc[i-2]
            second = df.iloc[i-1]
            third = df.iloc[i]

            f_body, f_dir = self._get_body(first['open'], first['close'])
            s_body, s_dir = self._get_body(second['open'], second['close'])
            t_body, t_dir = self._get_body(third['open'], third['close'])

            f_total = first['high'] - first['low']
            s_total = second['high'] - second['low']
            t_total = third['high'] - third['low']

            if f_total == 0 or s_total == 0 or t_total == 0:
                continue

            # Morning Star
            if (f_dir == -1 and s_body < f_body * 0.3 and t_dir == 1 and
                third['close'] > first['open'] + f_body * 0.5):
                confidence = 0.85
                patterns.append(Pattern(
                    name="Morning Star",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Powerful bullish reversal pattern. Three-candle confirmation.",
                    bullish=True
                ))

            # Evening Star
            if (f_dir == 1 and s_body < f_body * 0.3 and t_dir == -1 and
                third['close'] < first['open'] - f_body * 0.5):
                confidence = 0.85
                patterns.append(Pattern(
                    name="Evening Star",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Powerful bearish reversal pattern. Three-candle confirmation.",
                    bullish=False
                ))

            # Three White Soldiers
            if (f_dir == 1 and s_dir == 1 and t_dir == 1 and
                second['open'] > first['open'] and third['open'] > second['open'] and
                second['close'] > first['close'] and third['close'] > second['close']):
                confidence = 0.9
                patterns.append(Pattern(
                    name="Three White Soldiers",
                    type=PatternType.CONTINUATION,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="middle",
                    index=i,
                    description="Strong bullish continuation. Buyers in full control.",
                    bullish=True
                ))

            # Three Black Crows
            if (f_dir == -1 and s_dir == -1 and t_dir == -1 and
                second['open'] < first['open'] and third['open'] < second['open'] and
                second['close'] < first['close'] and third['close'] < second['close']):
                confidence = 0.9
                patterns.append(Pattern(
                    name="Three Black Crows",
                    type=PatternType.CONTINUATION,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    position="middle",
                    index=i,
                    description="Strong bearish continuation. Sellers in full control.",
                    bullish=False
                ))

            # Three Inside Up
            if (f_dir == -1 and s_dir == 1 and t_dir == 1 and
                second['open'] > first['close'] and second['close'] < first['open'] and
                third['close'] > first['close']):
                confidence = 0.8
                patterns.append(Pattern(
                    name="Three Inside Up",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="bottom",
                    index=i,
                    description="Bullish reversal confirmed by third candle.",
                    bullish=True
                ))

            # Three Inside Down
            if (f_dir == 1 and s_dir == -1 and t_dir == -1 and
                second['open'] < first['close'] and second['close'] > first['open'] and
                third['close'] < first['close']):
                confidence = 0.8
                patterns.append(Pattern(
                    name="Three Inside Down",
                    type=PatternType.REVERSAL,
                    strength=PatternStrength.STRONG,
                    confidence=confidence,
                    position="top",
                    index=i,
                    description="Bearish reversal confirmed by third candle.",
                    bullish=False
                ))

        return patterns

    def get_latest_patterns(self, df: pd.DataFrame, n: int = 5) -> List[Pattern]:
        """Get patterns from last n candles"""
        all_patterns = self.detect_all(df)
        latest_idx = len(df) - 1
        return [p for p in all_patterns if latest_idx - p.index <= n]

    def get_pattern_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of detected patterns"""
        patterns = self.detect_all(df)

        if not patterns:
            return {
                'total': 0,
                'latest': None,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }

        latest = patterns[0]

        bullish = sum(1 for p in patterns if p.bullish is True)
        bearish = sum(1 for p in patterns if p.bullish is False)
        neutral = sum(1 for p in patterns if p.bullish is None)

        return {
            'total': len(patterns),
            'latest': {
                'name': latest.name,
                'type': latest.type.value,
                'strength': latest.strength.name,
                'confidence': round(latest.confidence, 2),
                'position': latest.position,
                'bullish': latest.bullish,
                'description': latest.description
            },
            'bullish_count': bullish,
            'bearish_count': bearish,
            'neutral_count': neutral
        }


# Global instance
pattern_engine = PatternEngine()
