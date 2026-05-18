"""
EGX Pro Terminal - Backtesting Engine
Historical strategy testing with performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from config.settings import app_config
from data.storage import local_storage


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Trade:
    """Individual trade record"""
    entry_date: str
    exit_date: Optional[str]
    entry_price: float
    exit_price: Optional[float]
    shares: int
    signal: SignalType
    pnl: Optional[float]
    pnl_pct: Optional[float]
    holding_days: int
    exit_reason: str


@dataclass
class BacktestResult:
    """Complete backtest results"""
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_trade_return: float
    avg_holding_days: float
    trades: List[Trade]
    equity_curve: pd.DataFrame
    monthly_returns: pd.DataFrame
    params: Dict


class BacktestEngine:
    """Professional backtesting engine"""

    def __init__(self, initial_capital: float = None, commission: float = None):
        self.initial_capital = initial_capital or app_config.BACKTEST_INITIAL_CAPITAL
        self.commission = commission or app_config.BACKTEST_COMMISSION

    def run_strategy(self, df: pd.DataFrame, strategy_func: Callable, 
                     symbol: str, strategy_name: str = "Custom Strategy",
                     params: Dict = None) -> BacktestResult:
        """
        Run a backtest for a given strategy

        Args:
            df: OHLCV dataframe with indicators
            strategy_func: Function that takes df and returns signal series
            symbol: Stock symbol
            strategy_name: Name of the strategy
            params: Strategy parameters

        Returns:
            BacktestResult with full performance metrics
        """
        if df is None or len(df) < 50:
            return None

        # Generate signals
        signals = strategy_func(df, params or {})

        # Initialize
        capital = self.initial_capital
        position = 0  # number of shares
        trades = []
        equity_curve = []

        for i in range(1, len(df)):
            date = df.index[i]
            price = df['close'].iloc[i]
            signal = signals.iloc[i]
            prev_signal = signals.iloc[i-1]

            # Track equity
            equity = capital + (position * price)
            equity_curve.append({'date': date, 'equity': equity, 'price': price, 'signal': signal})

            # Execute trades on signal changes
            if signal == 1 and position == 0:  # Buy
                # Calculate shares
                cost = price * (1 + self.commission)
                shares = int(capital / cost)

                if shares > 0:
                    position = shares
                    capital -= shares * cost

                    trades.append(Trade(
                        entry_date=str(date),
                        exit_date=None,
                        entry_price=price,
                        exit_price=None,
                        shares=shares,
                        signal=SignalType.BUY,
                        pnl=None,
                        pnl_pct=None,
                        holding_days=0,
                        exit_reason="OPEN"
                    ))

            elif signal == -1 and position > 0:  # Sell
                # Close position
                revenue = position * price * (1 - self.commission)
                pnl = revenue - (position * trades[-1].entry_price)
                pnl_pct = (pnl / (position * trades[-1].entry_price)) * 100
                holding_days = (pd.to_datetime(date) - pd.to_datetime(trades[-1].entry_date)).days

                trades[-1].exit_date = str(date)
                trades[-1].exit_price = price
                trades[-1].pnl = pnl
                trades[-1].pnl_pct = pnl_pct
                trades[-1].holding_days = holding_days
                trades[-1].exit_reason = "SELL_SIGNAL"

                capital += revenue
                position = 0

        # Close any open position at last price
        if position > 0:
            last_price = df['close'].iloc[-1]
            revenue = position * last_price * (1 - self.commission)
            pnl = revenue - (position * trades[-1].entry_price)
            pnl_pct = (pnl / (position * trades[-1].entry_price)) * 100
            holding_days = (pd.to_datetime(df.index[-1]) - pd.to_datetime(trades[-1].entry_date)).days

            trades[-1].exit_date = str(df.index[-1])
            trades[-1].exit_price = last_price
            trades[-1].pnl = pnl
            trades[-1].pnl_pct = pnl_pct
            trades[-1].holding_days = holding_days
            trades[-1].exit_reason = "END_OF_DATA"

            capital += revenue

        # Calculate metrics
        equity_df = pd.DataFrame(equity_curve)
        if equity_df.empty:
            return None

        final_equity = equity_df['equity'].iloc[-1]
        total_return = final_equity - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        # Max drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = equity_df['equity'] - equity_df['peak']
        equity_df['drawdown_pct'] = (equity_df['drawdown'] / equity_df['peak']) * 100
        max_drawdown = equity_df['drawdown'].min()
        max_drawdown_pct = equity_df['drawdown_pct'].min()

        # Trade statistics
        completed_trades = [t for t in trades if t.exit_date is not None]
        winning_trades = [t for t in completed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in completed_trades if t.pnl and t.pnl <= 0]

        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0
        avg_trade_return = np.mean([t.pnl_pct for t in completed_trades if t.pnl_pct is not None]) if completed_trades else 0
        avg_holding_days = np.mean([t.holding_days for t in completed_trades]) if completed_trades else 0

        # Sharpe ratio (simplified)
        equity_df['returns'] = equity_df['equity'].pct_change()
        sharpe = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252) if equity_df['returns'].std() != 0 else 0

        # Monthly returns
        equity_df['date'] = pd.to_datetime(equity_df['date'])
        equity_df['month'] = equity_df['date'].dt.to_period('M')
        monthly = equity_df.groupby('month')['returns'].sum().reset_index()

        result = BacktestResult(
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=str(df.index[0]),
            end_date=str(df.index[-1]),
            initial_capital=self.initial_capital,
            final_capital=round(final_equity, 2),
            total_return=round(total_return, 2),
            total_return_pct=round(total_return_pct, 2),
            max_drawdown=round(max_drawdown, 2),
            max_drawdown_pct=round(max_drawdown_pct, 2),
            sharpe_ratio=round(sharpe, 2),
            win_rate=round(win_rate, 2),
            total_trades=len(completed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_trade_return=round(avg_trade_return, 2),
            avg_holding_days=round(avg_holding_days, 1),
            trades=completed_trades,
            equity_curve=equity_df,
            monthly_returns=monthly,
            params=params or {}
        )

        # Store result
        self._store_result(result)

        return result

    def _store_result(self, result: BacktestResult):
        """Store backtest result in database"""
        try:
            result_dict = {
                'strategy_name': result.strategy_name,
                'symbol': result.symbol,
                'start_date': result.start_date,
                'end_date': result.end_date,
                'initial_capital': result.initial_capital,
                'final_capital': result.final_capital,
                'total_return': result.total_return_pct,
                'max_drawdown': result.max_drawdown_pct,
                'sharpe_ratio': result.sharpe_ratio,
                'win_rate': result.win_rate,
                'total_trades': result.total_trades,
                'params': result.params
            }
            local_storage.store_backtest(result_dict)
        except Exception as e:
            print(f"Error storing backtest: {e}")

    def rsi_strategy(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """RSI-based strategy"""
        oversold = params.get('oversold', 30)
        overbought = params.get('overbought', 70)

        if 'rsi' not in df.columns:
            return pd.Series(0, index=df.index)

        signals = pd.Series(0, index=df.index)
        signals[df['rsi'] < oversold] = 1   # Buy
        signals[df['rsi'] > overbought] = -1  # Sell

        return signals

    def macd_strategy(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """MACD crossover strategy"""
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            return pd.Series(0, index=df.index)

        signals = pd.Series(0, index=df.index)
        signals[(df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))] = 1
        signals[(df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))] = -1

        return signals

    def ema_cross_strategy(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """EMA crossover strategy"""
        fast = params.get('fast', 9)
        slow = params.get('slow', 21)

        fast_col = f'ema_{fast}'
        slow_col = f'ema_{slow}'

        if fast_col not in df.columns or slow_col not in df.columns:
            return pd.Series(0, index=df.index)

        signals = pd.Series(0, index=df.index)
        signals[(df[fast_col] > df[slow_col]) & (df[fast_col].shift(1) <= df[slow_col].shift(1))] = 1
        signals[(df[fast_col] < df[slow_col]) & (df[fast_col].shift(1) >= df[slow_col].shift(1))] = -1

        return signals

    def bb_strategy(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Bollinger Bands mean reversion strategy"""
        if 'bb_lower' not in df.columns or 'bb_upper' not in df.columns:
            return pd.Series(0, index=df.index)

        signals = pd.Series(0, index=df.index)
        signals[df['close'] < df['bb_lower']] = 1   # Buy at lower band
        signals[df['close'] > df['bb_upper']] = -1  # Sell at upper band

        return signals

    def composite_strategy(self, df: pd.DataFrame, params: Dict) -> pd.Series:
        """Composite strategy using multiple indicators"""
        signals = pd.Series(0, index=df.index)
        score = pd.Series(0, index=df.index)

        # RSI contribution
        if 'rsi' in df.columns:
            score[df['rsi'] < 30] += 2
            score[df['rsi'] > 70] -= 2

        # MACD contribution
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            score[df['macd'] > df['macd_signal']] += 1
            score[df['macd'] < df['macd_signal']] -= 1

        # EMA contribution
        if 'ema_9' in df.columns and 'ema_21' in df.columns:
            score[df['ema_9'] > df['ema_21']] += 1
            score[df['ema_9'] < df['ema_21']] -= 1

        # Volume contribution
        if 'volume_ratio' in df.columns:
            score[df['volume_ratio'] > 2] += 1

        # Generate signals
        signals[score >= 3] = 1
        signals[score <= -3] = -1

        return signals

    def get_strategy_list(self) -> Dict[str, Callable]:
        """Get available strategies"""
        return {
            'RSI Strategy': self.rsi_strategy,
            'MACD Crossover': self.macd_strategy,
            'EMA Crossover': self.ema_cross_strategy,
            'Bollinger Bands': self.bb_strategy,
            'Composite Strategy': self.composite_strategy
        }


# Global instance
backtest_engine = BacktestEngine()
