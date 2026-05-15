# 🎓 أمثلة عملية لاستخدام ميزات EGX Pro Terminal v26
# =====================================================

"""
هذا الملف يحتوي على أمثلة عملية لكل ميزة جديدة
يمكنك نسخ هذه الأمثلة والتعديل عليها
"""

import numpy as np
from datetime import datetime

# ========== 1️⃣ أمثلة نظام التنبيهات ==========
print("=" * 60)
print("1️⃣ نظام التنبيهات الذكية")
print("=" * 60)

class AlertManager:
    def __init__(self):
        self.alerts = []
    
    def add_alert(self, symbol, alert_type, condition, value, action=""):
        alert = {
            'symbol': symbol,
            'type': alert_type,
            'condition': condition,
            'value': value,
            'action': action,
            'created_at': datetime.now(),
            'triggered': False
        }
        self.alerts.append(alert)
        return alert

# مثال 1: إضافة تنبيه سعر
alert_mgr = AlertManager()

# تنبيه عندما يرتفع السهم فوق سعر معين
alert1 = alert_mgr.add_alert(
    symbol="EBANK",
    alert_type="PRICE",
    condition=">",
    value=155.0,
    action="send_email"
)
print(f"✅ تم إضافة تنبيه: {alert1['symbol']} عندما يكون السعر > {alert1['value']}")

# تنبيه عندما ينخفض السهم تحت سعر معين
alert2 = alert_mgr.add_alert(
    symbol="EVCO",
    alert_type="PRICE",
    condition="<",
    value=190.0,
    action="send_telegram"
)
print(f"✅ تم إضافة تنبيه: {alert2['symbol']} عندما يكون السعر < {alert2['value']}")

# تنبيه على حجم
alert3 = alert_mgr.add_alert(
    symbol="ORWA",
    alert_type="VOLUME",
    condition=">",
    value=5000000,
    action="notify"
)
print(f"✅ تم إضافة تنبيه حجم: {alert3['symbol']} عندما يتجاوز 5 مليون")

print(f"\n📊 إجمالي التنبيهات النشطة: {len(alert_mgr.alerts)}")

# ========== 2️⃣ أمثلة إدارة المخاطر ==========
print("\n" + "=" * 60)
print("2️⃣ إدارة المخاطر المتقدمة")
print("=" * 60)

class RiskManager:
    @staticmethod
    def calculate_var(returns, confidence=0.95):
        """حساب Value at Risk"""
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return sorted_returns[index]
    
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.05):
        """حساب Sharpe Ratio"""
        if len(returns) < 2:
            return 0
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0
        return (mean_return - risk_free_rate) / std_return
    
    @staticmethod
    def calculate_max_drawdown(returns):
        """حساب Maximum Drawdown"""
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown)
    
    @staticmethod
    def calculate_sortino_ratio(returns, target_return=0.0):
        """حساب Sortino Ratio"""
        downside_returns = [r for r in returns if r < target_return]
        if not downside_returns:
            return 0
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0
        return (np.mean(returns) - target_return) / downside_std

# مثال 1: عائدات محاكاة
np.random.seed(42)
returns = np.random.normal(0.001, 0.02, 100).tolist()

# حساب المقاييس
risk_mgr = RiskManager()
var_95 = risk_mgr.calculate_var(returns, 0.95)
sharpe = risk_mgr.calculate_sharpe_ratio(returns)
sortino = risk_mgr.calculate_sortino_ratio(returns)
max_dd = risk_mgr.calculate_max_drawdown(returns)

print("\n📊 تقرير المخاطر:")
print(f"   Value at Risk (95%): {var_95:.2%}")
print(f"   Sharpe Ratio: {sharpe:.2f}")
print(f"   Sortino Ratio: {sortino:.2f}")
print(f"   Max Drawdown: {max_dd:.2%}")
print(f"   التذبذبية (Volatility): {np.std(returns):.2%}")

# مثال 2: تقييم مستوى المخاطر
volatility = np.std(returns)
risk_level = "منخفض" if volatility < 0.1 else "متوسط" if volatility < 0.2 else "عالي"
print(f"\n⚠️ مستوى المخاطر: {risk_level}")

# مثال 3: مقارنة استراتيجيات
print("\n📈 مقارنة استراتيجيتين:")

strategy_a_returns = np.random.normal(0.0015, 0.015, 100).tolist()
strategy_b_returns = np.random.normal(0.001, 0.025, 100).tolist()

