# def show():
#     data = load_data("Shoert_data")
#     detailed_data = load_data("Result_dict")
#     student_search(data, detailed_data)

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # Appwrite backend
# from backend.appwrite_db import load_results
# from backend.appwrite_db import get_short_results, get_detailed_results



# # -------------------------------------------------
# # Load & normalize Appwrite data
# # -------------------------------------------------
# # def load_data():
# #     raw = load_results()
# #     if not raw:
# #         return []

# #     normalized = []
# #     for r in raw:
# #         normalized.append({
# #             "seat_no": str(r.get("seat_no", "")),
# #             "name": str(r.get("name", "")),
# #             "percentage": str(r.get("percentage", "")),
# #             "status": str(r.get("status", "")),
# #             "code": r.get("code", []),
# #             "ua": r.get("ua", []),
# #             "ca": r.get("ca", []),
# #             "total": r.get("total", []),
# #             "status1": r.get("status1", [])
# #         })

# #     return normalized


# # -------------------------------------------------
# # Student Search
# # -------------------------------------------------
# def student_search(data):
#     st.header("🔍 Student Search")

#     if not data:
#         st.warning("No student data available.")
#         return

#     search_term = st.text_input(
#         "Search by Seat No or Name"
#     ).strip().lower()

#     if not search_term:
#         st.info("Enter a seat number or student name")
#         return

#     # 🔍 Search logic
#     results = [
#         s for s in data
#         if search_term in s["seat_no"].lower()
#         or search_term in s["name"].lower()
#     ]

#     if not results:
#         st.warning("No matching students found")
#         return

#     st.success(f"Found {len(results)} matching student(s)")

#     # -------------------------------------------------
#     # Summary table
#     # -------------------------------------------------
#     summary_df = pd.DataFrame([
#         {
#             "Seat No": s["seat_no"],
#             "Name": s["name"],
#             "Percentage": s["percentage"],
#             "Status": s["status"]
#         }
#         for s in results
#     ])

#     st.dataframe(summary_df, hide_index=True)

#     # -------------------------------------------------
#     # Select student
#     # -------------------------------------------------
#     options = [f"{s['seat_no']} - {s['name']}" for s in results]

#     selected = st.selectbox(
#         "Select a student to view detailed marks",
#         options
#     )

#     selected_seat = selected.split(" - ")[0]

#     student = next(s for s in results if s["seat_no"] == selected_seat)

#     # -------------------------------------------------
#     # Detailed marks
#     # -------------------------------------------------
#     st.subheader("📝 Detailed Marks")

#     rows = []
#     for i in range(min(
#         len(student["code"]),
#         len(student["total"]),
#         len(student["status1"])
#     )):
#         rows.append({
#             "Subject": student["code"][i],
#             "UA": student["ua"][i] if i < len(student["ua"]) else "",
#             "CA": student["ca"][i] if i < len(student["ca"]) else "",
#             "Total": student["total"][i],
#             "Status": student["status1"][i]
#         })

#     if not rows:
#         st.warning("No subject-wise data available")
#         return

#     marks_df = pd.DataFrame(rows)
#     st.dataframe(marks_df, hide_index=True)

#     # -------------------------------------------------
#     # Charts
#     # -------------------------------------------------
#     col1, col2 = st.columns(2)

#     with col1:
#         fig, ax = plt.subplots(figsize=(8, 4))
#         marks_df["Total"] = pd.to_numeric(
#             marks_df["Total"], errors="coerce"
#         ).fillna(0)

#         bars = ax.bar(
#             marks_df["Subject"],
#             marks_df["Total"],
#             color="#64B5F6"
#         )
#         ax.set_ylim(0, 100)
#         ax.set_ylabel("Marks")
#         ax.set_title("Subject-wise Marks")
#         ax.set_xticklabels(marks_df["Subject"], rotation=45, ha="right")
#         ax.bar_label(bars, fmt="%.0f")
#         st.pyplot(fig)

