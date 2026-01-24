#     # ---------------------------
#     # 🏆 TOP STUDENTS FEATURE
#     # ---------------------------
#     st.subheader("🏆 Top Students")

#     top_n = st.selectbox(
#         "Select Top Students",
#         options=[10, 20, 30, 40, "All"],
#         index=0
#     )

#     if top_n != "All":
#         top_students = df.head(int(top_n))
#     else:
#         top_students = df.copy()

#     col1, col2 = st.columns(2)
#     col1.metric("Total Students", len(df))
#     col2.metric("Displayed Students", len(top_students))

#     if top_students.empty:
#         st.info("No students to display.")
#         return

#     tab1, tab2 = st.tabs(["📄 Data", "📊 Visualization"])

#     # ---------------------------
#     # TABLE VIEW
#     # ---------------------------
#     with tab1:
#         st.dataframe(
#             top_students[["Rank", "Seat No", "Name", "Percentage", "Status"]],
#             hide_index=True
#         )

#     # ---------------------------
#     # VISUALIZATION
#     # ---------------------------
#     with tab2:
#         # Bar Chart
#         fig, ax = plt.subplots(figsize=(8, 5))
#         bars = ax.barh(
#             top_students["Name"].str[:20],
#             top_students["Percentage"],
#             color=plt.cm.viridis(np.linspace(0, 1, len(top_students)))
#         )
#         ax.set_xlabel("Percentage (%)")
#         ax.set_title("Top Students Performance")
#         ax.bar_label(bars, fmt="%.2f%%", padding=3)
#         ax.set_xlim(0, 100)
#         ax.invert_yaxis()
#         st.pyplot(fig)


# def show():
#     data = get_short_results()
#     find_top_ten(data)


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ✅ Appwrite backend import (MongoDB removed)
from backend.appwrite_db import load_results
from backend.appwrite_db import get_short_results, get_detailed_results


