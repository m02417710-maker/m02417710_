"""
EGX Pro Terminal - Local Data Storage Engine
SQLite-based persistent storage with backup and optimization
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import os
import json
import shutil
from pathlib import Path

from config.settings import app_config


class LocalStorage:
    """Advanced SQLite storage for EGX market data"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or app_config.DB_PATH
        self._ensure_dir()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self._init_indexes()

    def _ensure_dir(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_tables(self):
        """Initialize database tables"""
        tables = [
            """CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adj_close REAL,
                source TEXT DEFAULT 'unknown',
                fetched_at TEXT,
                UNIQUE(symbol, date)
            )""",
            """CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                condition TEXT,
                triggered_at TEXT,
                price REAL,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                severity TEXT DEFAULT 'info'
            )""",
            """CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                added_at TEXT,
                notes TEXT,
                target_price REAL,
                stop_loss REAL
            )""",
            """CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                rsi REAL,
                macd REAL,
                macd_signal REAL,
                macd_hist REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                ema_9 REAL,
                ema_21 REAL,
                ema_50 REAL,
                ema_200 REAL,
                sma_20 REAL,
                sma_50 REAL,
                sma_200 REAL,
                atr REAL,
                adx REAL,
                stochastic_k REAL,
                stochastic_d REAL,
                volume_ma REAL,
                trend TEXT,
                strength REAL,
                computed_at TEXT,
                UNIQUE(symbol, date)
            )""",
            """CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT,
                symbol TEXT,
                start_date TEXT,
                end_date TEXT,
                initial_capital REAL,
                final_capital REAL,
                total_return REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                win_rate REAL,
                total_trades INTEGER,
                params TEXT,
                created_at TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                module TEXT,
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        ]

        for table_sql in tables:
            self.conn.execute(table_sql)
        self.conn.commit()

    def _init_indexes(self):
        """Create performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date)",
            "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_symbol_date ON analysis_cache(symbol, date)"
        ]
        for idx in indexes:
            try:
                self.conn.execute(idx)
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def store_stock_data(self, df: pd.DataFrame) -> bool:
        """Store OHLCV data"""
        if df is None or df.empty:
            return False

        try:
            records = []
            for _, row in df.iterrows():
                records.append({
                    'symbol': row.get('symbol', 'UNKNOWN'),
                    'date': str(row.get('date', row.get('Date', datetime.now()))),
                    'open': float(row.get('open', row.get('Open', 0))),
                    'high': float(row.get('high', row.get('High', 0))),
                    'low': float(row.get('low', row.get('Low', 0))),
                    'close': float(row.get('close', row.get('Close', 0))),
                    'volume': int(row.get('volume', row.get('Volume', 0))),
                    'adj_close': float(row.get('adj_close', row.get('Close', 0))),
                    'source': row.get('source', 'unknown'),
                    'fetched_at': str(row.get('fetched_at', datetime.now()))
                })

            cursor = self.conn.cursor()
            for record in records:
                cursor.execute("""
                    INSERT OR REPLACE INTO stock_data 
                    (symbol, date, open, high, low, close, volume, adj_close, source, fetched_at)
                    VALUES (:symbol, :date, :open, :high, :low, :close, :volume, :adj_close, :source, :fetched_at)
                """, record)

            self.conn.commit()
            return True

        except Exception as e:
            self.log_error('storage', f"Error storing stock data: {e}")
            return False

    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Retrieve stock data from local storage"""
        try:
            days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            days = days_map.get(period, 365)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            query = """
                SELECT * FROM stock_data 
                WHERE symbol = ? AND date >= ? 
                ORDER BY date ASC
            """
            df = pd.read_sql_query(query, self.conn, params=(symbol, start_date))

            if df.empty:
                return None

            df['date'] = pd.to_datetime(df['date'])
            return df

        except Exception as e:
            self.log_error('storage', f"Error retrieving stock data: {e}")
            return None

    def store_analysis(self, symbol: str, date: str, indicators: Dict) -> bool:
        """Store computed technical indicators"""
        try:
            indicators['symbol'] = symbol
            indicators['date'] = date
            indicators['computed_at'] = datetime.now().isoformat()

            columns = ', '.join(indicators.keys())
            placeholders = ', '.join(['?' for _ in indicators])
            values = list(indicators.values())

            query = f"""
                INSERT OR REPLACE INTO analysis_cache ({columns})
                VALUES ({placeholders})
            """
            self.conn.execute(query, values)
            self.conn.commit()
            return True

        except Exception as e:
            self.log_error('storage', f"Error storing analysis: {e}")
            return False

    def get_analysis(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Retrieve cached analysis"""
        try:
            days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            days = days_map.get(period, 365)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            query = """
                SELECT * FROM analysis_cache 
                WHERE symbol = ? AND date >= ? 
                ORDER BY date ASC
            """
            df = pd.read_sql_query(query, self.conn, params=(symbol, start_date))

            if df.empty:
                return None

            df['date'] = pd.to_datetime(df['date'])
            return df

        except Exception as e:
            self.log_error('storage', f"Error retrieving analysis: {e}")
            return None

    def add_alert(self, symbol: str, alert_type: str, condition: str, 
                  price: float, message: str, severity: str = 'info') -> bool:
        """Add new alert"""
        try:
            self.conn.execute("""
                INSERT INTO alerts (symbol, alert_type, condition, triggered_at, price, message, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (symbol, alert_type, condition, datetime.now().isoformat(), price, message, severity))
            self.conn.commit()
            return True
        except Exception as e:
            self.log_error('storage', f"Error adding alert: {e}")
            return False

    def get_alerts(self, symbol: Optional[str] = None, 
                   unread_only: bool = False, limit: int = 100) -> pd.DataFrame:
        """Retrieve alerts"""
        try:
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []

            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)

            if unread_only:
                query += " AND is_read = 0"

            query += " ORDER BY triggered_at DESC LIMIT ?"
            params.append(limit)

            df = pd.read_sql_query(query, self.conn, params=params)
            return df

        except Exception as e:
            self.log_error('storage', f"Error retrieving alerts: {e}")
            return pd.DataFrame()

    def add_to_watchlist(self, symbol: str, notes: str = "", 
                         target_price: float = None, stop_loss: float = None) -> bool:
        """Add stock to watchlist"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO watchlist (symbol, added_at, notes, target_price, stop_loss)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol, datetime.now().isoformat(), notes, target_price, stop_loss))
            self.conn.commit()
            return True
        except Exception as e:
            self.log_error('storage', f"Error adding to watchlist: {e}")
            return False

    def get_watchlist(self) -> pd.DataFrame:
        """Get watchlist"""
        try:
            df = pd.read_sql_query("SELECT * FROM watchlist ORDER BY added_at DESC", self.conn)
            return df
        except Exception as e:
            self.log_error('storage', f"Error retrieving watchlist: {e}")
            return pd.DataFrame()

    def store_backtest(self, result: Dict) -> bool:
        """Store backtest result"""
        try:
            result['created_at'] = datetime.now().isoformat()
            result['params'] = json.dumps(result.get('params', {}))

            columns = ', '.join(result.keys())
            placeholders = ', '.join(['?' for _ in result])
            values = list(result.values())

            query = f"""
                INSERT INTO backtest_results ({columns})
                VALUES ({placeholders})
            """
            self.conn.execute(query, values)
            self.conn.commit()
            return True

        except Exception as e:
            self.log_error('storage', f"Error storing backtest: {e}")
            return False

    def get_backtests(self, limit: int = 50) -> pd.DataFrame:
        """Get backtest history"""
        try:
            df = pd.read_sql_query(
                "SELECT * FROM backtest_results ORDER BY created_at DESC LIMIT ?",
                self.conn, params=(limit,)
            )
            return df
        except Exception as e:
            self.log_error('storage', f"Error retrieving backtests: {e}")
            return pd.DataFrame()

    def log_error(self, module: str, message: str, level: str = 'ERROR'):
        """Log system error"""
        try:
            self.conn.execute("""
                INSERT INTO system_logs (level, module, message, created_at)
                VALUES (?, ?, ?, ?)
            """, (level, module, message, datetime.now().isoformat()))
            self.conn.commit()
        except:
            pass

    def backup(self, backup_path: str = None) -> str:
        """Create database backup"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.db_path}.backup_{timestamp}"

        try:
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            self.log_error('storage', f"Backup failed: {e}")
            return None

    def vacuum(self):
        """Optimize database"""
        try:
            self.conn.execute('VACUUM')
            self.conn.commit()
        except Exception as e:
            self.log_error('storage', f"Vacuum failed: {e}")

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}
            tables = ['stock_data', 'alerts', 'watchlist', 'analysis_cache', 'backtest_results']
            for table in tables:
                cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]

            cursor = self.conn.execute("SELECT SUM(pgsize) FROM dbstat()")
            stats['size_bytes'] = cursor.fetchone()[0] or 0

            return stats
        except Exception as e:
            self.log_error('storage', f"Error getting stats: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global instance
local_storage = LocalStorage()
