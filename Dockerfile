# استخدم صورة Python الرسمية
FROM python:3.10-slim

# ضع مجلد العمل
WORKDIR /app

# ثبت الحزم النظامية المطلوبة
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# انسخ ملف المتطلبات
COPY requirements.txt .

# ثبّت متطلبات Python
RUN pip install --no-cache-dir -r requirements.txt

# انسخ كل ملفات المشروع
COPY . .

# أنشئ مجلدات العمل
RUN mkdir -p /app/data /app/logs /app/cache /app/temp

# كشف المنفذ
EXPOSE 8501

# صحة الفحص
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# الأمر الافتراضي
CMD ["streamlit", "run", "egx_pro_terminal_v26_enhanced.py", "--server.port=8501", "--server.address=0.0.0.0"]
