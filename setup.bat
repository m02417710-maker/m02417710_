@echo off
REM ==========================================
REM EGX Pro Terminal v26 - Setup Script
REM سكريبت التثبيت التلقائي للـ Windows
REM ==========================================

echo.
echo 🚀 بدء تثبيت EGX Pro Terminal v26...
echo ==========================================
echo.

REM التحقق من Python
echo ✅ التحقق من Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو لم يتم إضافته إلى PATH
    echo يرجى تثبيت Python 3.8 أو أحدث من: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM حذف البيئة الافتراضية القديمة
if exist venv (
    echo 🗑️ حذف البيئة الافتراضية القديمة...
    rmdir /s /q venv
)

REM إنشاء بيئة افتراضية جديدة
echo 📦 إنشاء بيئة افتراضية جديدة...
python -m venv venv
if errorlevel 1 (
    echo ❌ فشل إنشاء البيئة الافتراضية
    pause
    exit /b 1
)

REM تفعيل البيئة الافتراضية
echo ⚡ تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

REM تحديث pip
echo 🔄 تحديث pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ⚠️ تحذير: حدثت مشكلة في تحديث pip
)

REM مسح cache pip
echo 🧹 مسح cache pip...
pip cache purge

REM تثبيت المتطلبات
echo 📥 تثبيت المتطلبات...
if exist requirements-fixed.txt (
    pip install -r requirements-fixed.txt --no-cache-dir
) else if exist requirements.txt (
    echo ⚠️ استخدام requirements.txt (قد يسبب مشاكل)
    pip install -r requirements.txt --no-cache-dir
) else (
    echo ⚠️ لم يتم العثور على requirements.txt
    echo 📦 تثبيت المكتبات الأساسية...
    pip install streamlit pandas numpy plotly python-dotenv pydantic requests reportlab --no-cache-dir
)

echo.
echo ✅ التحقق من التثبيت...
python -c "import streamlit; print('✅ Streamlit تم تثبيته بنجاح')" 2>nul || (
    echo ⚠️ تحذير: قد تكون هناك مشكلة في Streamlit
)

echo.
echo ==========================================
echo ✅ التثبيت اكتمل بنجاح!
echo ==========================================
echo.
echo 🚀 لتشغيل التطبيق، استخدم:
echo    streamlit run egx_pro_terminal_v26_enhanced.py
echo.
echo ملاحظة: لتفعيل البيئة الافتراضية في المستقبل:
echo    venv\Scripts\activate
echo.
pause
