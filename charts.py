"""
EGX Pro Terminal - Interactive Charting Engine
Professional financial charts with Plotly
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from config.settings import app_config


class ChartEngine:
    """Professional financial charting engine"""

    def __init__(self):
        self.primary_color = app_config.THEME_PRIMARY_COLOR
        self.secondary_color = app_config.THEME_SECONDARY_COLOR
        self.height = app_config.CHART_HEIGHT

    def create_main_chart(self, df: pd.DataFrame, symbol: str, 
                          show_indicators: List[str] = None) -> go.Figure:
        """Create main candlestick chart with indicators"""
        if df is None or df.empty:
            return go.Figure()

        show_indicators = show_indicators or ['ema_9', 'ema_21', 'ema_50']

        # Create subplots: main chart + volume + MACD
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f'{symbol} - Price Chart', 'Volume', 'MACD')
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ), row=1, col=1)

        # Moving Averages
        colors = {'ema_9': '#2196F3', 'ema_21': '#FF9800', 'ema_50': '#9C27B0', 
                  'ema_200': '#E91E63', 'sma_20': '#00BCD4'}

        for indicator in show_indicators:
            if indicator in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df[indicator],
                    mode='lines',
                    name=indicator.upper(),
                    line=dict(color=colors.get(indicator, '#666'), width=1.5),
                    opacity=0.8
                ), row=1, col=1)

        # Bollinger Bands
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['bb_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='rgba(128,128,128,0.3)', width=1),
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['bb_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='rgba(128,128,128,0.3)', width=1),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ), row=1, col=1)

        # Volume
        colors_volume = ['#26a69a' if df['close'].iloc[i] >= df['open'].iloc[i] 
                        else '#ef5350' for i in range(len(df))]

        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['volume'],
            name='Volume',
            marker_color=colors_volume,
            opacity=0.7
        ), row=2, col=1)

        # Volume MA
        if 'volume_ma' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['volume_ma'],
                mode='lines',
                name='Volume MA',
                line=dict(color='#FF9800', width=1.5)
            ), row=2, col=1)

        # MACD
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            colors_macd = ['#26a69a' if df['macd'].iloc[i] >= df['macd_signal'].iloc[i] 
                          else '#ef5350' for i in range(len(df))]

            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['macd_hist'],
                name='MACD Hist',
                marker_color=colors_macd,
                opacity=0.6
            ), row=3, col=1)

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#2196F3', width=1.5)
            ), row=3, col=1)

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['macd_signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#FF9800', width=1.5)
            ), row=3, col=1)

        # Layout
        fig.update_layout(
            title=f'📈 {symbol} Technical Analysis',
            height=self.height,
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=50, r=50, t=80, b=50)
        )

        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(128,128,128,0.2)')

        return fig

    def create_rsi_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create RSI chart"""
        if df is None or 'rsi' not in df.columns:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='#2196F3', width=2),
            fill='tozeroy',
            fillcolor='rgba(33,150,243,0.1)'
        ))

        # Overbought/oversold lines
        fig.add_hline(y=70, line_dash='dash', line_color='#ef5350', 
                      annotation_text='Overbought (70)', annotation_position='right')
        fig.add_hline(y=30, line_dash='dash', line_color='#26a69a',
                      annotation_text='Oversold (30)', annotation_position='right')
        fig.add_hline(y=50, line_dash='dot', line_color='gray',
                      annotation_text='Neutral (50)', annotation_position='right')

        fig.update_layout(
            title='RSI (Relative Strength Index)',
            height=350,
            template='plotly_dark',
            yaxis=dict(range=[0, 100]),
            showlegend=False
        )

        return fig

    def create_adx_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create ADX chart"""
        if df is None or 'adx' not in df.columns:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['adx'],
            mode='lines',
            name='ADX',
            line=dict(color='#9C27B0', width=2)
        ))

        if 'plus_di' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['plus_di'],
                mode='lines',
                name='+DI',
                line=dict(color='#26a69a', width=1.5)
            ))

        if 'minus_di' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['minus_di'],
                mode='lines',
                name='-DI',
                line=dict(color='#ef5350', width=1.5)
            ))

        fig.add_hline(y=25, line_dash='dash', line_color='gray',
                      annotation_text='Strong Trend (25)', annotation_position='right')

        fig.update_layout(
            title='ADX - Average Directional Index',
            height=350,
            template='plotly_dark',
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )

        return fig

    def create_stochastic_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create Stochastic Oscillator chart"""
        if df is None or 'stochastic_k' not in df.columns:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['stochastic_k'],
            mode='lines',
            name='%K',
            line=dict(color='#2196F3', width=2)
        ))

        if 'stochastic_d' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['stochastic_d'],
                mode='lines',
                name='%D',
                line=dict(color='#FF9800', width=1.5)
            ))

        fig.add_hline(y=80, line_dash='dash', line_color='#ef5350')
        fig.add_hline(y=20, line_dash='dash', line_color='#26a69a')

        fig.update_layout(
            title='Stochastic Oscillator',
            height=350,
            template='plotly_dark',
            yaxis=dict(range=[0, 100]),
            showlegend=True
        )

        return fig

    def create_equity_curve(self, equity_df: pd.DataFrame, title: str = "Equity Curve") -> go.Figure:
        """Create equity curve chart for backtesting"""
        if equity_df is None or equity_df.empty:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=equity_df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#26a69a', width=2),
            fill='tozeroy',
            fillcolor='rgba(38,166,154,0.1)'
        ))

        # Add initial capital line
        initial = equity_df['equity'].iloc[0]
        fig.add_hline(y=initial, line_dash='dash', line_color='gray',
                      annotation_text=f'Initial: {initial:,.0f}', annotation_position='right')

        fig.update_layout(
            title=title,
            height=400,
            template='plotly_dark',
            showlegend=False
        )

        return fig

    def create_drawdown_chart(self, equity_df: pd.DataFrame) -> go.Figure:
        """Create drawdown chart"""
        if equity_df is None or equity_df.empty:
            return go.Figure()

        equity_df = equity_df.copy()
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=equity_df['drawdown'],
            mode='lines',
            name='Drawdown %',
            line=dict(color='#ef5350', width=2),
            fill='tozeroy',
            fillcolor='rgba(239,83,80,0.2)'
        ))

        fig.add_hline(y=0, line_dash='solid', line_color='gray')

        fig.update_layout(
            title='Drawdown Analysis',
            height=300,
            template='plotly_dark',
            yaxis=dict(title='Drawdown %'),
            showlegend=False
        )

        return fig

    def create_monthly_returns_heatmap(self, monthly_df: pd.DataFrame) -> go.Figure:
        """Create monthly returns heatmap"""
        if monthly_df is None or monthly_df.empty:
            return go.Figure()

        fig = go.Figure(data=go.Bar(
            x=monthly_df['month'].astype(str),
            y=monthly_df['returns'] * 100,
            marker_color=['#26a69a' if r >= 0 else '#ef5350' for r in monthly_df['returns']],
            opacity=0.8
        ))

        fig.update_layout(
            title='Monthly Returns',
            height=300,
            template='plotly_dark',
            yaxis=dict(title='Return %'),
            showlegend=False
        )

        return fig

    def create_market_overview(self, quotes_df: pd.DataFrame) -> go.Figure:
        """Create market overview treemap"""
        if quotes_df is None or quotes_df.empty:
            return go.Figure()

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Symbol', 'Price', 'Change', 'Change %', 'Volume'],
                fill_color='#1a1a2e',
                align='center',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[
                    quotes_df['symbol'],
                    quotes_df['price'].round(2),
                    quotes_df['change'].round(2),
                    quotes_df['change_pct'].round(2),
                    quotes_df['volume'].apply(lambda x: f"{x:,.0f}")
                ],
                fill_color=[['#16213e' if i % 2 == 0 else '#0f3460' for i in range(len(quotes_df))]],
                align='center',
                font=dict(color='white', size=11),
                height=30
            )
        )])

        fig.update_layout(
            title='Market Overview',
            height=600,
            template='plotly_dark'
        )

        return fig

    def create_comparison_chart(self, data_dict: Dict[str, pd.DataFrame], 
                                normalize: bool = True) -> go.Figure:
        """Create multi-stock comparison chart"""
        if not data_dict:
            return go.Figure()

        fig = go.Figure()

        colors = px.colors.qualitative.Set1

        for idx, (symbol, df) in enumerate(data_dict.items()):
            if df is None or df.empty:
                continue

            prices = df['close']
            if normalize:
                prices = (prices / prices.iloc[0] - 1) * 100

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=prices,
                mode='lines',
                name=symbol,
                line=dict(color=colors[idx % len(colors)], width=2)
            ))

        title = 'Normalized Performance Comparison (%)' if normalize else 'Price Comparison'

        fig.update_layout(
            title=title,
            height=self.height,
            template='plotly_dark',
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )

        return fig


# Global instance
chart_engine = ChartEngine()
