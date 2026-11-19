import streamlit as st

from data_store import DataStoreError, add_record, read_records
from logic import classify_duration, validate_duration, validate_subject


st.set_page_config(
    page_title="Study Time Tracker",
    page_icon="📚",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4f8ff 0%, #ffffff 42%);
    }
    .block-container {
        max-width: 860px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e4eaf3;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 8px 24px rgba(34, 64, 112, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Study Time Tracker")
st.caption("ระบบบันทึกเวลาเรียนรู้ — บันทึกและติดตามเวลาเรียนของคุณ")

st.subheader("บันทึกเวลาเรียน")
with st.form("study_record_form", clear_on_submit=True):
    subject = st.text_input("ชื่อวิชา (Subject)", placeholder="เช่น คณิตศาสตร์")
    duration = st.number_input(
        "เวลาเรียน (นาที)",
        min_value=1,
        max_value=240,
        value=30,
        step=1,
        help="ระบุเวลาเรียนตั้งแต่ 1 ถึง 240 นาที",
    )
    submitted = st.form_submit_button(
        "บันทึกเวลาเรียน",
        type="primary",
        use_container_width=True,
    )

if submitted:
    errors = [
        message
        for message in (
            validate_subject(subject),
            validate_duration(duration),
        )
        if message is not None
    ]

    if errors:
        for message in errors:
            st.error(message)
    else:
        category = classify_duration(duration)
        try:
            records = add_record(subject.strip(), duration, category)
        except DataStoreError as error:
            st.error(f"ไม่สามารถบันทึกข้อมูลได้: {error}")
        else:
            st.success("บันทึกเวลาเรียนเรียบร้อยแล้ว")

st.divider()
st.subheader("ประวัติการเรียน")

try:
    records = read_records()
except DataStoreError as error:
    st.error(f"ไม่สามารถอ่านประวัติการเรียนได้: {error}")
else:
    if records:
        display_records = [
            {
                "ชื่อวิชา": record["subject"],
                "เวลาเรียน (นาที)": record["duration"],
                "ประเภทเวลาเรียน": record["category"],
                "วันและเวลาที่บันทึก": record["timestamp"],
            }
            for record in reversed(records)
        ]
        st.dataframe(
            display_records,
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("ยังไม่มีประวัติการเรียน เริ่มบันทึกเวลาเรียนรายการแรกได้เลย")
