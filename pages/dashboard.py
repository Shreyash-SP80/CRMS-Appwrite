import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from backend.appwrite_db import get_short_results, get_detailed_results


# ✅ Appwrite backend import (MongoDB removed)
from backend.appwrite_db import load_results


# def load_data(path=None):
#     appwrite_data = load_results()

#     if not appwrite_data:
#         return []

#     mapped = []
#     for record in appwrite_data:
#         mapped.append({
#             "Seat No": record.get("seat_no", ""),
#             "Name": record.get("name", ""),
#             "Percentage": record.get("percentage", ""),
#             "Status": record.get("status", "")
#         })

#     return mapped



def performance_dashboard(data):
    st.header("📈 Performance Dashboard")
    
    if not data:
        st.warning("No data available. Please upload and process a PDF first.")
        return
    
    df = pd.DataFrame(data)

    # ✅ SAFE numeric conversion
    df['Percentage'] = pd.to_numeric(df['Percentage'], errors='coerce')
    df = df.dropna(subset=['Percentage'])

    if df.empty:
        st.warning("No valid percentage data available.")
        return
    
    avg_percentage = df['Percentage'].mean()
    pass_rate = (len(df[df['Status'] == 'Pass']) / len(df)) * 100 if len(df) else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Percentage", f"{avg_percentage:.2f}%")
    col2.metric("Pass Rate", f"{pass_rate:.2f}%")
    col3.metric("Total Students", len(df))

    tab1, tab2 = st.tabs(["Percentage Distribution", "Status Overview"])

    with tab1:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(
            df['Percentage'],
            bins=15,
            color='skyblue',
            edgecolor='black',
            density=True,
            alpha=0.7
        )

        kde = gaussian_kde(df['Percentage'])
        x = np.linspace(df['Percentage'].min(), df['Percentage'].max(), 200)
        ax.plot(x, kde(x), color='darkblue', linewidth=2)

        ax.set_xlabel('Percentage')
        ax.set_ylabel('Density')
        ax.set_title('Percentage Distribution with Density Curve')
        ax.grid(axis='y', alpha=0.75)
        st.pyplot(fig)

    with tab2:
        status_counts = df['Status'].value_counts()

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            status_counts,
            labels=status_counts.index,
            autopct='%1.1f%%',
            startangle=90
        )
        ax.set_title('Student Status Distribution')
        st.pyplot(fig)

# def show():
#     data = get_short_results()
#     performance_dashboard(data)

def show():
    st.header("📈 Performance Dashboard")

    # ---------------------------
    # SESSION FLAGS
    # ---------------------------
    if "show_dashboard" not in st.session_state:
        st.session_state.show_dashboard = False

    if "filtered_dashboard_data" not in st.session_state:
        st.session_state.filtered_dashboard_data = []

    # ---------------------------
    # INPUTS (WITH KEYS)
    # ---------------------------
    course = st.selectbox(
        "Course",
        ["BCS", "BCA"],
        key="dash_course"
    )

    year = st.selectbox(
        "Year",
        ["1", "2", "3"],
        key="dash_year"
    )

    semester = st.selectbox(
        "Semester",
        ["SEM-1", "SEM-3", "SEM-5"],
        key="dash_semester"
    )

    academic_year = st.text_input(
        "Academic Year (e.g. 2024-25)",
        key="dash_academic_year"
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
            "dash_course",
            "dash_year",
            "dash_semester",
            "dash_academic_year",
            "filtered_dashboard_data",
            "show_dashboard"
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
            st.session_state.show_dashboard = False
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
                st.session_state.show_dashboard = False
            else:
                st.session_state.filtered_dashboard_data = filtered_data
                st.session_state.show_dashboard = True

    # ---------------------------
    # 📊 DISPLAY SUMMARY + DASHBOARD
    # ---------------------------
    if st.session_state.show_dashboard:
        st.divider()

        st.subheader("📌 Selected Result Details")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Course", course)
        c2.metric("Year", year)
        c3.metric("Semester", semester)
        c4.metric("Academic Year", academic_year)

        st.divider()

        performance_dashboard(
            st.session_state.filtered_dashboard_data
        )
