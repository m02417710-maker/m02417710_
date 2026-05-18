"""
EGX Pro Terminal - Analysis Unit Tests
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from core.analysis import analysis_engine


class TestTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        """Create sample data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        np.random.seed(42)

        base_price = 50
        returns = np.random.normal(0.001, 0.02, 100)
        prices = base_price * np.exp(np.cumsum(returns))

        self.sample_df = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.normal(0, 0.005, 100)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.01, 100))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.01, 100))),
            'close': prices,
            'volume': np.random.randint(100000, 5000000, 100)
        })

    def test_compute_all(self):
        """Test that all indicators are computed"""
        result = analysis_engine.compute_all(self.sample_df)

        # Check that key indicators exist
        self.assertIn('rsi', result.columns)
        self.assertIn('macd', result.columns)
        self.assertIn('macd_signal', result.columns)
        self.assertIn('bb_upper', result.columns)
        self.assertIn('bb_lower', result.columns)
        self.assertIn('ema_9', result.columns)
        self.assertIn('ema_21', result.columns)
        self.assertIn('ema_50', result.columns)
        self.assertIn('ema_200', result.columns)
        self.assertIn('atr', result.columns)
        self.assertIn('adx', result.columns)
        self.assertIn('trend', result.columns)
        self.assertIn('final_signal', result.columns)

    def test_rsi_range(self):
        """Test RSI is within 0-100 range"""
        result = analysis_engine.compute_all(self.sample_df)
        rsi_values = result['rsi'].dropna()

        self.assertTrue(all(rsi_values >= 0))
        self.assertTrue(all(rsi_values <= 100))

    def test_bollinger_bands(self):
        """Test Bollinger Bands relationship"""
        result = analysis_engine.compute_all(self.sample_df)

        for idx, row in result.iterrows():
            if pd.notna(row['bb_upper']) and pd.notna(row['bb_lower']):
                self.assertGreaterEqual(row['bb_upper'], row['bb_middle'])
                self.assertLessEqual(row['bb_lower'], row['bb_middle'])

    def test_signals(self):
        """Test signal generation"""
        result = analysis_engine.compute_all(self.sample_df)
        signals = result['final_signal'].unique()

        expected_signals = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']
        for signal in signals:
            self.assertIn(signal, expected_signals)

    def test_support_resistance(self):
        """Test support/resistance calculation"""
        result = analysis_engine.compute_all(self.sample_df)
        sr = analysis_engine.get_support_resistance(result)

        self.assertIn('supports', sr)
        self.assertIn('resistances', sr)
        self.assertIn('nearest_support', sr)
        self.assertIn('nearest_resistance', sr)

        current_price = result['close'].iloc[-1]
        self.assertLessEqual(sr['nearest_support'], current_price)
        self.assertGreaterEqual(sr['nearest_resistance'], current_price)

    def test_fibonacci_levels(self):
        """Test Fibonacci levels"""
        result = analysis_engine.compute_all(self.sample_df)
        fib = analysis_engine.get_fibonacci_levels(result)

        self.assertIn('0.0%', fib)
        self.assertIn('100.0%', fib)
        self.assertIn('61.8%', fib)
        self.assertIn('current', fib)

        self.assertGreaterEqual(fib['0.0%'], fib['100.0%'])

    def test_summary(self):
        """Test analysis summary"""
        result = analysis_engine.compute_all(self.sample_df)
        summary = analysis_engine.get_summary(result)

        self.assertIn('price', summary)
        self.assertIn('rsi', summary)
        self.assertIn('trend', summary)
        self.assertIn('final_signal', summary)
        self.assertIn('support_resistance', summary)


class TestEdgeCases(unittest.TestCase):

    def test_empty_dataframe(self):
        """Test with empty dataframe"""
        empty_df = pd.DataFrame()
        result = analysis_engine.compute_all(empty_df)
        self.assertTrue(result.empty)

    def test_insufficient_data(self):
        """Test with insufficient data"""
        small_df = pd.DataFrame({
            'date': [datetime.now()],
            'open': [10], 'high': [11], 'low': [9], 'close': [10], 'volume': [1000]
        })
        result = analysis_engine.compute_all(small_df)
        self.assertEqual(len(result), 1)

    def test_nan_handling(self):
        """Test handling of NaN values"""
        df = pd.DataFrame({
            'date': pd.date_range(end=datetime.now(), periods=50),
            'open': [10] * 50,
            'high': [11] * 50,
            'low': [9] * 50,
            'close': [10] * 50,
            'volume': [1000] * 50
        })
        result = analysis_engine.compute_all(df)
        # Should not raise exception
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
