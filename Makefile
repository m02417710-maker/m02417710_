# ==========================================
# EGX Pro Terminal v26 - Makefile
# أوامر سهلة للتثبيت والتشغيل
# ==========================================

.PHONY: help install clean run test deps update lint format

# المتغيرات
PYTHON := python3
PIP := pip
VENV := venv
APP := egx_pro_terminal_v26_enhanced.py

# الألوان
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# الهدف الافتراضي
help:
	@echo "$(BLUE)===================================$(NC)"
	@echo "$(BLUE)EGX Pro Terminal v26$(NC)"
	@echo "$(BLUE)===================================$(NC)"
	@echo ""
	@echo "$(YELLOW)الأوامر المتاحة:$(NC)"
	@echo ""
	@echo "  $(GREEN)make install$(NC)   - تثبيت المكتبات"
	@echo "  $(GREEN)make run$(NC)        - تشغيل التطبيق"
	@echo "  $(GREEN)make clean$(NC)      - حذف البيئة والـ cache"
	@echo "  $(GREEN)make setup$(NC)      - إعداد كامل (install + run)"
	@echo "  $(GREEN)make deps$(NC)       - عرض المتطلبات"
	@echo "  $(GREEN)make update$(NC)     - تحديث المكتبات"
	@echo "  $(GREEN)make check$(NC)      - التحقق من التثبيت"
	@echo "  $(GREEN)make lint$(NC)       - فحص الكود (إذا كان متاحاً)"
	@echo "  $(GREEN)make format$(NC)     - تنسيق الكود (إذا كان متاحاً)"
	@echo ""
	@echo "$(YELLOW)أمثلة:$(NC)"
	@echo "  make install && make run"
	@echo "  make clean && make setup"
	@echo ""

# إنشاء البيئة الافتراضية وتثبيت المتطلبات
install: venv deps
	@echo "$(GREEN)✅ التثبيت اكتمل!$(NC)"

# إنشاء البيئة الافتراضية
venv:
	@echo "$(YELLOW)📦 إنشاء البيئة الافتراضية...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✅ البيئة الافتراضية جاهزة$(NC)"

# تثبيت المتطلبات
deps:
	@echo "$(YELLOW)📥 تثبيت المتطلبات...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	$(PIP) install --upgrade pip --quiet; \
	if [ -f requirements-fixed.txt ]; then \
		$(PIP) install -r requirements-fixed.txt --no-cache-dir; \
	elif [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt --no-cache-dir; \
	else \
		$(PIP) install streamlit pandas numpy plotly python-dotenv pydantic requests reportlab --no-cache-dir; \
	fi
	@echo "$(GREEN)✅ المتطلبات تم تثبيتها$(NC)"

# تشغيل التطبيق
run:
	@echo "$(YELLOW)🚀 بدء التطبيق...$(NC)"
	@echo "$(BLUE)الرابط: http://localhost:8501$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	streamlit run $(APP)

# إعداد كامل (install + run)
setup: install run

# حذف البيئة الافتراضية والـ cache
clean:
	@echo "$(YELLOW)🗑️  تنظيف البيئة...$(NC)"
	@rm -rf $(VENV) 2>/dev/null || rmdir /s /q $(VENV) 2>/dev/null
	@rm -rf ~/.streamlit 2>/dev/null || rmdir /s /q %USERPROFILE%\.streamlit 2>/dev/null
	@$(PIP) cache purge 2>/dev/null || true
	@echo "$(GREEN)✅ البيئة نظيفة$(NC)"

# حذف البيئة فقط (بدون حذف cache)
clean-venv:
	@echo "$(YELLOW)🗑️  حذف البيئة الافتراضية...$(NC)"
	@rm -rf $(VENV) 2>/dev/null || rmdir /s /q $(VENV) 2>/dev/null
	@echo "$(GREEN)✅ تم الحذف$(NC)"

# تحديث المكتبات
update:
	@echo "$(YELLOW)🔄 تحديث المكتبات...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	$(PIP) install --upgrade pip; \
	if [ -f requirements.txt ]; then \
		$(PIP) install --upgrade -r requirements.txt; \
	fi
	@echo "$(GREEN)✅ التحديث اكتمل$(NC)"

