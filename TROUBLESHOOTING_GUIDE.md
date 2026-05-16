# 🔧 دليل حل مشاكل التثبيت والتشغيل

---

## ✅ **حلول سريعة فوراً**

### **الحل الأول (في 2 دقيقة):**

#### على Linux/Mac:
```bash
# 1. امسح البيئة القديمة
rm -rf venv ~/.streamlit

# 2. أنشئ بيئة جديدة
python3 -m venv venv
source venv/bin/activate

# 3. تحديث pip
python -m pip install --upgrade pip

# 4. ثبّت المكتبات الأساسية
pip install streamlit pandas numpy plotly python-dotenv

# 5. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

#### على Windows:
```bash
# 1. امسح البيئة القديمة
rmdir /s /q venv
rmdir /s /q %USERPROFILE%\.streamlit

# 2. أنشئ بيئة جديدة
python -m venv venv
venv\Scripts\activate

# 3. تحديث pip
python -m pip install --upgrade pip

# 4. ثبّت المكتبات الأساسية
pip install streamlit pandas numpy plotly python-dotenv

# 5. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## 🎯 **استخدام السكريبتات التلقائية**

### على Linux/Mac:
```bash
# 1. اجعل السكريبت قابلاً للتنفيذ
chmod +x setup.sh

# 2. شغّله
./setup.sh

# 3. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

### على Windows:
```bash
# 1. شغّل السكريبت
setup.bat

# 2. شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## 🔍 **تشخيص المشاكل**

### **مشكلة 1: "installer returned a non-zero exit code"**

**السبب:** مشكلة في تثبيت المكتبات

**الحل:**
```bash
# 1. تحديث pip
python -m pip install --upgrade pip

# 2. مسح cache
pip cache purge

# 3. ثبّت المكتبات الأساسية فقط
pip install streamlit --no-cache-dir
pip install pandas --no-cache-dir
pip install numpy --no-cache-dir
pip install plotly --no-cache-dir

# 4. أضف الباقي تدريجياً
pip install python-dotenv --no-cache-dir
pip install pydantic --no-cache-dir
pip install requests --no-cache-dir
pip install reportlab --no-cache-dir
```

---

### **مشكلة 2: "ModuleNotFoundError"**

**السبب:** لم يتم تفعيل البيئة الافتراضية

**الحل:**
```bash
# تفعيل البيئة الافتراضية

# على Linux/Mac:
source venv/bin/activate

# على Windows:
venv\Scripts\activate

# تحقق من التفعيل (يجب أن ترى (venv) في بداية الـ prompt)
```

---

### **مشكلة 3: "command not found: python"**

**السبب:** Python غير مثبت أو غير موجود في PATH

**الحل:**
```bash
# استخدم python3 بدلاً من python
python3 --version

# أو على Windows، أعد تثبيت Python مع "Add Python to PATH"
```

---

### **مشكلة 4: "Port 8501 already in use"**

**السبب:** البورت مستخدم من تطبيق آخر

**الحل:**
```bash
# شغّل على port مختلف
streamlit run egx_pro_terminal_v26_enhanced.py --server.port 8502

# أو أيقف العملية الأخرى:

# على Linux/Mac:
lsof -i :8501
kill -9 <PID>

# على Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

---

### **مشكلة 5: "RemoveChild not found"**

**السبب:** مشكلة في الـ cache أو المتصفح

**الحل:**
```bash
# 1. مسح streamlit cache
rm -rf ~/.streamlit

# 2. مسح cache المتصفح
# اضغط Ctrl+Shift+Delete
# واختر "All time" وحذف

# 3. أعد تشغيل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## 📋 **خطوات التثبيت الكاملة**

### **الطريقة 1: استخدام requirements-fixed.txt (الأفضل)**

```bash
# 1. تحقق من Python
python3 --version

# 2. امسح البيئة القديمة
rm -rf venv

# 3. أنشئ بيئة جديدة
python3 -m venv venv

# 4. فعّلها
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# 5. حدّث pip
python -m pip install --upgrade pip

# 6. امسح cache
pip cache purge

# 7. ثبّت من requirements-fixed.txt
pip install -r requirements-fixed.txt --no-cache-dir
```

---

### **الطريقة 2: التثبيت اليدوي (الأكثر أماناً)**

```bash
# بعد تفعيل البيئة الافتراضية:
pip install --no-cache-dir streamlit
pip install --no-cache-dir pandas
pip install --no-cache-dir numpy
pip install --no-cache-dir plotly
pip install --no-cache-dir python-dotenv
pip install --no-cache-dir pydantic
pip install --no-cache-dir requests
pip install --no-cache-dir reportlab
```

---

## 🚀 **التشغيل**

```bash
# تأكد من تفعيل البيئة الافتراضية
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows

# شغّل التطبيق
streamlit run egx_pro_terminal_v26_enhanced.py

# يجب أن تظهر:
# Local URL: http://localhost:8501
# Network URL: http://YOUR_IP:8501
```

---

## ✅ **التحقق من التثبيت**

```bash
# تحقق من المكتبات المثبتة
pip list | grep streamlit
pip list | grep pandas

# اختبر import المكتبات
python -c "import streamlit; import pandas; import numpy; import plotly; print('✅ جميع المكتبات OK')"

# اختبر تشغيل Streamlit
streamlit --version
```

---

## 🆘 **الحل النهائي (إذا فشل كل شيء)**

```bash
# 1. حذف كل شيء
rm -rf venv
rm -rf ~/.streamlit
pip cache purge

# 2. إعادة تثبيت كامل
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip

# 3. تثبيت بسيط جداً
pip install streamlit

# 4. تشغيل فوري
streamlit hello

# إذا نجح، جرب:
streamlit run egx_pro_terminal_v26_enhanced.py
```

---

## 📞 **معلومات للدعم**

إذا استمرت المشكلة، اجمع هذه المعلومات:

```bash
# اطبع معلومات النظام
python --version
pip --version
pip list > installed_packages.txt

# اطبع خطأ التثبيت
pip install -r requirements-fixed.txt -v > error.log 2>&1

# شارك الملفات معي:
# - error.log
# - installed_packages.txt
# - نظام التشغيل (Windows/Mac/Linux)
```

---

## 📚 **موارد إضافية**

- [Streamlit الدعم الرسمي](https://discuss.streamlit.io/)
- [تثبيت Python](https://www.python.org/downloads/)
- [Pip الدعم](https://pip.pypa.io/)

---

**جرب الحل الأول أولاً - عادة ينجح! ✨**
