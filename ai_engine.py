"""
EGX Pro Terminal - AI/ML Prediction Engine
Machine learning models for trend prediction and sentiment analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config.settings import app_config


@dataclass
class PredictionResult:
    """AI prediction result container"""
    symbol: str
    current_price: float
    predicted_direction: str  # UP, DOWN, SIDEWAYS
    confidence: float
    target_price: float
    stop_loss: float
    horizon_days: int
    features_importance: Dict[str, float]
    model_used: str
    timestamp: str


class AIPredictionEngine:
    """AI-powered prediction engine for EGX stocks"""

    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.is_trained = False

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare feature set for ML models"""
        if df is None or len(df) < 50:
            return None

        features = pd.DataFrame(index=df.index)

        # Price-based features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        features['price_momentum_5'] = df['close'].pct_change(5)
        features['price_momentum_10'] = df['close'].pct_change(10)
        features['price_momentum_20'] = df['close'].pct_change(20)

        # Volatility features
        features['volatility_5'] = features['returns'].rolling(5).std()
        features['volatility_10'] = features['returns'].rolling(10).std()
        features['volatility_20'] = features['returns'].rolling(20).std()

        # Technical indicator features
        if 'rsi' in df.columns:
            features['rsi'] = df['rsi']
            features['rsi_slope'] = df['rsi'].diff(5)

        if 'macd' in df.columns:
            features['macd'] = df['macd']
            features['macd_hist'] = df.get('macd_hist', 0)

        if 'adx' in df.columns:
            features['adx'] = df['adx']

        if 'atr' in df.columns:
            features['atr_pct'] = df['atr_pct']

        # Moving average features
        for col in ['ema_9', 'ema_21', 'ema_50', 'sma_20']:
            if col in df.columns:
                features[f'{col}_distance'] = (df['close'] - df[col]) / df[col]

        # Volume features
        if 'volume_ratio' in df.columns:
            features['volume_ratio'] = df['volume_ratio']
        features['volume_momentum'] = df['volume'].pct_change(5)

        # Trend features
        if 'trend_strength' in df.columns:
            features['trend_strength'] = df['trend_strength']

        # Lag features
        for lag in [1, 2, 3, 5]:
            features[f'returns_lag_{lag}'] = features['returns'].shift(lag)

        # Rolling statistics
        features['rolling_mean_10'] = df['close'].rolling(10).mean()
        features['rolling_std_10'] = df['close'].rolling(10).std()
        features['rolling_max_10'] = df['high'].rolling(10).max()
        features['rolling_min_10'] = df['low'].rolling(10).min()

        # Target variable (future returns)
        horizon = app_config.AI_PREDICTION_HORIZON
        features['target'] = df['close'].shift(-horizon) / df['close'] - 1

        # Drop NaN
        features = features.dropna()

        return features

    def predict(self, df: pd.DataFrame, symbol: str) -> Optional[PredictionResult]:
        """Generate AI prediction for a stock"""
        features_df = self._prepare_features(df)

        if features_df is None or len(features_df) < 10:
            return None

        latest = features_df.iloc[-1]
        current_price = df['close'].iloc[-1]

        # Simple rule-based ensemble (can be replaced with actual ML models)
        signals = []

        # RSI signal
        if 'rsi' in latest:
            rsi = latest['rsi']
            if rsi < 30:
                signals.append(('UP', 0.7))
            elif rsi > 70:
                signals.append(('DOWN', 0.7))
            else:
                signals.append(('SIDEWAYS', 0.5))

        # MACD signal
        if 'macd' in latest and 'macd_hist' in latest:
            if latest['macd'] > 0 and latest['macd_hist'] > 0:
                signals.append(('UP', 0.6))
            elif latest['macd'] < 0 and latest['macd_hist'] < 0:
                signals.append(('DOWN', 0.6))

        # Trend signal
        if 'trend_strength' in latest:
            ts = latest['trend_strength']
            if ts > 70:
                signals.append(('UP', 0.8))
            elif ts < 30:
                signals.append(('DOWN', 0.8))

        # Momentum signal
        if 'price_momentum_5' in latest:
            mom = latest['price_momentum_5']
            if mom > 0.05:
                signals.append(('UP', 0.6))
            elif mom < -0.05:
                signals.append(('DOWN', 0.6))

        # Volume signal
        if 'volume_ratio' in latest:
            vr = latest['volume_ratio']
            if vr > 2 and 'returns' in latest and latest['returns'] > 0:
                signals.append(('UP', 0.7))
            elif vr > 2 and 'returns' in latest and latest['returns'] < 0:
                signals.append(('DOWN', 0.7))

        # Aggregate signals
        if not signals:
            direction = 'SIDEWAYS'
            confidence = 0.5
        else:
            up_score = sum(conf for d, conf in signals if d == 'UP')
            down_score = sum(conf for d, conf in signals if d == 'DOWN')
            sideways_score = sum(conf for d, conf in signals if d == 'SIDEWAYS')

            total = up_score + down_score + sideways_score
            if total == 0:
                direction = 'SIDEWAYS'
                confidence = 0.5
            else:
                scores = {
                    'UP': up_score / total,
                    'DOWN': down_score / total,
                    'SIDEWAYS': sideways_score / total
                }
                direction = max(scores, key=scores.get)
                confidence = scores[direction]

        # Calculate target and stop loss
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02

        if direction == 'UP':
            target_price = current_price + (atr * 3)
            stop_loss = current_price - (atr * 1.5)
        elif direction == 'DOWN':
            target_price = current_price - (atr * 3)
            stop_loss = current_price + (atr * 1.5)
        else:
            target_price = current_price * 1.02
            stop_loss = current_price * 0.98

        # Feature importance (simplified)
        feature_importance = {
            'rsi': 0.25,
            'macd': 0.20,
            'trend_strength': 0.20,
            'volume_ratio': 0.15,
            'price_momentum': 0.10,
            'volatility': 0.10
        }

        return PredictionResult(
            symbol=symbol,
            current_price=round(current_price, 2),
            predicted_direction=direction,
            confidence=round(confidence, 2),
            target_price=round(target_price, 2),
            stop_loss=round(stop_loss, 2),
            horizon_days=app_config.AI_PREDICTION_HORIZON,
            features_importance=feature_importance,
            model_used="Ensemble Rule-Based",
            timestamp=datetime.now().isoformat()
        )

    def predict_batch(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, PredictionResult]:
        """Predict for multiple stocks"""
        results = {}
        for symbol, df in data_dict.items():
            result = self.predict(df, symbol)
            if result:
                results[symbol] = result
        return results

    def get_market_sentiment(self, predictions: Dict[str, PredictionResult]) -> Dict:
        """Calculate overall market sentiment"""
        if not predictions:
            return {'sentiment': 'NEUTRAL', 'score': 50, 'bullish': 0, 'bearish': 0, 'neutral': 0}

        bullish = sum(1 for p in predictions.values() if p.predicted_direction == 'UP')
        bearish = sum(1 for p in predictions.values() if p.predicted_direction == 'DOWN')
        neutral = sum(1 for p in predictions.values() if p.predicted_direction == 'SIDEWAYS')
        total = len(predictions)

        score = ((bullish * 100) + (neutral * 50)) / total

        if score > 65:
            sentiment = 'BULLISH'
        elif score < 35:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'

        return {
            'sentiment': sentiment,
            'score': round(score, 1),
            'bullish': bullish,
            'bearish': bearish,
            'neutral': neutral,
            'total': total
        }


# Global instance
ai_engine = AIPredictionEngine()