# التحقق من التثبيت
check:
	@echo "$(YELLOW)🔍 التحقق من التثبيت...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	$(PYTHON) --version; \
	echo ""; \
	echo "$(BLUE)المكتبات المثبتة:$(NC)"; \
	$(PIP) list | grep -E "streamlit|pandas|numpy|plotly"; \
	echo ""; \
	echo "$(YELLOW)اختبار المكتبات:$(NC)"; \
	$(PYTHON) -c "import streamlit; print('✅ Streamlit OK')" 2>/dev/null || echo "❌ Streamlit"; \
	$(PYTHON) -c "import pandas; print('✅ Pandas OK')" 2>/dev/null || echo "❌ Pandas"; \
	$(PYTHON) -c "import numpy; print('✅ Numpy OK')" 2>/dev/null || echo "❌ Numpy"; \
	$(PYTHON) -c "import plotly; print('✅ Plotly OK')" 2>/dev/null || echo "❌ Plotly"

# فحص الكود (إذا كان pylint متاحاً)
lint:
	@echo "$(YELLOW)🔎 فحص الكود...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	if command -v pylint &> /dev/null; then \
		pylint $(APP) --exit-zero; \
	elif command -v flake8 &> /dev/null; then \
		flake8 $(APP); \
	else \
		echo "$(YELLOW)⚠️  pylint أو flake8 غير مثبت$(NC)"; \
		echo "$(YELLOW)للتثبيت: pip install pylint flake8$(NC)"; \
	fi

# تنسيق الكود (إذا كان black متاحاً)
format:
	@echo "$(YELLOW)📝 تنسيق الكود...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	if command -v black &> /dev/null; then \
		black $(APP); \
	else \
		echo "$(YELLOW)⚠️  black غير مثبت$(NC)"; \
		echo "$(YELLOW)للتثبيت: pip install black$(NC)"; \
	fi

# حل سريع للمشاكل
fix:
	@echo "$(YELLOW)🔧 محاولة حل المشاكل...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	echo "$(BLUE)1. تحديث pip...$(NC)"; \
	$(PIP) install --upgrade pip; \
	echo "$(BLUE)2. مسح cache...$(NC)"; \
	$(PIP) cache purge; \
	echo "$(BLUE)3. إعادة تثبيت المتطلبات...$(NC)"; \
	$(PIP) install --no-cache-dir streamlit pandas numpy plotly python-dotenv; \
	echo "$(GREEN)✅ تم محاولة حل المشاكل$(NC)"

# إعادة تثبيت كامل
reinstall: clean install
	@echo "$(GREEN)✅ إعادة التثبيت اكتملت$(NC)"

# عرض المتطلبات
show-deps:
	@echo "$(BLUE)المتطلبات المطلوبة:$(NC)"
	@if [ -f requirements-fixed.txt ]; then \
		cat requirements-fixed.txt; \
	elif [ -f requirements.txt ]; then \
		cat requirements.txt; \
	else \
		echo "❌ لم يتم العثور على ملف المتطلبات"; \
	fi

# تصدير المكتبات المثبتة
freeze:
	@echo "$(YELLOW)📦 حفظ المكتبات المثبتة...$(NC)"
	@. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate.bat 2>/dev/null; \
	$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)✅ تم حفظ في requirements-frozen.txt$(NC)"

# معلومات النظام
info:
	@echo "$(BLUE)===================================$(NC)"
	@echo "$(BLUE)معلومات النظام$(NC)"
	@echo "$(BLUE)===================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Python:$(NC)"
	@$(PYTHON) --version
	@echo ""
	@echo "$(YELLOW)Pip:$(NC)"
	@$(PIP) --version
	@echo ""
	@echo "$(YELLOW)النظام:$(NC)"
	@uname -a 2>/dev/null || systeminfo 2>/dev/null || echo "غير متاح"
	@echo ""

# مساعدة إضافية
help-full:
	@echo "$(BLUE)===================================$(NC)"
	@echo "$(BLUE)دليل كامل للاستخدام$(NC)"
	@echo "$(BLUE)===================================$(NC)"
	@echo ""
	@echo "$(YELLOW)للبدء السريع:$(NC)"
	@echo "  make setup"
	@echo ""
	@echo "$(YELLOW)للتثبيت والتشغيل المنفصل:$(NC)"
	@echo "  make install"
	@echo "  make run"
	@echo ""
	@echo "$(YELLOW)لحل المشاكل:$(NC)"
	@echo "  make fix       # محاولة حل المشاكل الشائعة"
	@echo "  make clean     # حذف البيئة والـ cache"
	@echo "  make check     # التحقق من التثبيت"
	@echo ""
	@echo "$(YELLOW)لتطوير الكود:$(NC)"
	@echo "  make lint      # فحص الكود"
	@echo "  make format    # تنسيق الكود"
	@echo ""
	@echo "$(YELLOW)معلومات:$(NC)"
	@echo "  make info      # معلومات النظام"
	@echo "  make deps      # عرض المتطلبات"
	@echo ""