#     with col2:
#         total_marks = marks_df["Total"].sum()
#         passed = (marks_df["Status"] == "P").sum()

#         st.metric("Total Marks", int(total_marks))
#         st.metric("Passed Subjects", f"{passed}/{len(marks_df)}")

#         try:
#             pct = float(student["percentage"])
#             st.metric("Overall Percentage", f"{pct:.2f}%")
#         except:
#             st.metric("Overall Percentage", "N/A")


# # -------------------------------------------------
# # Streamlit entry
# # -------------------------------------------------
# def show():
#     data = get_short_results()
#     detailed_data = get_short_results
#     student_search(detailed_data)
#     # data = load_data()
#     # student_search(data)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Appwrite backend
# -------------------------------------------------
from backend.appwrite_db import get_detailed_results


# -------------------------------------------------
# Normalize data (KEY FIX)
# -------------------------------------------------
def normalize_data(raw_data):
    normalized = []

    for r in raw_data:
        normalized.append({
            "seat_no": str(r.get("seat_no", "")),
            "name": str(r.get("name", "")),
            "percentage": str(r.get("percentage", "")),
            "status": str(r.get("status", "")),

            "code": r.get("code", []) or [],
            "ua": r.get("ua", []) or [],
            "ca": r.get("ca", []) or [],
            "total": r.get("total", []) or [],
            "status1": r.get("status1", []) or [],

            # 🔥 METADATA (CRITICAL)
            "course": r.get("course", ""),
            "year": str(r.get("year", "")),
            "semester": r.get("semester", ""),
            "academic_year": r.get("academic_year", "")
        })

    return normalized


# -------------------------------------------------
# Student Search
# -------------------------------------------------
def student_search(data):
    st.header("🔍 Student Search")

    if not data:
        st.warning("No student data available.")
        return

    search_term = st.text_input(
        "Search by Seat No or Name"
    ).strip().lower()

    if not search_term:
        st.info("Enter a seat number or student name")
        return

    # ---------------- Safe Search ----------------
    results = [
        s for s in data
        if search_term in s["seat_no"].lower()
        or search_term in s["name"].lower()
    ]

    if not results:
        st.warning("No matching students found")
        return

    st.success(f"Found {len(results)} matching student(s)")

    # ---------------- Summary ----------------
    summary_df = pd.DataFrame([
        {
            "Seat No": s["seat_no"],
            "Name": s["name"],
            "Percentage": s["percentage"],
            "Status": s["status"]
        }
        for s in results
    ])

    st.dataframe(summary_df, hide_index=True)

    # ---------------- Student Selector ----------------
    options = [f"{s['seat_no']} - {s['name']}" for s in results]

    selected = st.selectbox(
        "Select a student to view detailed marks",
        options
    )

    selected_seat = selected.split(" - ")[0]
    student = next(s for s in results if s["seat_no"] == selected_seat)

    # ---------------- Detailed Marks ----------------
    st.subheader("📝 Detailed Marks")

    rows = []
    length = min(
        len(student["code"]),
        len(student["total"]),
        len(student["status1"])
    )

    for i in range(length):
        rows.append({
            "Subject": student["code"][i],
            "UA": student["ua"][i] if i < len(student["ua"]) else "",
            "CA": student["ca"][i] if i < len(student["ca"]) else "",
            "Total": student["total"][i],
            "Status": student["status1"][i]
        })

    if not rows:
        st.warning("No subject-wise data available")
        return

    marks_df = pd.DataFrame(rows)
    marks_df["Total"] = pd.to_numeric(
        marks_df["Total"], errors="coerce"
    ).fillna(0)

    st.dataframe(marks_df, hide_index=True)

    # ---------------- Charts ----------------
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(
            marks_df["Subject"],
            marks_df["Total"],
            color="#64B5F6"
        )
        ax.set_ylim(0, 100)
        ax.set_ylabel("Marks")
        ax.set_title("Subject-wise Marks")
        ax.set_xticklabels(
            marks_df["Subject"], rotation=45, ha="right"
        )
        ax.bar_label(bars, fmt="%.0f")
        st.pyplot(fig)

    with col2:
        total_marks = int(marks_df["Total"].sum())
        passed = (marks_df["Status"] == "P").sum()

        st.metric("Total Marks", total_marks)
        st.metric("Passed Subjects", f"{passed}/{len(marks_df)}")

        try:
            pct = float(student["percentage"])
            st.metric("Overall Percentage", f"{pct:.2f}%")
        except:
            st.metric("Overall Percentage", "N/A")


