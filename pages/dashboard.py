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

    course = st.selectbox("Course", ["BCS", "BCA"])
    year = st.selectbox("Year", ["1", "2", "3"])
    semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
    academic_year = st.text_input("Academic Year (e.g. 2024-25)")

    if not academic_year:
        st.info("Please enter Academic Year to view dashboard")
        return

    data = get_short_results()

    # 🔥 FILTER DATA
    filtered_data = [
        d for d in data
        if d["course"] == course
        and d["year"] == year
        and d["semester"] == semester
        and d["academic_year"] == academic_year
    ]

    if not filtered_data:
        st.warning("No records found for selected filters.")
        return

    performance_dashboard(filtered_data)