def find_top_ten(data):
    if not data:
        st.warning("No data available.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Safe numeric conversion
    df['Percentage'] = pd.to_numeric(df['Percentage'], errors='coerce')

    # Remove invalid percentages
    df = df.dropna(subset=['Percentage'])

    if df.empty:
        st.warning("No valid percentage data found.")
        return

    # Sort all students by percentage
    df = df.sort_values(by='Percentage', ascending=False).reset_index(drop=True)

    # Assign rank (ALL students)
    df["Rank"] = df.index + 1

    # ---------------------------
    # 🔍 CHECK MY RANK FEATURE
    # ---------------------------
    st.subheader("🔎 Check My Rank")

    seat_no_input = st.text_input("Enter your Seat No")

    if seat_no_input:
        student = df[df["Seat No"].astype(str) == seat_no_input.strip()]

        if student.empty:
            st.error("Seat No not found.")
        else:
            student = student.iloc[0]

            total_students = len(df)
            percentile = ((total_students - student["Rank"]) / total_students) * 100

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Seat No", student["Seat No"])
            # col2.metric("Name", student["Name"])          # ✅ NEW
            col2.metric("Rank", int(student["Rank"]))
            col3.metric("Percentage", f"{student['Percentage']:.2f}%")
            col4.metric("Percentile", f"{percentile:.2f}%")  # ✅ NEW
            st.markdown(
                f"""
                <div style="margin-top:10px;
                            padding:12px;
                            border-radius:8px;
                            background-color:#111827;
                            font-size:18px;">
                    <b>👤 Name:</b> {student["Name"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            if str(student["Status"]).lower() != "pass":
                st.error("❌ You are FAILED")
            else:
                st.success("✅ You are PASSED")
    st.markdown("---")

    # ---------------------------
    # 🏆 TOP STUDENTS FEATURE
    # ---------------------------
    st.subheader("🏆 Top Students")

    top_n = st.selectbox(
        "Select Top Students",
        options=[10, 20, 30, 40, "All"],
        index=0
    )

    if top_n != "All":
        top_students = df.head(int(top_n))
    else:
        top_students = df.copy()

    col1, col2 = st.columns(2)
    col1.metric("Total Students", len(df))
    col2.metric("Displayed Students", len(top_students))

    if top_students.empty:
        st.info("No students to display.")
        return

    tab1, tab2 = st.tabs(["📄 Data", "📊 Visualization"])

    # ---------------------------
    # TABLE VIEW
    # ---------------------------
    with tab1:
        st.dataframe(
            top_students[["Rank", "Seat No", "Name", "Percentage", "Status"]],
            hide_index=True
        )

    # ---------------------------
    # VISUALIZATION
    # ---------------------------
    with tab2:
        # Bar Chart
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(
            top_students["Name"].str[:20],
            top_students["Percentage"],
            color=plt.cm.viridis(np.linspace(0, 1, len(top_students)))
        )
        ax.set_xlabel("Percentage (%)")
        ax.set_title("Top Students Performance")
        ax.bar_label(bars, fmt="%.2f%%", padding=3)
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        st.pyplot(fig)


# def show():
#     st.header("🏆 Top Students & Rank Analysis")

#     # ---------------------------
#     # 🔽 REQUIRED FILTER INPUTS
#     # ---------------------------
#     course = st.selectbox("Course", ["BCS", "BCA"])
#     year = st.selectbox("Year", ["1", "2", "3"])
#     semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
#     academic_year = st.text_input("Academic Year (e.g. 2025-26)")

#     if not academic_year:
#         st.info("Please enter Academic Year to continue")
#         return

#     # ---------------------------
#     # 🔥 LOAD + FILTER DATA
#     # ---------------------------
#     data = get_short_results()

#     filtered_data = [
#         d for d in data
#         if d.get("course") == course
#         and d.get("year") == year
#         and d.get("semester") == semester
#         and d.get("academic_year") == academic_year
#     ]

#     if not filtered_data:
#         st.warning("No records found for selected filters.")
#         return

#     # ---------------------------
#     # ✅ SHOW RESULTS
#     # ---------------------------
#     find_top_ten(filtered_data)

# def show():
#     st.header("🏆 Top Students & Rank Analysis")

#     # ---------------------------
#     # 🔽 REQUIRED FILTER INPUTS
#     # ---------------------------
#     course = st.selectbox("Course", ["BCS", "BCA"])
#     year = st.selectbox("Year", ["1", "2", "3"])
#     semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
#     academic_year = st.text_input("Academic Year (e.g. 2025-26)")

#     # session flag
#     if "show_top_students" not in st.session_state:
#         st.session_state.show_top_students = False

#     # ---------------------------
#     # ➡️ CONTINUE BUTTON
#     # ---------------------------
#     if st.button("➡️ Continue"):
#         if not academic_year:
#             st.warning("Please enter Academic Year")
#             st.session_state.show_top_students = False
#         else:
#             data = get_short_results()

#             filtered_data = [
#                 d for d in data
#                 if d.get("course") == course
#                 and str(d.get("year")) == str(year)
#                 and d.get("semester") == semester
#                 and d.get("academic_year") == academic_year
#             ]

#             if not filtered_data:
#                 st.warning("No records found for selected filters.")
#                 st.session_state.show_top_students = False
#             else:
#                 st.session_state.filtered_top_data = filtered_data
#                 st.session_state.show_top_students = True

#     # ---------------------------
#     # ✅ DISPLAY SUMMARY + RESULTS
#     # ---------------------------
#     if st.session_state.show_top_students:
#         st.divider()

#         st.subheader("📌 Selected Result Details")
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Course", course)
#         col2.metric("Year", year)
#         col3.metric("Semester", semester)
#         col4.metric("Academic Year", academic_year)

#         st.divider()

#         find_top_ten(st.session_state.filtered_top_data)


def show():
    st.header("🏆 Top Students & Rank Analysis")

    # ---------------------------
    # INIT SESSION FLAGS
    # ---------------------------
    if "show_top_students" not in st.session_state:
        st.session_state.show_top_students = False

    # ---------------------------
    # INPUTS (WITH KEYS)
    # ---------------------------
    course = st.selectbox(
        "Course",
        ["BCS", "BCA"],
        key="top_course"
    )
    year = st.selectbox(
        "Year",
        ["1", "2", "3"],
        key="top_year"
    )
    semester = st.selectbox(
        "Semester",
        ["SEM-1", "SEM-3", "SEM-5"],
        key="top_semester"
    )
    academic_year = st.text_input(
        "Academic Year (e.g. 2025-26)",
        key="top_academic_year"
    )

    # ---------------------------
    # BUTTONS (SIDE BY SIDE)
    # ---------------------------
    col1, col2 = st.columns(2)

    with col1:
        continue_clicked = st.button("➡️ Continue")

    with col2:
        clear_clicked = st.button("🧹 Clear")

    # ---------------------------
    # CLEAR LOGIC (SAFE)
    # ---------------------------
    if clear_clicked:
        for key in [
            "top_course",
            "top_year",
            "top_semester",
            "top_academic_year",
            "filtered_top_data",
            "show_top_students"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()  # 🔥 REQUIRED

    # ---------------------------
    # CONTINUE LOGIC
    # ---------------------------
    if continue_clicked:
        if not academic_year:
            st.warning("Please enter Academic Year")
            st.session_state.show_top_students = False
        else:
            data = get_short_results()

            filtered_data = [
                d for d in data
                if d.get("course") == course
                and str(d.get("year")) == str(year)
                and d.get("semester") == semester
                and d.get("academic_year") == academic_year
            ]

            if not filtered_data:
                st.warning("No records found for selected filters.")
                st.session_state.show_top_students = False
            else:
                st.session_state.filtered_top_data = filtered_data
                st.session_state.show_top_students = True

    # ---------------------------
    # DISPLAY RESULTS
    # ---------------------------
    if st.session_state.show_top_students:
        st.divider()

        st.subheader("📌 Selected Result Details")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Course", course)
        col2.metric("Year", year)
        col3.metric("Semester", semester)
        col4.metric("Academic Year", academic_year)

        st.divider()

        find_top_ten(st.session_state.filtered_top_data)


# def show():
#     st.header("🏆 Top Students & Rank Analysis")

#     # ---------------------------
#     # 🔐 SESSION INITIALIZATION
#     # ---------------------------
#     if "show_top_students" not in st.session_state:
#         st.session_state.show_top_students = False

#     if "filtered_top_data" not in st.session_state:
#         st.session_state.filtered_top_data = []

#     # ---------------------------
#     # 🔽 REQUIRED FILTER INPUTS
#     # ---------------------------
#     course = st.selectbox(
#         "Course",
#         ["BCS", "BCA"],
#         key="top_course"
#     )

#     year = st.selectbox(
#         "Year",
#         ["1", "2", "3"],
#         key="top_year"
#     )

#     semester = st.selectbox(
#         "Semester",
#         ["SEM-1", "SEM-3", "SEM-5"],
#         key="top_semester"
#     )

#     academic_year = st.text_input(
#         "Academic Year (e.g. 2025-26)",
#         key="top_academic_year"
#     )

#     # ---------------------------
#     # ➡️ BUTTONS ROW
#     # ---------------------------
#     col_btn1, col_btn2 = st.columns(2)

#     # -------- CONTINUE --------
#     with col_btn1:
#         if st.button("➡️ Continue"):
#             if not academic_year:
#                 st.warning("Please enter Academic Year")
#                 st.session_state.show_top_students = False
#             else:
#                 data = get_short_results()

#                 filtered_data = [
#                     d for d in data
#                     if d.get("course") == course
#                     and str(d.get("year")) == str(year)
#                     and d.get("semester") == semester
#                     and d.get("academic_year") == academic_year
#                 ]

#                 if not filtered_data:
#                     st.warning("No records found for selected filters.")
#                     st.session_state.show_top_students = False
#                 else:
#                     st.session_state.filtered_top_data = filtered_data
#                     st.session_state.show_top_students = True

#     # -------- CLEAR --------
#     with col_btn2:
#         if st.button("🧹 Clear"):
#             # Reset UI state
#             st.session_state.show_top_students = False
#             st.session_state.filtered_top_data = []

#             # Clear input fields
#             st.session_state.top_course = "BCS"
#             st.session_state.top_year = "1"
#             st.session_state.top_semester = "SEM-1"
#             st.session_state.top_academic_year = ""

#             st.success("Inputs cleared")
#             st.rerun()

#     # ---------------------------
#     # ✅ DISPLAY SUMMARY + RESULTS
#     # ---------------------------
#     if st.session_state.show_top_students:
#         st.divider()

#         st.subheader("📌 Selected Result Details")
#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Course", course)
#         col2.metric("Year", year)
#         col3.metric("Semester", semester)
#         col4.metric("Academic Year", academic_year)

#         st.divider()

#         find_top_ten(st.session_state.filtered_top_data)


