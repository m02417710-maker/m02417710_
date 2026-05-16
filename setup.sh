#!/bin/bash

# ==========================================
# EGX Pro Terminal v26 - Setup Script
# سكريبت التثبيت التلقائي للـ Linux و Mac
# ==========================================

echo "🚀 بدء تثبيت EGX Pro Terminal v26..."
echo "=========================================="

# التحقق من Python
echo "✅ التحقق من Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python 3.8 أو أحدث"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION مثبت"

# حذف البيئة الافتراضية القديمة إذا كانت موجودة
if [ -d "venv" ]; then
    echo "🗑️ حذف البيئة الافتراضية القديمة..."
    rm -rf venv
fi

# إنشاء بيئة افتراضية جديدة
echo "📦 إنشاء بيئة افتراضية جديدة..."
python3 -m venv venv

# تفعيل البيئة الافتراضية
echo "⚡ تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تحديث pip
echo "🔄 تحديث pip..."
python -m pip install --upgrade pip --quiet

# مسح cache pip
echo "🧹 مسح cache pip..."
pip cache purge

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
if [ -f "requirements-fixed.txt" ]; then
    pip install -r requirements-fixed.txt --no-cache-dir
elif [ -f "requirements.txt" ]; then
    # استخدم ملف أبسط إذا فشل التثبيت
    echo "⚠️ محاولة تثبيت من requirements.txt..."
    pip install streamlit pandas numpy plotly python-dotenv pydantic requests reportlab --no-cache-dir
fi

# التحقق من التثبيت
echo ""
echo "✅ التحقق من التثبيت..."
python -c "import streamlit; print('✅ Streamlit تم تثبيته بنجاح')" 2>/dev/null || echo "⚠️ تحذير: قد تكون هناك مشكلة في Streamlit"

echo ""
echo "=========================================="
echo "✅ التثبيت اكتمل بنجاح!"
echo "=========================================="
echo ""
echo "🚀 لتشغيل التطبيق، استخدم:"
echo "   streamlit run egx_pro_terminal_v26_enhanced.py"
echo ""
echo "ملاحظة: لتفعيل البيئة الافتراضية في المستقبل:"
echo "   source venv/bin/activate"
echo ""
