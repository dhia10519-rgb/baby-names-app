import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# إعدادات الصفحة لتظهر بشكل تطبيق هاتف أنيق
st.set_page_config(page_title="أسماء المواليد", page_icon="👶", layout="centered")

# تغيير اتجاه النص إلى العربية وتعديل التصميم
st.markdown("""
    <style>
    .stApp { direction: RTL; text-align: right; }
    div[data-testid="stForm"] { background-color: #f9f9f9; border-radius: 10px; padding: 20px; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("👶 موسوعة أسماء المواليد")
st.subheader("اكتشف اسماً لمولودك القادم، أو اقترح اسماً لأبنائك!")

# الاتصال بجدول بيانات جوجل (Google Sheets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="5m")
    # تنظيف أسماء الأعمدة لحذف أي مسافات زائدة قد تسبب خطأ
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error("جاري إعداد الاتصال بقاعدة البيانات...")
    df = pd.DataFrame(columns=["الاسم", "النوع", "معنى الاسم", "مقترح الاسم"])

# --- القسم الأول: تصفح الأسماء ---
st.header("🔍 ابحث عن اسم")

col1, col2 = st.columns(2)
with col1:
    search_query = st.text_input("ابحث عن اسم معين...")
with col2:
    gender_filter = st.selectbox("تصفية حسب الجنس:", ["الكل", "ولد", "بنت"])

# تطبيق الفلاتر على البيانات
filtered_df = df.copy()

# التأكد من وجود عمود الاسم قبل الفلترة
if "الاسم" in filtered_df.columns and search_query:
    filtered_df = filtered_df[filtered_df["الاسم"].astype(str).str.contains(search_query, na=False)]

# التأكد من وجود عمود النوع قبل الفلترة
if "النوع" in filtered_df.columns and gender_filter != "الكل":
    filtered_df = filtered_df[filtered_df["النوع"].astype(str).str.strip() == gender_filter]

# عرض الأسماء على شكل بطاقات
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        # تحديد الإيموجي المناسب بناء على النوع إن وجد
        gender_val = str(row.get("النوع", "")).strip()
        emoji = "💙" if "ولد" in gender_val else "💗" if "بنت" in gender_val else "👶"
        
        name_val = row.get("الاسم", "اسم غير معروف")
        meaning_val = row.get("معنى الاسم", "لا يوجد معنى مضاف حالياً")
        suggested_val = row.get("مقترح الاسم", "")

        with st.container():
            st.markdown(f"### {emoji} {name_val}")
            st.write(f"**المعنى:** {meaning_val}")
            if pd.notna(suggested_val) and str(suggested_val).strip() != "":
                st.caption(f"اقترحه: {suggested_val}")
            st.markdown("---")
else:
    st.info("لا توجد أسماء مضافة حالياً. كن أول من يضيف اسماً بالأسفل!")

# --- القسم الثاني: إضافة اسم جديد ---
st.header("➕ شاركنا باسم أبنائك")

with st.form(key="add_name_form", clear_on_submit=True):
    new_name = st.text_input("الاسم:")
    new_gender = st.radio("النوع:", ["ولد", "بنت"])
    new_meaning = st.text_area("معنى الاسم (إن وجد):")
    suggested_by = st.text_input("اسمك (اختياري):")
    
    submit_button = st.form_submit_button(label="إضافة الاسم للموسوعة")

    if submit_button:
        if new_name.strip() == "":
            st.warning("رجاءً اكتب الاسم أولاً!")
        else:
            new_row = pd.DataFrame([{
                "الاسم": new_name.strip(),
                "النوع": new_gender,
                "معنى الاسم": new_meaning.strip(),
                "مقترح الاسم": suggested_by.strip()
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"تمت إضافة الاسم '{new_name}' بنجاح! شكراً لمشاركتك 🎉")
            st.rerun()
