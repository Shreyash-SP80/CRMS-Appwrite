import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

# ✅ Centralized Appwrite loaders
from backend.appwrite_db import get_short_results


# -------------------------------------------------
# Convert Appwrite data → Clean DataFrame
# -------------------------------------------------
def get_division_dataframe(filtered_data):
    if not filtered_data:
        return pd.DataFrame()

    df = pd.DataFrame(filtered_data)

    df["Percentage"] = pd.to_numeric(df["Percentage"], errors="coerce")
    df = df.dropna(subset=["Percentage"])

    return df


# -------------------------------------------------
# PDF Generator
# -------------------------------------------------
def create_division_pdf(df, div_name, min_pct, max_pct):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Sangola College - Division {div_name}", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(
        0, 10,
        f"Students with percentage between {min_pct}% and {max_pct}%",
        ln=True, align="C"
    )

    pdf.ln(8)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 8, "No", 1)
    pdf.cell(25, 8, "Seat No", 1)
    pdf.cell(80, 8, "Name", 1)
    pdf.cell(25, 8, "Percentage", 1)
    pdf.cell(30, 8, "Status", 1, ln=True)

    pdf.set_font("Arial", "", 10)

    for idx, row in enumerate(df.itertuples(index=False), 1):
        pdf.cell(10, 8, str(idx), 1)
        pdf.cell(25, 8, str(row._0), 1)   # Seat No
        pdf.cell(80, 8, row.Name[:35], 1)
        pdf.cell(25, 8, f"{row.Percentage:.2f}", 1)
        pdf.cell(30, 8, row.Status, 1, ln=True)

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S"))
    buffer.seek(0)
    return buffer



# -------------------------------------------------
# Division Analysis Page
# -------------------------------------------------
def division_analysis(df):
    st.header("📊 Custom Division Analysis")

    if df.empty:
        st.warning("No valid data available.")
        return

    # ---- Overall Stats ----
    max_percentage = df["Percentage"].max()
    failed_count = df[df["Status"].isin(["ATKT", "Fail"])].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(df))
    col2.metric("Highest Percentage", f"{max_percentage:.2f}%")
    col3.metric("Failed Students", failed_count)

    st.subheader("Set Analysis Criteria")

    col1, col2 = st.columns(2)
    with col1:
        min_pct = st.number_input(
            "Minimum Percentage",
            min_value=0.0,
            max_value=100.0,
            value=60.0,
            step=0.5
        )
    with col2:
        max_pct = st.number_input(
            "Maximum Percentage",
            min_value=0.0,
            max_value=100.0,
            value=float(max_percentage),
            step=0.5
        )

    status_filter = st.multiselect(
        "Filter by Status",
        options=["Pass", "ATKT", "Fail"],
        default=["Pass"]
    )

    if st.button("Analyze Division"):
        div_df = df[
            (df["Percentage"] >= min_pct) &
            (df["Percentage"] <= max_pct) &
            (df["Status"].isin(status_filter))
        ].sort_values(by="Name")

        st.subheader(f"Students between {min_pct}% and {max_pct}%")
        st.write(f"Found {len(div_df)} students")

        if div_df.empty:
            st.info("No students found matching the criteria.")
            return

        tab1, tab2, tab3 = st.tabs(["Data", "Visualizations", "Download"])

        with tab1:
            st.dataframe(div_df.reset_index(drop=True), hide_index=True)

        with tab2:
            col1, col2 = st.columns(2)

            with col1:
                status_counts = div_df["Status"].value_counts()
                fig1, ax1 = plt.subplots()
                ax1.pie(
                    status_counts,
                    labels=status_counts.index,
                    autopct="%1.1f%%",
                    startangle=90
                )
                ax1.set_title("Status Distribution")
                ax1.axis("equal")
                st.pyplot(fig1)

            with col2:
                div_df["Percentage Group"] = pd.cut(
                    div_df["Percentage"],
                    bins=[0, 60, 70, 80, 90, 100],
                    labels=["<60%", "60–70%", "70–80%", "80–90%", "90–100%"],
                    right=False
                )
                pct_counts = div_df["Percentage Group"].value_counts()

                fig2, ax2 = plt.subplots()
                ax2.pie(
                    pct_counts,
                    labels=pct_counts.index,
                    autopct="%1.1f%%",
                    startangle=90
                )
                ax2.set_title("Percentage Distribution")
                ax2.axis("equal")
                st.pyplot(fig2)

            fig3, ax3 = plt.subplots(figsize=(8, 4))
            ax3.hist(div_df["Percentage"], bins=15, edgecolor="black")
            ax3.set_xlabel("Percentage")
            ax3.set_ylabel("Students")
            ax3.set_title("Percentage Histogram")
            st.pyplot(fig3)

        with tab3:
            pdf = create_division_pdf(
                div_df,
                f"{min_pct}-{max_pct}",
                min_pct,
                max_pct
            )

            st.download_button(
                "📄 Download PDF",
                pdf,
                file_name=f"Division_{min_pct}_{max_pct}.pdf",
                mime="application/pdf"
            )

            csv = div_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📊 Download CSV",
                csv,
                file_name=f"Division_{min_pct}_{max_pct}.csv",
                mime="text/csv"
            )
# -------------------------------------------------
# Streamlit Entry
# -------------------------------------------------
    # def show():
    #     st.header("📊 Division Analysis")

    #     # 🔽 REQUIRED FILTERS
    #     course = st.selectbox("Course", ["BCS", "BCA"])
    #     year = st.selectbox("Year", ["1", "2", "3"])
    #     semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
    #     academic_year = st.text_input("Academic Year (e.g. 2025-26)")

    #     if not academic_year:
    #         st.info("Please enter Academic Year to continue")
    #         return

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

    #     df = get_division_dataframe(filtered_data)
    #     division_analysis(df)


def show():
    st.header("📊 Division Analysis")

    # ---------------------------
    # SESSION FLAGS
    # ---------------------------
    if "show_division_analysis" not in st.session_state:
        st.session_state.show_division_analysis = False

    # ---------------------------
    # INPUTS (WITH KEYS)
    # ---------------------------
    course = st.selectbox(
        "Course",
        ["BCS", "BCA"],
        key="div_course"
    )

    year = st.selectbox(
        "Year",
        ["1", "2", "3"],
        key="div_year"
    )

    semester = st.selectbox(
        "Semester",
        ["SEM-1", "SEM-3", "SEM-5"],
        key="div_semester"
    )

    academic_year = st.text_input(
        "Academic Year (e.g. 2025-26)",
        key="div_academic_year"
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
            "div_course",
            "div_year",
            "div_semester",
            "div_academic_year",
            "filtered_division_data",
            "show_division_analysis"
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
            st.session_state.show_division_analysis = False
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
                st.session_state.show_division_analysis = False
            else:
                st.session_state.filtered_division_data = filtered_data
                st.session_state.show_division_analysis = True

    # ---------------------------
    # 📊 DISPLAY SUMMARY + ANALYSIS
    # ---------------------------
    if st.session_state.show_division_analysis:
        st.divider()

        st.subheader("📌 Selected Result Details")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Course", course)
        col2.metric("Year", year)
        col3.metric("Semester", semester)
        col4.metric("Academic Year", academic_year)

        st.divider()

        df = get_division_dataframe(
            st.session_state.filtered_division_data
        )

        division_analysis(df)



