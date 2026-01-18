import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ Centralized Appwrite loader
from backend.appwrite_db import get_short_results


# -------------------------------------------------
# Pass / Fail Analysis
# -------------------------------------------------
# def find_pass_fail():
#     st.header("📊 Pass / Fail Analysis")

#     # 🔽 REQUIRED FILTERS
#     course = st.selectbox("Course", ["BCS", "BCA"])
#     year = st.selectbox("Year", ["1", "2", "3"])
#     semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
#     academic_year = st.text_input("Academic Year (e.g. 2025-26)")

#     if not academic_year:
#         st.info("Please enter Academic Year to continue")
#         return

#     data = get_short_results()
#     if not data:
#         st.warning("No data available.")
#         return

#     # 🔥 FILTER DATA FIRST
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

#     df = pd.DataFrame(filtered_data)

#     # Normalize Status
#     df["Status"] = df["Status"].fillna("").str.strip()

#     passed_df = df[df["Status"] == "Pass"]
#     failed_df = df[df["Status"].isin(["ATKT", "Fail"])]

#     total = len(df)
#     passed = len(passed_df)
#     failed = len(failed_df)

#     # ---------------- KPIs ----------------
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Students", total)
#     col2.metric("Passed Students", passed)
#     col3.metric("Failed Students", failed)

#     tab1, tab2 = st.tabs(["Data", "Visualization"])

#     # ---------------- Data Tab ----------------
#     with tab1:
#         option = st.selectbox(
#             "View details for:",
#             ["All Students", "Passed Students", "Failed Students"]
#         )

#         if option == "All Students":
#             st.dataframe(df.reset_index(drop=True), hide_index=True)
#         elif option == "Passed Students":
#             st.dataframe(passed_df.reset_index(drop=True), hide_index=True)
#         else:
#             st.dataframe(failed_df.reset_index(drop=True), hide_index=True)

#     # ---------------- Visualization Tab ----------------
#     with tab2:
#         if passed == 0 and failed == 0:
#             st.warning("No valid pass/fail data available for visualization.")
#             return

#         fig1, ax1 = plt.subplots(figsize=(6, 6))

#         sizes = []
#         labels = []
#         colors = []

#         if passed > 0:
#             sizes.append(passed)
#             labels.append("Passed")
#             colors.append("#4CAF50")

#         if failed > 0:
#             sizes.append(failed)
#             labels.append("Failed")
#             colors.append("#F44336")

#         ax1.pie(
#             sizes,
#             labels=labels,
#             autopct="%1.1f%%",
#             startangle=90,
#             colors=colors,
#             wedgeprops={"linewidth": 1, "edgecolor": "white"}
#         )
#         ax1.set_title("Pass / Fail Distribution")
#         ax1.axis("equal")
#         st.pyplot(fig1)

#         fig2, ax2 = plt.subplots(figsize=(6, 4))
#         ax2.bar(labels, sizes, color=colors)
#         ax2.set_ylabel("Number of Students")
#         ax2.set_title("Pass / Fail Comparison")

#         for i, v in enumerate(sizes):
#             ax2.text(i, v + 0.5, str(v), ha="center")

#         st.pyplot(fig2)

