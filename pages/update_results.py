
import streamlit as st
import pandas as pd

from backend.appwrite_db import (
    get_short_results,
    save_results,
    delete_all_results
)
from pages.upload_pdf import extract_student_data_from_bytes


def show():
    st.header("🔄 Update Results (Admin)")

    # -------------------------------------------------
    # 1️⃣ REQUIRED METADATA (ASK FIRST)
    # -------------------------------------------------
    st.subheader("🧾 Result Metadata")

    course = st.selectbox("Course", ["BCS", "BCA"])
    year = st.selectbox("Year", ["1", "2", "3"])
    semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
    exam_name = st.text_input("Exam Name (e.g. Winter 2025)")
    academic_year = st.text_input("Academic Year (e.g. 2025-26)")

    if not exam_name or not academic_year:
        st.info("Please enter Exam Name and Academic Year to continue")
        return

    st.divider()

    # -------------------------------------------------
    # 2️⃣ SHOW EXISTING RESULTS (AFTER METADATA)
    # -------------------------------------------------
    results = get_short_results()

    if results:
        st.subheader("📄 Existing Results")
        df = pd.DataFrame(results)
        st.dataframe(df, hide_index=True)

        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("❌ Delete All Results"):
                success = delete_all_results()

                if success:
                    st.success("All results deleted successfully")
                    st.rerun()
                else:
                    st.error("Failed to delete results")
    else:
        st.info("No results found in database")

    st.divider()

    # -------------------------------------------------
    # 3️⃣ UPLOAD & UPDATE RESULTS
    # -------------------------------------------------
    st.subheader("📤 Upload New Results (PDF)")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf"
    )

    if st.button("📥 Process & Update Results"):
        if not uploaded_file:
            st.warning("Please upload a PDF file")
            return

        with st.spinner("Processing PDF..."):
            student_data = extract_student_data_from_bytes(
                uploaded_file.getvalue(),
                course,
                year,
                semester,
                exam_name,
                academic_year
            )

        if not student_data:
            st.error("No student data found in the PDF")
            return

        success = save_results(student_data)

        if success:
            st.success("✅ Results updated successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to save results")
