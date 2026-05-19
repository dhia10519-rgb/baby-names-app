import pandas as pd
import streamlit as st

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

st.title("👶 موسوعة أسماء المواليد التشاركية")
st.subheader("اكتشف اسماً لمولودك القادم، أو اقترح اسماً لأبنائك!")

# إنشاء قاعدة بيانات أولية داخل التطبيق مباشرة لتلافي أخطاء الربط الخارجية
if "names_db" not in st.session_state:
    st.session_state.names_db = pd.DataFrame([
        {"الاسم": "محمد", "النوع": "ولد", "معنى الاسم": "الحامد الشاكر، الكثير الخصال الحميدة", "مقترح الاسم": "أدمن التطبيق"},
        {"الاسم": "فاطمة", "النوع": "بنت", "معنى الاسم": "التي فُطِم ولدها عنها، ابنة الرسول ﷺ", "مقترح الاسم": "أدمن التطبيق"},
        {"الاسم": "يوسف", "النوع": "ولد", "معنى الاسم": "يزيد ويهب، اسم نبي الله يوسف عليه السلام", "مقترح الاسم": "أدمن التطبيق"},
        {"الاسم": "مريم", "النوع": "بنت", "معنى الاسم": "العابدة الخادمة لبيت الله، العفيفة والطاهرة", "مقترح الاسم": "أدمن التطبيق"}
    ])

df = st.session_state.names_db

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
    filtered_df = filtered_df[filtered_df["الاسم"].astype(str).str.contains(search_query, na=False)]

if gender_filter != "الكل":
    filtered_df = filtered_df[filtered_df["النوع"].astype(str).str.strip() == gender_filter]

# عرض الأسماء على شكل بطاقات
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
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
                "الاسم": new_name.strip(),
                "النوع": new_gender,
                "معنى الاسم": new_meaning.strip(),
                "مقترح الاسم": suggested_by.strip()
            }])
            # تحديث قاعدة البيانات الداخلية فوراً
            st.session_state.names_db = pd.concat([df, new_row], ignore_index=True)
            st.success(f"تمت إضافة الاسم '{new_name}' بنجاح للموسوعة الحالية 🎉")
            st.rerun()