# -------------------------------------------------
# Streamlit Entry
# -------------------------------------------------
# def show():
#     st.header("🔍 Student Search")

#     # 🔽 REQUIRED FILTERS
#     course = st.selectbox("Course", ["BCS", "BCA"])
#     year = st.selectbox("Year", ["1", "2", "3"])
#     semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
#     academic_year = st.text_input("Academic Year (e.g. 2025-26)")

#     if not academic_year:
#         st.info("Please enter Academic Year to continue")
#         return

#     raw_data = get_detailed_results()

#     if not raw_data:
#         st.warning("No student data available.")
#         return

#     data = normalize_data(raw_data)

#     # 🔥 FILTER DATA FIRST
#     filtered_data = [
#         s for s in data
#         if s["course"] == course
#         and s["year"] == year
#         and s["semester"] == semester
#         and s["academic_year"] == academic_year
#     ]

#     if not filtered_data:
#         st.warning("No records found for selected filters.")
#         return

#     # 🔍 NOW SEARCH INSIDE FILTERED DATA
#     student_search(filtered_data)


def show():
    st.header("🔍 Student Search")

    # -----------------------------
    # Session defaults
    # -----------------------------
    if "student_continue" not in st.session_state:
        st.session_state.student_continue = False

    if "student_filtered" not in st.session_state:
        st.session_state.student_filtered = []

    # -----------------------------
    # Filters (WITH KEYS)
    # -----------------------------
    course = st.selectbox(
        "Course", ["BCS", "BCA"], key="student_course"
    )
    year = st.selectbox(
        "Year", ["1", "2", "3"], key="student_year"
    )
    semester = st.selectbox(
        "Semester", ["SEM-1", "SEM-3", "SEM-5"], key="student_sem"
    )
    academic_year = st.text_input(
        "Academic Year (e.g. 2025-26)", key="student_ay"
    )

    col1, col2 = st.columns(2)

    # -----------------------------
    # CONTINUE
    # -----------------------------
    with col1:
        if st.button("➡️ Continue"):
            st.session_state.student_continue = False
            st.session_state.student_filtered = []

            if not academic_year:
                st.warning("Please enter Academic Year")
                return

            raw_data = get_detailed_results()
            if not raw_data:
                st.warning("No student data available.")
                return

            data = normalize_data(raw_data)

            filtered = [
                s for s in data
                if s["course"] == course
                and str(s["year"]) == str(year)
                and s["semester"] == semester
                and s["academic_year"] == academic_year
            ]

            if not filtered:
                st.warning("No records found for selected filters.")
                return

            st.session_state.student_filtered = filtered
            st.session_state.student_continue = True

    # -----------------------------
    # CLEAR
    # -----------------------------
    with col2:
        if st.button("🧹 Clear"):
            for k in [
                "student_course",
                "student_year",
                "student_sem",
                "student_ay",
                "student_continue",
                "student_filtered"
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    # -----------------------------
    # SHOW SEARCH UI
    # -----------------------------
    if st.session_state.student_continue:
        st.divider()

        st.subheader("📌 Selected Result Details")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Course", course)
        c2.metric("Year", year)
        c3.metric("Semester", semester)
        c4.metric("Academic Year", academic_year)

        st.divider()

        # 🔍 SEARCH INSIDE FILTERED DATA
        student_search(st.session_state.student_filtered)


