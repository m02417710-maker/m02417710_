# 📦 دليل التثبيت الشامل - EGX Pro Terminal v26

---

## 📋 جدول المحتويات

1. [المتطلبات](#المتطلبات)
2. [التثبيت السريع](#التثبيت-السريع)
3. [التثبيت المفصل](#التثبيت-المفصل)
4. [التكوين](#التكوين)
5. [التشغيل](#التشغيل)
6. [التحقق من التثبيت](#التحقق-من-التثبيت)
7. [حل المشاكل](#حل-المشاكل)

---

## المتطلبات

### متطلبات النظام:

| المتطلب | الحد الأدنى | الموصى به |
|--------|-----------|---------|
| **OS** | Windows/Mac/Linux | Ubuntu 20.04+ / macOS 11+ |
| **CPU** | 2 Cores | 4 Cores |
| **RAM** | 2 GB | 8 GB |
| **Disk** | 500 MB | 2 GB |

### متطلبات البرمجيات:

```bash
# Python (إلزامي)
Python 3.8 أو أحدث

# Git (للاستنساخ من GitHub)
Git 2.0 أو أحدث

# pip (مدير الحزم)
pip 20.0 أو أحدث

# اختياري:
PostgreSQL 12+ (قاعدة البيانات)
Redis 6+ (Cache)
Docker (لـ containerization)
```

---

## التثبيت السريع

### للمبتدئين (3 دقائق فقط):

```bash
# 1. استنسخ المستودع
git clone https://github.com/m02417710-maker/m02417710_.git
cd m02417710_

# 2. أنشئ بيئة افتراضية
python -m venv venv

# 3. فعّل البيئة الافتراضية
# على Linux/Mac:
source venv/bin/activate

# على Windows:
venv\Scripts\activate

# 4. ثبت المتطلبات
pip install -r requirements.txt

# 5. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

**انتهى!** 🎉 التطبيق الآن متاح على http://localhost:8501

---

## التثبيت المفصل

### الخطوة 1: التحضير

#### على Linux/Mac:

```bash
# تحديث النظام
sudo apt-get update
sudo apt-get upgrade

# تثبيت Python وmgration الأساسية
sudo apt-get install python3 python3-pip python3-venv

# التحقق من الإصدار
python3 --version
pip3 --version
```

#### على Windows:

```bash
# 1. حمّل Python من: https://www.python.org/downloads/
# 2. ثبّت مع اختيار "Add Python to PATH"
# 3. فتح Command Prompt والتحقق من:
python --version
pip --version
```

### الخطوة 2: استنساخ المستودع

```bash
# اختر مجلد للمشروع
cd ~/projects

# استنسخ المستودع
git clone https://github.com/m02417710-maker/m02417710_.git
cd m02417710_

# تحقق من الملفات
ls -la
```

### الخطوة 3: إنشاء بيئة افتراضية

#### على Linux/Mac:

```bash
# أنشئ بيئة افتراضية
python3 -m venv venv

# فعّلها
source venv/bin/activate

# يجب أن ترى "(venv)" في بداية الـ prompt
```

#### على Windows:

```bash
# أنشئ بيئة افتراضية
python -m venv venv

# فعّلها
venv\Scripts\activate

# يجب أن ترى "(venv)" في بداية الـ prompt
```

### الخطوة 4: تثبيت المتطلبات

```bash
# تحديث pip (مهم!)
pip install --upgrade pip

# تثبيت جميع المتطلبات
pip install -r requirements.txt

# التحقق من التثبيت
pip list
```

### الخطوة 5: التكوين

#### أ) إنشاء ملف .env:

```bash
# انسخ الملف النموذجي
cp .env.example .env

# عدّل الملف حسب احتياجاتك
nano .env  # على Linux/Mac
# أو استخدم أي محرر نصي على Windows
```

#### ب) معلومات تكوينية مهمة:

```env
# الوضع
ENVIRONMENT=development

# الميزات المفعلة
FEATURE_ALERTS_ENABLED=true
FEATURE_RISK_ANALYSIS_ENABLED=true
FEATURE_STOCK_SCREENER_ENABLED=true
FEATURE_STRATEGIES_ENABLED=true
FEATURE_PDF_REPORTS_ENABLED=true

# قاعدة البيانات (اختياري)
DB_HOST=localhost
DB_PORT=5432
```

### الخطوة 6: التشغيل

#### تشغيل Streamlit:

```bash
# تأكد من تفعيل البيئة الافتراضية
# يجب أن ترى (venv) في الـ prompt

# شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py

# أو مع معاملات إضافية
streamlit run egx_pro_terminal_v26_enhanced.py \
  --logger.level=debug \
  --client.toolbarMode=minimal
```

#### الوصول للتطبيق:

```
التطبيق يعمل الآن على:
http://localhost:8501

استخدم هذا الرابط من المتصفح
```

---

## التحقق من التثبيت

### فحص شامل:

```bash
# 1. التحقق من Python
python --version
# يجب أن يكون 3.8 أو أحدث

# 2. التحقق من pip
pip --version

# 3. التحقق من المتطلبات
pip list | grep streamlit
pip list | grep pandas
pip list | grep plotly

# 4. التحقق من المجلدات
ls -la egx_pro_terminal_v26_enhanced.py

# 5. تشغيل اختبار بسيط
python -c "import streamlit as st; print('✅ Streamlit OK')"
```

### اختبار بسيط:

```python
# أنشئ ملف test.py
cat > test.py << 'EOF'
import streamlit as st
import pandas as pd
import numpy as np

st.title("✅ EGX Pro Terminal Test")
st.write("التثبيت نجح!")

# اختبر كل المكتبات المهمة
try:
    import plotly
    st.write("✅ Plotly")
except:
    st.write("❌ Plotly")

try:
    import reportlab
    st.write("✅ ReportLab")
except:
    st.write("❌ ReportLab")
EOF

streamlit run test.py
```

---

## حل المشاكل الشائعة

### ❌ مشكلة: "command not found: python"

**الحل:**
```bash
# استخدم python3 بدلاً من python
python3 --version

# أو أضفه للـ PATH
export PATH="/usr/bin/python3:$PATH"
```

### ❌ مشكلة: "virtualenv not found"

**الحل:**
```bash
# ثبّت virtualenv
pip install virtualenv

# أو استخدم venv المدمج
python -m venv venv
```

### ❌ مشكلة: "Module not found"

**الحل:**
```bash
# تأكد من تفعيل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# أعد تثبيت المتطلبات
pip install -r requirements.txt
```

### ❌ مشكلة: "Port already in use"

**الحل:**
```bash
# استخدم port مختلف
streamlit run egx_pro_terminal_v26_enhanced.py --server.port 8502

# أو اقتل العملية الأخرى
lsof -i :8501  # على Linux/Mac
netstat -ano | findstr :8501  # على Windows
```

### ❌ مشكلة: "Permission denied"

**الحل:**
```bash
# على Linux/Mac
chmod +x egx_pro_terminal_v26_enhanced.py

# أو استخدم sudo (غير موصى به)
sudo streamlit run egx_pro_terminal_v26_enhanced.py
```

### ❌ مشكلة: "pip: command not found"

**الحل:**
```bash
# استخدم python مباشرة
python -m pip install -r requirements.txt

# أو استخدم pip3
pip3 install -r requirements.txt
```

---

## التثبيت مع Docker (اختياري)

```bash
# بناء صورة Docker
docker build -t egx-pro-terminal .

# تشغيل الحاوية
docker run -p 8501:8501 egx-pro-terminal

# الوصول عبر:
# http://localhost:8501
```

---

## التثبيت مع conda (بديل)

```bash
# إنشاء بيئة جديدة
conda create -n egx-pro python=3.10

# تفعيل البيئة
conda activate egx-pro

# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## التثبيت على خادم (Production)

### 1. إعداد خادم Linux:

```bash
# تحديث النظام
sudo apt-get update
sudo apt-get upgrade -y

# تثبيت Python و pip
sudo apt-get install python3 python3-pip -y

# تثبيت supervisor لإدارة العملية
sudo apt-get install supervisor -y
```

### 2. نشر المشروع:

```bash
# انتقل إلى مجلد الخادم
cd /var/www

# استنسخ المشروع
git clone https://github.com/m02417710-maker/m02417710_.git
cd m02417710_

# أنشئ بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# ثبّت المتطلبات
pip install -r requirements.txt
```

### 3. إعداد Supervisor:

```bash
# انشئ ملف configuration
sudo nano /etc/supervisor/conf.d/egx-pro.conf
```

أضف المحتوى:
```ini
[program:egx-pro]
command=/var/www/m02417710_/venv/bin/streamlit run egx_pro_terminal_v26_enhanced.py --server.port 8501
directory=/var/www/m02417710_
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/egx-pro.err.log
stdout_logfile=/var/log/egx-pro.out.log
```

### 4. إعادة تشغيل Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start egx-pro
```

---

## الخطوات التالية

✅ التثبيت اكتمل!

الآن:

1. 📖 اقرأ [README.md](README.md)
2. 📚 استكشف [التوثيق الكاملة](FEATURES_DOCUMENTATION_AR.md)
3. 💻 جرّب [الأمثلة](USAGE_EXAMPLES.py)
4. 🚀 ابدأ باستخدام التطبيق

---

## الحصول على الدعم

إذا واجهت مشكلة:

1. 🔍 ابحث في [الأسئلة الشائعة](README.md#faq)
2. 💬 افتح [Issue على GitHub](https://github.com/m02417710-maker/m02417710_/issues)
3. 📧 اتصل بنا: support@egxpro.com

---

**شكراً لتثبيت EGX Pro Terminal v26!** 🎉

---

**آخر تحديث**: مايو 2026
