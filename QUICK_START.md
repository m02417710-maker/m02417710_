# ⚡ البدء السريع - EGX Pro Terminal v26

---

## 🚀 **التثبيت والتشغيل في 2 دقيقة**

### **الخيار 1️⃣: استخدام Makefile (الأسهل)**

```bash
# في مجلد المشروع:
make setup

# أو خطوة بخطوة:
make install
make run
```

---

### **الخيار 2️⃣: استخدام السكريبتات**

#### على Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
# ثم:
streamlit run egx_pro_terminal_v26_enhanced.py
```

#### على Windows:
```bash
setup.bat
# ثم:
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

### **الخيار 3️⃣: التثبيت اليدوي**

```bash
# 1. أنشئ بيئة افتراضية
python -m venv venv

# 2. فعّلها
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# 3. تحديث pip
python -m pip install --upgrade pip

# 4. ثبّت المكتبات
pip install -r requirements-fixed.txt

# 5. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## ✅ **التحقق من التثبيت**

```bash
# استخدم Makefile:
make check

# أو يدويًا:
python -c "import streamlit, pandas, numpy, plotly; print('✅ جميع المكتبات OK')"
```

---

## 🔗 **الوصول للتطبيق**

بعد التشغيل، سترى:
```
Local URL: http://localhost:8501
```

افتح هذا الرابط في المتصفح! 🌐

---

## 🆘 **إذا حدثت مشكلة**

```bash
# جرب هذا:
make fix

# أو احذف وأعد التثبيت:
make reinstall

# أو اقرأ دليل حل المشاكل:
# TROUBLESHOOTING_GUIDE.md
```

---

## 📚 **موارد إضافية**

- 📖 INSTALLATION_GUIDE.md - دليل تثبيت مفصل
- 🔧 TROUBLESHOOTING_GUIDE.md - حل المشاكل
- 📚 README.md - معلومات عامة

---

## 💡 **أوامر Makefile مفيدة**

```bash
make help          # عرض جميع الأوامر
make install       # تثبيت المتطلبات
make run           # تشغيل التطبيق
make clean         # حذف البيئة والـ cache
make update        # تحديث المكتبات
make check         # التحقق من التثبيت
make fix           # محاولة حل المشاكل
```

---

**تم! الآن أنت جاهز لاستخدام EGX Pro Terminal! 🎉**
