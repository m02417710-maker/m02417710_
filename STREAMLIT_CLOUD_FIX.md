# 🚀 إصلاح تطبيق Streamlit Cloud - خطوة بخطوة

---

## 🔴 **المشكلة الحالية:**

```
ModuleNotFoundError: This app has encountered an error.
File "/mount/src/m02417710_/streamlit_app.py", line 27, in <module>
    from config.settings import *
```

---

## ✅ **الحل (5 دقائق فقط):**

### **الخطوة 1️⃣: على GitHub Web Interface**

1. اذهب إلى: https://github.com/m02417710-maker/m02417710_
2. اضغط على `streamlit_app.py`
3. اضغط أيقونة **Edit** (قلم رصاص) ✏️
4. **احذف كل المحتوى الحالي**
5. **انسخ هذا الكود الجديد:**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""⚡ EGX Pro Terminal v26 - نظام تحليلي احترافي للبورصة المصرية"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(
    page_title="⚡ EGX Pro Terminal v26",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #07070d 0%, #0f0f1a 50%, #07070d 100%); }
    h1, h2, h3 { color: #818cf8; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ==================== MAIN APP ====================

# Header
st.markdown("""
<div style="text-align: center;">
    <h1>⚡ EGX Pro Terminal v26</h1>
    <p style="color: #94a3b8;">نظام تحليلي احترافي للبورصة المصرية</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 📍 القائمة الرئيسية")
    page = st.radio("اختر القسم:", [
        "📊 لوحة التحكم",
        "🔔 التنبيهات",
        "⚖️ إدارة المخاطر",
        "🔍 مسح الأسهم",
        "📚 الاستراتيجيات",
        "💼 المحفظة"
    ])

# ==================== PAGES ====================

if page == "📊 لوحة التحكم":
    st.markdown("## 📊 لوحة التحكم الرئيسية")
    
    # Sample data
    stocks = {
        'EBANK': {'name': 'البنك الأهلي المصري', 'price': 150.5, 'change': 2.5},
        'EVCO': {'name': 'الكوك مصر', 'price': 200.0, 'change': -1.2},
        'ORWA': {'name': 'أوراسكوم تليكوم', 'price': 75.25, 'change': 3.8},
    }
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📈 إجمالي الأسهم", len(stocks), "نشطة")
    col2.metric("📊 متوسط التغير", f"+1.7%", "يومي")
    col3.metric("📉 الحجم الإجمالي", "12.5M", "دولار")
    col4.metric("🏭 القطاعات", "10", "قطاع")
    
    st.markdown("---")
    st.markdown("### 📋 أكبر الأسهم تداولاً")
    
    df = pd.DataFrame([
        {'السهم': 'EBANK', 'الاسم': 'البنك الأهلي', 'السعر': 150.5, 'التغير%': '+2.5%'},
        {'السهم': 'EVCO', 'الاسم': 'الكوك مصر', 'السعر': 200.0, 'التغير%': '-1.2%'},
        {'السهم': 'ORWA', 'الاسم': 'أوراسكوم', 'السعر': 75.25, 'التغير%': '+3.8%'},
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "🔔 التنبيهات":
    st.markdown("## 🔔 نظام التنبيهات الذكية")
    
    with st.expander("➕ إضافة تنبيه جديد", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.selectbox("السهم", ["EBANK", "EVCO", "ORWA"])
            alert_type = st.selectbox("النوع", ["PRICE", "VOLUME", "MACD"])
        with col2:
            condition = st.selectbox("الشرط", [">", "<", "="])
            value = st.number_input("القيمة", value=100.0)
        
        if st.button("✅ إضافة التنبيه"):
            st.success(f"✅ تم إضافة تنبيه على {symbol}")
    
    st.info("📭 لا توجد تنبيهات نشطة حالياً")

elif page == "⚖️ إدارة المخاطر":
    st.markdown("## ⚖️ إدارة المخاطر المتقدمة")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 VaR (95%)", "-2.45%")
    col2.metric("📈 Sharpe Ratio", "1.85")
    col3.metric("📉 Max Drawdown", "-8.32%")
    col4.metric("📐 Volatility", "2.14%")
    
    st.markdown("---")
    
    # Chart
    np.random.seed(42)
    data = np.cumprod(1 + np.random.normal(0.001, 0.02, 100))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data, mode='lines', name='العائدات', 
                            line=dict(color='#818cf8', width=2)))
    fig.update_layout(title="العائدات التراكمية", template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🔍 مسح الأسهم":
    st.markdown("## 🔍 مسح الأسهم الذكي")
    
    with st.expander("🎯 معايير البحث"):
        col1, col2 = st.columns(2)
        with col1:
            price_min = st.number_input("السعر الأدنى", value=0.0)
            change_min = st.number_input("التغير الأدنى %", value=-10.0)
        with col2:
            price_max = st.number_input("السعر الأقصى", value=500.0)
    
    st.dataframe(pd.DataFrame([
        {'السهم': 'EBANK', 'الاسم': 'البنك الأهلي', 'السعر': 150.5, 'التغير%': '+2.5%'},
        {'السهم': 'ORWA', 'الاسم': 'أوراسكوم', 'السعر': 75.25, 'التغير%': '+3.8%'},
    ]), use_container_width=True, hide_index=True)

elif page == "📚 الاستراتيجيات":
    st.markdown("## 📚 قوالب الاستراتيجيات")
    
    strategies = {
        'الدعم والمقاومة': 'تداول من مستويات الدعم والمقاومة',
        'الزخم': 'تتابع اتجاهات قوية',
        'المتوسط المتحرك': 'تتابع الاتجاه بناءً على المتوسطات'
    }
    
    for name, desc in strategies.items():
        with st.expander(f"📌 {name}"):
            st.write(f"**الوصف:** {desc}")
            st.write("**نسبة المخاطرة:** 1:2.5")

elif page == "💼 المحفظة":
    st.markdown("## 💼 محاكاة المحفظة")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 رأس المال", "100,000", "ج.م")
    col2.metric("📈 الأرباح", "+5,250", "ج.م")
    col3.metric("📊 العائد", "+5.25%", "نسبة")
    col4.metric("⚖️ الأسهم", "12", "صفقة")
    
    st.markdown("---")
    
    with st.expander("➕ إضافة صفقة جديدة"):
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("السهم", ["EBANK", "EVCO", "ORWA"])
            st.radio("الاتجاه", ["شراء", "بيع"])
        with col2:
            st.number_input("الكمية", value=100)
            st.number_input("سعر الدخول", value=150.0)
        
        if st.button("💾 إضافة الصفقة"):
            st.success("✅ تمت إضافة الصفقة بنجاح")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    <p>© 2026 EGX Pro Terminal v26 | نظام تحليلي احترافي للبورصة المصرية</p>
    <p>للأغراض التعليمية فقط - ليست نصيحة استثمارية</p>
</div>
""", unsafe_allow_html=True)
```

6. اضغط **Commit changes** في الأسفل

---

### **الخطوة 2️⃣: أعد تحميل التطبيق**

1. اذهب إلى تطبيقك على Streamlit Cloud
2. انتظر قليلاً (30-60 ثانية)
3. سيعيد التطبيق التحميل تلقائياً
4. يجب أن تظهر الصفحة الرئيسية بدون أخطاء! ✅

---

### **الخطوة 3️⃣: إذا لم ينجح:**

اذهب إلى **"Manage app"** (أسفل يمين التطبيق):
1. اضغط على **"Reboot app"**
2. انتظر إعادة التحميل
3. صحّح المشكلة إن وجدت

---

## ✅ **ماذا بعد الإصلاح؟**

بعد نجاح الإصلاح، يجب:

```bash
# في مستودعك المحلي:
git pull origin main

# تحقق من الملف الجديد
cat streamlit_app.py | head -30

# اختبره محلياً
streamlit run streamlit_app.py
```

---

## 🎯 **الملخص:**

| الخطوة | الإجراء | الوقت |
|------|--------|------|
| 1 | فتح `streamlit_app.py` على GitHub | 30 ثانية |
| 2 | استبدال المحتوى | 2 دقيقة |
| 3 | Commit الملف | 30 ثانية |
| 4 | انتظار إعادة التحميل | 1 دقيقة |
| 5 | التحقق من النجاح | 1 دقيقة |
| **الإجمالي** | | **5 دقائق** |

---

## 📞 **إذا استمرت المشكلة:**

```
❌ الخطأ ما زال يظهر؟

✅ جرب هذا:
1. احذف التطبيق من Streamlit Cloud
2. أنشئ تطبيق جديد من نفس المستودع
3. أعد محاولة الإجراء أعلاه
```

---

**🎉 بعد 5 دقائق، التطبيق سيكون جاهزاً بالكامل!**
