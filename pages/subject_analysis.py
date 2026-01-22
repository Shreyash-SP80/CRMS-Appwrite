
#     rows = []
#     for code, stats in subject_stats.items():
#         rows.append({
#             "Subject": code,
#             "Average Marks": round(stats["total_marks"] / stats["count"], 2),
#             "Pass Rate (%)": round((stats["pass_count"] / stats["count"]) * 100, 2),
#             "Students": stats["count"],
#             "Passed": stats["pass_count"],
#             "Failed": stats["fail_count"]
#         })

#     df = pd.DataFrame(rows).sort_values("Average Marks", ascending=False)

#     # -------------------------------------------------
#     # UI
#     # -------------------------------------------------
#     col1, col2 = st.columns([1.2, 2])

#     with col1:
#         st.subheader("📄 Subject Summary")
#         st.dataframe(df.reset_index(drop=True), hide_index=True)

#     with col2:
#         st.subheader("📊 Visual Analysis")

#         tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])

#         with tab1:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Average Marks"], color="#64B5F6")
#             ax.set_ylabel("Average Marks")
#             ax.set_title("Average Marks per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.2f")
#             st.pyplot(fig)

#         with tab2:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Pass Rate (%)"], color="#81C784")
#             ax.set_ylabel("Pass Rate (%)")
#             ax.set_ylim(0, 100)
#             ax.set_title("Pass Rate per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.1f%%")
#             st.pyplot(fig)


# # -------------------------------------------------
# # Streamlit Entry
# # -------------------------------------------------
# def show():
#     raw_data = get_detailed_results()      # ✅ correct source
#     detailed_data = normalize_data(raw_data)
#     subject_analysis(detailed_data)



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Appwrite backend
# -------------------------------------------------
from backend.appwrite_db import get_detailed_results


# -------------------------------------------------
# Normalize Appwrite data (IMPORTANT)
# -------------------------------------------------
def normalize_data(student):
    return {
        "seat_no": student.get("Seat No"),
        "name": student.get("Name"),
        "prn_no": student.get("PRN No"),
        "status": student.get("Status"),
        "percentage": student.get("Percentage"),

        "code": student.get("Code", []),
        "ua": student.get("UA", []),
        "ca": student.get("CA", []),
        "total": student.get("Total", []),
        "status1": student.get("Status1", []),

        # ✅ METADATA
        "course": student.get("Course"),
        "year": str(student.get("Year")),
        "semester": student.get("Semester"),
        "exam_name": student.get("Exam"),
        "academic_year": student.get("AcademicYear"),
    }





# -------------------------------------------------
# Subject-wise Analysis
# -------------------------------------------------
def subject_analysis(detailed_data):
    st.header("📚 Subject-wise Analysis")

    if not detailed_data:
        st.warning("No detailed data available.")
        return

    subject_stats = {}

    for student in detailed_data:
        codes = student["code"]
        totals = student["total"]
        status_list = student["status1"]

        length = min(len(codes), len(totals), len(status_list))

        for i in range(length):
            code = str(codes[i]).strip()
            status = str(status_list[i]).strip()

            try:
                mark = float(totals[i])
            except:
                continue

            if not code:
                continue

            if code not in subject_stats:
                subject_stats[code] = {
                    "total_marks": 0,
                    "count": 0,
                    "pass_count": 0,
                    "fail_count": 0
                }

            subject_stats[code]["total_marks"] += mark
            subject_stats[code]["count"] += 1

            if status == "P":
                subject_stats[code]["pass_count"] += 1
            else:
                subject_stats[code]["fail_count"] += 1

    if not subject_stats:
        st.warning("No valid subject data found.")
        return

    # -------------------------------------------------
    # Build DataFrame
    # -------------------------------------------------
    rows = []
    for code, stats in subject_stats.items():
        rows.append({
            "Subject": code,
            "Average Marks": round(stats["total_marks"] / stats["count"], 2),
            "Pass Rate (%)": round((stats["pass_count"] / stats["count"]) * 100, 2),
            "Students": stats["count"],
            "Passed": stats["pass_count"],
            "Failed": stats["fail_count"]
        })

    df = pd.DataFrame(rows).sort_values("Average Marks", ascending=False)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    col1, col2 = st.columns([1.2, 2])

    with col1:
        st.subheader("📄 Subject Summary")
        st.dataframe(df.reset_index(drop=True), hide_index=True)

    with col2:
        st.subheader("📊 Visual Analysis")

        tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])

        with tab1:
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(df["Subject"], df["Average Marks"], color="#64B5F6")
            ax.set_ylabel("Average Marks")
            ax.set_title("Average Marks per Subject")
            ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
            ax.bar_label(bars, fmt="%.2f")
            st.pyplot(fig)

        with tab2:
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(df["Subject"], df["Pass Rate (%)"], color="#81C784")
            ax.set_ylabel("Pass Rate (%)")
            ax.set_ylim(0, 100)
            ax.set_title("Pass Rate per Subject")
            ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
            ax.bar_label(bars, fmt="%.1f%%")
            st.pyplot(fig)


# -------------------------------------------------
# Streamlit Entry
# -------------------------------------------------
def show():
    st.header("📚 Subject-wise Analysis")

    # -----------------------------
    # SESSION STATE DEFAULTS
    # -----------------------------
    if "subject_show" not in st.session_state:
        st.session_state.subject_show = False

    if "subject_filtered_data" not in st.session_state:
        st.session_state.subject_filtered_data = []

    # -----------------------------
    # INPUTS (WITH KEYS)
    # -----------------------------
    course = st.selectbox(
        "Course", ["BCS", "BCA"], key="sub_course"
    )
    year = st.selectbox(
        "Year", ["1", "2", "3"], key="sub_year"
    )
    semester = st.selectbox(
        "Semester", ["SEM-1", "SEM-3", "SEM-5"], key="sub_sem"
    )
    academic_year = st.text_input(
        "Academic Year (e.g. 2025-26)", key="sub_ay"
    )

    # -----------------------------
    # BUTTONS
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        continue_clicked = st.button("➡️ Continue")

    with col2:
        clear_clicked = st.button("🧹 Clear")

    # -----------------------------
    # 🧹 CLEAR LOGIC
    # -----------------------------
    if clear_clicked:
        for key in [
            "sub_course",
            "sub_year",
            "sub_sem",
            "sub_ay",
            "subject_show",
            "subject_filtered_data"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

    # -----------------------------
    # ➡️ CONTINUE LOGIC
    # -----------------------------
    if continue_clicked:
        if not academic_year:
            st.warning("Please enter Academic Year")
            st.session_state.subject_show = False
            return

        raw_data = get_detailed_results()

        if not raw_data:
            st.warning("No detailed data available.")
            st.session_state.subject_show = False
            return

        # 🔥 FILTER DIRECTLY (UNCHANGED LOGIC)
        filtered_data = [
            d for d in raw_data
            if d["course"] == course
            and str(d["year"]) == str(year)
            and d["semester"] == semester
            and d["academic_year"] == academic_year
        ]

        if not filtered_data:
            st.warning("No records found for selected filters.")
            st.session_state.subject_show = False
            return

        st.session_state.subject_filtered_data = filtered_data
        st.session_state.subject_show = True

    # -----------------------------
    # 📌 DISPLAY SUMMARY + ANALYSIS
    # -----------------------------
    if st.session_state.subject_show:
        st.divider()

        st.subheader("📌 Selected Result Details")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Course", course)
        c2.metric("Year", year)
        c3.metric("Semester", semester)
        c4.metric("Academic Year", academic_year)

        st.divider()

        subject_analysis(st.session_state.subject_filtered_data)







