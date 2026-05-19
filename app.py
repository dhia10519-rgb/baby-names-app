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
if search_query:
    filtered_df = filtered_df[filtered_df["الاسم"].str.contains(search_query, na=False)]
if gender_filter != "الكل":
    filtered_df = filtered_df[filtered_df["النوع"] == gender_filter]

# عرض الأسماء على شكل بطاقات
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        emoji = "💙" if row["النوع"] == "ولد" else "💗"
        with st.container():
            st.markdown(f"### {emoji} {row['الاسم']} ({row['النوع']})")
            st.write(f"**المعنى:** {row['معنى الاسم']}")
            if "مقترح الاسم" in row and pd.notna(row["مقترح الاسم"]):
                st.caption(f"اقترحه: {row['مقترح الاسم']}")
            st.markdown("---")
else:
    st.info("لا توجد أسماء تطابق بحثك حالياً.")

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
                "الاسم": new_name,
                "النوع": new_gender,
                "معنى الاسم": new_meaning,
                "مقترح الاسم": suggested_by
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"تمت إضافة الاسم '{new_name}' بنجاح! شكراً لمشاركتك 🎉")
            st.rerun()