def find_pass_fail():
    st.header("📊 Pass / Fail Analysis")

    # ---------------------------
    # SESSION FLAGS
    # ---------------------------
    if "show_pass_fail" not in st.session_state:
        st.session_state.show_pass_fail = False

    # ---------------------------
    # INPUTS (WITH KEYS)
    # ---------------------------
    course = st.selectbox(
        "Course",
        ["BCS", "BCA"],
        key="pf_course"
    )

    year = st.selectbox(
        "Year",
        ["1", "2", "3"],
        key="pf_year"
    )

    semester = st.selectbox(
        "Semester",
        ["SEM-1", "SEM-3", "SEM-5"],
        key="pf_semester"
    )

    academic_year = st.text_input(
        "Academic Year (e.g. 2025-26)",
        key="pf_academic_year"
    )

    # ---------------------------
    # BUTTONS
    # ---------------------------
    col1, col2 = st.columns(2)

    with col1:
        continue_clicked = st.button("➡️ Continue")

    with col2:
        clear_clicked = st.button("🧹 Clear")

    # ---------------------------
    # 🧹 CLEAR LOGIC
    # ---------------------------
    if clear_clicked:
        keys_to_clear = [
            "pf_course",
            "pf_year",
            "pf_semester",
            "pf_academic_year",
            "filtered_pass_fail_data",
            "show_pass_fail"
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

    # ---------------------------
    # ➡️ CONTINUE LOGIC
    # ---------------------------
    if continue_clicked:
        if not academic_year:
            st.warning("Please enter Academic Year")
            st.session_state.show_pass_fail = False
        else:
            data = get_short_results()

            if not data:
                st.warning("No data available.")
                st.session_state.show_pass_fail = False
            else:
                filtered_data = [
                    d for d in data
                    if d.get("course") == course
                    and str(d.get("year")) == str(year)
                    and d.get("semester") == semester
                    and d.get("academic_year") == academic_year
                ]

                if not filtered_data:
                    st.warning("No records found for selected filters.")
                    st.session_state.show_pass_fail = False
                else:
                    st.session_state.filtered_pass_fail_data = filtered_data
                    st.session_state.show_pass_fail = True

    # ---------------------------
    # 📊 DISPLAY SUMMARY + ANALYSIS
    # ---------------------------
    if st.session_state.show_pass_fail:
        st.divider()

        st.subheader("📌 Selected Result Details")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Course", course)
        col2.metric("Year", year)
        col3.metric("Semester", semester)
        col4.metric("Academic Year", academic_year)

        st.divider()

        # ---------------------------
        # ORIGINAL ANALYSIS LOGIC
        # ---------------------------
        df = pd.DataFrame(st.session_state.filtered_pass_fail_data)

        df["Status"] = df["Status"].fillna("").str.strip()

        passed_df = df[df["Status"] == "Pass"]
        failed_df = df[df["Status"].isin(["ATKT", "Fail"])]

        total = len(df)
        passed = len(passed_df)
        failed = len(failed_df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", total)
        col2.metric("Passed Students", passed)
        col3.metric("Failed Students", failed)

        tab1, tab2 = st.tabs(["Data", "Visualization"])

        with tab1:
            option = st.selectbox(
                "View details for:",
                ["All Students", "Passed Students", "Failed Students"],
                key="pf_view_option"
            )

            if option == "All Students":
                st.dataframe(df.reset_index(drop=True), hide_index=True)
            elif option == "Passed Students":
                st.dataframe(passed_df.reset_index(drop=True), hide_index=True)
            else:
                st.dataframe(failed_df.reset_index(drop=True), hide_index=True)

        with tab2:
            if passed == 0 and failed == 0:
                st.warning("No valid pass/fail data available for visualization.")
                return

            fig1, ax1 = plt.subplots(figsize=(6, 6))
            ax1.pie(
                [passed, failed],
                labels=["Passed", "Failed"],
                autopct="%1.1f%%",
                startangle=90,
                colors=["#4CAF50", "#F44336"],
                wedgeprops={"linewidth": 1, "edgecolor": "white"}
            )
            ax1.set_title("Pass / Fail Distribution")
            ax1.axis("equal")
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.bar(
                ["Passed", "Failed"],
                [passed, failed],
                color=["#4CAF50", "#F44336"]
            )
            ax2.set_ylabel("Number of Students")
            ax2.set_title("Pass / Fail Comparison")

            for i, v in enumerate([passed, failed]):
                ax2.text(i, v + 0.5, str(v), ha="center")

            st.pyplot(fig2)


# -------------------------------------------------
# Streamlit Entry
# -------------------------------------------------
def show():
    find_pass_fail()