sharpe_a = risk_mgr.calculate_sharpe_ratio(strategy_a_returns)
sharpe_b = risk_mgr.calculate_sharpe_ratio(strategy_b_returns)

print(f"   الاستراتيجية أ - Sharpe: {sharpe_a:.2f}")
print(f"   الاستراتيجية ب - Sharpe: {sharpe_b:.2f}")
print(f"   ✅ الأفضل: {'الاستراتيجية أ' if sharpe_a > sharpe_b else 'الاستراتيجية ب'}")

# ========== 3️⃣ أمثلة مسح الأسهم ==========
print("\n" + "=" * 60)
print("3️⃣ مسح الأسهم الذكي")
print("=" * 60)

class StockScreener:
    def __init__(self, stocks_data):
        self.stocks = stocks_data
    
    def filter_by_criteria(self, criteria):
        """تصفية الأسهم"""
        results = self.stocks.copy()
        
        if 'price_min' in criteria:
            results = [s for s in results if s.get('price', 0) >= criteria['price_min']]
        if 'price_max' in criteria:
            results = [s for s in results if s.get('price', 0) <= criteria['price_max']]
        if 'change_min' in criteria:
            results = [s for s in results if s.get('change_pct', 0) >= criteria['change_min']]
        if 'volume_min' in criteria:
            results = [s for s in results if s.get('volume', 0) >= criteria['volume_min']]
        
        return results
    
    def find_breakouts(self, threshold=0.05):
        """البحث عن الاختراقات"""
        breakouts = [s for s in self.stocks if abs(s.get('change_pct', 0)) > threshold * 100]
        return sorted(breakouts, key=lambda x: abs(x.get('change_pct', 0)), reverse=True)

# بيانات الأسهم
stocks = [
    {'symbol': 'EBANK', 'price': 150.5, 'change_pct': 2.5, 'volume': 5000000},
    {'symbol': 'EVCO', 'price': 200.0, 'change_pct': -1.2, 'volume': 3000000},
    {'symbol': 'ORWA', 'price': 75.25, 'change_pct': 3.8, 'volume': 2000000},
    {'symbol': 'CRNT', 'price': 120.0, 'change_pct': 0.5, 'volume': 1500000},
    {'symbol': 'MOIL', 'price': 180.75, 'change_pct': -2.1, 'volume': 4000000},
]

screener = StockScreener(stocks)

# مثال 1: البحث عن أسهم بأسعار معينة
print("\n🔍 البحث عن أسهم بسعر بين 100 و 200:")
results = screener.filter_by_criteria({
    'price_min': 100,
    'price_max': 200
})
for stock in results:
    print(f"   {stock['symbol']}: {stock['price']:.2f} ج.م")

# مثال 2: البحث عن أسهم بتغير موجب
print("\n📈 البحث عن أسهم برتفاع أكثر من 1%:")
results = screener.filter_by_criteria({
    'change_min': 1.0
})
for stock in results:
    print(f"   {stock['symbol']}: +{stock['change_pct']:.2f}%")

# مثال 3: البحث عن الاختراقات
print("\n🚀 الاختراقات (تغير > 2%):")
breakouts = screener.find_breakouts(threshold=0.02)
for stock in breakouts:
    emoji = "📈" if stock['change_pct'] > 0 else "📉"
    print(f"   {emoji} {stock['symbol']}: {stock['change_pct']:+.2f}%")

# ========== 4️⃣ أمثلة الاستراتيجيات ==========
print("\n" + "=" * 60)
print("4️⃣ قوالب الاستراتيجيات")
print("=" * 60)

class StrategyManager:
    TEMPLATES = {
        'الدعم والمقاومة': {
            'entry': 'ارتداد من الدعم',
            'exit': 'كسر المستوى',
            'risk_reward': '1:2'
        },
        'الزخم': {
            'entry': 'كسر مستوى عالي',
            'exit': 'انعكاس الاتجاه',
            'risk_reward': '1:3'
        },
        'المتوسط المتحرك': {
            'entry': 'تقاطع من الأسفل',
            'exit': 'تقاطع من الأعلى',
            'risk_reward': '1:2.5'
        }
    }
    
    def __init__(self):
        self.custom_strategies = {}
    
    def get_templates(self):
        return self.TEMPLATES
    
    def save_custom_strategy(self, name, config):
        self.custom_strategies[name] = config
    
    def get_strategy_details(self, strategy_name):
        return self.TEMPLATES.get(strategy_name)

strategy_mgr = StrategyManager()

