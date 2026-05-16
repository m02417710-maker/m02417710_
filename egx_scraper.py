
"""
EGX Companies Scraper & Database Updater
=========================================
نظام جلب وتحديث قائمة الشركات المقيدة في البورصة المصرية
متوافق مع: السوق الرئيسي | سوق النيل | الشركات خارج المقصورة

المؤلف: FinTech Developer
التاريخ: 2026-05-16
"""

import requests
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import time

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('egx_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MarketSegment(Enum):
    """تصنيفات السوق"""
    MAIN = "السوق الرئيسي"
    NILE = "سوق النيل (SME)"
    OFF_BOARD = "خارج المقصورة"
    TEMPORARY = "قيد مؤقت (طروحات)"


@dataclass
class EGXCompany:
    """نموذج شركة مقيدة في EGX"""
    symbol: str                    # الرمز: COMI.CA
    name_ar: str                   # الاسم العربي
    name_en: str                   # الاسم الإنجليزي
    market_segment: MarketSegment  # قطاع السوق
    sector: str                    # القطاع الاقتصادي
    is_active: bool                # نشط/موقوف
    listing_date: Optional[str]    # تاريخ القيد
    is_government: bool           # شركة حكومية؟
    temporary_listing: bool       # قيد مؤقت؟
    last_updated: str             # آخر تحديث

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['market_segment'] = self.market_segment.value
        return data


class EGXDatabase:
    """قاعدة بيانات SQLite للشركات المقيدة"""

    def __init__(self, db_path: str = "egx_companies.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """إنشاء الجداول"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    symbol TEXT PRIMARY KEY,
                    name_ar TEXT NOT NULL,
                    name_en TEXT,
                    market_segment TEXT NOT NULL,
                    sector TEXT,
                    is_active INTEGER DEFAULT 1,
                    listing_date TEXT,
                    is_government INTEGER DEFAULT 0,
                    temporary_listing INTEGER DEFAULT 0,
                    last_updated TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS listing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    event_type TEXT,  -- NEW_LISTING, DELISTING, SUSPENSION, REACTIVATION
                    event_date TEXT,
                    details TEXT,
                    FOREIGN KEY (symbol) REFERENCES companies(symbol)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_date TEXT,
                    total_companies INTEGER,
                    main_market_count INTEGER,
                    nile_count INTEGER,
                    off_board_count INTEGER,
                    temporary_count INTEGER,
                    government_count INTEGER
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_segment ON companies(market_segment);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sector ON companies(sector);
            """)
            conn.commit()

    def upsert_company(self, company: EGXCompany) -> Tuple[bool, str]:
        """
        إدراج أو تحديث شركة
        Returns: (is_new, message)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT symbol, market_segment, is_active FROM companies WHERE symbol = ?",
                (company.symbol,)
            )
            existing = cursor.fetchone()

            if existing:
                # تحديث
                conn.execute("""
                    UPDATE companies SET
                        name_ar = ?, name_en = ?, market_segment = ?,
                        sector = ?, is_active = ?, listing_date = ?,
                        is_government = ?, temporary_listing = ?, last_updated = ?
                    WHERE symbol = ?
                """, (
                    company.name_ar, company.name_en, company.market_segment.value,
                    company.sector, int(company.is_active), company.listing_date,
                    int(company.is_government), int(company.temporary_listing),
                    company.last_updated, company.symbol
                ))

                # تسجيل تغيير القطاع إذا حدث
                if existing[1] != company.market_segment.value:
                    conn.execute("""
                        INSERT INTO listing_history (symbol, event_type, event_date, details)
                        VALUES (?, 'SEGMENT_CHANGE', ?, ?)
                    """, (company.symbol, company.last_updated, 
                          f"من {existing[1]} إلى {company.market_segment.value}"))

                return False, f"تم تحديث: {company.symbol}"
            else:
                # شركة جديدة
                conn.execute("""
                    INSERT INTO companies 
                    (symbol, name_ar, name_en, market_segment, sector, is_active,
                     listing_date, is_government, temporary_listing, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company.symbol, company.name_ar, company.name_en,
                    company.market_segment.value, company.sector, int(company.is_active),
                    company.listing_date, int(company.is_government),
                    int(company.temporary_listing), company.last_updated
                ))

                conn.execute("""
                    INSERT INTO listing_history (symbol, event_type, event_date, details)
                    VALUES (?, 'NEW_LISTING', ?, ?)
                """, (company.symbol, company.last_updated, 
                      f"قيد جديد في {company.market_segment.value}"))

                return True, f"شركة جديدة: {company.symbol} - {company.name_ar}"

    def get_statistics(self) -> Dict:
        """إحصائيات السوق"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            stats = {}

            # العدد الإجمالي
            cursor = conn.execute("SELECT COUNT(*) FROM companies WHERE is_active = 1")
            stats['total_active'] = cursor.fetchone()[0]

            # التوزيع حسب السوق
            cursor = conn.execute("""
                SELECT market_segment, COUNT(*) as count 
                FROM companies WHERE is_active = 1 
                GROUP BY market_segment
            """)
            for row in cursor.fetchall():
                stats[row['market_segment']] = row['count']

            # الشركات الحكومية
            cursor = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE is_government = 1 AND is_active = 1"
            )
            stats['government_companies'] = cursor.fetchone()[0]

            # القيد المؤقت
            cursor = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE temporary_listing = 1 AND is_active = 1"
            )
            stats['temporary_listings'] = cursor.fetchone()[0]

            # الشركات الجديدة هذا الشهر
            cursor = conn.execute("""
                SELECT COUNT(*) FROM listing_history 
                WHERE event_type = 'NEW_LISTING' 
                AND event_date >= date('now', 'start of month')
            """)
            stats['new_this_month'] = cursor.fetchone()[0]

            return stats

    def get_companies_by_segment(self, segment: MarketSegment) -> List[Dict]:
        """جلب الشركات حسب قطاع السوق"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM companies 
                WHERE market_segment = ? AND is_active = 1
                ORDER BY symbol
            """, (segment.value,))
            return [dict(row) for row in cursor.fetchall()]

    def save_daily_snapshot(self):
        """حفظ لقطة يومية للإحصائيات"""
        stats = self.get_statistics()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO daily_snapshots 
                (snapshot_date, total_companies, main_market_count, nile_count,
                 off_board_count, temporary_count, government_count)
                VALUES (date('now'), ?, ?, ?, ?, ?, ?)
            """, (
                stats.get('total_active', 0),
                stats.get(MarketSegment.MAIN.value, 0),
                stats.get(MarketSegment.NILE.value, 0),
                stats.get(MarketSegment.OFF_BOARD.value, 0),
                stats.get('temporary_listings', 0),
                stats.get('government_companies', 0)
            ))
            conn.commit()


class EGXScraper:
    """
    جامع بيانات الشركات من البورصة المصرية
    يدعم: الموقع الرسمي + APIs البديلة
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'ar-EG,ar;q=0.9,en;q=0.8'
        })
        self.db = EGXDatabase()

    def fetch_from_egx_website(self) -> List[EGXCompany]:
        """
        جلب البيانات من موقع البورصة المصرية الرسمي
        ملاحظة: قد يتطلب تحديث selectors حسب تغييرات الموقع
        """
        companies = []

        try:
            # 1. جلب السوق الرئيسي
            logger.info("جلب شركات السوق الرئيسي...")
            main_companies = self._fetch_main_market()
            companies.extend(main_companies)

            # 2. جلب سوق النيل
            logger.info("جلب شركات سوق النيل...")
            nile_companies = self._fetch_nile_market()
            companies.extend(nile_companies)

            # 3. جلب خارج المقصورة
            logger.info("جلب شركات خارج المقصورة...")
            off_board = self._fetch_off_board()
            companies.extend(off_board)

        except Exception as e:
            logger.error(f"خطأ في جلب البيانات: {e}")

        return companies

    def _fetch_main_market(self) -> List[EGXCompany]:
        """جلب شركات السوق الرئيسي"""
        companies = []

        # API البورصة المصرية للسوق الرئيسي
        url = "https://www.egx.com.eg/ar/listing/listed%20companies/listed%20companies.aspx"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # تحليل HTML (يتطلب BeautifulSoup)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # البحث عن جدول الشركات
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # تخطي العنوان
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        symbol = cells[0].text.strip()
                        name_ar = cells[1].text.strip()
                        sector = cells[2].text.strip() if len(cells) > 2 else "غير محدد"

                        if symbol and name_ar:
                            companies.append(EGXCompany(
                                symbol=symbol,
                                name_ar=name_ar,
                                name_en="",
                                market_segment=MarketSegment.MAIN,
                                sector=sector,
                                is_active=True,
                                listing_date=None,
                                is_government=self._is_government_company(name_ar),
                                temporary_listing=False,
                                last_updated=datetime.now().isoformat()
                            ))

        except Exception as e:
            logger.error(f"خطأ في جلب السوق الرئيسي: {e}")

        return companies

    def _fetch_nile_market(self) -> List[EGXCompany]:
        """جلب شركات سوق النيل"""
        companies = []
        url = "https://www.egx.com.eg/ar/listing/listed%20companies/nilex%20listed%20companies.aspx"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # معالجة مشابهة للسوق الرئيسي
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        symbol = cells[0].text.strip()
                        name_ar = cells[1].text.strip()

                        if symbol and name_ar:
                            companies.append(EGXCompany(
                                symbol=symbol,
                                name_ar=name_ar,
                                name_en="",
                                market_segment=MarketSegment.NILE,
                                sector="غير محدد",
                                is_active=True,
                                listing_date=None,
                                is_government=False,
                                temporary_listing=False,
                                last_updated=datetime.now().isoformat()
                            ))
        except Exception as e:
            logger.error(f"خطأ في جلب سوق النيل: {e}")

        return companies

    def _fetch_off_board(self) -> List[EGXCompany]:
        """جلب شركات خارج المقصورة"""
        # عادةً ما تكون هذه البيانات متاحة في قسم خاص
        companies = []
        logger.info("شركات خارج المقصورة تتطلب مصادر إضافية")
        return companies

    def fetch_from_alternative_api(self) -> List[EGXCompany]:
        """
        جلب البيانات من APIs بديلة (مثل EOD Historical Data, Yahoo Finance)
        """
        companies = []

        # Yahoo Finance symbols للبورصة المصرية
        # اللاحقة .CA = Cairo
        known_symbols = [
            "COMI.CA", "HRHO.CA", "SWDY.CA", "ETEL.CA", "ORWE.CA",
            "PHDC.CA", "ISPH.CA", "CLHO.CA", "EFIH.CA", "HELI.CA"
        ]

        for symbol in known_symbols:
            try:
                # يمكن استخدام yfinance هنا
                # import yfinance as yf
                # ticker = yf.Ticker(symbol)
                # info = ticker.info
                pass
            except Exception as e:
                logger.warning(f"تعذر جلب {symbol}: {e}")

        return companies

    def _is_government_company(self, name: str) -> bool:
        """تحديد إذا كانت شركة حكومية بناءً على الاسم"""
        gov_keywords = [
            'القابضة', 'الق Holding', 'العامة', 'النصر', 'العربية',
            'المصرية', 'الدولة', 'الحكومية', 'مصر لل', 'ايجوث',
            'السياحة', 'الاسكان', 'الاسمنت', 'الصلب'
        ]
        name_upper = name.upper()
        return any(kw.upper() in name_upper for kw in gov_keywords)

    def update_database(self, companies: List[EGXCompany]) -> Dict:
        """تحديث قاعدة البيانات بقائمة الشركات"""
        results = {
            'new': 0,
            'updated': 0,
            'errors': 0,
            'details': []
        }

        for company in companies:
            try:
                is_new, message = self.db.upsert_company(company)
                if is_new:
                    results['new'] += 1
                else:
                    results['updated'] += 1
                results['details'].append(message)
                logger.info(message)
            except Exception as e:
                results['errors'] += 1
                logger.error(f"خطأ في {company.symbol}: {e}")

        # حفظ لقطة يومية
        self.db.save_daily_snapshot()

        return results

    def run_daily_update(self):
        """التشغيل اليومي الكامل"""
        logger.info("=" * 50)
        logger.info("بدء التحديث اليومي للبورصة المصرية")
        logger.info(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        logger.info("=" * 50)

        # جلب البيانات
        companies = self.fetch_from_egx_website()

        if not companies:
            logger.warning("لم يتم جلب أي بيانات! استخدام البيانات الاحتياطية...")
            companies = self._get_fallback_data()

        # تحديث القاعدة
        results = self.update_database(companies)

        # طباعة الإحصائيات
        stats = self.db.get_statistics()
        logger.info("\n" + "=" * 50)
        logger.info("إحصائيات السوق:")
        logger.info(f"  إجمالي الشركات النشطة: {stats['total_active']}")
        logger.info(f"  السوق الرئيسي: {stats.get(MarketSegment.MAIN.value, 0)}")
        logger.info(f"  سوق النيل: {stats.get(MarketSegment.NILE.value, 0)}")
        logger.info(f"  خارج المقصورة: {stats.get(MarketSegment.OFF_BOARD.value, 0)}")
        logger.info(f"  الشركات الحكومية: {stats['government_companies']}")
        logger.info(f"  القيد المؤقت: {stats['temporary_listings']}")
        logger.info(f"  جديد هذا الشهر: {stats['new_this_month']}")
        logger.info("=" * 50)

        return {
            'companies_fetched': len(companies),
            'new_companies': results['new'],
            'updated_companies': results['updated'],
            'errors': results['errors'],
            'statistics': stats
        }

    def _get_fallback_data(self) -> List[EGXCompany]:
        """بيانات احتياطية في حالة فشل الاتصال"""
        logger.info("استخدام البيانات الاحتياطية...")

        # قائمة بأبرز الشركات (للتشغيل اليدوي في حالة الطوارئ)
        fallback = [
            EGXCompany("COMI.CA", "البنك التجاري الدولي", "CIB", MarketSegment.MAIN, "بنوك", True, None, False, False, datetime.now().isoformat()),
            EGXCompany("HRHO.CA", "الهرم", "Al Hoham", MarketSegment.MAIN, "خدمات مالية", True, None, False, False, datetime.now().isoformat()),
            EGXCompany("SWDY.CA", "السويدي إلكتريك", "El Sewedy Electric", MarketSegment.MAIN, "صناعة", True, None, False, False, datetime.now().isoformat()),
            EGXCompany("ETEL.CA", "اتصالات مصر", "Telecom Egypt", MarketSegment.MAIN, "اتصالات", True, None, True, False, datetime.now().isoformat()),
            EGXCompany("ORWE.CA", "أوراسكوم للإنشاءات", "Orascom Construction", MarketSegment.MAIN, "إنشاءات", True, None, False, False, datetime.now().isoformat()),
        ]
        return fallback


class EGXAlertSystem:
    """نظام التنبيهات للتغييرات"""

    def __init__(self, db: EGXDatabase):
        self.db = db

    def check_new_listings(self) -> List[Dict]:
        """التحقق من الشركات الجديدة"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM listing_history 
                WHERE event_type = 'NEW_LISTING' 
                AND event_date >= date('now', '-7 days')
                ORDER BY event_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def check_segment_changes(self) -> List[Dict]:
        """التحقق من تغييرات قطاع السوق"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM listing_history 
                WHERE event_type = 'SEGMENT_CHANGE'
                AND event_date >= date('now', '-7 days')
                ORDER BY event_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def generate_weekly_report(self) -> str:
        """تقرير أسبوعي"""
        new_listings = self.check_new_listings()
        changes = self.check_segment_changes()
        stats = self.db.get_statistics()

        report = f"""
        ╔══════════════════════════════════════════════════════╗
        ║          تقرير البورصة المصرية - EGX Weekly           ║
        ║              {datetime.now().strftime('%Y-%m-%d')}                           ║
        ╚══════════════════════════════════════════════════════╝

        📊 إحصائيات السوق:
           • إجمالي الشركات النشطة: {stats['total_active']}
           • السوق الرئيسي: {stats.get(MarketSegment.MAIN.value, 0)}
           • سوق النيل: {stats.get(MarketSegment.NILE.value, 0)}
           • خارج المقصورة: {stats.get(MarketSegment.OFF_BOARD.value, 0)}
           • طروحات حكومية (قيد مؤقت): {stats['temporary_listings']}

        🆕 شركات جديدة هذا الأسبوع: {len(new_listings)}
        """

        if new_listings:
            report += "\n           الشركات الجديدة:\n"
            for item in new_listings:
                report += f"           • {item['symbol']} - {item['details']}\n"

        report += f"""
        🔄 تغييرات قطاعات: {len(changes)}
        """

        if changes:
            for item in changes:
                report += f"           • {item['symbol']}: {item['details']}\n"

        report += """
        ════════════════════════════════════════════════════════
        """

        return report


# ═══════════════════════════════════════════════════════════════
#                       نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 EGX Companies Scraper - البورصة المصرية")
    print("=" * 50)

    # إنشاء المثيل
    scraper = EGXScraper()

    # التشغيل اليومي
    result = scraper.run_daily_update()

    print("\n✅ تم الانتهاء من التحديث!")
    print(f"   • الشركات المجلوبة: {result['companies_fetched']}")
    print(f"   • جديد: {result['new_companies']}")
    print(f"   • محدث: {result['updated_companies']}")
    print(f"   • أخطاء: {result['errors']}")

    # طباعة التقرير الأسبوعي
    alert_system = EGXAlertSystem(scraper.db)
    print(alert_system.generate_weekly_report())
