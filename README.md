# 🇪🇬 EGX Market Scraper

نظام جلب وتحديث بيانات الشركات المقيدة في **البورصة المصرية (EGX)**.

## 📊 التغطية

| السوق | العدد التقريبي |
|-------|---------------|
| السوق الرئيسي | ~218-220 شركة |
| سوق النيل (SME) | ~17 شركة |
| خارج المقصورة | ~19 شركة |
| طروحات حكومية (قيد مؤقت) | متغير |

## 🚀 التشغيل السريع

```bash
# 1. استنساخ المستودع
git clone https://github.com/m02417710-maker/m02417710_.git
cd m02417710_

# 2. البناء والتشغيل
docker-compose up --build

# أو بدون Docker:
pip install -r requirements.txt
python egx_scraper.py
```

## 📁 هيكل المشروع

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── entrypoint.sh
├── egx_scraper.py      ← الكود الرئيسي
└── data/
    ├── egx_companies.db    ← قاعدة SQLite
    └── egx_scraper.log     ← سجل التشغيل
```

## 🗄️ قاعدة البيانات

### الجداول:
- `companies` — الشركات المقيدة
- `listing_history` — تاريخ القيد والشطب
- `daily_snapshots` — لقطات إحصائية يومية

### الاستعلام السريع:
```python
from egx_scraper import EGXDatabase, MarketSegment

db = EGXDatabase("data/egx_companies.db")
stats = db.get_statistics()
print(f"إجمالي الشركات: {stats['total_active']}")
```

## ⏰ التشغيل المجدول

يتضمن `docker-compose.yml` خدمة `egx-scheduler` تعمل كل **24 ساعة** تلقائياً.

## 📜 الترخيص

MIT License — مفتوح المصدر.