# مثال 1: عرض الاستراتيجيات المتاحة
print("\n📚 الاستراتيجيات المتاحة:")
for name, config in strategy_mgr.get_templates().items():
    print(f"\n   ✅ {name}")
    print(f"      الدخول: {config['entry']}")
    print(f"      الخروج: {config['exit']}")
    print(f"      المخاطرة/العائد: {config['risk_reward']}")

# مثال 2: حفظ استراتيجية مخصصة
print("\n\n💾 إضافة استراتيجية مخصصة:")
strategy_mgr.save_custom_strategy('استراتيجيتي', {
    'entry': 'عندما يقترب من الدعم بنسبة 1%',
    'exit': 'عندما يصل للهدف أو يكسر الدعم',
    'risk_reward': '1:2.5'
})
print("   ✅ تم حفظ الاستراتيجية 'استراتيجيتي'")

# ========== 5️⃣ أمثلة التقارير ==========
print("\n" + "=" * 60)
print("5️⃣ مولد التقارير")
print("=" * 60)

class ReportGenerator:
    @staticmethod
    def generate_summary(symbol, price, change_pct, volume):
        """توليد ملخص سريع"""
        return {
            'symbol': symbol,
            'price': price,
            'change': change_pct,
            'volume': volume,
            'timestamp': datetime.now(),
            'trend': 'صعودي' if change_pct > 0 else 'هبوطي'
        }

report_gen = ReportGenerator()

# مثال 1: توليد تقرير سهم
print("\n📄 تقرير السهم:")
report = report_gen.generate_summary('EBANK', 150.5, 2.5, 5000000)
print(f"   السهم: {report['symbol']}")
print(f"   السعر: {report['price']:.2f} ج.م")
print(f"   التغير: {report['change']:+.2f}%")
print(f"   الحجم: {report['volume']:,}")
print(f"   الاتجاه: {report['trend']}")

# ========== 6️⃣ مثال متكامل ==========
print("\n" + "=" * 60)
print("6️⃣ مثال متكامل: تحليل سهم كامل")
print("=" * 60)

def complete_stock_analysis(symbol, price, change_pct, volume, returns):
    """تحليل شامل لسهم واحد"""
    print(f"\n📊 التحليل الشامل للسهم: {symbol}")
    print("─" * 50)
    
    # 1. معلومات السهم
    print(f"\n1️⃣ معلومات السهم:")
    print(f"   السعر الحالي: {price:.2f} ج.م")
    print(f"   التغير اليومي: {change_pct:+.2f}%")
    print(f"   الحجم: {volume:,}")
    
    # 2. مقاييس المخاطر
    risk_mgr = RiskManager()
    var = risk_mgr.calculate_var(returns)
    sharpe = risk_mgr.calculate_sharpe_ratio(returns)
    max_dd = risk_mgr.calculate_max_drawdown(returns)
    
    print(f"\n2️⃣ مقاييس المخاطر:")
    print(f"   VaR (95%): {var:.2%}")
    print(f"   Sharpe Ratio: {sharpe:.2f}")
    print(f"   Max Drawdown: {max_dd:.2%}")
    
    # 3. التقييم
    risk_score = 0
    if abs(var) > 0.1:
        risk_score += 3
    if max_dd < -0.15:
        risk_score += 2
    if sharpe < 0.5:
        risk_score += 2
    
    risk_levels = {0: '🟢 منخفج جداً', 1: '🟢 منخفض', 2: '🟡 متوسط', 3: '🟡 متوسط مرتفع', 4: '🟠 عالي', 5: '🔴 عالي جداً'}
    
    print(f"\n3️⃣ التقييم الإجمالي:")
    print(f"   مستوى المخاطر: {risk_levels.get(risk_score, '🔴 عالي جداً')}")
    
    # 4. التوصية
    print(f"\n4️⃣ التوصية:")
    if sharpe > 0.8:
        print("   ✅ استراتيجية قوية - يفضل المتابعة")
    elif sharpe > 0.5:
        print("   ⚠️ استراتيجية متوسطة - يحتاج مراقبة")
    else:
        print("   ❌ استراتيجية ضعيفة - لا يفضل التداول")

# تنفيذ التحليل الشامل
returns = np.random.normal(0.001, 0.02, 100).tolist()
complete_stock_analysis('EBANK', 150.5, 2.5, 5000000, returns)

print("\n" + "=" * 60)
print("✅ اكتملت جميع الأمثلة")
print("=" * 60)
